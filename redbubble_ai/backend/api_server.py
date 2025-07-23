from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List
import mysql.connector
import os
import subprocess
import sys
import json
from datetime import datetime
from pydantic import BaseModel

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
    keyword: str
    pages: int = 1

def get_db_conn():
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="123456789",
        database="redbubble_ai"
    )

@app.get("/api/products")
def get_products():
    conn = get_db_conn()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT id, title, img, score, link, local_img FROM products ORDER BY id DESC")
    products = cursor.fetchall()
    cursor.close()
    conn.close()

    # 处理图片路径，使用本地图片
    for product in products:
        if product.get('local_img'):
            # 从 local_img 路径中提取文件名
            filename = os.path.basename(product['local_img'])
            # 构建本地图片的 URL
            product['img'] = f"http://localhost:8000/images/{filename}"

    return products

def run_crawler(keyword, pages):
    import subprocess
    import sys
    import os
    crawler_dir = os.path.join(os.path.dirname(__file__), "..", "crawler")
    python_executable = sys.executable
    script_input = f"{keyword}\n{pages}\n"
    process = subprocess.Popen(
        [python_executable, "main.py"],
        cwd=crawler_dir,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    # 不等待，直接返回
    process.communicate(input=script_input)

@app.post("/api/crawl")
async def start_crawl(request: CrawlRequest, background_tasks: BackgroundTasks):
    """
    启动爬虫任务（异步后台执行）
    """
    if not request.keyword.strip():
        raise HTTPException(status_code=400, detail="关键词不能为空")
    if request.pages < 1 or request.pages > 10:
        raise HTTPException(status_code=400, detail="页数必须在1-10之间")
    # 启动爬虫任务
    background_tasks.add_task(run_crawler, request.keyword, request.pages)
    return {
        "success": True,
        "message": f"已启动爬虫任务，关键词 '{request.keyword}'，页数 {request.pages}，请稍候查看进度"
    }

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
    获取爬虫实时进度（crawler_status.json）
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