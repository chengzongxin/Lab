import os
from crawler import crawl_redbubble
from download import download_image, save_results, save_to_mysql
from generate_html import generate_html
from scorer import nima_score
import webbrowser
import re
import mysql.connector
import json

def update_status(status: dict):
    """兼容旧版本的状态更新（写入文件）"""
    with open("crawler_status.json", "w", encoding="utf-8") as f:
        json.dump(status, f, ensure_ascii=False)

def update_task_status(task_id: str, status: str, current: int = 0, total: int = 0, 
                      step: str = "", title: str = "", error_message: str = "", current_score: float = None):
    """更新数据库中的任务状态"""
    try:
        conn = mysql.connector.connect(
            host="localhost",
            port=3306,
            user="root",
            password="123456789",
            database="redbubble_ai"
        )
        cursor = conn.cursor()
        
        if status == 'completed':
            cursor.execute("""
                UPDATE crawl_tasks 
                SET status = %s, progress_current = %s, progress_total = %s, 
                    current_step = %s, current_title = %s, completed_at = NOW(), current_score = %s
                WHERE id = %s
            """, (status, current, total, step, title, current_score, task_id))
        else:
            cursor.execute("""
                UPDATE crawl_tasks 
                SET status = %s, progress_current = %s, progress_total = %s, 
                    current_step = %s, current_title = %s, error_message = %s, current_score = %s
                WHERE id = %s
            """, (status, current, total, step, title, error_message, current_score, task_id))
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # 同时更新文件状态（兼容旧版本）
        update_status({
            "step": step,
            "keyword": "",  # 从数据库获取
            "pages": 0,     # 从数据库获取
            "current": current,
            "total": total,
            "title": title
        })
        
    except Exception as e:
        print(f"更新任务状态失败: {e}")

def safe_filename(title: str, idx: int) -> str:
    # 只保留中英文、数字、下划线，空格转下划线，截断过长标题
    name = re.sub(r'[\\/:*?"<>|]', '', title)
    name = name.replace(' ', '_')
    name = name[:40]  # 最多40字符
    return f"{name}_{idx + 1}.jpg"

def main():
    # 获取任务ID（如果提供）
    task_id = None
    try:
        task_id = input("请输入任务ID（可选）: ").strip()
        if not task_id:
            task_id = None
    except:
        task_id = None
    
    # 获取搜索关键词
    keyword = input("请输入搜索关键词: ").strip()
    # 获取页数
    try:
        pages = int(input("请输入要爬取的页数（1-10）: "))
        if pages < 1 or pages > 10:
            print("页数必须在1-10之间")
            return
    except ValueError:
        print("请输入有效的数字")
        return
    # 获取类目
    category = input("请输入类目代码（如u-clothing/u-bags/u-socks等，默认u-clothing）: ").strip() or "u-clothing"
    print(f"\n开始爬取 Redbubble，类目: {category}，关键词: {keyword}，页数: {pages}")
    # 更新任务状态
    if task_id:
        update_task_status(task_id, "running", 0, 0, "开始爬取", keyword)
    # 爬取商品
    print("正在爬取商品信息...")
    items = crawl_redbubble(keyword, pages, category)
    if not items:
        print("未找到任何商品")
        if task_id:
            update_task_status(task_id, "failed", 0, 0, "未找到商品", "", "未找到任何商品")
        return
    print(f"找到 {len(items)} 个商品")
    if task_id:
        update_task_status(task_id, "running", 0, len(items), "下载图片", "")
    os.makedirs("results", exist_ok=True)
    products = []
    for idx, item in enumerate(items):
        try:
            print(f"正在处理第 {idx + 1}/{len(items)} 个商品: {item['title'][:50]}...")
            img_filename = safe_filename(item['title'], idx)
            img_path = os.path.join("results", img_filename)
            success = download_image(item['img'], img_path)
            print(f"图片下载成功: {success}")
            score = 0.0
            if success and os.path.exists(img_path):
                try:
                    score = nima_score(img_path)
                except Exception as e:
                    print(f"评分失败: {e}")
                    score = 0.0
            else:
                print(f"图片未下载成功: {img_path}")
                score = 0.0
            if task_id:
                update_task_status(task_id, "running", idx, len(items), "下载图片", item['title'], "", score)
            # 确保category字段写入product
            product = {
                'title': item['title'],
                'img': item['img'],
                'score': score,
                'link': item['link'],
                'local_img': img_path,
                'category': category
            }
            print(f"product入库前: {product}")
            products.append(product)
            print(f"评分: {score:.2f}")
        except Exception as e:
            print(f"处理商品时出错: {e}")
            continue
    if not products:
        print("没有成功处理任何商品")
        if task_id:
            update_task_status(task_id, "failed", 0, len(items), "处理失败", "", "没有成功处理任何商品")
        return
    print(f"\n成功处理 {len(products)} 个商品")
    print("正在保存到数据库...")
    if task_id:
        update_task_status(task_id, "running", len(products), len(products), "保存数据", "")
    try:
        save_to_mysql(products)
        print("数据已保存到数据库")
        # save_results(products, "products.csv")
        # print("数据已保存到 products.csv")
        # generate_html(products, "products.html")
        # print("已生成 products.html")
        if task_id:
            update_task_status(task_id, "completed", len(products), len(products), "爬取完成", "")
        print(f"\n爬取完成！共处理 {len(products)} 个商品")
        print("可以在前端页面查看结果")
    except Exception as e:
        print(f"保存数据时出错: {e}")
        if task_id:
            update_task_status(task_id, "failed", len(products), len(products), "保存失败", "", str(e))

if __name__ == "__main__":
    main()