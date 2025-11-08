#!/bin/bash

# 后端服务启动脚本
# 确保使用虚拟环境中的 Python 和依赖

echo "🔧 启动后端 API 服务..."

# 进入后端目录
cd "$(dirname "$0")"

# 检查虚拟环境是否存在
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

# 激活虚拟环境
echo "📦 激活虚拟环境..."
source venv/bin/activate

# 检查并安装依赖
echo "📦 检查依赖..."
pip install -q -r requirements.txt

# 启动服务器
echo "🚀 启动 FastAPI 服务器 (http://127.0.0.1:8000)..."
echo "📚 API 文档: http://127.0.0.1:8000/docs"
echo ""
echo "按 Ctrl+C 停止服务器"
echo ""

uvicorn api_server:app --reload --port 8000

