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
            
            # 访问店铺首页，使用load策略
            try:
                page.goto(base_url, wait_until="load", timeout=60000)  # 增加到60秒超时
            except Exception as e:
                logger.warning(f"页面加载超时，尝试继续: {e}")
            
            # 等待商品加载，增加超时时间
            try:
                page.wait_for_selector('div.EKDT7a3v', timeout=30000)
                logger.info("商品元素已加载")
            except Exception as e:
                logger.warning(f"等待商品元素超时: {e}")
                # 尝试等待其他可能的商品容器
                try:
                    page.wait_for_selector('div[class*="EKDT"]', timeout=10000)
                    logger.info("找到商品容器（使用备用选择器）")
                except:
                    logger.error("无法找到商品元素，可能页面结构已变化或需要登录")
                    raise Exception("无法找到商品元素，请检查页面是否需要登录")
            
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


def crawl_temu_category(category_url, min_sales=1000, use_persistent_context=False, user_data_dir=None, debug_port=None):
    """
    爬取TEMU某个类目下的所有商品，筛选销量大于指定值的爆款商品
    :param category_url: 类目URL
    :param min_sales: 最小销量（默认1000）
    :param use_persistent_context: 是否使用持久化上下文
    :param user_data_dir: 用户数据目录路径
    :param debug_port: 调试端口
    :return: 商品信息列表，每个元素包含goods_id, title, img, link, price, sales_count等
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
                    contexts = browser.contexts
                    if contexts:
                        context = contexts[0]
                    else:
                        context = browser.new_context()
                except Exception as e:
                    logger.error(f"连接调试端口失败: {e}")
                    browser = None
            
            # 方式2：使用持久化上下文
            if not browser and use_persistent_context:
                if not user_data_dir:
                    import tempfile
                    user_data_dir = tempfile.mkdtemp(prefix="temu_browser_")
                
                logger.info(f"使用持久化上下文，用户数据目录: {user_data_dir}")
                context = p.chromium.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    headless=False,
                    channel="chrome",
                    args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu", "--window-size=1920,1080"],
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    locale="en-US",
                    viewport={"width": 1920, "height": 1080}
                )
            
            # 方式3：普通启动浏览器
            if not browser and not context:
                logger.info("启动新浏览器（使用Chrome）...")
                browser = p.chromium.launch(
                    headless=False,
                    channel="chrome",
                    args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu", "--disable-web-security", "--window-size=1920,1080"]
                )
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    locale="en-US",
                    viewport={"width": 1920, "height": 1080}
                )
            
            context.set_default_timeout(30000)
            
            if context.pages:
                page = context.pages[0]
            else:
                page = context.new_page()
            
            logger.info(f"正在访问TEMU类目: {category_url}")
            
            # 访问页面，使用load策略而不是networkidle（因为TEMU可能有持续的网络请求）
            try:
                page.goto(category_url, wait_until="load", timeout=60000)  # 增加到60秒超时
            except Exception as e:
                logger.warning(f"页面加载超时，尝试继续: {e}")
                # 即使超时也继续，可能页面已经部分加载
            
            # 等待商品加载，增加超时时间
            try:
                page.wait_for_selector('div.EKDT7a3v', timeout=30000)
                logger.info("商品元素已加载")
            except Exception as e:
                logger.warning(f"等待商品元素超时: {e}")
                # 尝试等待其他可能的商品容器
                try:
                    page.wait_for_selector('div[class*="EKDT"]', timeout=10000)
                    logger.info("找到商品容器（使用备用选择器）")
                except:
                    logger.error("无法找到商品元素，可能页面结构已变化或需要登录")
                    raise Exception("无法找到商品元素，请检查页面是否需要登录")
            
            seen_goods_ids = set()
            
            # 点击"See more"按钮加载更多商品
            max_click_attempts = 1  # 最多点击20次
            click_attempts = 0
            
            while click_attempts < max_click_attempts:
                # 查找"See more"按钮
                see_more_button = None
                try:
                    # 尝试多种选择器
                    see_more_button = page.query_selector('div[aria-label="See more items"]')
                    if not see_more_button:
                        see_more_button = page.query_selector('button[aria-label="See more items"]')
                    if not see_more_button:
                        # 通过class查找
                        see_more_button = page.query_selector('div._2ugbvrpI[aria-label*="See more"]')
                    if not see_more_button:
                        # 通过文本查找（遍历所有div元素）
                        all_divs = page.query_selector_all('div')
                        for div in all_divs:
                            try:
                                text = div.inner_text().strip()
                                aria_label = div.get_attribute("aria-label") or ""
                                if ("See more" in text or "See more" in aria_label) and div.is_visible():
                                    see_more_button = div
                                    break
                            except:
                                continue
                    
                    if see_more_button:
                        # 检查按钮是否可见和可点击
                        is_visible = see_more_button.is_visible()
                        if is_visible:
                            logger.info(f"找到See more按钮，点击加载更多商品 (第{click_attempts + 1}次)")
                            # 滚动到按钮位置，确保按钮在视口中
                            see_more_button.scroll_into_view_if_needed()
                            page.wait_for_timeout(500)  # 等待滚动完成
                            see_more_button.click()
                            page.wait_for_timeout(3000)  # 等待新商品加载
                            click_attempts += 1
                        else:
                            logger.info("See more按钮不可见，可能已加载完所有商品")
                            break
                    else:
                        logger.info("未找到See more按钮，可能已加载完所有商品")
                        break
                except Exception as e:
                    logger.warning(f"点击See more按钮时出错: {e}")
                    break
            
            # 获取所有商品卡片
            cards = page.query_selector_all('div.EKDT7a3v')
            logger.info(f"找到 {len(cards)} 个商品卡片")
            
            # 解析每个商品卡片
            for card in cards:
                try:
                    # 获取商品链接
                    link_element = None
                    link_element = card.query_selector('a._2Tl9qLr1._1ak1dai3')
                    if not link_element:
                        link_element = card.query_selector('a[class*="_2Tl9qLr1"]')
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
                    
                    # 从链接中提取goods_id
                    goods_id = None
                    if "/g-" in link:
                        parts = link.split("/g-")
                        if len(parts) > 1:
                            goods_id = parts[1].split(".")[0].split("?")[0]
                    
                    if not goods_id or goods_id in seen_goods_ids:
                        continue
                    seen_goods_ids.add(goods_id)
                    
                    # 获取商品标题
                    title = None
                    title_element = card.query_selector('span._2D9RBAXL')
                    if title_element:
                        title = title_element.inner_text().strip()
                    if not title:
                        h2_element = card.query_selector('h2._2BvQbnbN')
                        if h2_element:
                            title = h2_element.inner_text().strip()
                    if not title:
                        title_attr = link_element.get_attribute("aria-label")
                        if title_attr:
                            title = title_attr.strip()
                    
                    # 获取商品图片
                    img_url = None
                    img_element = card.query_selector('img.goods-img-external')
                    if not img_element:
                        img_element = card.query_selector('img[class*="goods-img"]')
                    if not img_element:
                        all_imgs = card.query_selector_all('img[src]')
                        for img in all_imgs:
                            src = img.get_attribute("src")
                            if src and ("kwcdn.com" in src or "temu.com" in src):
                                img_element = img
                                break
                    
                    if img_element:
                        img_url = img_element.get_attribute("src")
                        if not img_url:
                            img_url = img_element.get_attribute("data-src")
                    
                    # 获取价格
                    price = None
                    price_element = card.query_selector('span._2XgTiMJi')
                    if price_element:
                        price = price_element.inner_text().strip()
                    
                    # 获取原价
                    original_price = None
                    original_price_element = card.query_selector('span._3TAPHDOX')
                    if original_price_element:
                        original_price_text = original_price_element.inner_text().strip()
                        if "Original price" in original_price_text:
                            original_price = original_price_text.replace("Original price", "").strip()
                    
                    # 获取销量（关键信息）
                    sales_count = 0
                    sales_text = None
                    # 尝试多种选择器查找销量元素
                    sales_element = card.query_selector('span._1GKMA1Nk')
                    if not sales_element:
                        sales_element = card.query_selector('span[class*="_1GKMA1Nk"]')
                    if not sales_element:
                        # 查找包含 "sold" 文本的元素
                        all_spans = card.query_selector_all('span')
                        for span in all_spans:
                            text = span.inner_text().strip().lower()
                            if 'sold' in text and ('k' in text or 'm' in text):
                                sales_element = span
                                break
                    
                    if sales_element:
                        # 获取销量文本，优先从 _2XgTiMJi 类获取（包含完整文本）
                        sales_text_element = sales_element.query_selector('span._2XgTiMJi')
                        if sales_text_element:
                            sales_text = sales_text_element.inner_text().strip()
                        else:
                            sales_text = sales_element.inner_text().strip()
                        
                        # 解析销量文本，支持格式如 "1.2K+sold" -> 1200, "100K+" -> 100000
                        if sales_text:
                            sales_text_lower = sales_text.lower()
                            try:
                                # 移除 "sold" 文本
                                num_text = sales_text_lower.replace("sold", "").strip()
                                
                                # 处理 K+ 格式（如 "1.2K+" -> 1200）
                                if "k+" in num_text or (num_text.endswith("k") and "+" not in num_text):
                                    # 提取数字部分
                                    num_str = num_text.replace("k+", "").replace("k", "").replace("+", "").strip()
                                    if num_str:
                                        sales_count = int(float(num_str) * 1000)
                                
                                # 处理 M+ 格式（如 "1.5M+" -> 1500000）
                                elif "m+" in num_text or (num_text.endswith("m") and "+" not in num_text):
                                    num_str = num_text.replace("m+", "").replace("m", "").replace("+", "").strip()
                                    if num_str:
                                        sales_count = int(float(num_str) * 1000000)
                                
                                # 如果是纯数字，直接转换
                                elif num_text.replace(".", "").replace("+", "").isdigit():
                                    sales_count = int(float(num_text.replace("+", "")))
                                
                                logger.debug(f"解析销量: '{sales_text}' -> {sales_count}")
                            except Exception as e:
                                logger.warning(f"解析销量失败: '{sales_text}', 错误: {e}")
                                sales_count = 0
                    
                    # 获取评分
                    rating = None
                    rating_element = card.query_selector('div.oMRVEXZ7')
                    if rating_element:
                        # 从style中提取评分百分比，如 width:92.8571% -> 4.64 (92.8571/20)
                        style = rating_element.get_attribute("style")
                        if style and "width:" in style:
                            try:
                                width_str = style.split("width:")[1].split("%")[0].strip()
                                width_percent = float(width_str)
                                rating = round(width_percent / 20, 2)  # 转换为5分制
                            except:
                                pass
                    
                    # 获取评论数
                    review_count = 0
                    review_element = card.query_selector('span._3cWlbpFG')
                    if review_element:
                        review_text = review_element.inner_text().strip()
                        if review_text:
                            try:
                                review_text_clean = review_text.replace("reviews", "").replace(",", "").strip()
                                review_count = int(review_text_clean)
                            except:
                                pass
                    
                    # 只保存销量大于等于min_sales的商品
                    if sales_count >= min_sales:
                        product = {
                            "goods_id": goods_id,
                            "title": title,
                            "link": link,
                            "img": img_url or "",
                            "price": price or "",
                            "original_price": original_price or "",
                            "sales_count": sales_count,
                            "sales_text": sales_text or "",
                            "rating": rating,
                            "review_count": review_count
                        }
                        results.append(product)
                        logger.info(f"找到爆款商品: {title[:50]}... 销量: {sales_count}")
                    else:
                        logger.debug(f"商品销量不足: {title[:50] if title else 'Unknown'}... 销量: {sales_count}")
                        
                except Exception as e:
                    logger.warning(f"解析商品卡片失败: {e}")
                    continue
            
            # 关闭浏览器
            if browser and not use_persistent_context and not debug_port:
                try:
                    browser.close()
                except:
                    pass
            
    except Exception as e:
        import traceback
        logger.error(f"详细错误信息: {traceback.format_exc()}")
        logger.error(f"TEMU类目爬虫执行失败: {e}")
        raise e
    
    logger.info(f"TEMU类目爬取完成，共获取 {len(results)} 个爆款商品（销量>={min_sales}）")
    return results


def crawl_temu_product_detail(product_url, use_persistent_context=False, user_data_dir=None, debug_port=None):
    """
    爬取TEMU商品详情页，提取卖家店铺信息
    :param product_url: 商品详情页URL
    :param use_persistent_context: 是否使用持久化上下文
    :param user_data_dir: 用户数据目录路径
    :param debug_port: 调试端口
    :return: 商品详情信息，包含mall_id, seller_url等
    """
    result = {}
    browser = None
    context = None
    
    try:
        with sync_playwright() as p:
            # 连接到浏览器（复用之前的逻辑）
            if debug_port:
                try:
                    browser = p.chromium.connect_over_cdp(f"http://localhost:{debug_port}")
                    contexts = browser.contexts
                    if contexts:
                        context = contexts[0]
                    else:
                        context = browser.new_context()
                except:
                    browser = None
            
            if not browser and use_persistent_context:
                if not user_data_dir:
                    import tempfile
                    user_data_dir = tempfile.mkdtemp(prefix="temu_browser_")
                context = p.chromium.launch_persistent_context(
                    user_data_dir=user_data_dir,
                    headless=False,
                    channel="chrome",
                    args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu", "--window-size=1920,1080"],
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    locale="en-US",
                    viewport={"width": 1920, "height": 1080}
                )
            
            if not browser and not context:
                browser = p.chromium.launch(
                    headless=False,
                    channel="chrome",
                    args=["--no-sandbox", "--disable-dev-shm-usage", "--disable-gpu", "--disable-web-security", "--window-size=1920,1080"]
                )
                context = browser.new_context(
                    user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
                    locale="en-US",
                    viewport={"width": 1920, "height": 1080}
                )
            
            context.set_default_timeout(30000)
            
            if context.pages:
                page = context.pages[0]
            else:
                page = context.new_page()
            
            logger.info(f"正在访问商品详情页: {product_url}")
            
            # 访问页面，使用load策略
            try:
                page.goto(product_url, wait_until="load", timeout=60000)  # 增加到60秒超时
            except Exception as e:
                logger.warning(f"页面加载超时，尝试继续: {e}")
            
            page.wait_for_timeout(3000)  # 等待页面完全加载，增加等待时间
            
            # 从URL中提取goods_id
            goods_id = None
            if "/g-" in product_url:
                parts = product_url.split("/g-")
                if len(parts) > 1:
                    goods_id = parts[1].split(".")[0].split("?")[0]
            
            result["goods_id"] = goods_id
            
            # 查找卖家店铺链接
            # 方法1：查找包含mall_id的链接
            mall_id = None
            seller_url = None
            
            # 查找所有链接，寻找包含mall.html的链接
            all_links = page.query_selector_all('a[href*="mall.html"]')
            for link in all_links:
                href = link.get_attribute("href")
                if href and "mall_id=" in href:
                    # 提取mall_id
                    import re
                    match = re.search(r'mall_id=(\d+)', href)
                    if match:
                        mall_id = match.group(1)
                        if href.startswith("/"):
                            seller_url = "https://www.temu.com" + href
                        elif not href.startswith("http"):
                            seller_url = "https://www.temu.com/" + href
                        else:
                            seller_url = href
                        break
            
            # 方法2：如果没找到，尝试从页面中查找mall_id
            if not mall_id:
                page_content = page.content()
                import re
                match = re.search(r'mall_id["\']?\s*[:=]\s*["\']?(\d+)', page_content)
                if match:
                    mall_id = match.group(1)
                    seller_url = f"https://www.temu.com/mall.html?mall_id={mall_id}"
            
            result["mall_id"] = mall_id
            result["seller_url"] = seller_url
            
            # 获取商品描述
            description = None
            desc_element = page.query_selector('div[class*="description"]')
            if not desc_element:
                desc_element = page.query_selector('div[class*="Description"]')
            if desc_element:
                description = desc_element.inner_text().strip()
            result["description"] = description
            
            # 获取商品图片列表
            images = []
            img_elements = page.query_selector_all('img[src*="kwcdn.com"]')
            for img in img_elements:
                src = img.get_attribute("src")
                if src and src not in images:
                    images.append(src)
            result["images"] = images
            
            # 获取视频URL
            video_url = None
            video_element = page.query_selector('video[src]')
            if video_element:
                video_url = video_element.get_attribute("src")
            result["video_url"] = video_url
            
            # 获取卖家名称
            seller_name = None
            # 尝试多种方式查找卖家名称
            seller_name_element = page.query_selector('span[class*="seller"]')
            if not seller_name_element:
                seller_name_element = page.query_selector('a[href*="mall.html"]')
            if seller_name_element:
                seller_name = seller_name_element.inner_text().strip()
            result["seller_name"] = seller_name
            
            # 关闭浏览器
            if browser and not use_persistent_context and not debug_port:
                try:
                    browser.close()
                except:
                    pass
            
    except Exception as e:
        import traceback
        logger.error(f"详细错误信息: {traceback.format_exc()}")
        logger.error(f"TEMU商品详情爬虫执行失败: {e}")
        raise e
    
    logger.info(f"商品详情爬取完成: goods_id={result.get('goods_id')}, mall_id={result.get('mall_id')}")
    return result


def crawl_temu_category_full_workflow(
    category_url: str,
    min_sales: int = 1000,
    crawl_details: bool = True,
    crawl_seller_products: bool = True,
    use_persistent_context: bool = False,
    user_data_dir: str = None,
    debug_port: int = None
):
    """
    完整的TEMU类目爬取工作流：
    1. 爬取类目下的所有爆款商品
    2. 爬取每个商品的详情页，获取卖家信息
    3. 爬取每个卖家的店铺所有商品
    
    :param category_url: 类目URL
    :param min_sales: 最小销量（默认1000）
    :param crawl_details: 是否爬取商品详情
    :param crawl_seller_products: 是否爬取卖家店铺商品
    :param use_persistent_context: 是否使用持久化上下文
    :param user_data_dir: 用户数据目录路径
    :param debug_port: 调试端口
    :return: 统计信息字典
    """
    from temu_db_utils import (
        save_category, save_products, save_product_detail,
        save_seller, save_seller_products,
        update_category_status, update_seller_status
    )
    
    stats = {
        "category_id": None,
        "total_products": 0,
        "saved_products": 0,
        "details_crawled": 0,
        "sellers_found": 0,
        "seller_products_crawled": 0
    }
    
    try:
        # 步骤1：保存类目信息
        logger.info("步骤1: 保存类目信息...")
        category_id = save_category(category_url)
        stats["category_id"] = category_id
        if not category_id:
            logger.error("保存类目失败")
            return stats
        
        update_category_status(category_id, "crawling")
        
        # 步骤2：爬取类目下的爆款商品
        logger.info("步骤2: 爬取类目下的爆款商品...")
        products = crawl_temu_category(
            category_url, min_sales, use_persistent_context, user_data_dir, debug_port
        )
        stats["total_products"] = len(products)
        
        # 保存商品到数据库
        if products:
            saved_count = save_products(products, category_id, category_url)
            stats["saved_products"] = saved_count
            update_category_status(category_id, "crawling", len(products), saved_count)
        
        # 步骤3：爬取商品详情，获取卖家信息
        if crawl_details and products:
            logger.info("步骤3: 爬取商品详情，获取卖家信息...")
            seen_mall_ids = set()
            
            for idx, product in enumerate(products, 1):
                try:
                    logger.info(f"处理商品 {idx}/{len(products)}: {product.get('title', '')[:50]}...")
                    
                    # 爬取商品详情
                    detail = crawl_temu_product_detail(
                        product.get('link'),
                        use_persistent_context,
                        user_data_dir,
                        debug_port
                    )
                    
                    if detail.get('goods_id'):
                        # 保存商品详情
                        product_id = None
                        conn = get_db_conn()
                        cursor = conn.cursor()
                        try:
                            cursor.execute("SELECT id FROM temu_products WHERE goods_id = %s", (detail.get('goods_id'),))
                            result = cursor.fetchone()
                            if result:
                                product_id = result[0]
                        finally:
                            cursor.close()
                            conn.close()
                        
                        if save_product_detail(detail, product_id):
                            stats["details_crawled"] += 1
                        
                        # 记录找到的卖家
                        mall_id = detail.get('mall_id')
                        if mall_id and mall_id not in seen_mall_ids:
                            seen_mall_ids.add(mall_id)
                            save_seller(mall_id, detail.get('seller_name'), detail.get('seller_url'))
                            stats["sellers_found"] += 1
                    
                except Exception as e:
                    logger.error(f"处理商品详情失败: {e}")
                    continue
        
        # 步骤4：爬取卖家店铺的所有商品
        if crawl_seller_products and stats["sellers_found"] > 0:
            logger.info("步骤4: 爬取卖家店铺的所有商品...")
            
            # 获取所有需要爬取的卖家
            conn = get_db_conn()
            cursor = conn.cursor(dictionary=True)
            try:
                cursor.execute("""
                    SELECT DISTINCT tpd.mall_id, ts.id as seller_id
                    FROM temu_product_details tpd
                    JOIN temu_sellers ts ON tpd.mall_id = ts.mall_id
                    WHERE tpd.mall_id IS NOT NULL
                    AND ts.status != 'completed'
                """)
                sellers = cursor.fetchall()
            finally:
                cursor.close()
                conn.close()
            
            for seller in sellers:
                try:
                    mall_id = seller['mall_id']
                    seller_id = seller['seller_id']
                    
                    logger.info(f"爬取卖家店铺: mall_id={mall_id}")
                    update_seller_status(seller_id, "crawling")
                    
                    # 爬取店铺商品
                    seller_products = crawl_temu_mall(
                        mall_id, max_pages=10,
                        use_persistent_context=use_persistent_context,
                        user_data_dir=user_data_dir,
                        debug_port=debug_port
                    )
                    
                    # 保存店铺商品
                    if seller_products:
                        saved_count = save_seller_products(seller_products, seller_id, mall_id)
                        stats["seller_products_crawled"] += saved_count
                    
                    update_seller_status(seller_id, "completed")
                    
                except Exception as e:
                    logger.error(f"爬取卖家店铺失败: {e}")
                    if seller.get('seller_id'):
                        update_seller_status(seller['seller_id'], "failed")
                    continue
        
        # 更新类目状态为完成
        update_category_status(category_id, "completed", stats["total_products"], stats["saved_products"])
        
        logger.info(f"完整工作流执行完成！统计: {stats}")
        
    except Exception as e:
        logger.error(f"完整工作流执行失败: {e}")
        if stats.get("category_id"):
            update_category_status(stats["category_id"], "failed")
        raise e
    
    return stats


def get_db_conn():
    """获取数据库连接（临时函数，用于crawler_utils）"""
    import mysql.connector
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="123456789",
        database="redbubble_ai"
    )


if __name__ == "__main__":
    # 测试Redbubble爬虫
    # results = crawl_redbubble("animal", 1, "u-socks")
    # print(results)
    
    # 测试TEMU爬虫
    results = crawl_temu_mall("634418223796259", max_pages=1, use_persistent_context=True, user_data_dir="/tmp/chrome_debug", debug_port=9222)
    print(f"爬取到 {len(results)} 个商品")
    for i, item in enumerate(results[:5], 1):  # 只打印前5个
        print(f"{i}. {item['title'][:50]}... - {item['price']}")