"""
TEMU商品标题清洗 + Redbubble搜索匹配工作流
"""

import logging
import mysql.connector
from typing import List, Dict, Optional
from ai_title_cleaner import clean_title_with_fallback
from crawler_utils import crawl_redbubble
import json

logger = logging.getLogger(__name__)


def get_db_conn():
    """获取数据库连接"""
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="123456789",
        database="redbubble_ai"
    )


def get_uncleaned_temu_products(limit: int = 50, category_id: Optional[int] = None) -> List[Dict]:
    """
    获取未清洗的TEMU商品（按时间倒序，优先处理最新爬取的商品）
    
    :param limit: 最多获取数量
    :param category_id: 类目ID过滤（可选）
    :return: 商品列表
    """
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 查询未清洗的商品（不在temu_title_cleaning表中或status='failed'的）
        query = """
            SELECT p.id, p.goods_id, p.title, p.img, p.link, p.price, p.sales_count, p.created_at
            FROM temu_products p
            LEFT JOIN temu_title_cleaning tc ON p.id = tc.product_id AND tc.status = 'completed'
            WHERE tc.id IS NULL
        """
        
        params = []
        if category_id:
            query += " AND p.category_id = %s"
            params.append(category_id)
        
        # 按时间倒序排序，优先处理最新爬取的商品
        query += " ORDER BY p.created_at DESC, p.sales_count DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, tuple(params) if params else (limit,))
        products = cursor.fetchall()
        
        logger.info(f"找到 {len(products)} 个未清洗的TEMU商品（按时间倒序）")
        return products
        
    finally:
        cursor.close()
        conn.close()


def save_title_cleaning_result(product_id: int, goods_id: str, original_title: str, 
                               cleaning_result: Dict, status: str = 'completed') -> int:
    """
    保存标题清洗结果
    
    :param product_id: TEMU商品ID
    :param goods_id: TEMU商品goods_id
    :param original_title: 原始标题
    :param cleaning_result: 清洗结果
    :param status: 状态
    :return: 插入的记录ID
    """
    conn = get_db_conn()
    cursor = conn.cursor()
    
    try:
        cleaned_keywords = cleaning_result.get('cleaned_keywords')
        keywords_list = cleaning_result.get('keywords_list', [])
        model_used = cleaning_result.get('model_used', 'unknown')
        error_message = cleaning_result.get('error') if not cleaning_result.get('success') else None
        
        cursor.execute("""
            INSERT INTO temu_title_cleaning 
            (product_id, goods_id, original_title, cleaned_keywords, keywords_json, ai_model, status, error_message)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            product_id,
            goods_id,
            original_title,
            cleaned_keywords,
            json.dumps(keywords_list, ensure_ascii=False),
            model_used,
            status,
            error_message
        ))
        
        cleaning_id = cursor.lastrowid
        conn.commit()
        
        logger.info(f"保存清洗结果成功: cleaning_id={cleaning_id}, keywords={cleaned_keywords}")
        return cleaning_id
        
    except Exception as e:
        logger.error(f"保存清洗结果失败: {e}")
        conn.rollback()
        return 0
    finally:
        cursor.close()
        conn.close()


def save_redbubble_matches(
    temu_product_id: int,
    temu_goods_id: str,
    search_keywords: str,
    redbubble_results: List[Dict],
    search_category: str
) -> int:
    """
    保存TEMU商品和Redbubble商品的匹配关系
    """
    conn = get_db_conn()
    cursor = conn.cursor()
    
    saved_count = 0
    try:
        if not redbubble_results:
            logger.warning(f"没有Redbubble匹配结果可保存: temu_product_id={temu_product_id}")
            return 0

        for idx, product in enumerate(redbubble_results, 1):
            try:
                # 1. 确保Redbubble商品存在于redbubble_products表
                # 先检查是否存在
                cursor.execute("SELECT id FROM redbubble_products WHERE link = %s", (product['link'],))
                result = cursor.fetchone()
                
                if result:
                    redbubble_product_id = result[0]
                    # 更新信息（可选）
                else:
                    # 插入新商品
                    cursor.execute("""
                        INSERT INTO redbubble_products (title, img, score, link, category)
                        VALUES (%s, %s, %s, %s, 'ai-matched')
                    """, (
                        product['title'],
                        product['img'],
                        product.get('score', 0.0),
                        product['link']
                    ))
                    redbubble_product_id = cursor.lastrowid
                
                # 2. 保存匹配关系（去除冗余字段，增加search_category）
                cursor.execute("""
                    INSERT INTO temu_redbubble_matches 
                    (temu_product_id, temu_goods_id, search_keywords, redbubble_product_id,
                     search_category, match_score, rank_position)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    temu_product_id,
                    temu_goods_id,
                    search_keywords,
                    redbubble_product_id,
                    search_category,
                    max(0.1, 1.0 - (idx - 1) * 0.05),  # 匹配分数
                    idx
                ))
                
                saved_count += 1
                
            except Exception as e:
                logger.warning(f"保存匹配记录失败: {e}")
                continue
        
        conn.commit()
        logger.info(f"成功保存 {saved_count} 条匹配记录")
        return saved_count
        
    except Exception as e:
        logger.error(f"保存匹配结果失败: {e}")
        conn.rollback()
        return 0
    finally:
        cursor.close()
        conn.close()


def process_temu_to_redbubble_workflow(
    category_id: Optional[int] = None,
    batch_size: int = 10,
    redbubble_pages: int = 2,
    redbubble_category: str = "u-socks",
    order_by: str = "time_desc"  # 新增：排序方式
) -> Dict:
    """
    完整工作流：清洗TEMU标题 → 搜索Redbubble → 保存匹配结果
    优化版：跳过已处理的商品，避免重复工作
    
    :param category_id: 类目ID（可选，为None时处理所有类目）
    :param batch_size: 每批处理数量
    :param redbubble_pages: Redbubble搜索页数
    :param redbubble_category: Redbubble搜索类目
    :param order_by: 排序方式 time_desc(时间倒序), time_asc(时间正序), sales(销量排序)
    :return: 统计信息
    """
    stats = {
        "total_checked": 0,
        "cleaned_success": 0,
        "cleaned_skipped": 0,  # 已清洗过，跳过
        "cleaned_failed": 0,
        "redbubble_searched": 0,
        "redbubble_skipped": 0,  # 已有搜索结果，跳过
        "matches_saved": 0
    }
    
    try:
        # 步骤1：获取TEMU商品（包括已清洗和未清洗的），根据排序方式选择商品
        order_by_name = {
            'time_desc': '时间倒序（最新优先）',
            'time_asc': '时间正序（最旧优先）',
            'sales': '销量排序（最热优先）'
        }.get(order_by, '时间倒序')
        
        logger.info(f"步骤1: 获取TEMU商品（batch_size={batch_size}，排序: {order_by_name}）...")
        
        conn = get_db_conn()
        cursor = conn.cursor(dictionary=True)
        
        # 查询TEMU商品
        query = """
            SELECT p.id, p.goods_id, p.title, p.img, p.link, p.price, p.sales_count, p.created_at,
                   tc.id as cleaning_id, tc.cleaned_keywords, tc.status as cleaning_status
            FROM temu_products p
            LEFT JOIN temu_title_cleaning tc ON p.id = tc.product_id
        """
        
        params = []
        if category_id:
            query += " WHERE p.category_id = %s"
            params.append(category_id)
        
        # 根据排序方式动态生成ORDER BY子句
        if order_by == "time_desc":
            query += " ORDER BY p.created_at DESC, p.sales_count DESC"
        elif order_by == "time_asc":
            query += " ORDER BY p.created_at ASC, p.sales_count DESC"
        else:  # sales
            query += " ORDER BY p.sales_count DESC, p.created_at DESC"
        
        query += " LIMIT %s"
        params.append(batch_size)
        
        cursor.execute(query, tuple(params) if params else (batch_size,))
        products = cursor.fetchall()
        
        cursor.close()
        conn.close()
        
        if not products:
            logger.info("没有需要处理的商品")
            return stats
        
        logger.info(f"找到 {len(products)} 个商品待检查")
        stats["total_checked"] = len(products)
        
        # 步骤2: 逐个处理商品
        for idx, product in enumerate(products, 1):
            product_id = product['id']
            goods_id = product['goods_id']
            title = product['title']
            cleaning_status = product.get('cleaning_status')
            cleaned_keywords = product.get('cleaned_keywords')
            
            logger.info(f"\n{'='*60}")
            logger.info(f"处理商品 {idx}/{len(products)}")
            logger.info(f"商品ID: {product_id}, goods_id: {goods_id}")
            logger.info(f"原标题: {title}")
            logger.info(f"{'='*60}")
            
            # 2.1 检查是否已清洗
            if cleaning_status == 'completed' and cleaned_keywords:
                logger.info(f"✓ 标题已清洗过，跳过清洗步骤")
                logger.info(f"  清洗后关键词: {cleaned_keywords}")
                stats["cleaned_skipped"] += 1
            else:
                # 需要清洗标题
                logger.info("→ 开始AI清洗标题...")
                cleaning_result = clean_title_with_fallback(title)
                
                if not cleaning_result.get('success'):
                    logger.error(f"✗ 标题清洗失败: {cleaning_result.get('error')}")
                    save_title_cleaning_result(product_id, goods_id, title, cleaning_result, status='failed')
                    stats["cleaned_failed"] += 1
                    continue
                
                cleaned_keywords = cleaning_result['cleaned_keywords']
                logger.info(f"✓ 清洗成功: {cleaned_keywords}")
                
                # 保存清洗结果
                cleaning_id = save_title_cleaning_result(product_id, goods_id, title, cleaning_result, status='completed')
                if cleaning_id:
                    stats["cleaned_success"] += 1
            
            # 2.2 检查是否已有该类目的Redbubble搜索结果
            conn = get_db_conn()
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) as count 
                FROM temu_redbubble_matches 
                WHERE temu_product_id = %s AND search_category = %s
            """, (product_id, redbubble_category))
            result = cursor.fetchone()
            existing_matches = result[0] if result else 0
            cursor.close()
            conn.close()
            
            if existing_matches > 0:
                logger.info(f"✓ 已有 {existing_matches} 条 '{redbubble_category}' 类目的搜索结果，跳过")
                stats["redbubble_skipped"] += 1
                continue
            
            # 2.3 使用清洗后的关键词在Redbubble搜索
            logger.info(f"→ 在Redbubble搜索关键词: {cleaned_keywords} (类目: {redbubble_category})...")
            try:
                redbubble_results = crawl_redbubble(
                    keyword=cleaned_keywords,
                    pages=redbubble_pages,
                    category=redbubble_category
                )
                
                logger.info(f"✓ Redbubble搜索完成，找到 {len(redbubble_results)} 个商品")
                stats["redbubble_searched"] += 1
                
                # 2.4 保存匹配结果
                if redbubble_results:
                    logger.info("→ 保存匹配结果...")
                    matched_count = save_redbubble_matches(
                        product_id, goods_id, cleaned_keywords, redbubble_results, 
                        search_category=redbubble_category
                    )
                    stats["matches_saved"] += matched_count
                    logger.info(f"✓ 成功保存 {matched_count} 条匹配结果")
                else:
                    logger.warning("✗ 未找到Redbubble匹配商品")
                
            except Exception as e:
                logger.error(f"✗ Redbubble搜索失败: {e}")
                import traceback
                logger.error(traceback.format_exc())
                continue
        
        logger.info(f"\n{'='*60}")
        logger.info("工作流完成！")
        logger.info(f"{'='*60}")
        logger.info(f"统计信息:")
        logger.info(f"  检查商品数: {stats['total_checked']}")
        logger.info(f"  新清洗成功: {stats['cleaned_success']}")
        logger.info(f"  已清洗跳过: {stats['cleaned_skipped']}")
        logger.info(f"  清洗失败: {stats['cleaned_failed']}")
        logger.info(f"  新搜索次数: {stats['redbubble_searched']}")
        logger.info(f"  已搜索跳过: {stats['redbubble_skipped']}")
        logger.info(f"  保存匹配数: {stats['matches_saved']}")
        logger.info(f"{'='*60}\n")
        
        return stats
        
    except Exception as e:
        logger.error(f"工作流执行失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise e



if __name__ == "__main__":
    # 测试
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    stats = process_temu_to_redbubble_workflow(
        batch_size=3,
        redbubble_pages=1
    )
    print(f"\n最终统计: {stats}")

