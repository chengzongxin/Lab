#!/bin/bash

echo "========================================"
echo "           停止项目服务"
echo "========================================"
echo

echo "[信息] 正在停止后端服务..."
pkill -f "python.*main.py" >/dev/null 2>&1
pkill -f "uvicorn.*main:app" >/dev/null 2>&1

echo "[信息] 正在停止前端服务..."
pkill -f "vite" >/dev/null 2>&1
pkill -f "npm.*run.*dev" >/dev/null 2>&1

echo "[信息] 正在停止Node.js进程..."
pkill -f "node.*vite" >/dev/null 2>&1

echo
echo "[信息] 服务已停止！"
echo "[提示] 如果仍有进程在运行，请手动检查并停止"
echo 