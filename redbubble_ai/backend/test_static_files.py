"""
简单测试backend的静态文件访问配置
"""

import os
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_static_file_setup():
    """测试静态文件设置"""
    try:
        logger.info("测试静态文件设置...")
        
        # 检查results目录
        results_dir = "results"
        if os.path.exists(results_dir):
            logger.info(f"✅ results目录存在: {os.path.abspath(results_dir)}")
        else:
            logger.error(f"❌ results目录不存在")
            return False
            
        # 创建测试文件
        test_file = os.path.join(results_dir, "test.txt")
        with open(test_file, "w") as f:
            f.write("Hello Backend Images!")
            
        if os.path.exists(test_file):
            logger.info(f"✅ 测试文件创建成功: {test_file}")
            logger.info(f"文件大小: {os.path.getsize(test_file)} bytes")
            
            # 显示API访问URL
            api_url = "http://localhost:8000/images/test.txt"
            logger.info(f"📝 API访问URL: {api_url}")
            logger.info("💡 启动backend服务后可以访问这个URL测试")
            
            return True
        else:
            logger.error(f"❌ 测试文件创建失败")
            return False
            
    except Exception as e:
        logger.error(f"❌ 静态文件测试失败: {e}")
        return False

def show_configuration_summary():
    """显示配置总结"""
    logger.info("\n" + "=" * 50)
    logger.info("🎯 Backend图片访问配置总结")
    logger.info("=" * 50)
    
    logger.info("📁 图片存储目录: backend/results/")
    logger.info("🌐 API挂载路径: /images")
    logger.info("🔗 访问URL格式: http://localhost:8000/images/{filename}")
    logger.info("⚙️ FastAPI配置: app.mount('/images', StaticFiles(directory='results'))")
    
    logger.info("\n📝 使用示例:")
    logger.info("  1. 图片保存到: backend/results/product_1.jpg")
    logger.info("  2. 前端访问URL: http://localhost:8000/images/product_1.jpg")
    logger.info("  3. 数据库中存储的img字段会自动生成正确的URL")
    
    logger.info("\n🚀 启动服务:")
    logger.info("  cd backend")
    logger.info("  uvicorn api_server:app --reload --port 8000")
    
    logger.info("=" * 50)

if __name__ == "__main__":
    success = test_static_file_setup()
    show_configuration_summary()
    
    if success:
        logger.info("🎉 静态文件配置测试通过！")
    else:
        logger.warning("⚠️ 静态文件配置存在问题") 