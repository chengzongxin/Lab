import requests  # 导入 requests 库，用于发送 HTTP 请求
import json      # 导入 json 库，用于处理 JSON 数据
import time      # 导入 time 库，用于添加请求间隔

# 1. 设置目标 URL
url = "https://www.redbubble.com/_next/data/AQyVrFfu7irWOEAP1IvK4/en/shop.json?country=TW&iaCode=u-bags&locale=en&page=2&sortOrder=top+selling"

# 2. 设置请求头（headers），模拟浏览器访问
send_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
    "Connection": "keep-alive",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8"
}

# 3. 发送 GET 请求
response = requests.get(url, headers=send_headers)

print("状态码：", response.status_code)
if response.status_code == 200:
    print("请求成功！")
    data = response.json()  # 解析返回的 JSON 数据

    # 5. 保存数据到本地文件（可选）
    with open("list.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("数据已保存到 list.json 文件。")

    # 读取并打印 pageProps 的所有键，帮助你定位数据
    print("pageProps 的所有键：", data.get('pageProps', {}).keys())

    # 假设你发现商品列表在 data['pageProps']['results'] 里
    try:
        # 你需要根据实际结构调整这里的字段
        items = data['pageProps']['results']  # 或其他实际字段
        for item in items:
            title = item['inventoryItem']['work']['title']
            preview = item['inventoryItem']['previewSet']['previews'][0]['url']
            url = item['inventoryItem']['productPageUrl']
            print("商品信息：", title, preview, url)
    except Exception as e:
        print("解析商品信息时出错：", e)
else:
    print("请求失败，状态码：", response.status_code)
    print("返回内容：", response.text) 