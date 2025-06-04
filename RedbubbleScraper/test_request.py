"""
测试请求脚本
"""
import time
import logging
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_request():
    """测试请求"""
    url = "https://www.redbubble.com/shop/bags?page=1"
    driver = None
    
    try:
        # 配置Chrome选项
        logger.info("配置Chrome选项...")
        chrome_options = Options()
        chrome_options.add_argument('--headless=new')  # 使用新的无头模式
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option('excludeSwitches', ['enable-automation'])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 设置用户代理
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/136.0.0.0 Safari/537.36'
        chrome_options.add_argument(f'user-agent={user_agent}')
        
        # 初始化WebDriver
        logger.info("初始化WebDriver...")
        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        # 设置页面加载超时
        driver.set_page_load_timeout(30)
        
        # 执行JavaScript来修改navigator.webdriver
        logger.info("修改浏览器特征...")
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        # 访问URL
        logger.info(f"访问URL: {url}")
        driver.get(url)
        
        # 等待页面加载
        logger.info("等待页面加载...")
        time.sleep(10)  # 增加等待时间
        
        # 打印当前URL
        current_url = driver.current_url
        logger.info(f"当前URL: {current_url}")
        
        # 检查是否被重定向到验证页面
        if "challenge" in current_url or "verify" in current_url:
            logger.warning("被重定向到验证页面，等待验证...")
            time.sleep(30)  # 给更多时间进行验证
        
        # 等待产品卡片出现
        logger.info("等待产品卡片加载...")
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'div[data-testid="product-card"]'))
            )
        except TimeoutException:
            logger.error("等待产品卡片超时")
            # 保存页面源码以供调试
            with open('error_page.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
            logger.info("已保存错误页面到 error_page.html")
            return
        
        # 获取页面内容
        logger.info("获取页面内容...")
        page_source = driver.page_source
        
        # 保存响应内容
        with open('response.html', 'w', encoding='utf-8') as f:
            f.write(page_source)
        logger.info("响应内容已保存到 response.html")
        
        # 获取产品信息
        logger.info("解析产品信息...")
        products = driver.find_elements(By.CSS_SELECTOR, 'div[data-testid="product-card"]')
        logger.info(f"找到 {len(products)} 个产品")
        
        # 打印产品信息
        for i, product in enumerate(products, 1):
            try:
                title = product.find_element(By.CSS_SELECTOR, 'h3[data-testid="product-title"]').text
                price = product.find_element(By.CSS_SELECTOR, 'span[data-testid="product-price"]').text
                logger.info(f"产品 {i}:")
                logger.info(f"  标题: {title}")
                logger.info(f"  价格: {price}")
            except Exception as e:
                logger.error(f"解析产品 {i} 时出错: {str(e)}")
        
    except WebDriverException as e:
        logger.error(f"WebDriver错误: {str(e)}")
    except Exception as e:
        logger.error(f"发生错误: {str(e)}")
    finally:
        # 关闭浏览器
        if driver:
            try:
                driver.quit()
                logger.info("浏览器已关闭")
            except Exception as e:
                logger.error(f"关闭浏览器时出错: {str(e)}")

if __name__ == "__main__":
    test_request() 