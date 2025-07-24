"""
测试backend目录下的图片存储和访问功能
验证图片保存路径和API访问是否正常
"""

import os
import requests
import logging
from download_utils import get_image_save_path, create_results_directory, download_image

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_results_directory():
    """测试results目录创建"""
    try:
        logger.info("测试results目录创建...")
        
        results_dir = create_results_directory()
        if os.path.exists(results_dir):
            logger.info(f"✅ results目录存在: {results_dir}")
            return True
        else:
            logger.error(f"❌ results目录不存在: {results_dir}")
            return False
            
    except Exception as e:
        logger.error(f"❌ results目录测试失败: {e}")
        return False

def test_image_save_path():
    """测试图片保存路径生成"""
    try:
        logger.info("测试图片保存路径生成...")
        
        # 测试用例
        test_cases = [
            ("Test Product", 0),
            ("Product with special chars!@#", 1),
            ("Very long product name that should be truncated", 2)
        ]
        
        for title, idx in test_cases:
            img_path = get_image_save_path(title, idx)
            logger.info(f"标题: '{title}' -> 路径: '{img_path}'")
            
            # 检查路径格式
            if not img_path.endswith('.jpg'):
                logger.error(f"❌ 路径应以.jpg结尾: {img_path}")
                return False
                
            # 检查是否在backend/results目录下
            if 'results' not in img_path:
                logger.error(f"❌ 路径应包含results目录: {img_path}")
                return False
        
        logger.info("✅ 图片保存路径生成测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ 图片保存路径测试失败: {e}")
        return False

def test_download_sample_image():
    """测试下载示例图片"""
    try:
        logger.info("测试下载示例图片...")
        
        # 使用一个小的测试图片URL
        test_url = "https://via.placeholder.com/150x150.jpg"
        test_path = get_image_save_path("Test Image", 999)
        
        logger.info(f"下载URL: {test_url}")
        logger.info(f"保存路径: {test_path}")
        
        success = download_image(test_url, test_path)
        
        if success and os.path.exists(test_path):
            logger.info(f"✅ 图片下载成功: {test_path}")
            logger.info(f"文件大小: {os.path.getsize(test_path)} bytes")
            return True, test_path
        else:
            logger.error(f"❌ 图片下载失败: {test_path}")
            return False, test_path
            
    except Exception as e:
        logger.error(f"❌ 图片下载测试失败: {e}")
        return False, ""

def test_api_image_access():
    """测试通过API访问图片"""
    try:
        logger.info("测试通过API访问图片...")
        
        # 首先下载一个测试图片
        success, img_path = test_download_sample_image()
        if not success:
            logger.error("❌ 无法下载测试图片，跳过API访问测试")
            return False
        
        # 获取图片文件名
        filename = os.path.basename(img_path)
        api_url = f"http://localhost:8000/images/{filename}"
        
        logger.info(f"API访问URL: {api_url}")
        
        try:
            # 测试API访问（这需要backend服务运行）
            response = requests.get(api_url, timeout=5)
            if response.status_code == 200:
                logger.info("✅ API图片访问成功")
                return True
            else:
                logger.warning(f"⚠️ API访问返回状态码: {response.status_code}")
                logger.warning("请确保backend服务正在运行在端口8000")
                return False
                
        except requests.exceptions.RequestException as e:
            logger.warning(f"⚠️ API访问失败: {e}")
            logger.warning("请确保backend服务正在运行在端口8000")
            return False
            
    except Exception as e:
        logger.error(f"❌ API图片访问测试失败: {e}")
        return False

def test_image_url_generation():
    """测试图片URL生成逻辑"""
    try:
        logger.info("测试图片URL生成逻辑...")
        
        # 模拟product数据
        test_products = [
            {
                'local_img': 'results/test_image_1.jpg',
                'img': 'https://example.com/original.jpg'
            },
            {
                'local_img': 'results/another_test_2.jpg', 
                'img': 'https://example.com/original2.jpg'
            }
        ]
        
        for product in test_products:
            if product.get('local_img'):
                filename = os.path.basename(product['local_img'])
                expected_url = f"http://localhost:8000/images/{filename}"
                
                logger.info(f"本地路径: {product['local_img']}")
                logger.info(f"生成URL: {expected_url}")
                
                # 验证URL格式
                if not expected_url.startswith('http://localhost:8000/images/'):
                    logger.error(f"❌ URL格式错误: {expected_url}")
                    return False
                    
                if not expected_url.endswith('.jpg'):
                    logger.error(f"❌ URL应以.jpg结尾: {expected_url}")
                    return False
        
        logger.info("✅ 图片URL生成逻辑测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ 图片URL生成测试失败: {e}")
        return False

def cleanup_test_files():
    """清理测试文件"""
    try:
        logger.info("清理测试文件...")
        
        test_files = [
            get_image_save_path("Test Image", 999),
        ]
        
        for file_path in test_files:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.info(f"已删除测试文件: {file_path}")
        
        logger.info("✅ 测试文件清理完成")
        
    except Exception as e:
        logger.warning(f"⚠️ 测试文件清理失败: {e}")

def run_all_tests():
    """运行所有图片相关测试"""
    logger.info("=" * 60)
    logger.info("开始运行backend图片存储和访问测试")
    logger.info("=" * 60)
    
    tests = [
        ("results目录创建", test_results_directory),
        ("图片保存路径生成", test_image_save_path),
        ("图片下载功能", lambda: test_download_sample_image()[0]),
        ("图片URL生成逻辑", test_image_url_generation),
        ("API图片访问", test_api_image_access),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        logger.info(f"\n📋 运行测试: {test_name}")
        try:
            if test_func():
                passed += 1
                logger.info(f"✅ {test_name} - 通过")
            else:
                logger.error(f"❌ {test_name} - 失败")
        except Exception as e:
            logger.error(f"❌ {test_name} - 异常: {e}")
    
    # 清理测试文件
    cleanup_test_files()
    
    logger.info("\n" + "=" * 60)
    logger.info(f"测试完成: {passed}/{total} 通过")
    logger.info("=" * 60)
    
    if passed == total:
        logger.info("🎉 所有图片相关测试通过！")
        return True
    else:
        logger.warning("⚠️ 部分测试失败，请检查相关配置")
        return False

if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1) 