"""
TEMU数据库工具模块 - 负责保存TEMU相关数据到数据库
"""

import mysql.connector
import logging
import json
import hashlib
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)

def calculate_url_hash(url: str) -> str:
    """计算URL的MD5哈希值，用于唯一性检查"""
    if not url:
        return ''
    return hashlib.md5(url.encode('utf-8')).hexdigest()

def get_db_conn():
    """获取数据库连接"""
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="123456789",
        database="redbubble_ai"
    )

def save_category(category_url: str, category_name: str = None) -> Optional[int]:
    """
    保存或更新类目信息
    :return: 类目ID
    """
    conn = get_db_conn()
    cursor = conn.cursor()
    
    try:
        # 计算URL哈希值
        url_hash = calculate_url_hash(category_url)
        
        # 检查类目是否已存在（使用哈希值）
        cursor.execute("SELECT id FROM temu_categories WHERE category_url_hash = %s", (url_hash,))
        existing = cursor.fetchone()
        
        if existing:
            category_id = existing[0]
            # 更新类目信息
            if category_name:
                cursor.execute(
                    "UPDATE temu_categories SET category_name = %s, category_url = %s WHERE id = %s",
                    (category_name, category_url, category_id)
                )
        else:
            # 插入新类目
            cursor.execute(
                "INSERT INTO temu_categories (category_url, category_url_hash, category_name, status) VALUES (%s, %s, %s, 'pending')",
                (category_url, url_hash, category_name)
            )
            category_id = cursor.lastrowid
        
        conn.commit()
        return category_id
    except Exception as e:
        logger.error(f"保存类目失败: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()

def save_products(products: List[Dict], category_id: int = None, category_url: str = None) -> int:
    """
    批量保存TEMU商品（从类目页爬取的）
    :return: 成功保存的商品数量
    """
    if not products:
        return 0
    
    conn = get_db_conn()
    cursor = conn.cursor()
    saved_count = 0
    
    try:
        for product in products:
            try:
                # 检查商品是否已存在
                cursor.execute("SELECT id FROM temu_products WHERE goods_id = %s", (product.get('goods_id'),))
                existing = cursor.fetchone()
                
                # 计算链接哈希值
                link_hash = calculate_url_hash(product.get('link', ''))
                
                # 确保标题长度不超过数据库限制（1000字符）
                title = product.get('title', '')
                if title and len(title) > 1000:
                    logger.warning(f"标题过长（{len(title)}字符），截断至1000字符: {title[:50]}...")
                    title = title[:1000]
                
                if existing:
                    # 更新商品信息
                    cursor.execute("""
                        UPDATE temu_products SET
                            title = %s, img = %s, link = %s, link_hash = %s, price = %s, original_price = %s,
                            sales_count = %s, sales_text = %s, rating = %s, review_count = %s,
                            category_id = %s, category_url = %s
                        WHERE goods_id = %s
                    """, (
                        title,
                        product.get('img'),
                        product.get('link'),
                        link_hash,
                        product.get('price'),
                        product.get('original_price'),
                        product.get('sales_count', 0),
                        product.get('sales_text'),
                        product.get('rating'),
                        product.get('review_count', 0),
                        category_id,
                        category_url,
                        product.get('goods_id')
                    ))
                else:
                    # 插入新商品
                    cursor.execute("""
                        INSERT INTO temu_products (
                            goods_id, title, img, link, link_hash, price, original_price,
                            sales_count, sales_text, rating, review_count,
                            category_id, category_url
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        product.get('goods_id'),
                        title,
                        product.get('img'),
                        product.get('link'),
                        link_hash,
                        product.get('price'),
                        product.get('original_price'),
                        product.get('sales_count', 0),
                        product.get('sales_text'),
                        product.get('rating'),
                        product.get('review_count', 0),
                        category_id,
                        category_url
                    ))
                
                saved_count += 1
            except Exception as e:
                logger.warning(f"保存商品失败: {e}, goods_id: {product.get('goods_id')}")
                continue
        
        conn.commit()
        logger.info(f"成功保存 {saved_count} 个商品")
    except Exception as e:
        logger.error(f"批量保存商品失败: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    
    return saved_count

def save_product_detail(detail: Dict, product_id: int = None) -> bool:
    """
    保存商品详情信息
    :return: 是否成功
    """
    conn = get_db_conn()
    cursor = conn.cursor()
    
    try:
        goods_id = detail.get('goods_id')
        if not goods_id:
            logger.error("商品详情缺少goods_id")
            return False
        
        # 如果没有提供product_id，尝试从goods_id查找
        if not product_id:
            cursor.execute("SELECT id FROM temu_products WHERE goods_id = %s", (goods_id,))
            result = cursor.fetchone()
            if result:
                product_id = result[0]
        
        # 检查详情是否已存在
        cursor.execute("SELECT id FROM temu_product_details WHERE goods_id = %s", (goods_id,))
        existing = cursor.fetchone()
        
        images_json = json.dumps(detail.get('images', [])) if detail.get('images') else None
        
        # 计算seller_url哈希值
        seller_url_hash = calculate_url_hash(detail.get('seller_url', ''))
        
        if existing:
            # 更新详情
            cursor.execute("""
                UPDATE temu_product_details SET
                    product_id = %s, description = %s, images = %s, video_url = %s,
                    mall_id = %s, seller_name = %s, seller_url = %s, seller_url_hash = %s
                WHERE goods_id = %s
            """, (
                product_id,
                detail.get('description'),
                images_json,
                detail.get('video_url'),
                detail.get('mall_id'),
                detail.get('seller_name'),
                detail.get('seller_url'),
                seller_url_hash,
                goods_id
            ))
        else:
            # 插入新详情
            cursor.execute("""
                INSERT INTO temu_product_details (
                    goods_id, product_id, description, images, video_url,
                    mall_id, seller_name, seller_url, seller_url_hash
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                goods_id,
                product_id,
                detail.get('description'),
                images_json,
                detail.get('video_url'),
                detail.get('mall_id'),
                detail.get('seller_name'),
                detail.get('seller_url'),
                seller_url_hash
            ))
        
        # 更新商品表的mall_id和seller_url
        if product_id and detail.get('mall_id'):
            cursor.execute("""
                UPDATE temu_products SET
                    mall_id = %s, seller_url = %s, detail_crawled = TRUE, detail_crawled_at = NOW()
                WHERE id = %s
            """, (detail.get('mall_id'), detail.get('seller_url'), product_id))
        
        conn.commit()
        return True
    except Exception as e:
        logger.error(f"保存商品详情失败: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()

def save_seller(mall_id: str, seller_name: str = None, seller_url: str = None) -> Optional[int]:
    """
    保存或更新卖家信息
    :return: 卖家ID
    """
    conn = get_db_conn()
    cursor = conn.cursor()
    
    try:
        # 计算seller_url哈希值
        seller_url_hash = calculate_url_hash(seller_url or '')
        
        # 检查卖家是否已存在
        cursor.execute("SELECT id FROM temu_sellers WHERE mall_id = %s", (mall_id,))
        existing = cursor.fetchone()
        
        if existing:
            seller_id = existing[0]
            # 更新卖家信息
            if seller_name or seller_url:
                cursor.execute(
                    "UPDATE temu_sellers SET seller_name = %s, seller_url = %s, seller_url_hash = %s WHERE id = %s",
                    (seller_name, seller_url, seller_url_hash, seller_id)
                )
        else:
            # 插入新卖家
            cursor.execute(
                "INSERT INTO temu_sellers (mall_id, seller_name, seller_url, seller_url_hash, status) VALUES (%s, %s, %s, %s, 'pending')",
                (mall_id, seller_name, seller_url, seller_url_hash)
            )
            seller_id = cursor.lastrowid
        
        conn.commit()
        return seller_id
    except Exception as e:
        logger.error(f"保存卖家失败: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()

def save_seller_products(products: List[Dict], seller_id: int, mall_id: str) -> int:
    """
    批量保存店铺商品
    :return: 成功保存的商品数量
    """
    if not products:
        return 0
    
    conn = get_db_conn()
    cursor = conn.cursor()
    saved_count = 0
    
    try:
        for product in products:
            try:
                # 从链接中提取goods_id
                link = product.get('link', '')
                goods_id = None
                if "/g-" in link:
                    parts = link.split("/g-")
                    if len(parts) > 1:
                        goods_id = parts[1].split(".")[0].split("?")[0]
                
                if not goods_id:
                    continue
                
                # 确保标题长度不超过数据库限制（1000字符）
                title = product.get('title', '')
                if title and len(title) > 1000:
                    logger.warning(f"标题过长（{len(title)}字符），截断至1000字符: {title[:50]}...")
                    title = title[:1000]
                
                # 检查商品是否已存在（同一卖家的同一商品）
                cursor.execute(
                    "SELECT id FROM temu_seller_products WHERE goods_id = %s AND seller_id = %s",
                    (goods_id, seller_id)
                )
                existing = cursor.fetchone()
                
                if not existing:
                    # 计算链接哈希值
                    link_hash = calculate_url_hash(product.get('link', ''))
                    
                    # 插入新商品
                    cursor.execute("""
                        INSERT INTO temu_seller_products (
                            goods_id, seller_id, mall_id, title, img, link, link_hash, price
                        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, (
                        goods_id,
                        seller_id,
                        mall_id,
                        title,
                        product.get('img'),
                        product.get('link'),
                        link_hash,
                        product.get('price')
                    ))
                    saved_count += 1
            except Exception as e:
                logger.warning(f"保存店铺商品失败: {e}")
                continue
        
        # 更新卖家的商品数量
        cursor.execute(
            "UPDATE temu_sellers SET crawled_products = crawled_products + %s WHERE id = %s",
            (saved_count, seller_id)
        )
        
        conn.commit()
        logger.info(f"成功保存 {saved_count} 个店铺商品")
    except Exception as e:
        logger.error(f"批量保存店铺商品失败: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()
    
    return saved_count

def update_category_status(category_id: int, status: str, total_products: int = None, crawled_products: int = None):
    """更新类目状态"""
    conn = get_db_conn()
    cursor = conn.cursor()
    
    try:
        if total_products is not None and crawled_products is not None:
            cursor.execute(
                "UPDATE temu_categories SET status = %s, total_products = %s, crawled_products = %s WHERE id = %s",
                (status, total_products, crawled_products, category_id)
            )
        else:
            cursor.execute(
                "UPDATE temu_categories SET status = %s WHERE id = %s",
                (status, category_id)
            )
        conn.commit()
    except Exception as e:
        logger.error(f"更新类目状态失败: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

def update_seller_status(seller_id: int, status: str):
    """更新卖家状态"""
    conn = get_db_conn()
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "UPDATE temu_sellers SET status = %s WHERE id = %s",
            (status, seller_id)
        )
        conn.commit()
    except Exception as e:
        logger.error(f"更新卖家状态失败: {e}")
        conn.rollback()
    finally:
        cursor.close()
        conn.close()

