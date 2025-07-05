# 在后台启动后端服务
cd ~/Desktop/Lab/temu-violent/backend
source venv/bin/activate
nohup python -m uvicorn main:app --reload > backend.log 2>&1 &
BACKEND_PID=$!

# 在后台启动前端服务
cd ~/Desktop/Lab/temu-violent/frontend
nohup npm run dev > frontend.log 2>&1 &
FRONTEND_PID=$!