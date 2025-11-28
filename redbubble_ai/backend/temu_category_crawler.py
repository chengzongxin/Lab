"""
TEMU类目爬虫模块
负责爬取TEMU类目页面的商品信息
"""

from playwright.sync_api import sync_playwright
import logging
import asyncio
import sys
import os

# 配置日志
logger = logging.getLogger(__name__)

# 修复Windows下的事件循环问题
if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())


def crawl_temu_category(category_url, max_pages=10, min_sales=1000, use_persistent_context=False, user_data_dir=None, debug_port=None):
    """
    爬取TEMU某个类目下的所有商品，筛选销量大于指定值的爆款商品
    :param category_url: 类目URL
    :param max_pages: 最大滚动次数（默认10次）
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
                # 确保连接本地调试端口时不走代理
                os.environ["NO_PROXY"] = "localhost,127.0.0.1"
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
            
            # 检测是否出现安全验证页面
            security_check_detected = False
            try:
                # 检测多种可能的安全验证标识
                security_selectors = [
                    'div.title-DH5-h:has-text("Security Verification")',
                    'div:has-text("Security Verification")',
                    'div:has-text("安全验证")',
                    'div:has-text("Please verify")',
                    'div[class*="security"]',
                    'div[class*="verification"]'
                ]
                
                for selector in security_selectors:
                    try:
                        element = page.query_selector(selector)
                        if element:
                            text = element.inner_text().strip().lower()
                            if 'security' in text or 'verification' in text or '验证' in text:
                                security_check_detected = True
                                break
                    except:
                        continue
                
                # 也检查页面标题
                if not security_check_detected:
                    page_title = page.title().lower()
                    if 'security' in page_title or 'verification' in page_title:
                        security_check_detected = True
                
                if security_check_detected:
                    logger.warning("=" * 60)
                    logger.warning("⚠️  检测到安全验证页面！")
                    logger.warning("=" * 60)
                    logger.warning("请在浏览器中完成安全验证（滑块验证、点击图片等）")
                    logger.warning("完成后，爬虫将自动继续...")
                    logger.warning("=" * 60)
                    
                    # 等待用户完成验证 - 检测页面是否跳转或验证元素消失
                    max_wait_time = 300  # 最多等待5分钟
                    wait_interval = 5  # 每5秒检查一次
                    waited_time = 0
                    
                    while waited_time < max_wait_time:
                        page.wait_for_timeout(wait_interval * 1000)
                        waited_time += wait_interval
                        
                        # 检查是否还在验证页面
                        still_in_verification = False
                        for selector in security_selectors:
                            try:
                                element = page.query_selector(selector)
                                if element and element.is_visible():
                                    still_in_verification = True
                                    break
                            except:
                                continue
                        
                        if not still_in_verification:
                            logger.info("✅ 安全验证已完成，继续爬取...")
                            break
                        
                        logger.info(f"⏳ 等待验证完成... 已等待 {waited_time}/{max_wait_time} 秒")
                    
                    if waited_time >= max_wait_time:
                        logger.error("❌ 等待安全验证超时，请手动完成验证后重新运行")
                        raise Exception("安全验证超时")
                    
                    # 验证完成后，等待页面加载
                    page.wait_for_timeout(3000)
            except Exception as e:
                if "安全验证超时" in str(e):
                    raise e
                logger.debug(f"安全验证检测出错（可能没有验证）: {e}")
            
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
            max_click_attempts = max_pages  # 使用用户指定的滚动次数
            click_attempts = 0
            
            logger.info(f"将最多点击 {max_click_attempts} 次 'See more' 按钮加载商品")
            
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
            
            # 等待商品卡片内容加载完成
            logger.info("等待商品卡片内容加载...")
            page.wait_for_timeout(2000)  # 等待2秒让内容完全加载
            
            # 获取所有商品卡片
            cards = page.query_selector_all('div.EKDT7a3v')
            logger.info(f"找到 {len(cards)} 个商品卡片")
            
            if len(cards) == 0:
                logger.warning("未找到任何商品卡片，尝试使用备用选择器...")
                # 尝试备用选择器
                cards = page.query_selector_all('div[class*="EKDT"]')
                logger.info(f"使用备用选择器找到 {len(cards)} 个商品卡片")
            
            # 解析每个商品卡片
            parsed_count = 0
            for idx, card in enumerate(cards, 1):
                logger.debug(f"正在解析卡片 {idx}/{len(cards)}")
                try:
                    # 等待卡片内容加载（如果元素是动态加载的）
                    try:
                        # 尝试等待卡片内的链接元素出现
                        card.wait_for_selector('a[href]', timeout=2000, state="attached")
                    except Exception as wait_err:
                        logger.debug(f"卡片 {idx}: 等待链接元素超时: {wait_err}")
                        pass  # 如果超时也继续，可能已经加载了
                    
                    # 尝试获取卡片的HTML内容用于调试（仅前几个）
                    if idx <= 3:
                        try:
                            card_html = card.inner_html()[:200]  # 只取前200字符
                            logger.debug(f"卡片 {idx} HTML预览: {card_html}...")
                        except:
                            pass
                    
                    # 获取商品链接 - 使用更宽松的选择器
                    link_element = None
                    # 方法1：使用完整的class组合
                    try:
                        link_element = card.query_selector('a._2Tl9qLr1._1ak1dai3')
                    except:
                        pass
                    
                    # 方法2：如果方法1失败，尝试只匹配部分class
                    if not link_element:
                        try:
                            link_element = card.query_selector('a[class*="_2Tl9qLr1"]')
                        except:
                            pass
                    
                    # 方法3：查找所有包含href的a标签
                    if not link_element:
                        try:
                            all_links = card.query_selector_all('a[href]')
                            for a in all_links:
                                try:
                                    href = a.get_attribute("href")
                                    if href and ("/g-" in href or ".html" in href or "goods" in href.lower()):
                                        link_element = a
                                        break
                                except:
                                    continue
                        except:
                            pass
                    
                    if not link_element:
                        logger.debug(f"卡片 {idx}: 未找到链接元素")
                        continue
                    
                    link = link_element.get_attribute("href")
                    if not link:
                        continue
                    
                    # 构建完整URL
                    if link.startswith("/"):
                        link = "https://www.temu.com" + link
                    elif not link.startswith("http"):
                        link = "https://www.temu.com/" + link
                    
                    # 尝试从链接中提取goods_id（如果有的话）
                    goods_id = None
                    if link and "/g-" in link:
                        try:
                            parts = link.split("/g-")
                            if len(parts) > 1:
                                goods_id = parts[1].split(".")[0].split("?")[0]
                        except:
                            pass
                    
                    # 如果没有goods_id，尝试从URL中提取其他唯一标识
                    if not goods_id and link:
                        # 尝试从URL中提取可能的商品ID
                        import re
                        match = re.search(r'goods[_-]?id[=:](\d+)', link)
                        if match:
                            goods_id = match.group(1)
                        else:
                            # 使用URL的一部分作为标识
                            goods_id = link.split('/')[-1].split('?')[0].split('.')[0][:50]
                    
                    # 获取商品标题 - 使用更宽松的选择器
                    title = None
                    try:
                        title_element = card.query_selector('span._2D9RBAXL')
                        if title_element:
                            title = title_element.inner_text().strip()
                    except:
                        pass
                    
                    if not title:
                        try:
                            h2_element = card.query_selector('h2._2BvQbnbN')
                            if h2_element:
                                title = h2_element.inner_text().strip()
                        except:
                            pass
                    
                    if not title:
                        try:
                            # 尝试查找任何包含文本的标题元素
                            title_elements = card.query_selector_all('span, h2, h3, div[class*="title"]')
                            for elem in title_elements:
                                try:
                                    text = elem.inner_text().strip()
                                    if text and len(text) > 5:  # 标题应该有一定长度
                                        title = text
                                        break
                                except:
                                    continue
                        except:
                            pass
                    
                    if not title:
                        try:
                            title_attr = link_element.get_attribute("aria-label")
                            if title_attr:
                                title = title_attr.strip()
                        except:
                            pass
                    
                    # 获取商品图片 - 使用更宽松的选择器
                    img_url = None
                    img_element = None
                    try:
                        img_element = card.query_selector('img.goods-img-external')
                    except:
                        pass
                    
                    if not img_element:
                        try:
                            img_element = card.query_selector('img[class*="goods-img"]')
                        except:
                            pass
                    
                    if not img_element:
                        try:
                            # 查找所有图片
                            all_imgs = card.query_selector_all('img')
                            for img in all_imgs:
                                try:
                                    src = img.get_attribute("src") or img.get_attribute("data-src")
                                    if src and ("kwcdn.com" in src or "temu.com" in src or "cdn" in src.lower()):
                                        img_element = img
                                        break
                                except:
                                    continue
                        except:
                            pass
                    
                    if img_element:
                        try:
                            img_url = img_element.get_attribute("src")
                            if not img_url:
                                img_url = img_element.get_attribute("data-src")
                            if not img_url:
                                img_url = img_element.get_attribute("data-lazy-src")
                        except:
                            pass
                    
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
                    
                    # 验证必要字段：至少需要标题和链接之一
                    if not title and not link:
                        logger.debug(f"卡片 {idx}: 缺少标题和链接，跳过")
                        continue
                    
                    # 如果没有标题，尝试生成默认标题
                    if not title:
                        if goods_id:
                            title = f"商品 {goods_id}"
                        else:
                            title = f"未命名商品 {idx}"
                        logger.debug(f"卡片 {idx}: 使用默认标题: {title}")
                    
                    # 使用标题作为唯一性校验（避免重复）
                    if title in seen_goods_ids:
                        logger.debug(f"卡片 {idx}: 标题重复，跳过: {title[:50]}")
                        continue
                    seen_goods_ids.add(title)
                    
                    # 只保存销量大于等于min_sales的商品
                    if sales_count >= min_sales:
                        product = {
                            "goods_id": goods_id or "",  # goods_id可能为空
                            "title": title,
                            "link": link or "",
                            "img": img_url or "",
                            "price": price or "",
                            "original_price": original_price or "",
                            "sales_count": sales_count,
                            "sales_text": sales_text or "",
                            "rating": rating,
                            "review_count": review_count
                        }
                        results.append(product)
                        parsed_count += 1
                        logger.info(f"找到爆款商品 [{parsed_count}]: {title[:50]}... 销量: {sales_count}, goods_id: {goods_id or 'N/A'}")
                    else:
                        logger.debug(f"商品销量不足: {title[:50]}... 销量: {sales_count}")
                        
                except Exception as e:
                    logger.warning(f"解析商品卡片 {idx} 失败: {e}")
                    import traceback
                    logger.debug(f"详细错误: {traceback.format_exc()}")
                    continue
            
            logger.info(f"成功解析 {parsed_count}/{len(cards)} 个商品卡片")
            
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
    max_pages: int = 10,  # 最大滚动次数
    min_sales: int = 1000,
    crawl_details: bool = False,  # 默认改为False，暂时不执行
    crawl_seller_products: bool = False,  # 默认改为False，暂时不执行
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
    :param max_pages: 最大滚动次数
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
            category_url, max_pages, min_sales, use_persistent_context, user_data_dir, debug_port
        )
        stats["total_products"] = len(products)
        
        # 保存商品到数据库
        if products:
            saved_count = save_products(products, category_id, category_url)
            stats["saved_products"] = saved_count
            update_category_status(category_id, "crawling", len(products), saved_count)
        
        # 更新类目状态为完成
        update_category_status(category_id, "completed", stats["total_products"], stats["saved_products"])
        
        logger.info(f"完整工作流执行完成！统计: {stats}")
        
    except Exception as e:
        logger.error(f"完整工作流执行失败: {e}")
        if stats.get("category_id"):
            update_category_status(stats["category_id"], "failed")
        raise e
    
    return stats


if __name__ == "__main__":
    # 测试代码
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 可以在这里添加测试代码
    pass

