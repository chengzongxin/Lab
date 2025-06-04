"""
Redbubble产品爬虫
"""
import os
import time
import random
import logging
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from urllib.parse import urljoin
from config.config import *
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class RedbubbleSpider:
    def __init__(self):
        """初始化爬虫"""
        # 配置Chrome选项
        chrome_options = Options()
        chrome_options.add_argument('--headless')  # 无头模式
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--window-size=1920,1080')
        
        # 设置用户代理
        chrome_options.add_argument(f'user-agent={USER_AGENT}')
        
        # 初始化WebDriver
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
        # 设置Cookie
        self.driver.get(BASE_URL)
        for cookie in INITIAL_COOKIES:
            self.driver.add_cookie(cookie)
        
    def get_page(self, page_num):
        """获取页面内容"""
        url = f"{BASE_URL}/shop/bags?page={page_num}"
        logger.info(f"正在爬取第 {page_num} 页")
        logger.info(f"请求URL: {url}")
        
        for attempt in range(MAX_RETRIES):
            try:
                # 访问页面
                self.driver.get(url)
                
                # 等待页面加载
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "ProductCard_productCardImage____xct"))
                )
                
                # 添加随机延迟
                delay = random.uniform(REQUEST_DELAY_MIN, REQUEST_DELAY_MAX)
                logger.info(f"等待 {delay:.2f} 秒...")
                time.sleep(delay)
                
                # 获取页面内容
                page_source = self.driver.page_source
                
                # 检查是否被重定向到验证页面
                if "challenge" in self.driver.current_url or "verify" in self.driver.current_url:
                    logger.error("被重定向到验证页面，需要处理验证")
                    logger.info(f"重定向URL: {self.driver.current_url}")
                    return None
                
                return page_source
                
            except Exception as e:
                logger.error(f"请求失败 (尝试 {attempt + 1}/{MAX_RETRIES}): {str(e)}")
                if attempt == MAX_RETRIES - 1:
                    return None
                time.sleep(RETRY_DELAY)
    
    def parse_product(self, html_content):
        """解析产品页面HTML内容"""
        try:
            # 记录页面信息
            logging.info(f"开始解析页面，HTML长度: {len(html_content)}")
            
            # 使用BeautifulSoup解析HTML
            soup = BeautifulSoup(html_content, 'html.parser')
            
            # 查找所有产品卡片
            product_cards = soup.find_all('div', {'data-testid': 'search-result-card'})
            logging.info(f"找到 {len(product_cards)} 个产品卡片")
            
            products = []
            for index, card in enumerate(product_cards, 1):
                try:
                    # 获取产品链接
                    product_link = card.find('a', {'data-testid': 'related-work-card'})
                    if not product_link:
                        logging.warning(f"产品 {index} 未找到链接")
                        continue
                        
                    href = product_link.get('href', '')
                    if not href:
                        logging.warning(f"产品 {index} 链接为空")
                        continue
                        
                    # 构建完整URL
                    product_url = urljoin('https://www.redbubble.com', href)
                    
                    # 获取产品ID
                    product_id = href.split('/')[-1].split('.')[0] if href else None
                    
                    # 获取产品图片
                    img = card.find('img', {'class': 'ProductCard_productCardImage____xct'})
                    image_url = img.get('src') if img else None
                    
                    # 获取产品标题
                    title_elem = card.find('span', {'class': 'styles_body2__5c7a80ef'})
                    title = title_elem.text.strip() if title_elem else None
                    
                    # 获取艺术家信息
                    artist_elem = card.find('div', {'class': 'ProductCard_caption__zzNfV'})
                    artist = artist_elem.find('span').text.strip() if artist_elem else None
                    
                    # 获取价格信息
                    price_elem = card.find('span', {'data-testid': 'line-item-price-price'})
                    price = price_elem.text.strip() if price_elem else None
                    
                    # 检查数据完整性
                    if not all([product_id, title, price, image_url, product_url, artist]):
                        logging.warning(f"产品 {index} 数据不完整，跳过")
                        continue
                    
                    # 构建产品数据
                    product = {
                        'id': product_id,
                        'title': title,
                        'price': price,
                        'image_url': image_url,
                        'product_url': product_url,
                        'artist': artist
                    }
                    
                    # 记录解析结果
                    logging.info(f"成功解析产品 {index}:")
                    logging.info(f"  - 标题: {title}")
                    logging.info(f"  - 价格: {price}")
                    logging.info(f"  - 图片: {image_url}")
                    logging.info(f"  - 链接: {product_url}")
                    logging.info(f"  - 艺术家: {artist}")
                    
                    products.append(product)
                    
                except Exception as e:
                    logging.error(f"解析产品 {index} 时出错: {str(e)}")
                    continue
            
            return products
            
        except Exception as e:
            logging.error(f"解析产品页面时出错: {str(e)}")
            return []
    
    def save_products(self, products, page_num):
        """保存产品数据"""
        if not products:
            return
            
        # 保存为CSV
        csv_file = os.path.join(DATA_DIR, f'products_page_{page_num}.csv')
        df = pd.DataFrame(products)
        df.to_csv(csv_file, index=False, encoding='utf-8')
        logger.info(f"已保存 {len(products)} 个产品到 {csv_file}")
        
        # 保存为JSON
        json_file = os.path.join(DATA_DIR, f'products_page_{page_num}.json')
        df.to_json(json_file, orient='records', force_ascii=False, indent=2)
        logger.info(f"已保存 {len(products)} 个产品到 {json_file}")
    
    def crawl(self, start_page=1, end_page=1):
        """爬取指定页面范围的产品"""
        try:
            for page in range(start_page, end_page + 1):
                html = self.get_page(page)
                if html:
                    products = self.parse_product(html)
                    self.save_products(products, page)
                else:
                    logger.error(f"第 {page} 页获取失败")
                
                # 页面间随机延迟
                if page < end_page:
                    delay = random.uniform(PAGE_DELAY_MIN, PAGE_DELAY_MAX)
                    logger.info(f"等待 {delay:.2f} 秒后继续...")
                    time.sleep(delay)
        finally:
            # 确保关闭浏览器
            self.driver.quit()

if __name__ == "__main__":
    spider = RedbubbleSpider()
    spider.crawl(1, 3)  # 测试爬取前3页 