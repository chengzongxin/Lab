#!/bin/bash

echo "========================================"
echo "          Temu Violent 项目停止器"
echo "========================================"
echo

# 从文件读取进程ID
if [ -f ".pids" ]; then
    PIDS=$(cat .pids)
    echo "[信息] 从文件读取进程ID: $PIDS"
else
    echo "[信息] 未找到进程ID文件，尝试查找相关进程..."
    # 查找相关进程
    BACKEND_PIDS=$(pgrep -f "uvicorn main:app" 2>/dev/null || echo "")
    FRONTEND_PIDS=$(pgrep -f "npm run dev" 2>/dev/null || echo "")
    PIDS="$BACKEND_PIDS $FRONTEND_PIDS"
fi

if [ -z "$PIDS" ]; then
    echo "[信息] 未找到运行中的项目进程"
    exit 0
fi

echo "[信息] 正在停止进程..."
for pid in $PIDS; do
    if kill -0 $pid 2>/dev/null; then
        echo "[信息] 停止进程 $pid"
        kill $pid
        sleep 2
        # 如果进程仍在运行，强制终止
        if kill -0 $pid 2>/dev/null; then
            echo "[信息] 强制终止进程 $pid"
            kill -9 $pid
        fi
    else
        echo "[信息] 进程 $pid 已不存在"
    fi
done

# 清理进程ID文件
if [ -f ".pids" ]; then
    rm .pids
    echo "[信息] 已清理进程ID文件"
fi

echo
echo "[成功] 项目已停止"
echo "[信息] 后端日志: backend/backend.log"
echo "[信息] 前端日志: frontend/frontend.log"
echo 