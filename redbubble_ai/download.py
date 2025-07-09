import requests
import os
import csv

# 用户指定的请求头
send_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
    "Connection": "keep-alive",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8"
}

def download_image(url, filename):
    """
    下载图片到本地，使用用户指定的header
    """
    try:
        response = requests.get(url, headers=send_headers)
        if response.status_code == 200:
            with open(filename, 'wb') as f:
                f.write(response.content)
            return True
        else:
            print(f"下载失败: {url}，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"下载异常: {url}, 错误: {e}")
        return False

def save_results(results, filename="products.csv"):
    if not results:
        print("没有结果需要保存。")
        return
    # 自动获取所有字段名
    fieldnames = list(results[0].keys())
    with open(filename, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)
    print(f"已保存结果到 {filename}")

# 测试用例（可删除）
if __name__ == "__main__":
    # 测试图片下载
    url = "https://ih1.redbubble.net/image.123456789.1234/flat,750x,075,f-pad,750x1000,f8f8f8.jpg"
    os.makedirs("results", exist_ok=True)
    download_image(url, "results/test.jpg")
    # 测试保存CSV
    test_results = [
        {"title": "test", "img": url, "link": "https://redbubble.com","score":10}
    ]
    save_results(test_results) 