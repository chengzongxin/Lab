# Backend 模块

Redbubble AI 项目的 FastAPI 后端服务，提供 RESTful API 和静态文件服务。

## 🎯 功能概述

- 🚀 **高性能 API**：基于 FastAPI 的现代化 Web API
- 💾 **数据服务**：从 MySQL 数据库提供商品数据
- 🖼️ **静态文件**：提供本地图片访问服务
- 🔒 **CORS 支持**：跨域请求支持
- 📚 **自动文档**：Swagger UI API 文档

## 📁 文件结构

```
backend/
├── api_server.py        # FastAPI 主服务器
├── requirements.txt     # Python 依赖
└── README.md           # 本文件
```

## 🛠️ 技术栈

- **FastAPI** - 现代化 Web API 框架
- **Uvicorn** - ASGI 服务器
- **MySQL Connector** - 数据库连接
- **StaticFiles** - 静态文件服务
- **CORS Middleware** - 跨域支持

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 配置数据库
确保 MySQL 服务运行，并修改 `api_server.py` 中的连接参数：

```python
def get_db_conn():
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="123456789",
        database="redbubble_ai"
    )
```

### 3. 启动服务
```bash
uvicorn api_server:app --reload --port 8000
```

### 4. 访问服务
- API 服务：http://localhost:8000
- API 文档：http://localhost:8000/docs
- 图片服务：http://localhost:8000/images/

## 📖 API 接口

### 获取商品列表
```
GET /api/products
```

**响应格式**：
```json
[
  {
    "id": 1,
    "title": "Cute Cat Design",
    "img": "http://localhost:8000/images/cute_cat.jpg",
    "score": 7.5,
    "link": "https://www.redbubble.com/...",
    "local_img": "results/cute_cat.jpg"
  }
]
```

**查询参数**：
- `limit` (可选)：限制返回数量
- `offset` (可选)：分页偏移量
- `min_score` (可选)：最低评分过滤

### 静态文件服务
```
GET /images/{filename}
```
- 提供 `crawler/results/` 目录下的图片文件
- 支持 JPG、PNG、GIF 等格式

## 🔧 配置说明

### 环境变量
创建 `.env` 文件：
```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=root
DB_PASSWORD=123456789
DB_NAME=redbubble_ai
API_PORT=8000
CORS_ORIGINS=http://localhost:3000
```

### 数据库配置
```python
# 数据库连接参数
DB_CONFIG = {
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "123456789",
    "database": "redbubble_ai"
}
```

### CORS 配置
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🗄️ 数据库结构

### products 表
```sql
CREATE TABLE products (
  id INT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(512),        -- 商品标题
  img VARCHAR(1024),         -- 网络图片URL
  score FLOAT,              -- 美学评分 (1-10)
  link VARCHAR(1024),        -- 商品链接
  local_img VARCHAR(1024)    -- 本地图片路径
);
```

### 索引优化
```sql
-- 为常用查询创建索引
CREATE INDEX idx_score ON products(score);
CREATE INDEX idx_title ON products(title);
```

## 🚀 性能优化

### 数据库优化
- 连接池管理
- 查询优化
- 索引策略

### API 优化
- 响应缓存
- 分页支持
- 异步处理

### 静态文件优化
- 文件缓存
- 压缩传输
- CDN 支持

## 🔒 安全考虑

### 输入验证
```python
from pydantic import BaseModel, validator

class ProductQuery(BaseModel):
    limit: int = 20
    offset: int = 0
    min_score: float = 0.0
    
    @validator('limit')
    def validate_limit(cls, v):
        if v > 100:
            raise ValueError('Limit cannot exceed 100')
        return v
```

### 错误处理
```python
from fastapi import HTTPException

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"}
    )
```

## 🐛 故障排除

### 常见问题

1. **数据库连接失败**
   ```bash
   # 检查 MySQL 服务状态
   sudo systemctl status mysql
   
   # 测试连接
   mysql -u root -p -h localhost
   ```

2. **端口被占用**
   ```bash
   # 查看端口占用
   lsof -i :8000
   
   # 使用不同端口
   uvicorn api_server:app --port 8001
   ```

3. **CORS 错误**
   - 检查前端 URL 是否在允许列表中
   - 确认 CORS 中间件配置正确

4. **图片无法访问**
   - 确认 `crawler/results/` 目录存在
   - 检查文件权限
   - 验证静态文件挂载路径

### 调试技巧

1. **启用详细日志**
   ```bash
   uvicorn api_server:app --log-level debug
   ```

2. **API 文档测试**
   - 访问 http://localhost:8000/docs
   - 使用 Swagger UI 测试接口

3. **数据库查询调试**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

## 📊 监控和日志

### 日志配置
```python
import logging
from fastapi.logger import logger

# 配置日志格式
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

### 健康检查
```python
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now()}
```

### 性能监控
- 请求响应时间
- 数据库查询性能
- 内存使用情况

## 🔄 扩展功能

### 可能的改进
1. **认证授权**：JWT 认证
2. **缓存系统**：Redis 缓存
3. **搜索功能**：全文搜索
4. **文件上传**：图片上传 API
5. **WebSocket**：实时通知

### 中间件扩展
```python
from fastapi import Request
import time

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

## 📦 部署说明

### 生产环境部署
```bash
# 使用 Gunicorn
pip install gunicorn
gunicorn api_server:app -w 4 -k uvicorn.workers.UvicornWorker

# 使用 Docker
docker build -t redbubble-backend .
docker run -p 8000:8000 redbubble-backend
```

### 环境变量配置
```bash
export DB_HOST=production-db-host
export DB_PASSWORD=secure-password
export CORS_ORIGINS=https://yourdomain.com
```

### 反向代理配置
```nginx
server {
    listen 80;
    server_name api.yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔧 开发工具

### 代码格式化
```bash
pip install black isort
black api_server.py
isort api_server.py
```

### 类型检查
```bash
pip install mypy
mypy api_server.py
```

### 测试框架
```bash
pip install pytest httpx
pytest test_api.py
```

---

**Happy API Development!** 🚀✨ 