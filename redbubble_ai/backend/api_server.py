from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import mysql.connector
import os
import json
import logging
from datetime import datetime
from pydantic import BaseModel
import uuid

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('backend.log', encoding='utf-8')
    ]
)

logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录，提供图片访问
# 指向backend/results目录（迁移后的图片存储位置）
# 确保 results 目录存在（在挂载之前创建）
os.makedirs("results", exist_ok=True)
app.mount("/images", StaticFiles(directory="results"), name="images")

class CrawlRequest(BaseModel):
    keyword: str = ""
    pages: int = 1
    category: str = "u-clothing"  # 默认衣服

class TemuCrawlRequest(BaseModel):
    mall_id: str  # TEMU店铺ID（必填）
    max_pages: int = 10  # 最大爬取页数（默认10页）
    use_persistent_context: bool = False  # 是否使用持久化上下文（保持登录状态）
    user_data_dir: Optional[str] = None  # 用户数据目录路径（可选）
    debug_port: Optional[int] = None  # 调试端口（连接到已打开的浏览器，例如9222）

class TemuCategoryCrawlRequest(BaseModel):
    category_url: str  # TEMU类目URL（必填）
    min_sales: int = 1000  # 最小销量（默认1000）
    crawl_details: bool = True  # 是否爬取商品详情
    crawl_seller_products: bool = True  # 是否爬取卖家店铺商品
    use_persistent_context: bool = False  # 是否使用持久化上下文
    user_data_dir: Optional[str] = None  # 用户数据目录路径
    debug_port: Optional[int] = None  # 调试端口

def get_db_conn():
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="123456789",
        database="redbubble_ai"
    )

def init_database():
    """初始化数据库，创建任务表"""
    conn = mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="123456789"
    )
    cursor = conn.cursor()
    
    # 创建数据库
    cursor.execute("CREATE DATABASE IF NOT EXISTS redbubble_ai DEFAULT CHARACTER SET utf8mb4;")
    cursor.execute("USE redbubble_ai;")
    
    # 创建商品表（Redbubble）
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
    
    # 创建TEMU类目表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS temu_categories (
      id INT PRIMARY KEY AUTO_INCREMENT,
      category_url VARCHAR(1000) NOT NULL,
      category_url_hash VARCHAR(64) NOT NULL UNIQUE,
      category_name VARCHAR(255),
      status ENUM('pending', 'crawling', 'completed', 'failed') DEFAULT 'pending',
      total_products INT DEFAULT 0,
      crawled_products INT DEFAULT 0,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      INDEX idx_category_url_hash (category_url_hash)
    ) DEFAULT CHARACTER SET utf8mb4;
    """)
    
    # 创建TEMU商品表（从类目页爬取的爆款商品）
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS temu_products (
      id INT PRIMARY KEY AUTO_INCREMENT,
      goods_id VARCHAR(50) NOT NULL UNIQUE,
      title VARCHAR(500) NOT NULL,
      img VARCHAR(1000),
      link VARCHAR(1000) NOT NULL,
      link_hash VARCHAR(64),
      price VARCHAR(50),
      original_price VARCHAR(50),
      sales_count INT DEFAULT 0,
      sales_text VARCHAR(50),
      rating DECIMAL(3,2),
      review_count INT DEFAULT 0,
      category_id INT,
      category_url VARCHAR(1000),
      mall_id VARCHAR(50),
      seller_url VARCHAR(1000),
      detail_crawled BOOLEAN DEFAULT FALSE,
      detail_crawled_at TIMESTAMP NULL,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      INDEX idx_goods_id (goods_id),
      INDEX idx_category_id (category_id),
      INDEX idx_mall_id (mall_id),
      INDEX idx_sales_count (sales_count),
      INDEX idx_detail_crawled (detail_crawled),
      INDEX idx_link_hash (link_hash),
      FOREIGN KEY (category_id) REFERENCES temu_categories(id) ON DELETE SET NULL
    ) DEFAULT CHARACTER SET utf8mb4;
    """)
    
    # 创建TEMU商品详情表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS temu_product_details (
      id INT PRIMARY KEY AUTO_INCREMENT,
      goods_id VARCHAR(50) NOT NULL UNIQUE,
      product_id INT,
      description TEXT,
      specifications TEXT,
      images TEXT,
      video_url VARCHAR(1000),
      mall_id VARCHAR(50),
      seller_name VARCHAR(255),
      seller_url VARCHAR(1000),
      seller_url_hash VARCHAR(64),
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      INDEX idx_goods_id (goods_id),
      INDEX idx_product_id (product_id),
      INDEX idx_mall_id (mall_id),
      INDEX idx_seller_url_hash (seller_url_hash),
      FOREIGN KEY (product_id) REFERENCES temu_products(id) ON DELETE CASCADE
    ) DEFAULT CHARACTER SET utf8mb4;
    """)
    
    # 创建TEMU卖家店铺表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS temu_sellers (
      id INT PRIMARY KEY AUTO_INCREMENT,
      mall_id VARCHAR(50) NOT NULL UNIQUE,
      seller_name VARCHAR(255),
      seller_url VARCHAR(1000),
      seller_url_hash VARCHAR(64),
      total_products INT DEFAULT 0,
      crawled_products INT DEFAULT 0,
      status ENUM('pending', 'crawling', 'completed', 'failed') DEFAULT 'pending',
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      INDEX idx_mall_id (mall_id),
      INDEX idx_seller_url_hash (seller_url_hash)
    ) DEFAULT CHARACTER SET utf8mb4;
    """)
    
    # 创建TEMU店铺商品表（从店铺页面爬取的）
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS temu_seller_products (
      id INT PRIMARY KEY AUTO_INCREMENT,
      goods_id VARCHAR(50) NOT NULL,
      seller_id INT,
      mall_id VARCHAR(50),
      title VARCHAR(500) NOT NULL,
      img VARCHAR(1000),
      link VARCHAR(1000) NOT NULL,
      link_hash VARCHAR(64),
      price VARCHAR(50),
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      UNIQUE KEY uk_goods_seller (goods_id, seller_id),
      INDEX idx_goods_id (goods_id),
      INDEX idx_seller_id (seller_id),
      INDEX idx_mall_id (mall_id),
      INDEX idx_link_hash (link_hash),
      FOREIGN KEY (seller_id) REFERENCES temu_sellers(id) ON DELETE CASCADE
    ) DEFAULT CHARACTER SET utf8mb4;
    """)
    
    # 创建任务表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS crawl_tasks (
        id VARCHAR(36) PRIMARY KEY,
        keyword VARCHAR(255) NOT NULL,
        pages INT NOT NULL,
        category VARCHAR(50) DEFAULT NULL,
        status ENUM('pending', 'running', 'completed', 'failed') DEFAULT 'pending',
        progress_current INT DEFAULT 0,
        progress_total INT DEFAULT 0,
        current_step VARCHAR(255) DEFAULT '',
        current_title VARCHAR(500) DEFAULT '',
        current_score DECIMAL(3,2) DEFAULT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
        completed_at TIMESTAMP NULL,
        error_message TEXT NULL
    ) DEFAULT CHARACTER SET utf8mb4;
    """)
    
    conn.commit()
    cursor.close()
    conn.close()

def create_task(keyword: str, pages: int, category: str) -> str:
    """创建新任务"""
    task_id = str(uuid.uuid4())
    conn = get_db_conn()
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO crawl_tasks (id, keyword, pages, category, status)
        VALUES (%s, %s, %s, %s, 'pending')
    """, (task_id, keyword, pages, category))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return task_id

def create_temu_task(mall_id: str, max_pages: int = 10) -> str:
    """创建TEMU爬虫任务"""
    task_id = str(uuid.uuid4())
    conn = get_db_conn()
    cursor = conn.cursor()
    
    # 使用category字段存储"temu"标识，keyword字段存储mall_id
    cursor.execute("""
        INSERT INTO crawl_tasks (id, keyword, pages, category, status)
        VALUES (%s, %s, %s, %s, 'pending')
    """, (task_id, mall_id, max_pages, "temu"))
    
    conn.commit()
    cursor.close()
    conn.close()
    
    return task_id

def get_running_tasks() -> List[dict]:
    """获取正在运行的任务"""
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT * FROM crawl_tasks 
        WHERE status IN ('pending', 'running')
        ORDER BY created_at DESC
    """)
    
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()
    
    return tasks

def get_task_status(task_id: str) -> Optional[dict]:
    """获取指定任务的状态"""
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("SELECT * FROM crawl_tasks WHERE id = %s", (task_id,))
    task = cursor.fetchone()
    
    cursor.close()
    conn.close()
    
    return task

def update_task_status(task_id: str, status: str, current: int = 0, total: int = 0, 
                      step: str = "", title: str = "", error_message: str = "", current_score: float = None):
    """更新任务状态"""
    conn = get_db_conn()
    cursor = conn.cursor()
    
    if status == 'completed':
        cursor.execute("""
            UPDATE crawl_tasks 
            SET status = %s, progress_current = %s, progress_total = %s, 
                current_step = %s, current_title = %s, current_score = %s, completed_at = NOW()
            WHERE id = %s
        """, (status, current, total, step, title, current_score, task_id))
    else:
        cursor.execute("""
            UPDATE crawl_tasks 
            SET status = %s, progress_current = %s, progress_total = %s, 
                current_step = %s, current_title = %s, error_message = %s, current_score = %s
            WHERE id = %s
        """, (status, current, total, step, title, error_message, current_score, task_id))
    
    conn.commit()
    cursor.close()
    conn.close()

def run_crawler_sync(task_id: str, keyword: str, pages: int, category: str):
    """同步运行爬虫任务的内部函数"""
    # 在函数开始就定义logger，避免作用域问题
    task_logger = logging.getLogger(__name__)
    
    try:
        # 导入迁移的工具模块（使用绝对导入）
        from crawler_utils import crawl_redbubble
        from download_utils import download_image, save_to_mysql, get_image_save_path
        from scorer_utils import nima_score
        
        task_logger.info(f"开始爬虫任务: {task_id}, 关键词: {keyword}, 页数: {pages}, 类目: {category}")
        
        # 更新任务状态为运行中
        update_task_status(task_id, "running", 0, 0, "启动爬虫")
        
        # 第一步：爬取商品信息
        update_task_status(task_id, "running", 0, 0, "正在爬取商品信息", keyword)
        items = crawl_redbubble(keyword, pages, category)
        
        if not items:
            task_logger.warning("未找到任何商品")
            update_task_status(task_id, "failed", 0, 0, "未找到商品", "", "未找到任何商品")
            return
        
        task_logger.info(f"找到 {len(items)} 个商品")
        
        # 第二步：下载图片并评分
        products = []
        total_items = len(items)
        
        for idx, item in enumerate(items):
            try:
                current_progress = idx + 1
                title = item['title'][:50] + "..." if len(item['title']) > 50 else item['title']
                
                task_logger.info(f"正在处理第 {current_progress}/{total_items} 个商品: {title}")
                update_task_status(task_id, "running", current_progress, total_items, "下载图片", title)
                
                # 获取图片保存路径
                img_path = get_image_save_path(item['title'], idx)
                
                # 下载图片
                success = download_image(item['img'], img_path)
                task_logger.info(f"图片下载成功: {success}")
                
                # AI美学评分
                score = 0.0
                if success and os.path.exists(img_path):
                    try:
                        score = nima_score(img_path)
                        task_logger.info(f"AI评分: {score:.2f}")
                    except Exception as e:
                        task_logger.warning(f"评分失败: {e}")
                        score = 0.0
                else:
                    task_logger.warning(f"图片未下载成功: {img_path}")
                    score = 0.0
                
                # 更新任务状态，包含当前评分
                update_task_status(task_id, "running", current_progress, total_items, "处理中", title, "", current_score=score)
                
                # 组装商品数据
                product = {
                    'title': item['title'],
                    'img': item['img'],
                    'score': score,
                    'link': item['link'],
                    'local_img': img_path,
                    'category': category
                }
                
                products.append(product)
                task_logger.info(f"商品处理完成: {title}, 评分: {score:.2f}")
                
            except Exception as e:
                task_logger.error(f"处理商品时出错: {e}")
                continue
        
        if not products:
            task_logger.error("没有成功处理任何商品")
            update_task_status(task_id, "failed", 0, total_items, "处理失败", "", "没有成功处理任何商品")
            return
        
        # 第三步：保存到数据库
        task_logger.info(f"成功处理 {len(products)} 个商品，正在保存到数据库...")
        update_task_status(task_id, "running", total_items, total_items, "保存数据", f"处理了{len(products)}个商品")
        
        try:
            save_to_mysql(products)
            task_logger.info("数据已保存到数据库")
            update_task_status(task_id, "completed", total_items, total_items, "爬取完成", f"成功处理{len(products)}个商品")
            task_logger.info(f"爬虫任务完成！任务ID: {task_id}, 共处理 {len(products)} 个商品")
            
        except Exception as e:
            task_logger.error(f"保存数据时出错: {e}")
            update_task_status(task_id, "failed", total_items, total_items, "保存失败", "", str(e))
            
    except Exception as e:
        task_logger.error(f"爬虫任务执行失败: {e}")
        update_task_status(task_id, "failed", 0, 0, "执行失败", "", str(e))
    finally:
        # 确保清理资源
        task_logger.info(f"爬虫任务资源清理完成: {task_id}")

async def run_crawler_async(task_id: str, keyword: str, pages: int, category: str):
    """异步运行爬虫任务 - 避免阻塞主线程"""
    import asyncio
    import concurrent.futures
    
    # 使用线程池执行同步的爬虫任务
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        try:
            await loop.run_in_executor(
                executor, 
                run_crawler_sync, 
                task_id, keyword, pages, category
            )
        except Exception as e:
            logger.error(f"异步爬虫任务执行失败: {e}")
            update_task_status(task_id, "failed", 0, 0, "异步执行失败", "", str(e))

def run_temu_crawler_sync(task_id: str, mall_id: str, max_pages: int = 10, 
                          use_persistent_context: bool = False, 
                          user_data_dir: str = None, 
                          debug_port: int = None):
    """同步运行TEMU爬虫任务的内部函数"""
    task_logger = logging.getLogger(__name__)
    
    try:
        # 导入TEMU爬虫工具模块
        from crawler_utils import crawl_temu_mall
        from download_utils import download_image, save_to_mysql, get_image_save_path
        from scorer_utils import nima_score
        
        task_logger.info(f"开始TEMU爬虫任务: {task_id}, 店铺ID: {mall_id}, 最大页数: {max_pages}")
        if debug_port:
            task_logger.info(f"使用调试端口: {debug_port}")
        if use_persistent_context:
            task_logger.info(f"使用持久化上下文: {user_data_dir or '默认目录'}")
        
        # 更新任务状态为运行中
        update_task_status(task_id, "running", 0, 0, "启动TEMU爬虫")
        
        # 第一步：爬取商品信息
        update_task_status(task_id, "running", 0, 0, "正在爬取TEMU店铺商品", f"店铺ID: {mall_id}")
        items = crawl_temu_mall(
            mall_id, 
            max_pages, 
            use_persistent_context=use_persistent_context,
            user_data_dir=user_data_dir,
            debug_port=debug_port
        )
        
        if not items:
            task_logger.warning("未找到任何商品")
            update_task_status(task_id, "failed", 0, 0, "未找到商品", "", "未找到任何商品")
            return
        
        task_logger.info(f"找到 {len(items)} 个商品")
        
        # 第二步：下载图片并评分（可选）
        products = []
        total_items = len(items)
        
        for idx, item in enumerate(items):
            try:
                current_progress = idx + 1
                title = item['title'][:50] + "..." if len(item['title']) > 50 else item['title']
                
                task_logger.info(f"正在处理第 {current_progress}/{total_items} 个商品: {title}")
                update_task_status(task_id, "running", current_progress, total_items, "下载图片", title)
                
                # 获取图片保存路径
                img_path = get_image_save_path(item['title'], idx)
                
                # 下载图片（如果有图片URL）
                success = False
                if item.get('img'):
                    success = download_image(item['img'], img_path)
                    task_logger.info(f"图片下载成功: {success}")
                else:
                    task_logger.warning("商品没有图片URL")
                
                # AI美学评分（可选，如果图片下载成功）
                score = 0.0
                if success and os.path.exists(img_path):
                    try:
                        score = nima_score(img_path)
                        task_logger.info(f"AI评分: {score:.2f}")
                    except Exception as e:
                        task_logger.warning(f"评分失败: {e}")
                        score = 0.0
                
                # 更新任务状态，包含当前评分
                update_task_status(task_id, "running", current_progress, total_items, "处理中", title, "", current_score=score)
                
                # 组装商品数据
                product = {
                    'title': item['title'],
                    'img': item.get('img', ''),
                    'score': score,
                    'link': item['link'],
                    'local_img': img_path if success else '',
                    'category': 'temu'  # 标记为TEMU商品
                }
                
                products.append(product)
                task_logger.info(f"商品处理完成: {title}, 价格: {item.get('price', 'N/A')}, 评分: {score:.2f}")
                
            except Exception as e:
                task_logger.error(f"处理商品时出错: {e}")
                continue
        
        if not products:
            task_logger.error("没有成功处理任何商品")
            update_task_status(task_id, "failed", 0, total_items, "处理失败", "", "没有成功处理任何商品")
            return
        
        # 第三步：保存到数据库
        task_logger.info(f"成功处理 {len(products)} 个商品，正在保存到数据库...")
        update_task_status(task_id, "running", total_items, total_items, "保存数据", f"处理了{len(products)}个商品")
        
        try:
            save_to_mysql(products)
            task_logger.info("数据已保存到数据库")
            update_task_status(task_id, "completed", total_items, total_items, "爬取完成", f"成功处理{len(products)}个商品")
            task_logger.info(f"TEMU爬虫任务完成！任务ID: {task_id}, 共处理 {len(products)} 个商品")
            
        except Exception as e:
            task_logger.error(f"保存数据时出错: {e}")
            update_task_status(task_id, "failed", total_items, total_items, "保存失败", "", str(e))
            
    except Exception as e:
        task_logger.error(f"TEMU爬虫任务执行失败: {e}")
        update_task_status(task_id, "failed", 0, 0, "执行失败", "", str(e))
    finally:
        # 确保清理资源
        task_logger.info(f"TEMU爬虫任务资源清理完成: {task_id}")

async def run_temu_crawler_async(task_id: str, mall_id: str, max_pages: int = 10,
                                 use_persistent_context: bool = False,
                                 user_data_dir: str = None,
                                 debug_port: int = None):
    """异步运行TEMU爬虫任务 - 避免阻塞主线程"""
    import asyncio
    import concurrent.futures
    
    # 使用线程池执行同步的爬虫任务
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        try:
            await loop.run_in_executor(
                executor, 
                run_temu_crawler_sync, 
                task_id, mall_id, max_pages, use_persistent_context, user_data_dir, debug_port
            )
        except Exception as e:
            logger.error(f"异步TEMU爬虫任务执行失败: {e}")
            update_task_status(task_id, "failed", 0, 0, "异步执行失败", "", str(e))

# 初始化数据库
init_database()

# 预加载NIMA模型（可选，提升首次评分速度）
@app.on_event("startup")
async def startup_event():
    """应用启动时的初始化"""
    try:
        logger.info("应用启动中...")
        
        # 创建results目录
        os.makedirs("results", exist_ok=True)
        logger.info("已创建results目录")
        
        # 可选：预加载NIMA模型
        # 注释掉以避免启动时间过长，首次使用时会自动加载
        # from .scorer_utils import preload_nima_model
        # if preload_nima_model():
        #     logger.info("NIMA模型预加载成功")
        # else:
        #     logger.warning("NIMA模型预加载失败，将在首次使用时加载")
            
        logger.info("应用启动完成")
        
    except Exception as e:
        logger.error(f"应用启动时出错: {e}")

@app.get("/api/products")
def get_products(category: str = None):
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)
    if category:
        cursor.execute("SELECT id, title, img, score, link, local_img, category FROM products WHERE category = %s ORDER BY id DESC", (category,))
    else:
        cursor.execute("SELECT id, title, img, score, link, local_img, category FROM products ORDER BY id DESC")
    products = cursor.fetchall()
    cursor.close()
    conn.close()
    # 处理图片路径，使用本地图片
    for product in products:
        if product.get('local_img'):
            filename = os.path.basename(product['local_img'])
            product['img'] = f"http://localhost:8000/images/{filename}"
    return products

@app.post("/api/crawl")
async def start_crawl(request: CrawlRequest, background_tasks: BackgroundTasks):
    """
    启动爬虫任务（异步后台执行）
    """
    if not request.category:
        raise HTTPException(status_code=400, detail="类目不能为空")
    if request.pages < 1 or request.pages > 10:
        raise HTTPException(status_code=400, detail="页数必须在1-10之间")
    
    # 检查是否有正在运行的任务
    running_tasks = get_running_tasks()
    if running_tasks:
        raise HTTPException(status_code=400, detail="已有任务正在运行，请等待完成")
    
    # 创建新任务
    task_id = create_task(request.keyword, request.pages, request.category)
    
    # 启动爬虫任务（异步）
    background_tasks.add_task(run_crawler_async, task_id, request.keyword, request.pages, request.category)
    
    return {
        "success": True,
        "task_id": task_id,
        "message": f"已启动爬虫任务，类目 '{request.category}'，关键词 '{request.keyword}'，页数 {request.pages}"
    }

@app.post("/api/crawl/temu")
async def start_temu_crawl(request: TemuCrawlRequest, background_tasks: BackgroundTasks):
    """
    启动TEMU店铺爬虫任务（异步后台执行）
    :param request: 包含mall_id和max_pages的请求体
    :return: 任务ID和状态信息
    """
    if not request.mall_id:
        raise HTTPException(status_code=400, detail="店铺ID不能为空")
    if request.max_pages < 1 or request.max_pages > 20:
        raise HTTPException(status_code=400, detail="最大页数必须在1-20之间")
    
    # 检查是否有正在运行的任务
    running_tasks = get_running_tasks()
    if running_tasks:
        raise HTTPException(status_code=400, detail="已有任务正在运行，请等待完成")
    
    # 创建新任务
    task_id = create_temu_task(request.mall_id, request.max_pages)
    
    # 启动TEMU爬虫任务（异步）
    background_tasks.add_task(
        run_temu_crawler_async, 
        task_id, 
        request.mall_id, 
        request.max_pages,
        request.use_persistent_context,
        request.user_data_dir,
        request.debug_port
    )
    
    message = f"已启动TEMU爬虫任务，店铺ID: {request.mall_id}，最大页数: {request.max_pages}"
    if request.debug_port:
        message += f"，调试端口: {request.debug_port}"
    if request.use_persistent_context:
        message += f"，使用持久化上下文: {request.user_data_dir or '默认目录'}"
    
    return {
        "success": True,
        "task_id": task_id,
        "message": message
    }

@app.post("/api/crawl/temu/category")
async def start_temu_category_crawl(request: TemuCategoryCrawlRequest, background_tasks: BackgroundTasks):
    """
    启动TEMU类目完整爬取工作流（异步后台执行）
    包括：爬取类目爆款商品 -> 爬取商品详情 -> 爬取卖家店铺商品
    """
    if not request.category_url:
        raise HTTPException(status_code=400, detail="类目URL不能为空")
    if request.min_sales < 0:
        raise HTTPException(status_code=400, detail="最小销量不能小于0")
    
    # 检查是否有正在运行的任务
    running_tasks = get_running_tasks()
    if running_tasks:
        raise HTTPException(status_code=400, detail="已有任务正在运行，请等待完成")
    
    # 创建任务ID
    task_id = str(uuid.uuid4())
    
    # 启动完整工作流（异步）
    background_tasks.add_task(
        run_temu_category_workflow_async,
        task_id,
        request.category_url,
        request.min_sales,
        request.crawl_details,
        request.crawl_seller_products,
        request.use_persistent_context,
        request.user_data_dir,
        request.debug_port
    )
    
    message = f"已启动TEMU类目爬取工作流，类目URL: {request.category_url[:50]}...，最小销量: {request.min_sales}"
    if request.debug_port:
        message += f"，调试端口: {request.debug_port}"
    
    return {
        "success": True,
        "task_id": task_id,
        "message": message
    }

async def run_temu_category_workflow_async(
    task_id: str,
    category_url: str,
    min_sales: int,
    crawl_details: bool,
    crawl_seller_products: bool,
    use_persistent_context: bool,
    user_data_dir: str,
    debug_port: int
):
    """异步运行TEMU类目完整工作流"""
    import asyncio
    import concurrent.futures
    from crawler_utils import crawl_temu_category_full_workflow
    
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
        try:
            stats = await loop.run_in_executor(
                executor,
                crawl_temu_category_full_workflow,
                category_url,
                min_sales,
                crawl_details,
                crawl_seller_products,
                use_persistent_context,
                user_data_dir,
                debug_port
            )
            logger.info(f"TEMU类目工作流完成: {stats}")
        except Exception as e:
            logger.error(f"TEMU类目工作流执行失败: {e}")

@app.get("/api/crawl/status")
def get_crawl_status():
    """
    获取当前爬虫任务状态
    """
    running_tasks = get_running_tasks()
    
    if not running_tasks:
        return {
            "has_running_task": False,
            "current_task": None
        }
    
    # 返回最新的运行中任务
    current_task = running_tasks[0]
    
    return {
        "has_running_task": True,
        "current_task": {
            "id": current_task["id"],
            "keyword": current_task["keyword"],
            "pages": current_task["pages"],
            "status": current_task["status"],
            "progress": {
                "current": current_task["progress_current"],
                "total": current_task["progress_total"]
            },
            "step": current_task["current_step"],
            "title": current_task["current_title"],
            "current_score": current_task.get("current_score"),
            "created_at": current_task["created_at"].isoformat() if current_task["created_at"] else None,
            "updated_at": current_task["updated_at"].isoformat() if current_task["updated_at"] else None
        }
    }

@app.get("/api/crawl/tasks")
def get_all_tasks():
    """
    获取所有任务历史
    """
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)
    
    cursor.execute("""
        SELECT * FROM crawl_tasks 
        ORDER BY created_at DESC 
        LIMIT 20
    """)
    
    tasks = cursor.fetchall()
    cursor.close()
    conn.close()
    
    # 处理时间格式
    for task in tasks:
        if task["created_at"]:
            task["created_at"] = task["created_at"].isoformat()
        if task["updated_at"]:
            task["updated_at"] = task["updated_at"].isoformat()
        if task["completed_at"]:
            task["completed_at"] = task["completed_at"].isoformat()
    
    return tasks

@app.delete("/api/crawl/tasks/{task_id}")
def cancel_task(task_id: str):
    """
    取消指定任务
    """
    task = get_task_status(task_id)
    if not task:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    if task["status"] not in ["pending", "running"]:
        raise HTTPException(status_code=400, detail="只能取消待执行或运行中的任务")
    
    update_task_status(task_id, "failed", 0, 0, "已取消", "", "用户取消")
    
    return {"success": True, "message": "任务已取消"}

@app.get("/api/crawl/status")
def get_crawl_status():
    """
    获取爬虫状态
    """
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) as count FROM products")
        result = cursor.fetchone()
        total_products = result[0] if result else 0
        
        cursor.execute("SELECT AVG(score) as avg_score FROM products WHERE score IS NOT NULL")
        result = cursor.fetchone()
        avg_score = float(result[0]) if result and result[0] else 0
        
        cursor.execute("SELECT COUNT(*) as high_score_count FROM products WHERE score >= 7")
        result = cursor.fetchone()
        high_score_count = result[0] if result else 0
        
        cursor.close()
        conn.close()
        
        return {
            "total_products": total_products,
            "average_score": round(avg_score, 2),
            "high_score_products": high_score_count,
            "last_updated": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取状态失败: {str(e)}")

@app.delete("/api/products")
def clear_products():
    """
    清空所有商品数据
    """
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM products")
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"success": True, "message": "已清空所有商品数据"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"清空数据失败: {str(e)}")

@app.post("/api/proxy/reset")
def reset_proxy_cache_api():
    """
    重置代理配置缓存，下次下载时会重新检测代理
    """
    try:
        from download_utils import reset_proxy_cache
        reset_proxy_cache()
        return {"success": True, "message": "代理配置缓存已重置，下次下载时会重新检测"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重置代理缓存失败: {str(e)}")

@app.get("/api/crawl_status")
def get_crawler_progress():
    """
    获取爬虫实时进度（兼容旧版本）
    """
    status_path = os.path.join(os.path.dirname(__file__), "..", "crawler", "crawler_status.json")
    try:
        if os.path.exists(status_path):
            with open(status_path, "r", encoding="utf-8") as f:
                return json.load(f)
        else:
            return {"step": "空闲", "current": 0, "total": 0, "title": ""}
    except Exception as e:
        return {"step": "空闲", "current": 0, "total": 0, "title": "", "error": str(e)} 


if __name__ == "__main__":
    run_crawler("123", "animal", 1, "u-socks")