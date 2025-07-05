#!/bin/bash

echo "========================================"
echo "          Temu Violent 项目启动器"
echo "========================================"
echo

# 设置正确的Node.js版本
export PATH="/opt/homebrew/opt/node@20/bin:$PATH"

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

# 检查Node.js版本
NODE_VERSION=$(node -v | cut -d'v' -f2)
REQUIRED_NODE_VERSION="18.18.0"

# 版本比较函数
version_compare() {
    if [[ $1 == $2 ]]; then
        return 0
    fi
    local IFS=.
    local i ver1=($1) ver2=($2)
    for ((i=${#ver1[@]}; i<${#ver2[@]}; i++)); do
        ver1[i]=0
    done
    for ((i=0; i<${#ver1[@]}; i++)); do
        if [[ -z ${ver2[i]} ]]; then
            ver2[i]=0
        fi
        if ((10#${ver1[i]} > 10#${ver2[i]})); then
            return 1
        fi
        if ((10#${ver1[i]} < 10#${ver2[i]})); then
            return 2
        fi
    done
    return 0
}

version_compare $NODE_VERSION $REQUIRED_NODE_VERSION
if [[ $? -eq 2 ]]; then
    echo "[警告] Node.js版本过低 (当前: $NODE_VERSION, 需要: $REQUIRED_NODE_VERSION)"
    echo "[提示] 正在尝试使用Node.js 20..."
    if [ -d "/opt/homebrew/opt/node@20" ]; then
        export PATH="/opt/homebrew/opt/node@20/bin:$PATH"
        NODE_VERSION=$(node -v | cut -d'v' -f2)
        echo "[信息] 已切换到Node.js版本: $NODE_VERSION"
    else
        echo "[错误] 未找到Node.js 20，请安装: brew install node@20"
        exit 1
    fi
fi

echo "[信息] 检测到Python3和Node.js环境"
echo "[信息] Python版本: $(python3 --version)"
echo "[信息] Node.js版本: $NODE_VERSION"
echo

# 启动后端服务
echo "[信息] 正在启动后端服务..."
echo "[信息] 后端服务将在 http://localhost:8000 启动"
echo

cd backend

# 检查是否存在虚拟环境
if [ ! -d "venv" ]; then
    echo "[信息] 创建Python虚拟环境..."
    python3 -m venv venv
fi

echo "[信息] 激活虚拟环境..."
source venv/bin/activate

echo "[信息] 安装后端依赖..."
pip install -r requirements.txt

echo "[信息] 启动后端服务..."
# 在后台启动后端服务
nohup python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

# 等待后端启动并检查状态
echo "[信息] 等待后端服务启动..."
sleep 5

# 检查后端是否成功启动
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "[错误] 后端服务启动失败，请检查日志: backend/backend.log"
    exit 1
fi

# 检查端口是否被占用
if ! lsof -i :8000 > /dev/null 2>&1; then
    echo "[错误] 后端服务端口8000未响应，请检查日志: backend/backend.log"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo "[成功] 后端服务启动成功 (PID: $BACKEND_PID)"

# 启动前端服务
echo "[信息] 正在启动前端服务..."
echo "[信息] 前端服务将在 http://localhost:5173 启动"
echo

cd ../frontend

echo "[信息] 安装前端依赖..."
if [ ! -d "node_modules" ]; then
    npm install
else
    echo "[信息] 依赖已存在，跳过安装"
fi

echo "[信息] 启动前端服务..."
# 在后台启动前端服务
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!

# 等待前端启动并检查状态
echo "[信息] 等待前端服务启动..."
sleep 8

# 检查前端是否成功启动
if ! kill -0 $FRONTEND_PID 2>/dev/null; then
    echo "[错误] 前端服务启动失败，请检查日志: frontend/frontend.log"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

# 检查端口是否被占用
if ! lsof -i :5173 > /dev/null 2>&1; then
    echo "[错误] 前端服务端口5173未响应，请检查日志: frontend/frontend.log"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 1
fi

echo "[成功] 前端服务启动成功 (PID: $FRONTEND_PID)"

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
echo "[提示] 服务正在后台运行"
echo "[提示] 后端日志: backend/backend.log"
echo "[提示] 前端日志: frontend/frontend.log"
echo "[提示] 如需停止服务，请运行: ./stop.sh"
echo

# 保存进程ID到文件，供停止脚本使用
echo "$BACKEND_PID $FRONTEND_PID" > .pids

echo "[提示] 按任意键打开浏览器访问前端页面"
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
echo "[提示] 如需停止服务，请运行: ./stop.sh"
echo 