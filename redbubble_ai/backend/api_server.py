from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List, Optional
import mysql.connector
import os
import subprocess
import sys
import json
from datetime import datetime
from pydantic import BaseModel
import uuid

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 挂载静态文件目录，提供图片访问
app.mount("/images", StaticFiles(directory="../crawler/results"), name="images")

class CrawlRequest(BaseModel):
    keyword: str = ""
    pages: int = 1
    category: str = "u-clothing"  # 默认衣服

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
    
    # 创建商品表
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
                      step: str = "", title: str = "", error_message: str = ""):
    """更新任务状态"""
    conn = get_db_conn()
    cursor = conn.cursor()
    
    if status == 'completed':
        cursor.execute("""
            UPDATE crawl_tasks 
            SET status = %s, progress_current = %s, progress_total = %s, 
                current_step = %s, current_title = %s, completed_at = NOW()
            WHERE id = %s
        """, (status, current, total, step, title, task_id))
    else:
        cursor.execute("""
            UPDATE crawl_tasks 
            SET status = %s, progress_current = %s, progress_total = %s, 
                current_step = %s, current_title = %s, error_message = %s
            WHERE id = %s
        """, (status, current, total, step, title, error_message, task_id))
    
    conn.commit()
    cursor.close()
    conn.close()

def run_crawler(task_id: str, keyword: str, pages: int, category: str):
    """运行爬虫任务"""
    try:
        # 更新任务状态为运行中
        update_task_status(task_id, "running", 0, 0, "启动爬虫")
        
        import subprocess
        import sys
        import os
        crawler_dir = os.path.join(os.path.dirname(__file__), "..", "crawler")
        python_executable = sys.executable
        script_input = f"{task_id}\n{keyword}\n{pages}\n{category}\n"
        
        process = subprocess.Popen(
            [python_executable, "main.py"],
            cwd=crawler_dir,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # 等待爬虫完成
        stdout, stderr = process.communicate(input=script_input)
        
        if process.returncode == 0:
            update_task_status(task_id, "completed", 100, 100, "爬取完成")
        else:
            update_task_status(task_id, "failed", 0, 0, "爬取失败", "", stderr)
            
    except Exception as e:
        update_task_status(task_id, "failed", 0, 0, "启动失败", "", str(e))

# 初始化数据库
init_database()

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
    
    # 启动爬虫任务
    background_tasks.add_task(run_crawler, task_id, request.keyword, request.pages, request.category)
    
    return {
        "success": True,
        "task_id": task_id,
        "message": f"已启动爬虫任务，类目 '{request.category}'，关键词 '{request.keyword}'，页数 {request.pages}"
    }

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