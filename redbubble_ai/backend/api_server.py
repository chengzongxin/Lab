from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List
import mysql.connector
import os

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

# 启动命令：
# uvicorn api_server:app --reload --host 0.0.0.0 --port 5000 