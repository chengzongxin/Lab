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
    获取未清洗的TEMU商品
    
    :param limit: 最多获取数量
    :param category_id: 类目ID过滤（可选）
    :return: 商品列表
    """
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)
    
    try:
        # 查询未清洗的商品（不在temu_title_cleaning表中或status='failed'的）
        query = """
            SELECT p.id, p.goods_id, p.title, p.img, p.link, p.price, p.sales_count
            FROM temu_products p
            LEFT JOIN temu_title_cleaning tc ON p.id = tc.product_id AND tc.status = 'completed'
            WHERE tc.id IS NULL
        """
        
        params = []
        if category_id:
            query += " AND p.category_id = %s"
            params.append(category_id)
        
        query += " ORDER BY p.sales_count DESC LIMIT %s"
        params.append(limit)
        
        cursor.execute(query, tuple(params) if params else (limit,))
        products = cursor.fetchall()
        
        logger.info(f"找到 {len(products)} 个未清洗的TEMU商品")
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


def save_redbubble_matches(temu_product_id: int, temu_goods_id: str, search_keywords: str,
                           redbubble_products: List[Dict]) -> int:
    """
    保存TEMU与Redbubble的匹配结果
    
    :param temu_product_id: TEMU商品ID
    :param temu_goods_id: TEMU商品goods_id
    :param search_keywords: 搜索关键词
    :param redbubble_products: Redbubble商品列表（已包含评分）
    :return: 保存的记录数
    """
    if not redbubble_products:
        logger.warning(f"没有Redbubble匹配结果可保存: temu_product_id={temu_product_id}")
        return 0
    
    conn = get_db_conn()
    cursor = conn.cursor()
    saved_count = 0
    
    try:
        for idx, product in enumerate(redbubble_products, 1):
            try:
                # 先保存或更新Redbubble商品到products表
                cursor.execute("""
                    SELECT id FROM products WHERE link = %s
                """, (product['link'],))
                existing = cursor.fetchone()
                
                if existing:
                    redbubble_product_id = existing[0]
                else:
                    # 插入新商品
                    cursor.execute("""
                        INSERT INTO products (title, img, score, link, category)
                        VALUES (%s, %s, %s, %s, 'ai-matched')
                    """, (
                        product['title'],
                        product['img'],
                        product.get('score', 0.0),
                        product['link']
                    ))
                    redbubble_product_id = cursor.lastrowid
                
                # 保存匹配关系
                cursor.execute("""
                    INSERT INTO temu_redbubble_matches 
                    (temu_product_id, temu_goods_id, search_keywords, redbubble_product_id,
                     redbubble_title, redbubble_img, redbubble_link, redbubble_score,
                     match_score, rank_position)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    temu_product_id,
                    temu_goods_id,
                    search_keywords,
                    redbubble_product_id,
                    product['title'],
                    product['img'],
                    product['link'],
                    product.get('score', 0.0),
                    1.0 - (idx - 1) * 0.1,  # 简单的匹配分数：排名越靠前分数越高
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
    redbubble_pages: int = 2
) -> Dict:
    """
    完整工作流：清洗TEMU标题 → 搜索Redbubble → 保存匹配结果
    
    :param category_id: 类目ID（可选，为None时处理所有类目）
    :param batch_size: 每批处理数量
    :param redbubble_pages: Redbubble搜索页数
    :return: 统计信息
    """
    stats = {
        "total_processed": 0,
        "cleaned_success": 0,
        "cleaned_failed": 0,
        "redbubble_searched": 0,
        "matches_saved": 0
    }
    
    try:
        # 步骤1：获取未清洗的TEMU商品
        logger.info(f"步骤1: 获取未清洗的TEMU商品（batch_size={batch_size}）...")
        products = get_uncleaned_temu_products(limit=batch_size, category_id=category_id)
        
        if not products:
            logger.info("没有需要处理的商品")
            return stats
        
        stats["total_processed"] = len(products)
        
        # 步骤2: 逐个处理商品
        for idx, product in enumerate(products, 1):
            product_id = product['id']
            goods_id = product['goods_id']
            title = product['title']
            
            logger.info(f"===== 处理商品 {idx}/{len(products)} =====")
            logger.info(f"商品ID: {product_id}, goods_id: {goods_id}")
            logger.info(f"原标题: {title}")
            
            # 2.1 AI清洗标题
            logger.info("步骤2.1: AI清洗标题...")
            cleaning_result = clean_title_with_fallback(title)
            
            if not cleaning_result.get('success'):
                logger.error(f"标题清洗失败: {cleaning_result.get('error')}")
                save_title_cleaning_result(product_id, goods_id, title, cleaning_result, status='failed')
                stats["cleaned_failed"] += 1
                continue
            
            cleaned_keywords = cleaning_result['cleaned_keywords']
            logger.info(f"清洗后关键词: {cleaned_keywords}")
            
            # 保存清洗结果
            cleaning_id = save_title_cleaning_result(product_id, goods_id, title, cleaning_result, status='completed')
            if cleaning_id:
                stats["cleaned_success"] += 1
            
            # 2.2 使用清洗后的关键词在Redbubble搜索
            logger.info(f"步骤2.2: 在Redbubble搜索关键词: {cleaned_keywords}...")
            try:
                redbubble_results = crawl_redbubble(
                    keyword=cleaned_keywords,
                    pages=redbubble_pages,
                    category="u-clothing"  # 默认搜索服装类
                )
                
                logger.info(f"Redbubble搜索完成，找到 {len(redbubble_results)} 个商品")
                stats["redbubble_searched"] += 1
                
                # 2.3 保存匹配结果
                if redbubble_results:
                    logger.info("步骤2.3: 保存匹配结果...")
                    matched_count = save_redbubble_matches(
                        product_id, goods_id, cleaned_keywords, redbubble_results
                    )
                    stats["matches_saved"] += matched_count
                else:
                    logger.warning("未找到Redbubble匹配商品")
                
            except Exception as e:
                logger.error(f"Redbubble搜索失败: {e}")
                continue
        
        logger.info(f"工作流完成！统计: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"工作流执行失败: {e}")
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

