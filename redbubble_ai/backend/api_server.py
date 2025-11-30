from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional, Dict
import mysql.connector
import os
import json
import logging
from datetime import datetime
from pydantic import BaseModel
import uuid

# 加载.env环境变量
from dotenv import load_dotenv
load_dotenv()  # 这会自动加载当前目录的.env文件

# 导入AI调试工具
from ai_debugger import chat_with_ai, get_presets

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
    category: str = "u-socks"  # 默认袜子

class TemuCrawlRequest(BaseModel):
    mall_id: str  # TEMU店铺ID（必填）
    max_pages: int = 10  # 最大爬取页数（默认10页）
    use_persistent_context: bool = False  # 是否使用持久化上下文（保持登录状态）
    user_data_dir: Optional[str] = None  # 用户数据目录路径（可选）
    debug_port: Optional[int] = None  # 调试端口（连接到已打开的浏览器，例如9222）

class TemuCategoryCrawlRequest(BaseModel):
    category_url: str  # TEMU类目URL（必填）
    max_pages: int = 10  # 最大滚动次数（默认10次）
    min_sales: int = 200  # 最小销量（默认200）
    crawl_details: bool = False  # 是否爬取商品详情（暂时禁用）
    crawl_seller_products: bool = False  # 是否爬取卖家店铺商品（暂时禁用）
    use_persistent_context: bool = False  # 是否使用持久化上下文
    user_data_dir: Optional[str] = None  # 用户数据目录路径
    debug_port: Optional[int] = None  # 调试端口

class TemuAIWorkflowRequest(BaseModel):
    category_id: Optional[int] = None  # 类目ID（可选，为None时处理所有类目）
    batch_size: int = 10  # 每批处理数量（默认10）
    redbubble_pages: int = 1  # Redbubble搜索页数（默认1页）
    redbubble_category: str = "u-socks"  # Redbubble搜索类目（默认袜子）
    order_by: str = "time_desc"  # 排序方式：time_desc(时间倒序), time_asc(时间正序), sales(销量排序)

class TemuSellerCrawlRequest(BaseModel):
    mall_id: str  # 卖家店铺ID（必填）
    max_pages: int = 10  # 最多滚动加载次数（默认10次）
    min_sales: int = 0  # 最小销量过滤（默认0，不过滤）
    use_persistent_context: bool = False  # 是否使用持久化上下文
    user_data_dir: Optional[str] = None  # 用户数据目录
    debug_port: Optional[int] = None  # 调试端口

class AIDebuggerChatRequest(BaseModel):
    messages: List[Dict[str, str]]  # 消息列表
    model: str = "gpt-4o-mini"  # 模型名称
    temperature: float = 0.7  # 温度参数
    max_tokens: int = 500  # 最大token数

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
    
    # 创建Redbubble商品表
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
      seller_name VARCHAR(255),
      seller_avatar VARCHAR(1000),
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
    
    # 创建TEMU标题清洗记录表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS temu_title_cleaning (
      id INT PRIMARY KEY AUTO_INCREMENT,
      product_id INT NOT NULL,
      goods_id VARCHAR(50),
      original_title VARCHAR(1000) NOT NULL,
      cleaned_keywords TEXT,
      keywords_json JSON,
      ai_model VARCHAR(50) DEFAULT 'gpt-4',
      status ENUM('pending', 'processing', 'completed', 'failed') DEFAULT 'pending',
      error_message TEXT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
      INDEX idx_product_id (product_id),
      INDEX idx_goods_id (goods_id),
      INDEX idx_status (status),
      FOREIGN KEY (product_id) REFERENCES temu_products(id) ON DELETE CASCADE
    ) DEFAULT CHARACTER SET utf8mb4;
    """)
    
    # 创建TEMU商品与Redbubble搜索关联表
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS temu_redbubble_matches (
      id INT PRIMARY KEY AUTO_INCREMENT,
      temu_product_id INT NOT NULL,
      temu_goods_id VARCHAR(50),
      search_keywords TEXT NOT NULL,
      redbubble_product_id INT,
      search_category VARCHAR(50) DEFAULT 'u-socks',
      match_score DECIMAL(5,4),
      rank_position INT,
      created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
      INDEX idx_temu_product_id (temu_product_id),
      INDEX idx_temu_goods_id (temu_goods_id),
      INDEX idx_redbubble_product_id (redbubble_product_id),
      INDEX idx_match_score (match_score),
      FOREIGN KEY (temu_product_id) REFERENCES temu_products(id) ON DELETE CASCADE,
      FOREIGN KEY (redbubble_product_id) REFERENCES redbubble_products(id) ON DELETE SET NULL
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
        from redbubble_crawler import crawl_redbubble
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


# 初始化数据库
init_database()

@app.post("/api/temu/ai-workflow")
async def start_temu_ai_workflow(request: TemuAIWorkflowRequest, background_tasks: BackgroundTasks):
    """
    启动TEMU商品标题AI清洗 + Redbubble搜索匹配工作流
    工作流程：
    1. 获取未清洗的TEMU商品
    2. 使用AI清洗标题，提取核心关键词
    3. 用关键词在Redbubble搜索相关商品
    4. 保存匹配关系
    """
    import asyncio
    from concurrent.futures import ThreadPoolExecutor
    from temu_ai_workflow import process_temu_to_redbubble_workflow
    
    task_id = str(uuid.uuid4())
    
    async def run_ai_workflow():
        """异步执行AI工作流"""
        try:
            logger.info(f"开始执行TEMU AI工作流: task_id={task_id}")
            logger.info(f"参数: category_id={request.category_id}, batch_size={request.batch_size}, redbubble_pages={request.redbubble_pages}, order_by={request.order_by}")
            
            # 在线程池中执行同步的工作流函数
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                stats = await loop.run_in_executor(
                    executor,
                    process_temu_to_redbubble_workflow,
                    request.category_id,
                    request.batch_size,
                    request.redbubble_pages,
                    request.redbubble_category,
                    request.order_by  # 传递排序参数
                )
            
            logger.info(f"TEMU AI工作流执行完成: {stats}")
            
        except Exception as e:
            logger.error(f"TEMU AI工作流执行失败: {e}")
            import traceback
            logger.error(traceback.format_exc())
    
    # 添加后台任务
    background_tasks.add_task(run_ai_workflow)
    
    # 排序方式描述
    order_by_desc = {
        'time_desc': '按时间倒序（最新优先）',
        'time_asc': '按时间正序（最旧优先）',
        'sales': '按销量排序（最热优先）'
    }.get(request.order_by, '按时间倒序')
    
    return {
        "success": True,
        "task_id": task_id,
        "message": f"已启动TEMU AI清洗工作流，批量处理 {request.batch_size} 个商品（{order_by_desc}）"
    }

@app.get("/api/temu/ai-workflow/stats")
def get_ai_workflow_stats(category_id: Optional[int] = None):
    """
    获取AI工作流统计信息
    """
    try:
        conn = get_db_conn()
        cursor = conn.cursor(dictionary=True)
        
        # 清洗统计
        query = "SELECT COUNT(*) as total, SUM(CASE WHEN status='completed' THEN 1 ELSE 0 END) as completed FROM temu_title_cleaning"
        params = []
        
        if category_id:
            query += " WHERE product_id IN (SELECT id FROM temu_products WHERE category_id = %s)"
            params.append(category_id)
        
        cursor.execute(query, tuple(params) if params else ())
        cleaning_stats = cursor.fetchone()
        
        # 匹配统计
        query = "SELECT COUNT(DISTINCT temu_product_id) as matched_products, COUNT(*) as total_matches FROM temu_redbubble_matches"
        if category_id:
            query += " WHERE temu_product_id IN (SELECT id FROM temu_products WHERE category_id = %s)"
        
        cursor.execute(query, tuple(params) if params else ())
        match_stats = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        return {
            "cleaning": {
                "total": cleaning_stats['total'] or 0,
                "completed": cleaning_stats['completed'] or 0
            },
            "matches": {
                "matched_products": match_stats['matched_products'] or 0,
                "total_matches": match_stats['total_matches'] or 0
            }
        }
        
    except Exception as e:
        logger.error(f"获取AI工作流统计失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取统计信息失败: {str(e)}")

@app.get("/api/temu/matches")
def get_temu_matches(
    limit: int = 50,
    offset: int = 0,
    category_id: Optional[int] = None,
    min_match_score: float = 0.5
):
    """
    获取TEMU商品与Redbubble的匹配结果
    """
    try:
        conn = get_db_conn()
        cursor = conn.cursor(dictionary=True)
        
        query = """
            SELECT 
                m.id,
                m.temu_product_id,
                m.temu_goods_id,
                tp.title as temu_title,
                tp.img as temu_img,
                tp.price as temu_price,
                tp.sales_count,
                m.search_keywords,
                m.redbubble_title,
                m.redbubble_img,
                m.redbubble_link,
                m.redbubble_score,
                m.match_score,
                m.rank_position,
                m.created_at
            FROM temu_redbubble_matches m
            LEFT JOIN temu_products tp ON m.temu_product_id = tp.id
            WHERE m.match_score >= %s
        """
        params = [min_match_score]
        
        if category_id:
            query += " AND tp.category_id = %s"
            params.append(category_id)
        
        query += " ORDER BY tp.sales_count DESC, m.match_score DESC LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(query, tuple(params))
        matches = cursor.fetchall()
        
        # 获取总数
        count_query = """
            SELECT COUNT(*) as total
            FROM temu_redbubble_matches m
            LEFT JOIN temu_products tp ON m.temu_product_id = tp.id
            WHERE m.match_score >= %s
        """
        count_params = [min_match_score]
        if category_id:
            count_query += " AND tp.category_id = %s"
            count_params.append(category_id)
        
        cursor.execute(count_query, tuple(count_params))
        total = cursor.fetchone()['total']
        
        cursor.close()
        conn.close()
        
        return {
            "total": total,
            "matches": matches,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"获取匹配结果失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取匹配结果失败: {str(e)}")

@app.get("/api/temu/products-with-matches")
def get_temu_products_with_matches(
    limit: int = 20,
    offset: int = 0,
    category_id: Optional[int] = None,
    min_match_score: float = 0.5,
    redbubble_category: Optional[str] = None,
    order_by: str = "time_desc"  # 排序方式：time_desc, time_asc, sales
):
    """
    获取TEMU商品及其AI清洗结果和Redbubble搜索结果（分组展示）
    支持按Redbubble类目筛选结果，支持多种排序方式
    """
    try:
        conn = get_db_conn()
        cursor = conn.cursor(dictionary=True)
        
        # 第一步：获取TEMU商品列表（包括未清洗的），包含卖家信息
        products_query = """
            SELECT 
                p.id,
                p.goods_id,
                p.title,
                p.img,
                p.price,
                p.sales_count,
                p.category_id,
                p.mall_id,
                p.seller_name,
                p.seller_avatar,
                p.seller_url,
                p.created_at,
                tc.cleaned_keywords,
                tc.status as cleaning_status,
                tc.created_at as cleaned_at
            FROM temu_products p
            LEFT JOIN temu_title_cleaning tc ON p.id = tc.product_id
            WHERE 1=1
        """
        params = []
        
        if category_id:
            products_query += " AND p.category_id = %s"
            params.append(category_id)
        
        # 根据排序方式动态生成ORDER BY子句
        if order_by == "time_desc":
            products_query += " ORDER BY p.created_at DESC, p.sales_count DESC"
        elif order_by == "time_asc":
            products_query += " ORDER BY p.created_at ASC, p.sales_count DESC"
        else:  # sales
            products_query += " ORDER BY p.sales_count DESC, p.created_at DESC"
        
        products_query += " LIMIT %s OFFSET %s"
        params.extend([limit, offset])
        
        cursor.execute(products_query, tuple(params))
        temu_products = cursor.fetchall()
        
        # 第二步：为每个TEMU商品获取对应的Redbubble搜索结果
        result_products = []
        for product in temu_products:
            # 查询该商品的Redbubble匹配结果 (JOIN redbubble_products表获取详情)
            matches_query = """
                SELECT 
                    m.id,
                    p.title as redbubble_title,
                    p.img as redbubble_img,
                    p.link as redbubble_link,
                    p.score as redbubble_score,
                    m.match_score,
                    m.rank_position,
                    m.search_category,
                    m.created_at
                FROM temu_redbubble_matches m
                JOIN redbubble_products p ON m.redbubble_product_id = p.id
                WHERE m.temu_product_id = %s
                AND m.match_score >= %s
            """
            match_params = [product['id'], min_match_score]
            
            if redbubble_category:
                matches_query += " AND m.search_category = %s"
                match_params.append(redbubble_category)
                
            # 增加限制到100，允许前端显示更多Redbubble匹配结果
            matches_query += " ORDER BY m.rank_position ASC, m.match_score DESC LIMIT 100"
            
            cursor.execute(matches_query, tuple(match_params))
            redbubble_results = cursor.fetchall()
            
            # 组装数据（包含卖家信息）
            result_products.append({
                "temu_product": {
                    "id": product['id'],
                    "goods_id": product['goods_id'],
                    "title": product['title'],
                    "img": product['img'],
                    "price": product['price'],
                    "sales_count": product['sales_count'],
                    "category_id": product['category_id'],
                    "mall_id": product.get('mall_id'),
                    "seller_name": product.get('seller_name'),
                    "seller_avatar": product.get('seller_avatar'),
                    "seller_url": product.get('seller_url'),
                    "created_at": product.get('created_at').isoformat() if product.get('created_at') else None
                },
                "cleaned_keywords": product['cleaned_keywords'],
                "cleaning_status": product['cleaning_status'],
                "cleaned_at": product['cleaned_at'].isoformat() if product['cleaned_at'] else None,
                "redbubble_results": redbubble_results
            })
        
        # 第三步：获取总数（用于分页）
        count_query = """
            SELECT COUNT(*) as total
            FROM temu_products p
            WHERE 1=1
        """
        count_params = []
        if category_id:
            count_query += " AND p.category_id = %s"
            count_params.append(category_id)
        
        cursor.execute(count_query, tuple(count_params) if count_params else ())
        total = cursor.fetchone()['total']
        
        cursor.close()
        conn.close()
        
        return {
            "total": total,
            "products": result_products,
            "limit": limit,
            "offset": offset
        }
        
    except Exception as e:
        logger.error(f"获取TEMU商品及匹配结果失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"获取数据失败: {str(e)}")

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
        cursor.execute("SELECT id, title, img, score, link, local_img, category FROM redbubble_products WHERE category = %s ORDER BY id DESC", (category,))
    else:
        cursor.execute("SELECT id, title, img, score, link, local_img, category FROM redbubble_products ORDER BY id DESC")
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


@app.post("/api/crawl/temu/seller")
async def start_temu_seller_crawl(request: TemuSellerCrawlRequest):
    """
    启动TEMU卖家店铺爬取任务（同步执行，等待完成后返回）
    功能：爬取指定卖家店铺的所有商品，并提取卖家信息（名称、头像、ID）
    """
    if not request.mall_id:
        raise HTTPException(status_code=400, detail="卖家店铺ID不能为空")
    if request.max_pages < 1 or request.max_pages > 30:
        raise HTTPException(status_code=400, detail="滚动次数必须在1-30之间")
    
    # 创建任务ID
    task_id = str(uuid.uuid4())
    
    # 检查该店铺是否已经爬取过
    try:
        conn = get_db_conn()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(DISTINCT goods_id) as product_count, 
                   MAX(created_at) as last_crawl_time
            FROM temu_products 
            WHERE mall_id = %s
        """, (request.mall_id,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if result and result[0] > 0:
            product_count = result[0]
            last_crawl_time = result[1]
            logger.warning(f"店铺 {request.mall_id} 已存在 {product_count} 个商品，上次爬取时间: {last_crawl_time}")
            return {
                "success": False,
                "skipped": True,
                "message": f"店铺已存在！该店铺已有 {product_count} 个商品，上次爬取时间: {last_crawl_time}",
                "mall_id": request.mall_id,
                "existing_products": product_count,
                "last_crawl_time": str(last_crawl_time) if last_crawl_time else None
            }
    except Exception as e:
        logger.warning(f"检查店铺是否存在时出错: {e}，继续执行爬取")
    
    try:
        logger.info(f"开始执行TEMU卖家店铺爬取: task_id={task_id}, mall_id={request.mall_id}")
        
        # 导入爬虫函数
        from temu_seller_crawler import crawl_temu_seller_products
        from temu_db_utils import save_temu_products_to_db
        
        # 在线程池中执行同步爬虫（等待完成）
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            products = await loop.run_in_executor(
                executor,
                crawl_temu_seller_products,
                request.mall_id,
                request.max_pages,
                request.min_sales,
                request.use_persistent_context,
                request.user_data_dir,
                request.debug_port
            )
        
        saved_count = 0
        if products:
            logger.info(f"爬取到 {len(products)} 个商品，正在保存到数据库...")
            # 保存到数据库
            saved_count = save_temu_products_to_db(products, source_type='seller')
            logger.info(f"✓ 成功保存 {saved_count} 个卖家商品")
        else:
            logger.warning("未找到任何商品")
        
        message = f"✅ 成功爬取卖家店铺 (ID: {request.mall_id})，保存了 {saved_count} 个商品"
        if request.min_sales > 0:
            message += f"（销量 >= {request.min_sales}）"
        
        return {
            "success": True,
            "task_id": task_id,
            "message": message,
            "products_count": len(products) if products else 0,
            "saved_count": saved_count
        }
            
    except Exception as e:
        logger.error(f"TEMU卖家店铺爬取失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"爬取失败: {str(e)}")


@app.post("/api/crawl/temu/category")
async def start_temu_category_crawl(request: TemuCategoryCrawlRequest):
    """
    启动TEMU类目完整爬取工作流（同步执行，等待完成后返回）
    包括：爬取类目爆款商品 -> 爬取商品详情 -> 爬取卖家店铺商品
    """
    if not request.category_url:
        raise HTTPException(status_code=400, detail="类目URL不能为空")
    if request.max_pages < 1 or request.max_pages > 30:
        raise HTTPException(status_code=400, detail="滚动次数必须在1-30之间")
    if request.min_sales < 0:
        raise HTTPException(status_code=400, detail="最小销量不能小于0")
    
    # 创建任务ID
    task_id = str(uuid.uuid4())
    
    # 检查该类目URL是否已经爬取过
    try:
        import hashlib
        category_url_hash = hashlib.md5(request.category_url.encode()).hexdigest()
        
        conn = get_db_conn()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                id,
                category_name,
                total_products,
                crawled_products,
                status,
                created_at,
                updated_at
            FROM temu_categories 
            WHERE category_url_hash = %s
        """, (category_url_hash,))
        existing_category = cursor.fetchone()
        
        if existing_category:
            # 统计该类目下的商品数量
            cursor.execute("""
                SELECT COUNT(*) as product_count
                FROM temu_products
                WHERE category_id = %s
            """, (existing_category['id'],))
            product_result = cursor.fetchone()
            product_count = product_result['product_count'] if product_result else 0
            
            cursor.close()
            conn.close()
            
            logger.warning(f"类目URL已存在: {request.category_url[:100]}..., 已有 {product_count} 个商品")
            return {
                "success": False,
                "skipped": True,
                "message": f"类目已存在！该类目已有 {product_count} 个商品，上次爬取时间: {existing_category['updated_at']}",
                "category_url": request.category_url,
                "category_name": existing_category.get('category_name'),
                "existing_products": product_count,
                "last_crawl_time": str(existing_category['updated_at']) if existing_category.get('updated_at') else None,
                "status": existing_category.get('status')
            }
        
        cursor.close()
        conn.close()
    except Exception as e:
        logger.warning(f"检查类目是否存在时出错: {e}，继续执行爬取")
    
    try:
        logger.info(f"开始执行TEMU类目爬取: task_id={task_id}, url={request.category_url}")
        
        # 导入爬虫函数
        from temu_category_crawler import crawl_temu_category_full_workflow
        
        # 在线程池中执行同步爬虫（等待完成）
        import asyncio
        from concurrent.futures import ThreadPoolExecutor
        
        loop = asyncio.get_event_loop()
        with ThreadPoolExecutor() as executor:
            stats = await loop.run_in_executor(
                executor,
                crawl_temu_category_full_workflow,
                request.category_url,
                request.max_pages,
                request.min_sales,
                request.crawl_details,
                request.crawl_seller_products,
                request.use_persistent_context,
                request.user_data_dir,
                request.debug_port
            )
        
        message = f"✅ 成功爬取类目，保存了 {stats.get('saved_products', 0)} 个商品"
        if request.min_sales > 0:
            message += f"（销量 >= {request.min_sales}）"
        
        return {
            "success": True,
            "task_id": task_id,
            "message": message,
            "stats": stats
        }
            
    except Exception as e:
        logger.error(f"TEMU类目爬取失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"爬取失败: {str(e)}")

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
        cursor.execute("SELECT COUNT(*) as count FROM redbubble_products")
        result = cursor.fetchone()
        total_products = result[0] if result else 0
        
        cursor.execute("SELECT AVG(score) as avg_score FROM redbubble_products WHERE score IS NOT NULL")
        result = cursor.fetchone()
        avg_score = float(result[0]) if result and result[0] else 0
        
        cursor.execute("SELECT COUNT(*) as high_score_count FROM redbubble_products WHERE score >= 7")
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
        cursor.execute("DELETE FROM redbubble_products")
        conn.commit()
        cursor.close()
        conn.close()
        
        return {"success": True, "message": "已清空所有Redbubble商品数据"}
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

# ============ AI调试器 API ============

@app.get("/api/ai-debugger/presets")
def get_ai_presets():
    """
    获取预设的AI提示词模板
    """
    try:
        presets = get_presets()
        return {
            "success": True,
            "presets": presets
        }
    except Exception as e:
        logger.error(f"获取预设失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取预设失败: {str(e)}")

@app.post("/api/ai-debugger/chat")
def ai_debugger_chat(request: AIDebuggerChatRequest):
    """
    通用AI对话接口 - 用于调试和测试AI功能
    """
    try:
        logger.info(f"收到AI调试请求 - 模型: {request.model}, 温度: {request.temperature}")
        
        result = chat_with_ai(
            messages=request.messages,
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens
        )
        
        return result
    
    except Exception as e:
        logger.error(f"AI调试请求失败: {e}")
        raise HTTPException(status_code=500, detail=f"AI请求失败: {str(e)}")


if __name__ == "__main__":
    run_crawler("123", "animal", 1, "u-socks")