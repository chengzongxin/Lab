import os
from crawler import crawl_redbubble
from download import download_image, save_results
from scorer import aesthetic_clip_score

# 主程序入口
if __name__ == "__main__":
    keyword = input("请输入搜索关键词：")
    limit = 20  # 可自定义
    score_threshold = 6.5  # 评分阈值

    # 1. 爬取商品信息
    print(f"正在爬取Redbubble商品（关键词：{keyword}）...")
    items = crawl_redbubble(keyword, limit=limit)
    print(f"共获取到{len(items)}个商品。")

    # 2. 下载图片并评分
    os.makedirs("results", exist_ok=True)
    good_items = []
    for idx, item in enumerate(items):
        img_url = item["img"]
        img_path = f"results/{keyword}_{idx}.jpg"
        if download_image(img_url, img_path):
            score = aesthetic_clip_score(img_path)
            print(f"商品{idx+1}: {item['title']}，评分：{score:.2f}")
            if score >= score_threshold:
                good_items.append({
                    "title": item["title"],
                    "img": img_url,
                    "link": item["link"]
                })
        else:
            print(f"图片下载失败，跳过该商品。")

    # 3. 保存高分商品信息
    save_results(good_items, filename="products.csv")
    print(f"已保存{len(good_items)}个高分商品到 products.csv")
    print("主图已保存在 results/ 目录下。") 