"""
爬虫工具模块 - 负责从Redbubble抓取商品信息
从 crawler/crawler.py 迁移而来，适配backend环境
"""

from playwright.sync_api import sync_playwright
import logging

# 配置日志
logger = logging.getLogger(__name__)

def crawl_redbubble(keyword, pages, category):
    """
    爬取Redbubble多页商品信息
    :param keyword: 搜索关键词
    :param pages: 要爬取的页数
    :param category: 商品类目（如u-clothing等）
    :return: 商品信息列表，每个元素包含title, img, link
    """
    results = []
    try:
        with sync_playwright() as p:
            # 启动浏览器，使用headless模式
            browser = p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage", 
                    "--disable-gpu",
                    "--window-size=1920,1080"
                ]
            )
            
            # 创建浏览器上下文，设置用户代理
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
                locale="zh-CN"
            )
            
            page = context.new_page()
            
            # 逐页爬取商品信息
            for page_num in range(1, pages + 1):
                try:
                    # 构建搜索URL
                    url = f"https://www.redbubble.com/shop/?iaCode={category}&query={keyword}&ref=search_box&page={page_num}"
                    logger.info(f"正在爬取第{page_num}页: {url}")
                    
                    # 访问页面
                    page.goto(url)
                    
                    # 等待商品卡片加载
                    page.wait_for_selector('div[data-testid="search-result-card"]', timeout=30000)
                    
                    # 获取所有商品卡片
                    cards = page.query_selector_all('div[data-testid="search-result-card"]')
                    logger.info(f"第{page_num}页找到{len(cards)}个商品")
                    
                    # 解析每个商品卡片
                    for card in cards:
                        try:
                            # 获取商品链接
                            a_tag = card.query_selector('a[data-testid="related-work-card"]')
                            # 获取商品图片
                            img_tag = card.query_selector('img[alt^="Item preview"]')
                            
                            if a_tag and img_tag:
                                # 提取链接，确保是完整URL
                                link = a_tag.get_attribute("href")
                                if link and not link.startswith("http"):
                                    link = "https://www.redbubble.com" + link
                                
                                # 提取图片URL
                                img_url = img_tag.get_attribute("src")
                                
                                # 提取标题，去除前缀
                                title = img_tag.get_attribute("alt")
                                if title and title.startswith("Item preview, "):
                                    title = title.replace("Item preview, ", "", 1)
                                
                                # 添加到结果列表
                                if title and img_url and link:
                                    results.append({
                                        "title": title,
                                        "img": img_url,
                                        "link": link
                                    })
                                    
                        except Exception as e:
                            logger.warning(f"解析商品卡片失败: {e}")
                            continue
                            
                except Exception as e:
                    logger.error(f"爬取第{page_num}页失败: {e}")
                    continue
            
            # 关闭浏览器
            browser.close()
            
    except Exception as e:
        logger.error(f"爬虫执行失败: {e}")
        raise e
    
    logger.info(f"爬取完成，共获取{len(results)}个商品")
    return results 


if __name__ == "__main__":
    results = crawl_redbubble("cat", 1, "u-clothing")
    print(results)