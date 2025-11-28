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

# 代理配置缓存
_proxy_config_cache = None
_proxy_checked = False

# 用户指定的请求头
send_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
    "Connection": "keep-alive", 
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8"
}

def get_proxy_config(force_refresh=False):
    """
    智能获取代理配置，支持多种方式：
    1. 环境变量 HTTP_PROXY 和 HTTPS_PROXY
    2. 常见代理端口自动检测
    3. 无代理模式
    :param force_refresh: 是否强制重新检测（忽略缓存）
    :return: 代理配置字典或None
    """
    global _proxy_config_cache, _proxy_checked
    
    # 如果已经检测过且不强制刷新，直接返回缓存结果
    if _proxy_checked and not force_refresh:
        return _proxy_config_cache
    
    logger.info("开始检测代理配置...")
    
    # 方法1：从环境变量读取代理
    http_proxy = os.environ.get('HTTP_PROXY') or os.environ.get('http_proxy')
    https_proxy = os.environ.get('HTTPS_PROXY') or os.environ.get('https_proxy')
    
    if http_proxy or https_proxy:
        proxies = {}
        if http_proxy:
            proxies['http'] = http_proxy
        if https_proxy:
            proxies['https'] = https_proxy
        logger.info(f"使用环境变量代理: {proxies}")
        _proxy_config_cache = proxies
        _proxy_checked = True
        return proxies
    
    # 方法2：检测常见代理端口
    common_proxy_ports = [7897, 7890, 1087, 1080, 8118, 8080]
    for port in common_proxy_ports:
        proxy_url = f"http://127.0.0.1:{port}"
        if test_proxy_connection(proxy_url):
            proxies = {
                "http": proxy_url,
                "https": proxy_url
            }
            logger.info(f"检测到可用代理: {proxy_url}")
            _proxy_config_cache = proxies
            _proxy_checked = True
            return proxies
    
    # 方法3：无代理模式
    logger.info("未检测到可用代理，使用直连模式")
    _proxy_config_cache = None
    _proxy_checked = True
    return None

def reset_proxy_cache():
    """
    重置代理配置缓存，下次调用时会重新检测
    适用于代理环境发生变化的情况
    """
    global _proxy_config_cache, _proxy_checked
    _proxy_config_cache = None
    _proxy_checked = False
    logger.info("代理配置缓存已重置")

def test_proxy_connection(proxy_url, timeout=3):
    """
    测试代理连接是否可用
    :param proxy_url: 代理URL
    :param timeout: 超时时间（秒）
    :return: 是否可用
    """
    try:
        proxies = {"http": proxy_url, "https": proxy_url}
        # 使用一个轻量级的测试URL
        response = requests.get(
            "http://httpbin.org/ip", 
            proxies=proxies, 
            timeout=timeout,
            headers={"User-Agent": "ProxyTest"}
        )
        return response.status_code == 200
    except:
        return False

def download_image(url, filename):
    """
    下载图片到本地，智能使用代理配置
    :param url: 图片链接
    :param filename: 保存的文件名
    :return: 是否下载成功
    """
    try:
        # 获取代理配置
        proxies = get_proxy_config()
        
        # 下载图片（先尝试使用代理，失败后尝试直连）
        response = None
        
        # 尝试使用代理下载
        if proxies:
            try:
                response = requests.get(url, headers=send_headers, proxies=proxies, timeout=30)
                if response.status_code != 200:
                    logger.warning(f"代理下载失败，状态码: {response.status_code}，尝试直连")
                    response = None
            except Exception as e:
                logger.warning(f"代理下载异常: {e}，尝试直连")
                response = None
        
        # 如果代理失败或无代理，尝试直连
        if response is None:
            response = requests.get(url, headers=send_headers, timeout=30)
        
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
        
        # 创建redbubble_products表（如果不存在）
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS redbubble_products (
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
                INSERT INTO redbubble_products (title, img, score, link, local_img, category)
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