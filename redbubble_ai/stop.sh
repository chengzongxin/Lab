#!/bin/bash

# Redbubble AI 项目停止脚本

echo "🛑 停止 Redbubble AI 项目..."

# 停止后端服务
if [ -f ".backend_pid" ]; then
    BACKEND_PID=$(cat .backend_pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "🔧 停止后端服务 (PID: $BACKEND_PID)..."
        kill $BACKEND_PID
        echo "✅ 后端服务已停止"
    else
        echo "⚠️  后端服务进程不存在"
    fi
    rm -f .backend_pid
else
    echo "⚠️  未找到后端服务 PID 文件"
fi

# 停止前端服务
if [ -f ".frontend_pid" ]; then
    FRONTEND_PID=$(cat .frontend_pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "🎨 停止前端服务 (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        echo "✅ 前端服务已停止"
    else
        echo "⚠️  前端服务进程不存在"
    fi
    rm -f .frontend_pid
else
    echo "⚠️  未找到前端服务 PID 文件"
fi

# 清理可能的残留进程
echo "🧹 清理残留进程..."
pkill -f "uvicorn api_server:app" 2>/dev/null
pkill -f "npm start" 2>/dev/null

echo "🎉 所有服务已停止！" 