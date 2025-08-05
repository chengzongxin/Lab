#!/bin/bash

# Docker 部署脚本
set -e

echo "🚀 开始部署 Temu 项目..."

# 检查 Docker 是否安装
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装，请先安装 Docker"
    exit 1
fi

# 检查 Docker Compose 是否安装
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose 未安装，请先安装 Docker Compose"
    exit 1
fi

# 创建日志目录
mkdir -p logs

# 停止并删除现有容器
echo "🛑 停止现有容器..."
docker-compose down --remove-orphans

# 清理旧镜像（可选）
# echo "🧹 清理旧镜像..."
# docker system prune -f

# 构建镜像
# echo "🔨 构建 Docker 镜像..."
# docker-compose build --no-cache

docker-compose build

# 启动服务
echo "🚀 启动服务..."
docker-compose up -d

# 等待服务启动
echo "⏳ 等待服务启动..."
sleep 10

# 检查服务状态
echo "📊 检查服务状态..."
docker-compose ps

# 检查健康状态
echo "🏥 检查健康状态..."
docker-compose exec -T backend curl -f http://localhost:8000/ || echo "⚠️  后端健康检查失败"
docker-compose exec -T frontend curl -f http://localhost:80 || echo "⚠️  前端健康检查失败"

echo "✅ 部署完成！"
echo "🌐 前端访问地址: http://localhost:8082"
echo "🔧 后端 API 地址: http://localhost:8082/api"
echo "🔄 统一入口地址: http://localhost:8082"

# 显示日志
echo "📋 查看日志命令:"
echo "  docker-compose logs -f"
echo "  docker-compose logs -f backend"
echo "  docker-compose logs -f frontend" 