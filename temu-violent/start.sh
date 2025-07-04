#!/bin/bash

echo "========================================"
echo "          Temu Violent 项目启动器"
echo "========================================"
echo

# 检查Python是否安装
if ! command -v python3 &> /dev/null; then
    echo "[错误] 未检测到Python3，请先安装Python3"
    exit 1
fi

# 检查Node.js是否安装
if ! command -v node &> /dev/null; then
    echo "[错误] 未检测到Node.js，请先安装Node.js"
    exit 1
fi

echo "[信息] 检测到Python3和Node.js环境"
echo

# 启动后端服务
echo "[信息] 正在启动后端服务..."
echo "[信息] 后端服务将在 http://localhost:8000 启动"
echo

cd backend

echo "[信息] 安装后端依赖..."
pip3 install -r requirements.txt

echo "[信息] 启动后端服务..."
# 在后台启动后端服务
nohup python3 -m uvicorn main:app --reload > backend.log 2>&1 &
BACKEND_PID=$!

# 等待后端启动
sleep 3

# 启动前端服务
echo "[信息] 正在启动前端服务..."
echo "[信息] 前端服务将在 http://localhost:5173 启动"
echo

cd ../frontend

echo "[信息] 安装前端依赖..."
if [ ! -d "node_modules" ]; then
    npm install
fi

echo "[信息] 启动前端服务..."
# 在后台启动前端服务
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!

# 等待前端启动
sleep 5

echo
echo "========================================"
echo "            启动完成！"
echo "========================================"
echo
echo "[信息] 后端服务: http://localhost:8000"
echo "[信息] 前端服务: http://localhost:5173"
echo
echo "[信息] 后端进程ID: $BACKEND_PID"
echo "[信息] 前端进程ID: $FRONTEND_PID"
echo
echo "[提示] 请等待几秒钟让服务完全启动"
echo "[提示] 按任意键打开浏览器访问前端页面"
echo
read -n 1 -s

# 打开浏览器
if command -v xdg-open &> /dev/null; then
    # Linux
    xdg-open http://localhost:5173
elif command -v open &> /dev/null; then
    # macOS
    open http://localhost:5173
else
    echo "[提示] 请手动打开浏览器访问: http://localhost:5173"
fi

echo
echo "[信息] 项目启动完成！"
echo "[提示] 服务正在后台运行"
echo "[提示] 后端日志: backend/backend.log"
echo "[提示] 前端日志: frontend/frontend.log"
echo "[提示] 如需停止服务，请运行: kill $BACKEND_PID $FRONTEND_PID"
echo 