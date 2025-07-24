"""
图片下载和数据保存工具模块
从 crawler/download.py 和 crawler/main.py 迁移而来，适配backend环境
"""

import requests
import os
import csv
import mysql.connector
import re
import logging

# 配置日志
logger = logging.getLogger(__name__)

# 用户指定的请求头
send_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
    "Connection": "keep-alive", 
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8"
}

def download_image(url, filename):
    """
    下载图片到本地，支持代理（从环境变量 HTTP_PROXY 读取），使用用户指定的header
    :param url: 图片链接
    :param filename: 保存的文件名
    :return: 是否下载成功
    """
    try:
        # 从环境变量读取代理地址
        proxies = {
            "http": "http://127.0.0.1:7897",
            "https": "http://127.0.0.1:7897"
        }
        
        # 下载图片
        response = requests.get(url, headers=send_headers, proxies=proxies, timeout=30)
        
        if response.status_code == 200:
            # 确保目录存在
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # 保存图片
            with open(filename, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"图片下载成功: {filename}")
            return True
        else:
            logger.warning(f"下载失败: {url}，状态码: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"下载异常: {url}, 错误: {e}")
        return False

def safe_filename(title: str, idx: int) -> str:
    """
    生成安全的文件名，去除特殊字符，限制长度
    从 crawler/main.py 迁移而来
    :param title: 商品标题
    :param idx: 商品索引
    :return: 安全的文件名
    """
    # 只保留中英文、数字、下划线，空格转下划线，截断过长标题
    name = re.sub(r'[\\/:*?"<>|]', '', title)
    name = name.replace(' ', '_')
    name = name[:40]  # 最多40字符
    return f"{name}_{idx + 1}.jpg"

def save_results(results, filename="products.csv"):
    """
    保存结果到CSV文件
    从 crawler/download.py 迁移而来
    :param results: 商品数据列表
    :param filename: 保存的文件名
    """
    if not results:
        logger.warning("没有结果需要保存。")
        return
    
    try:
        # 自动获取所有字段名
        fieldnames = list(results[0].keys())
        
        with open(filename, "w", newline='', encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        
        logger.info(f"已保存结果到 {filename}")
        
    except Exception as e:
        logger.error(f"保存CSV失败: {e}")
        raise e

def get_db_connection():
    """
    获取数据库连接
    使用与api_server.py相同的连接参数
    """
    try:
        conn = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="123456789",
            database="redbubble_ai"
        )
        return conn
    except Exception as e:
        logger.error(f"数据库连接失败: {e}")
        raise e

def save_to_mysql(products):
    """
    保存商品数据到MySQL数据库
    从 crawler/download.py 迁移而来，优化了数据库连接逻辑
    :param products: 商品数据列表
    """
    if not products:
        logger.warning("没有商品数据需要保存")
        return
    
    conn = None
    cursor = None
    
    try:
        # 首先连接到MySQL服务器（不指定数据库）
        conn = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="123456789"
        )
        cursor = conn.cursor()
        
        # 创建数据库（如果不存在）
        cursor.execute("CREATE DATABASE IF NOT EXISTS redbubble_ai DEFAULT CHARACTER SET utf8mb4;")
        cursor.execute("USE redbubble_ai;")
        
        # 创建products表（如果不存在）
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS products (
          id INT PRIMARY KEY AUTO_INCREMENT,
          title VARCHAR(500) NOT NULL,
          img VARCHAR(1000) NOT NULL,
          score DECIMAL(3,2),
          link VARCHAR(1000) NOT NULL,
          local_img VARCHAR(500),
          category VARCHAR(50) DEFAULT NULL,
          created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ) DEFAULT CHARACTER SET utf8mb4;
        """)
        
        # 批量插入商品数据
        insert_count = 0
        for product in products:
            try:
                cursor.execute("""
                INSERT INTO products (title, img, score, link, local_img, category)
                VALUES (%s, %s, %s, %s, %s, %s)
                """, (
                    product['title'],
                    product['img'], 
                    product['score'],
                    product['link'],
                    product['local_img'],
                    product['category']
                ))
                insert_count += 1
                
            except Exception as e:
                logger.warning(f"插入商品数据失败: {product.get('title', 'Unknown')}, 错误: {e}")
                continue
        
        # 提交事务
        conn.commit()
        logger.info(f"成功保存 {insert_count}/{len(products)} 个商品到数据库")
        
    except Exception as e:
        logger.error(f"保存到MySQL失败: {e}")
        if conn:
            conn.rollback()
        raise e
        
    finally:
        # 关闭连接
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def create_results_directory(base_path="results"):
    """
    创建结果目录
    :param base_path: 基础路径，默认为results
    :return: 创建的目录路径
    """
    try:
        # 在backend目录下创建results目录
        results_dir = os.path.join(os.path.dirname(__file__), base_path)
        os.makedirs(results_dir, exist_ok=True)
        logger.info(f"创建结果目录: {results_dir}")
        return results_dir
    except Exception as e:
        logger.error(f"创建结果目录失败: {e}")
        raise e

def get_image_save_path(title: str, idx: int, base_path="results"):
    """
    获取图片保存路径
    :param title: 商品标题
    :param idx: 商品索引
    :param base_path: 基础路径
    :return: 完整的图片保存路径
    """
    results_dir = create_results_directory(base_path)
    filename = safe_filename(title, idx)
    return os.path.join(results_dir, filename) 