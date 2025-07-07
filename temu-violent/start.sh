# 在后台启动后端服务
cd ~/Desktop/Lab/temu-violent/backend
# 检查是否存在虚拟环境，如果存在则激活，否则直接运行
if [ -d "venv" ]; then
    source venv/bin/activate
fi
nohup python -m uvicorn main:app --reload > backend.log 2>&1 &
BACKEND_PID=$!

# 在后台启动前端服务
cd ~/Desktop/Lab/temu-violent/frontend
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!