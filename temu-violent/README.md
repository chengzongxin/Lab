你应该这样启动 FastAPI 项目：
# 进入 backend 目录
cd backend

# 安装依赖（如果还没装）
pip install fastapi uvicorn requests beautifulsoup4

# 用 uvicorn 启动服务
uvicorn main:app --reload