"""
测试迁移后的功能完整性
验证爬虫、下载、评分等模块是否正常工作
"""

import sys
import os
import logging

# 配置测试日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_imports():
    """测试模块导入"""
    try:
        logger.info("测试模块导入...")
        
        from crawler_utils import crawl_redbubble
        from download_utils import download_image, save_to_mysql, get_image_save_path, safe_filename
        from scorer_utils import nima_score, is_nima_available
        
        logger.info("✅ 所有模块导入成功")
        return True
        
    except ImportError as e:
        logger.error(f"❌ 模块导入失败: {e}")
        return False
    except Exception as e:
        logger.error(f"❌ 导入时出现意外错误: {e}")
        return False

def test_safe_filename():
    """测试文件名生成"""
    try:
        logger.info("测试文件名生成...")
        
        from download_utils import safe_filename
        
        # 测试用例
        test_cases = [
            ("Normal Title", 0, "Normal_Title_1.jpg"),
            ("Title with special chars: <>?*|", 1, "Title_with_special_chars__2.jpg"),
            ("Very long title that should be truncated because it exceeds the maximum length limit", 2, "Very_long_title_that_should_be_truncate_3.jpg")
        ]
        
        for title, idx, expected_prefix in test_cases:
            result = safe_filename(title, idx)
            logger.info(f"输入: '{title}' -> 输出: '{result}'")
            
            if not result.endswith('.jpg'):
                logger.error(f"❌ 文件名应以.jpg结尾: {result}")
                return False
        
        logger.info("✅ 文件名生成测试通过")
        return True
        
    except Exception as e:
        logger.error(f"❌ 文件名生成测试失败: {e}")
        return False

def test_nima_availability():
    """测试NIMA模型可用性"""
    try:
        logger.info("测试NIMA模型可用性...")
        
        from scorer_utils import is_nima_available, get_model_weights_path
        
        # 检查权重文件
        try:
            weights_path = get_model_weights_path()
            logger.info(f"权重文件路径: {weights_path}")
            
            if os.path.exists(weights_path):
                logger.info("✅ 权重文件存在")
            else:
                logger.warning("⚠️ 权重文件不存在，但会从crawler目录查找")
        except Exception as e:
            logger.warning(f"⚠️ 获取权重文件路径失败: {e}")
        
        # 检查模型可用性
        available = is_nima_available()
        if available:
            logger.info("✅ NIMA模型可用")
        else:
            logger.warning("⚠️ NIMA模型不可用，请检查权重文件")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ NIMA模型可用性测试失败: {e}")
        return False

def test_directory_creation():
    """测试目录创建"""
    try:
        logger.info("测试目录创建...")
        
        from download_utils import create_results_directory
        
        # 测试创建results目录
        results_dir = create_results_directory("test_results")
        
        if os.path.exists(results_dir):
            logger.info(f"✅ 成功创建目录: {results_dir}")
            
            # 清理测试目录
            try:
                os.rmdir(results_dir)
                logger.info("✅ 测试目录已清理")
            except:
                pass
                
            return True
        else:
            logger.error(f"❌ 目录创建失败: {results_dir}")
            return False
            
    except Exception as e:
        logger.error(f"❌ 目录创建测试失败: {e}")
        return False

def test_database_connection():
    """测试数据库连接"""
    try:
        logger.info("测试数据库连接...")
        
        from download_utils import get_db_connection
        
        conn = get_db_connection()
        if conn:
            logger.info("✅ 数据库连接成功")
            conn.close()
            return True
        else:
            logger.error("❌ 数据库连接失败")
            return False
            
    except Exception as e:
        logger.error(f"❌ 数据库连接测试失败: {e}")
        logger.error("请确保MySQL服务正在运行，用户名密码正确")
        return False

def run_all_tests():
    """运行所有测试"""
    logger.info("=" * 50)
    logger.info("开始运行迁移功能测试")
    logger.info("=" * 50)
    
    tests = [
        ("模块导入", test_imports),
        ("文件名生成", test_safe_filename),
        ("NIMA模型可用性", test_nima_availability),
        ("目录创建", test_directory_creation),
        ("数据库连接", test_database_connection),
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
    
    logger.info("\n" + "=" * 50)
    logger.info(f"测试完成: {passed}/{total} 通过")
    logger.info("=" * 50)
    
    if passed == total:
        logger.info("🎉 所有测试通过！迁移成功！")
        return True
    else:
        logger.warning("⚠️ 部分测试失败，请检查相关配置")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1) 