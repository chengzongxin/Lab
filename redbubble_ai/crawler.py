from playwright.sync_api import sync_playwright

# 爬虫函数：根据关键词抓取Redbubble商品信息
# 参数：keyword - 搜索关键词，limit - 最多抓取商品数量
# 返回：商品信息列表，每个元素是字典，包含title, img, link

def crawl_redbubble(keyword, pages=1):
    """
    爬取Redbubble多页商品信息
    :param keyword: 搜索关键词
    :param pages: 要爬取的页数
    :return: 商品信息列表
    """
    results = []
    with sync_playwright() as p:
        browser = p.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--window-size=1920,1080"
            ]
        )
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
            locale="zh-CN"
        )
        page = context.new_page()
        for page_num in range(1, pages + 1):
            url = f"https://www.redbubble.com/shop/?iaCode=u-clothing&query={keyword}&ref=search_box&page={page_num}"
            page.goto(url)
            page.wait_for_selector('div[data-testid="search-result-card"]', timeout=30000)
            cards = page.query_selector_all('div[data-testid="search-result-card"]')
            for card in cards:
                a_tag = card.query_selector('a[data-testid="related-work-card"]')
                img_tag = card.query_selector('img[alt^="Item preview"]')
                if a_tag and img_tag:
                    link = a_tag.get_attribute("href")
                    if link and not link.startswith("http"):
                        link = "https://www.redbubble.com" + link
                    img_url = img_tag.get_attribute("src")
                    title = img_tag.get_attribute("alt")
                    # 去除前缀
                    if title and title.startswith("Item preview, "):
                        title = title.replace("Item preview, ", "", 1)
                    results.append({
                        "title": title,
                        "img": img_url,
                        "link": link
                    })
        browser.close()
    return results

# 测试用例（可删除）
if __name__ == "__main__":
    keyword = "cat"
    items = crawl_redbubble(keyword, pages=5)
    for item in items:
        print(item) 