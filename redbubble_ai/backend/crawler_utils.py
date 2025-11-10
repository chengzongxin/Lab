"""
爬虫工具模块 - 负责从Redbubble抓取商品信息
从 crawler/crawler.py 迁移而来，适配backend环境
"""

from playwright.sync_api import sync_playwright
import logging
import asyncio
import sys

# 配置日志
logger = logging.getLogger(__name__)

# 修复Windows下的事件循环问题
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

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
            # 启动浏览器，使用headless模式，增加稳定性配置
            # 使用系统的Chrome浏览器
            browser = p.chromium.launch(
                headless=True,
                channel="chrome",  # 使用系统的Chrome浏览器
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage", 
                    "--disable-gpu",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                    "--window-size=1920,1080"
                ]
            )
            
            # 创建浏览器上下文，设置用户代理和超时
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
                locale="zh-CN"
            )
            
            # 设置页面超时
            context.set_default_timeout(30000)  # 30秒超时
            
            page = context.new_page()
            
            # 逐页爬取商品信息
            for page_num in range(1, pages + 1):
                try:
                    # 构建搜索URL
                    # 判断keyword是否存在，如果不存在则不添加query参数
                    if keyword:
                        url = f"https://www.redbubble.com/shop/?iaCode={category}&query={keyword}&ref=search_box&page={page_num}&sortOrder=top%20selling"
                    else:
                        url = f"https://www.redbubble.com/shop/?iaCode={category}&ref=search_box&page={page_num}&sortOrder=top%20selling"
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
                            # 获取商品链接 - 使用正确的data-testid
                            a_tag = card.query_selector('a[data-testid="search-results-page-product-card"]')
                            # 获取商品图片
                            img_tag = card.query_selector('img[alt^="Item preview"]')
                            
                            if a_tag and img_tag:
                                # 提取链接，确保是完整URL
                                link = a_tag.get_attribute("href")
                                if link and not link.startswith("http"):
                                    link = "https://www.redbubble.com" + link
                                
                                # 提取图片URL
                                img_url = img_tag.get_attribute("src")
                                
                                # 提取标题 - 优先从标题元素提取，如果没有则从图片alt属性提取
                                title = None
                                title_element = card.query_selector('span.SearchResultCard_title__XlcOR')
                                if title_element:
                                    title = title_element.inner_text().strip()
                                
                                # 如果标题元素提取失败，从图片alt属性提取
                                if not title:
                                    title = img_tag.get_attribute("alt")
                                    if title and title.startswith("Item preview, "):
                                        # 移除 "Item preview, " 前缀，并移除 " designed and sold by ..." 后缀
                                        title = title.replace("Item preview, ", "", 1)
                                        # 移除 " designed and sold by ..." 部分
                                        if " designed and sold by " in title:
                                            title = title.split(" designed and sold by ")[0]
                                
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
            try:
                browser.close()
            except Exception as close_error:
                logger.warning(f"浏览器关闭时出现错误（忽略）: {close_error}")
            
    except Exception as e:
        import traceback
        logger.error(f"详细错误信息: {traceback.format_exc()}")
        logger.error(f"爬虫执行失败: {e}")
        
        # 检查是否是浏览器安装问题
        error_str = str(e)
        if "executable doesn't exist" in error_str or "browser not found" in error_str or "not found" in error_str:
            logger.error("❌ Playwright浏览器未安装！")
            logger.error("解决方案：运行 'python -m playwright install chromium'")
            raise Exception("Playwright浏览器未安装，请运行: python -m playwright install chromium")
        
        # 检查是否是事件循环问题
        if "NotImplementedError" in error_str or "ProactorEventLoop" in error_str:
            logger.error("❌ Windows事件循环问题！")
            logger.error("解决方案：重启服务器应该能修复此问题")
            raise Exception("Windows事件循环问题，请重启FastAPI服务")
        
        raise e
    
    logger.info(f"爬取完成，共获取{len(results)}个商品")
    return results 


def crawl_temu_mall(mall_id, max_pages=10, use_persistent_context=False, user_data_dir=None, debug_port=None):
    """
    爬取TEMU某个卖家店铺的所有商品
    :param mall_id: 店铺ID（从URL中的mall_id参数获取）
    :param max_pages: 最大爬取页数（默认10页，防止无限爬取）
    :param use_persistent_context: 是否使用持久化上下文（保持登录状态）
    :param user_data_dir: 用户数据目录路径（用于保持登录状态）
    :param debug_port: 调试端口（连接到已打开的浏览器，例如9222）
    :return: 商品信息列表，每个元素包含title, img, link, price
    """
    results = []
    browser = None
    context = None
    
    try:
        with sync_playwright() as p:
            # 方式1：连接到已打开的浏览器（调试模式）
            if debug_port:
                logger.info(f"连接到调试端口 {debug_port} 的浏览器...")
                try:
                    browser = p.chromium.connect_over_cdp(f"http://localhost:{debug_port}")
                    logger.info("成功连接到已打开的浏览器")
                    # 获取或创建上下文
                    contexts = browser.contexts
                    if contexts:
                        context = contexts[0]
                        logger.info("使用已存在的浏览器上下文")
                    else:
                        context = browser.new_context()
                        logger.info("创建新的浏览器上下文")
                except Exception as e:
                    logger.error(f"连接调试端口失败: {e}")
                    logger.info("回退到启动新浏览器...")
                    browser = None
            
            # 方式2：使用持久化上下文（保持登录状态）
            if not browser and use_persistent_context:
                if not user_data_dir:
                    # 使用默认的用户数据目录
                    import tempfile
                    user_data_dir = tempfile.mkdtemp(prefix="temu_browser_")
                    logger.info(f"使用临时用户数据目录: {user_data_dir}")
                
                logger.info(f"使用持久化上下文，用户数据目录: {user_data_dir}")
                # 使用系统的Chrome浏览器
                context = p.chromium.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    headless=False,
                    channel="chrome",  # 使用系统的Chrome浏览器
                    args=[
                        "--no-sandbox",
                        "--disable-dev-shm-usage", 
                        "--disable-gpu",
                        "--window-size=1920,1080"
                    ],
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    locale="en-US",
                    viewport={"width": 1920, "height": 1080}
                )
                logger.info("持久化上下文已创建，将保持登录状态（使用Chrome浏览器）")
            
            # 方式3：普通启动浏览器（默认方式）
            if not browser and not context:
                logger.info("启动新浏览器（使用Chrome）...")
                # 使用系统的Chrome浏览器
                browser = p.chromium.launch(
                    headless=False,
                    channel="chrome",  # 使用系统的Chrome浏览器
                    args=[
                        "--no-sandbox",
                        "--disable-dev-shm-usage", 
                        "--disable-gpu",
                        "--disable-web-security",
                        "--window-size=1920,1080"
                    ]
                )
                
                # 创建浏览器上下文
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    locale="en-US",
                    viewport={"width": 1920, "height": 1080}
                )
            
            # 设置页面超时
            context.set_default_timeout(30000)  # 30秒超时
            
            # 获取或创建页面
            if context.pages:
                page = context.pages[0]
                logger.info("使用已存在的页面")
            else:
                page = context.new_page()
                logger.info("创建新页面")
            
            # 构建店铺URL（简化版，只保留必要的参数）
            base_url = f"https://www.temu.com/mall.html?mall_id={mall_id}"
            logger.info(f"正在访问TEMU店铺: {base_url}")
            
            # 访问店铺首页
            page.goto(base_url, wait_until="networkidle")
            
            # 等待商品加载
            page.wait_for_selector('div.EKDT7a3v', timeout=30000)
            
            # 记录已爬取的商品链接，避免重复
            seen_links = set()
            
            # 滚动页面以加载更多商品（TEMU可能使用无限滚动）
            last_height = 0
            scroll_attempts = 0
            max_scroll_attempts = 5  # 最多滚动5次
            
            while scroll_attempts < max_scroll_attempts:
                # 滚动到底部
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(2000)  # 等待2秒让内容加载
                
                # 检查是否有新内容加载
                current_height = page.evaluate("document.body.scrollHeight")
                if current_height == last_height:
                    scroll_attempts += 1
                else:
                    scroll_attempts = 0
                last_height = current_height
            
            # 获取所有商品卡片
            cards = page.query_selector_all('div.EKDT7a3v')
            logger.info(f"找到 {len(cards)} 个商品卡片")
            
            # 解析每个商品卡片
            for card in cards:
                try:
                    # 获取商品链接 - 尝试多种选择器
                    link_element = None
                    # 方法1：使用完整的class组合
                    link_element = card.query_selector('a._2Tl9qLr1._1ak1dai3')
                    # 方法2：如果方法1失败，尝试只匹配部分class
                    if not link_element:
                        link_element = card.query_selector('a[class*="_2Tl9qLr1"]')
                    # 方法3：如果还是失败，尝试查找包含href的a标签
                    if not link_element:
                        all_links = card.query_selector_all('a[href]')
                        for a in all_links:
                            href = a.get_attribute("href")
                            if href and ("/g-" in href or ".html" in href):
                                link_element = a
                                break
                    
                    if not link_element:
                        continue
                    
                    link = link_element.get_attribute("href")
                    if not link:
                        continue
                    
                    # 构建完整URL
                    if link.startswith("/"):
                        link = "https://www.temu.com" + link
                    elif not link.startswith("http"):
                        link = "https://www.temu.com/" + link
                    
                    # 检查是否已爬取过（避免重复）
                    if link in seen_links:
                        continue
                    seen_links.add(link)
                    
                    # 获取商品标题 - 尝试多种方法
                    title = None
                    # 方法1：从标题span获取
                    title_element = card.query_selector('span._2D9RBAXL')
                    if title_element:
                        title = title_element.inner_text().strip()
                    
                    # 方法2：如果标题元素不存在，尝试从h3标签获取
                    if not title:
                        h3_element = card.query_selector('h3._2BvQbnbN')
                        if h3_element:
                            title = h3_element.inner_text().strip()
                    
                    # 方法3：从链接的aria-label获取
                    if not title:
                        title_attr = link_element.get_attribute("aria-label")
                        if title_attr:
                            title = title_attr.strip()
                    
                    # 方法4：从图片的alt属性获取
                    if not title:
                        img_element = card.query_selector('img[alt]')
                        if img_element:
                            alt_text = img_element.get_attribute("alt")
                            if alt_text and "item picture" in alt_text.lower():
                                # 清理alt文本
                                title = alt_text.replace("item picture", "").strip()
                    
                    # 获取商品图片 - 尝试多种选择器
                    img_url = None
                    # 方法1：使用goods-img-external class
                    img_element = card.query_selector('img.goods-img-external')
                    # 方法2：如果失败，尝试匹配包含goods-img的class
                    if not img_element:
                        img_element = card.query_selector('img[class*="goods-img"]')
                    # 方法3：如果还是失败，尝试查找所有img标签
                    if not img_element:
                        all_imgs = card.query_selector_all('img[src]')
                        for img in all_imgs:
                            src = img.get_attribute("src")
                            if src and ("kwcdn.com" in src or "temu.com" in src):
                                img_element = img
                                break
                    
                    if img_element:
                        img_url = img_element.get_attribute("src")
                        # 如果没有src，尝试从data-src获取（懒加载）
                        if not img_url:
                            img_url = img_element.get_attribute("data-src")
                    
                    # 获取商品价格
                    price = None
                    price_element = card.query_selector('span._2XgTiMJi')
                    if price_element:
                        price = price_element.inner_text().strip()
                    
                    # 添加到结果列表（至少需要标题和链接）
                    if title and link:
                        product = {
                            "title": title,
                            "link": link,
                            "img": img_url or "",
                            "price": price or ""
                        }
                        results.append(product)
                        logger.debug(f"提取商品: {title[:50]}...")
                        
                except Exception as e:
                    logger.warning(f"解析商品卡片失败: {e}")
                    continue
            
            # 关闭浏览器（只有普通启动的浏览器才需要关闭）
            # 注意：使用持久化上下文或连接到已打开的浏览器时，不要关闭
            if browser and not use_persistent_context and not debug_port:
                try:
                    browser.close()
                    logger.info("浏览器已关闭")
                except Exception as close_error:
                    logger.warning(f"浏览器关闭时出现错误（忽略）: {close_error}")
            elif use_persistent_context:
                logger.info("使用持久化上下文，浏览器保持打开状态")
            elif debug_port:
                logger.info("连接到已打开的浏览器，不关闭浏览器")
            
    except Exception as e:
        import traceback
        logger.error(f"详细错误信息: {traceback.format_exc()}")
        logger.error(f"TEMU爬虫执行失败: {e}")
        
        # 检查是否是浏览器安装问题
        error_str = str(e)
        if "executable doesn't exist" in error_str or "browser not found" in error_str:
            logger.error("❌ Playwright浏览器未安装！")
            logger.error("解决方案：运行 'python -m playwright install chromium'")
            raise Exception("Playwright浏览器未安装，请运行: python -m playwright install chromium")
        
        raise e
    
    logger.info(f"TEMU店铺爬取完成，共获取 {len(results)} 个商品")
    return results


if __name__ == "__main__":
    # 测试Redbubble爬虫
    # results = crawl_redbubble("animal", 1, "u-socks")
    # print(results)
    
    # 测试TEMU爬虫
    results = crawl_temu_mall("23225409861", max_pages=1, use_persistent_context=True, user_data_dir="/tmp/chrome_debug", debug_port=9222)
    print(f"爬取到 {len(results)} 个商品")
    for i, item in enumerate(results[:5], 1):  # 只打印前5个
        print(f"{i}. {item['title'][:50]}... - {item['price']}")