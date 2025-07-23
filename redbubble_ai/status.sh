#!/bin/bash

# Redbubble AI 项目状态检查脚本

echo "📊 Redbubble AI 项目状态检查"
echo "================================"

# 检查 MySQL 服务
echo "🔍 检查 MySQL 服务..."
if mysqladmin ping -h localhost -u root -p123456789 --silent; then
    echo "✅ MySQL 服务正常运行"
else
    echo "❌ MySQL 服务未运行"
fi

# 检查后端服务
echo "🔍 检查后端 API 服务..."
if curl -s http://localhost:8000/docs > /dev/null; then
    echo "✅ 后端 API 服务正常运行 (http://localhost:8000)"
else
    echo "❌ 后端 API 服务未运行"
fi

# 检查前端服务
echo "🔍 检查前端开发服务器..."
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ 前端开发服务器正常运行 (http://localhost:3000)"
else
    echo "❌ 前端开发服务器未运行"
fi

# 检查数据库连接
echo "🔍 检查数据库连接..."
if mysql -h localhost -u root -p123456789 -e "USE redbubble_ai; SELECT COUNT(*) FROM products;" 2>/dev/null; then
    echo "✅ 数据库连接正常"
    PRODUCT_COUNT=$(mysql -h localhost -u root -p123456789 -e "USE redbubble_ai; SELECT COUNT(*) FROM products;" 2>/dev/null | tail -n 1)
    echo "📊 数据库中有 $PRODUCT_COUNT 个商品"
else
    echo "❌ 数据库连接失败"
fi

# 检查图片文件
echo "🔍 检查图片文件..."
if [ -d "crawler/results" ]; then
    IMAGE_COUNT=$(find crawler/results -name "*.jpg" -o -name "*.png" -o -name "*.gif" | wc -l)
    echo "✅ 图片目录存在，包含 $IMAGE_COUNT 个图片文件"
else
    echo "❌ 图片目录不存在"
fi

# 检查 NIMA 模型文件
echo "🔍 检查 AI 模型文件..."
if [ -f "crawler/weights_mobilenet_aesthetic_0.07.hdf5" ]; then
    FILE_SIZE=$(ls -lh crawler/weights_mobilenet_aesthetic_0.07.hdf5 | awk '{print $5}')
    echo "✅ NIMA 模型文件存在 ($FILE_SIZE)"
else
    echo "❌ NIMA 模型文件不存在"
fi

echo ""
echo "📱 访问地址："
echo "   前端界面: http://localhost:3000"
echo "   后端 API:  http://localhost:8000"
echo "   API 文档:  http://localhost:8000/docs"
echo ""
echo "🔧 管理命令："
echo "   启动项目: ./start.sh"
echo "   停止项目: ./stop.sh"
echo "   检查状态: ./status.sh"
echo "   数据采集: cd crawler && python main.py" 