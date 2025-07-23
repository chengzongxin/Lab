#!/bin/bash

# Redbubble AI 项目启动脚本
# 一键启动后端和前端服务

echo "🚀 启动 Redbubble AI 项目..."

# 检查 MySQL 服务
echo "📊 检查 MySQL 服务..."
if ! mysqladmin ping -h localhost -u root -p123456789 --silent; then
    echo "❌ MySQL 服务未运行，请先启动 MySQL 服务"
    echo "   在 macOS 上可以使用: brew services start mysql"
    echo "   在 Ubuntu 上可以使用: sudo systemctl start mysql"
    exit 1
fi
echo "✅ MySQL 服务正常运行"

# 启动后端服务
echo "🔧 启动后端 API 服务..."
cd backend
if [ ! -d "venv" ]; then
    echo "📦 创建虚拟环境..."
    python3 -m venv venv
fi

echo "📦 激活虚拟环境并安装依赖..."
source venv/bin/activate
pip install -r requirements.txt

echo "🚀 启动 FastAPI 服务器..."
uvicorn api_server:app --reload --port 8000 &
BACKEND_PID=$!
echo "✅ 后端服务已启动 (PID: $BACKEND_PID)"

# 等待后端启动
sleep 3

# 启动前端服务
echo "🎨 启动前端开发服务器..."
cd ../frontend

echo "📦 安装前端依赖..."
npm install

echo "🚀 启动 React 开发服务器..."
npm start &
FRONTEND_PID=$!
echo "✅ 前端服务已启动 (PID: $FRONTEND_PID)"

# 等待前端启动
sleep 5

echo ""
echo "🎉 Redbubble AI 项目启动完成！"
echo ""
echo "📱 访问地址："
echo "   前端界面: http://localhost:3000"
echo "   后端 API:  http://localhost:8000"
echo "   API 文档:  http://localhost:8000/docs"
echo ""
echo "🔧 数据采集："
echo "   cd crawler && python main.py"
echo ""
echo "🛑 停止服务："
echo "   按 Ctrl+C 停止所有服务"
echo ""

# 保存进程 ID 到文件，方便后续停止
echo $BACKEND_PID > .backend_pid
echo $FRONTEND_PID > .frontend_pid

# 等待用户中断
trap 'echo ""; echo "🛑 正在停止服务..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; rm -f .backend_pid .frontend_pid; echo "✅ 服务已停止"; exit 0' INT

# 保持脚本运行
wait 