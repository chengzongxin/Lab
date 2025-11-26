"""
TEMU卖家店铺商品爬取功能

功能：爬取指定TEMU卖家店铺的所有商品，提取卖家信息（名称、头像、ID）
"""

import os
import re
import logging
import sys
import asyncio
from playwright.sync_api import sync_playwright

logger = logging.getLogger(__name__)

def crawl_temu_seller_products(mall_id, max_pages=10, min_sales=0, use_persistent_context=False, user_data_dir=None, debug_port=None):
    """
    爬取TEMU卖家店铺的商品
    
    :param mall_id: 卖家店铺ID（从URL的mall_id参数获取，如：634418218462973）
    :param max_pages: 最多滚动加载次数（默认10次）
    :param min_sales: 最小销量过滤（默认0，即不过滤）
    :param use_persistent_context: 是否使用持久化上下文（保持登录）
    :param user_data_dir: 用户数据目录
    :param debug_port: 调试端口
    :return: 商品列表，包含卖家信息
    """
    results = []
    browser = None
    context = None
    seller_info = {}
    
    try:
        # 在Windows上强制使用ProactorEventLoopPolicy，以支持子进程（Playwright需要）
        if sys.platform == 'win32':
            asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

        with sync_playwright() as p:
            # 启动浏览器（与类目爬取逻辑一致）
            if debug_port:
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
            
            if not browser and use_persistent_context:
                if not user_data_dir:
                    import tempfile
                    user_data_dir = tempfile.mkdtemp(prefix="temu_seller_")
                
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
            
            # 构建卖家店铺URL
            seller_url = f"https://www.temu.com/mall.html?mall_id={mall_id}"
            logger.info(f"正在访问TEMU卖家店铺: {seller_url}")
            
            try:
                page.goto(seller_url, wait_until="load", timeout=60000)
            except Exception as e:
                logger.warning(f"页面加载超时，尝试继续: {e}")
            
            # ===== 检测安全验证页面 =====
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
            
            # 等待卖家信息区域加载
            try:
                page.wait_for_selector('div._9oW_90Kh, h1.PX7EseE2', timeout=10000)
                logger.info("卖家信息区域已加载")
            except Exception as e:
                logger.warning(f"等待卖家信息超时: {e}")
            
            # ===== 提取卖家信息 =====
            try:
                # 提取卖家名称
                seller_name_elem = page.query_selector('h1.PX7EseE2._2DshZJ_y, h1.PX7EseE2')
                if seller_name_elem:
                    seller_info['seller_name'] = seller_name_elem.inner_text().strip()
                    logger.info(f"卖家名称: {seller_info['seller_name']}")
                
                # 提取卖家头像
                seller_avatar_elem = page.query_selector('img[alt*="Home"], div._2kL1JO3V img, div._22I9hNUw img')
                if seller_avatar_elem:
                    seller_info['seller_avatar'] = seller_avatar_elem.get_attribute('src')
                    logger.info(f"卖家头像: {seller_info['seller_avatar'][:80]}...")
                
                # mall_id 已知
                seller_info['mall_id'] = mall_id
                seller_info['seller_url'] = seller_url
                
                logger.info(f"✓ 成功提取卖家信息: {seller_info.get('seller_name', 'Unknown')}")
            except Exception as e:
                logger.error(f"提取卖家信息失败: {e}")
            
            # ===== 爬取商品 =====
            # 等待商品网格加载
            try:
                page.wait_for_selector('div.EKDT7a3v, div[class*="EKDT"]', timeout=15000)
                logger.info("商品列表已加载")
            except Exception as e:
                logger.warning(f"等待商品列表超时: {e}")
                # 尝试等待其他可能的商品容器
                try:
                    page.wait_for_selector('div[class*="EKDT"]', timeout=10000)
                    logger.info("找到商品容器（使用备用选择器）")
                except:
                    logger.error("无法找到商品元素，可能页面结构已变化或需要登录")
                    raise Exception("无法找到商品元素，请检查页面是否需要登录")
            
            seen_links = set()
            
            # ===== 筛选：按销量排序（Top sales） =====
            logger.info("开始设置筛选条件：按销量排序（Top sales）...")
            try:
                # 等待筛选下拉菜单加载
                try:
                    page.wait_for_selector('div.IR0nIPsF, div._2-JRVsSd', timeout=10000)
                    logger.info("筛选下拉菜单已加载")
                except Exception as e:
                    logger.warning(f"等待筛选下拉菜单超时: {e}，尝试继续...")
                
                # 查找并点击筛选下拉按钮
                sort_button = None
                # 方法1：通过class查找下拉按钮
                sort_button = page.query_selector('div._2-JRVsSd[role="button"]')
                # 方法2：通过包含"Sort by"文本的父容器查找
                if not sort_button:
                    sort_container = page.query_selector('div.IR0nIPsF')
                    if sort_container:
                        sort_button = sort_container.query_selector('div._2-JRVsSd[role="button"]')
                # 方法3：通过文本查找包含"Top sales"的按钮
                if not sort_button:
                    all_buttons = page.query_selector_all('div[role="button"]')
                    for btn in all_buttons:
                        try:
                            text = btn.inner_text().strip()
                            if "Top sales" in text or "Sort by" in text:
                                sort_button = btn
                                break
                        except:
                            continue
                
                if sort_button:
                    # 检查当前是否已经是"Top sales"排序
                    current_text = sort_button.inner_text().strip()
                    if "Top sales" in current_text:
                        logger.info("当前已经是按销量排序（Top sales），跳过筛选操作")
                    else:
                        logger.info("点击筛选下拉按钮...")
                        # 滚动到按钮位置
                        sort_button.scroll_into_view_if_needed()
                        page.wait_for_timeout(500)
                        # 点击打开下拉菜单
                        sort_button.click()
                        page.wait_for_timeout(1000)  # 等待下拉菜单展开
                        
                        # 查找并点击"Top sales"选项
                        top_sales_option = None
                        # 方法1：通过data-item属性查找
                        top_sales_option = page.query_selector('li[data-item="Top sales"]')
                        # 方法2：通过data-filter属性查找（data-filter="1:1"）
                        if not top_sales_option:
                            top_sales_option = page.query_selector('li[data-filter="1:1"]')
                        # 方法3：通过文本内容查找
                        if not top_sales_option:
                            all_list_items = page.query_selector_all('li._1asRZIQH')
                            for li in all_list_items:
                                try:
                                    text = li.inner_text().strip()
                                    if text == "Top sales":
                                        top_sales_option = li
                                        break
                                except:
                                    continue
                        
                        if top_sales_option:
                            logger.info("找到'Top sales'选项，正在点击...")
                            # 滚动到选项位置
                            top_sales_option.scroll_into_view_if_needed()
                            page.wait_for_timeout(300)
                            # 点击选项
                            top_sales_option.click()
                            logger.info("✓ 已选择按销量排序（Top sales）")
                            # 等待页面重新加载/排序完成
                            page.wait_for_timeout(3000)  # 等待3秒让页面重新排序
                            logger.info("等待页面排序完成...")
                        else:
                            logger.warning("未找到'Top sales'选项，可能页面结构已变化")
                else:
                    logger.warning("未找到筛选下拉按钮，可能页面结构已变化，继续使用默认排序")
            except Exception as e:
                logger.warning(f"设置筛选条件时出错: {e}，继续使用默认排序")
                import traceback
                logger.debug(traceback.format_exc())
            
            # ===== 点击"See more"按钮加载更多商品 =====
            logger.info(f"开始点击'See more'按钮加载商品（最多 {max_pages} 次）...")
            click_attempts = 0
            
            while click_attempts < max_pages:
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
            
            # 解析每个商品
            for card in cards:
                try:
                    # 提取链接
                    link_element = card.query_selector('a._2Tl9qLr1._1ak1dai3, a[class*="_2Tl9qLr1"], a[href*="/g-"]')
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
                    
                    # 去重
                    if link in seen_links:
                        continue
                    seen_links.add(link)
                    
                    # 提取商品ID（从link中提取）
                    goods_id = None
                    # 方法1：尝试从URL中提取goods_id（支持多种格式）
                    # 格式1: /g-601100311994848.html
                    # 格式2: ---g-601100311994848.html
                    if link:
                        # 使用正则表达式匹配 /g- 或 -g- 后面的数字
                        match = re.search(r'[-/]g-(\d+)', link)
                        if match:
                            goods_id = match.group(1)
                    
                    # 方法2：如果没有goods_id，尝试从URL参数中提取
                    if not goods_id and link:
                        match = re.search(r'goods[_-]?id[=:](\d+)', link)
                        if match:
                            goods_id = match.group(1)
                    
                    # 方法3：如果还是没有，尝试提取URL中任何连续的纯数字（至少10位）
                    if not goods_id and link:
                        match = re.search(r'(\d{10,})', link)
                        if match:
                            goods_id = match.group(1)
                    
                    # 提取标题
                    title = None
                    # 方法1：从标题span获取
                    title_elem = card.query_selector('span._2D9RBAXL')
                    if title_elem:
                        title = title_elem.inner_text().strip()
                    
                    # 方法2：如果标题元素不存在，尝试从h3标签获取
                    if not title:
                        h3_element = card.query_selector('h3._2BvQbnbN, h2._2BvQbnbN')
                        if h3_element:
                            title = h3_element.inner_text().strip()
                    
                    # 方法3：从链接的aria-label获取
                    if not title and link_element:
                        title_attr = link_element.get_attribute("aria-label")
                        if title_attr:
                            title = title_attr.strip()
                    
                    # 提取图片
                    img = None
                    # 方法1：查找goods-img-external类
                    img_elem = card.query_selector('img.goods-img-external')
                    # 方法2：查找_3frBeExI类
                    if not img_elem:
                        img_elem = card.query_selector('img._3frBeExI')
                    # 方法3：查找任何包含src的img标签
                    if not img_elem:
                        img_elem = card.query_selector('img[src]')
                    
                    if img_elem:
                        img = img_elem.get_attribute("src")
                        # 如果没有src，尝试从data-src获取（懒加载）
                        if not img:
                            img = img_elem.get_attribute("data-src")
                    
                    # 提取价格
                    price = None
                    # 查找价格容器中的_2XgTiMJi类
                    price_elem = card.query_selector('div[data-type="price"] span._2XgTiMJi')
                    if not price_elem:
                        price_elem = card.query_selector('span._2XgTiMJi')
                    if price_elem:
                        price = price_elem.inner_text().strip()
                    
                    # 提取销量（关键信息）
                    sales_count = 0
                    sales_text = None
                    # 尝试多种选择器查找销量元素
                    sales_elem = card.query_selector('span._1GKMA1Nk')
                    if not sales_elem:
                        sales_elem = card.query_selector('span[class*="_1GKMA1Nk"]')
                    if not sales_elem:
                        # 查找包含 "sold" 文本的元素
                        all_spans = card.query_selector_all('span')
                        for span in all_spans:
                            try:
                                text = span.inner_text().strip().lower()
                                if 'sold' in text and any(c.isdigit() for c in text):
                                    sales_elem = span
                                    break
                            except:
                                continue
                    
                    if sales_elem:
                        # 获取销量文本，优先从 _2XgTiMJi 类获取（包含完整文本）
                        sales_text_element = sales_elem.query_selector('span._2XgTiMJi')
                        if sales_text_element:
                            sales_text = sales_text_element.inner_text().strip()
                        else:
                            sales_text = sales_elem.inner_text().strip()
                        
                        # 解析销量文本，支持格式如 "102sold", "1.2K+sold" -> 1200, "100K+" -> 100000
                        if sales_text:
                            sales_text_lower = sales_text.lower()
                            try:
                                # 移除 "sold" 文本
                                num_text = sales_text_lower.replace("sold", "").strip()
                                
                                # 如果清理后的文本为空或只有标点符号，跳过
                                if not num_text or not any(c.isdigit() for c in num_text):
                                    sales_count = 0
                                # 处理 K+ 格式（如 "1.2K+" -> 1200）
                                elif "k+" in num_text or (num_text.endswith("k") and "+" not in num_text):
                                    # 提取数字部分
                                    num_str = num_text.replace("k+", "").replace("k", "").replace("+", "").strip()
                                    if num_str and num_str.replace(".", "").isdigit():
                                        sales_count = int(float(num_str) * 1000)
                                # 处理 M+ 格式（如 "1.5M+" -> 1500000）
                                elif "m+" in num_text or (num_text.endswith("m") and "+" not in num_text):
                                    num_str = num_text.replace("m+", "").replace("m", "").replace("+", "").strip()
                                    if num_str and num_str.replace(".", "").isdigit():
                                        sales_count = int(float(num_str) * 1000000)
                                # 如果是纯数字，直接转换
                                elif num_text.replace(".", "").replace("+", "").replace(",", "").isdigit():
                                    sales_count = int(float(num_text.replace("+", "").replace(",", "")))
                                
                                logger.debug(f"解析销量: '{sales_text}' -> {sales_count}")
                            except Exception as e:
                                logger.warning(f"解析销量失败: '{sales_text}', 错误: {e}")
                                sales_count = 0
                    
                    # 销量过滤
                    if sales_count < min_sales:
                        continue
                    
                    # 确保goods_id有效且不超过50个字符（数据库限制）
                    if not goods_id:
                        # 尝试从URL最后部分提取短ID
                        url_last_part = link.split('/')[-1]
                        # 如果URL包含 .html，移除它
                        url_last_part = url_last_part.replace('.html', '')
                        # 如果仍然太长，使用link的hash值
                        if len(url_last_part) > 50:
                            import hashlib
                            goods_id = hashlib.md5(link.encode('utf-8')).hexdigest()[:50]
                            logger.warning(f"goods_id过长，使用hash: {url_last_part[:30]}... -> {goods_id}")
                        else:
                            goods_id = url_last_part
                    
                    # 再次检查长度（双重保险）
                    if goods_id and len(goods_id) > 50:
                        goods_id = goods_id[:50]
                        logger.warning(f"goods_id截断至50字符: {goods_id}")
                    
                    # 组装商品数据（包含卖家信息）
                    product = {
                        'goods_id': goods_id,
                        'title': title,
                        'img': img,
                        'link': link,
                        'price': price,
                        'sales_count': sales_count,
                        'sales_text': sales_text,
                        **seller_info  # 合并卖家信息
                    }
                    
                    results.append(product)
                    logger.info(f"✓ 商品: {title[:50]}... 销量:{sales_count} 价格:{price}")
                    
                except Exception as e:
                    logger.warning(f"解析商品卡片失败: {e}")
                    continue
            
            logger.info(f"爬取完成！共获取 {len(results)} 个商品（销量 >= {min_sales}）")
            
    except Exception as e:
        logger.error(f"爬取卖家店铺失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
    finally:
        if context and not use_persistent_context:
            try:
                context.close()
            except:
                pass
        if browser:
            try:
                browser.close()
            except:
                pass
    
    return results
