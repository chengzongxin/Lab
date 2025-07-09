import os
from crawler import crawl_redbubble
from download import download_image, save_results
from generate_html import generate_html
from scorer import nima_score
import webbrowser
import re

# 主程序入口
if __name__ == "__main__":
    keyword = input("请输入搜索关键词：")
    try:
        pages = int(input("请输入要爬取的页数（回车默认1）：") or 1)
    except ValueError:
        pages = 1
    limit = 20  # 可自定义
    score_threshold = 1  # 评分阈值

    # 1. 爬取商品信息
    print(f"正在爬取Redbubble商品（关键词：{keyword}，页数：{pages}）...")
    items = crawl_redbubble(keyword, pages=pages)
    print(f"共获取到{len(items)}个商品。")

    # 2. 下载图片并评分
    os.makedirs("results", exist_ok=True)
    good_items = []
    for idx, item in enumerate(items):
        img_url = item["img"]
        # 合法化商品名作为文件名
        safe_title = re.sub(r'[\\/:*?"<>|]', '_', item["title"])[:50]
        img_path = f"results/{safe_title}.jpg"
        if download_image(img_url, img_path):
            score = nima_score(img_path)
            print(f"商品{idx+1}: {item['title']}，评分：{score:.2f}")
            if score >= score_threshold:
                good_items.append({
                    "title": item["title"],
                    "img": img_url,
                    "score": score,
                    "link": item["link"],
                    "local_img": img_path
                })
        else:
            print(f"图片下载失败，跳过该商品。")

    # 3. 保存高分商品信息
    save_results(good_items, filename="products.csv")
    print(f"已保存{len(good_items)}个高分商品到 products.csv")
    print("主图已保存在 results/ 目录下。")
    generate_html("products.csv")

    # 使用 webbrowser 模块打开本地 HTML 文件
    html_path = os.path.abspath("products.html")  # 获取绝对路径
    webbrowser.open(f"file://{html_path}")

    # 提示用户网页已自动打开
    print("已自动在浏览器中打开商品展示网页（products.html）。")