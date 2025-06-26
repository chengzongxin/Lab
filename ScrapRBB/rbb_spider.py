import requests  # 导入 requests 库，用于发送 HTTP 请求
import time      # 导入 time 库，用于设置请求间隔，防止被封
import pymysql   # 导入 pymysql 库，用于操作 MySQL 数据库

# 1. 设置基础 URL，注意 page 参数会变化
base_url = "https://www.redbubble.com/_next/data/AQyVrFfu7irWOEAP1IvK4/en/shop.json?country=TW&iaCode=u-bags&locale=en&page={page}&sortOrder=top+selling"

# 2. 设置请求头（headers），模拟浏览器访问
send_headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
    "Connection": "keep-alive",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "zh-CN,zh;q=0.8"
}

# 3. 连接到本地 MySQL 数据库（请根据你的实际用户名和密码修改）
conn = pymysql.connect(
    host='localhost',      # 数据库主机地址
    user='root',           # 数据库用户名（请替换为你的用户名）
    password='123456789',  # 数据库密码（请替换为你的密码）
    database='scrap_rbb',  # 数据库名（请确保已创建）
    charset='utf8mb4'      # 字符集
)
cursor = conn.cursor()

# 4. 创建商品信息表（只需运行一次）
# id为自增主键，inventoryId为商品唯一ID
create_table_sql = '''
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,         -- 自增主键
    inventoryId VARCHAR(64) UNIQUE,            -- 商品唯一ID
    title VARCHAR(255),
    preview TEXT,
    url TEXT
)
'''
cursor.execute(create_table_sql)
conn.commit()

# 5. 设置要爬取的页数
start_page = 1  # 起始页
end_page = 5    # 结束页（包含），你可以根据需要修改

for page in range(start_page, end_page + 1):
    url = base_url.format(page=page)  # 构造当前页的 URL
    print(f"正在请求第 {page} 页: {url}")
    response = requests.get(url, headers=send_headers)
    print("状态码：", response.status_code)
    if response.status_code == 200:
        data = response.json()
        # 假设商品信息在 data['pageProps']['results'] 字段
        results = data.get('pageProps', {}).get('results', [])
        if results:
            print(f"第 {page} 页商品信息：")
            for item in results:
                # 提取商品信息
                inventoryId = item['inventoryItem']['id']
                title = item['inventoryItem']['work']['title']
                preview = item['inventoryItem']['previewSet']['previews'][0]['url']
                url = item['inventoryItem']['productPageUrl']
                print(title, preview, url)
                # 插入数据到 MySQL，使用 INSERT IGNORE 防止唯一约束重复报错
                insert_sql = """
                INSERT IGNORE INTO products (inventoryId, title, preview, url) VALUES (%s, %s, %s, %s)
                """
                cursor.execute(insert_sql, (inventoryId, title, preview, url))
                conn.commit()  # 提交事务
        else:
            print(f"第 {page} 页未找到商品信息字段 'results'，请检查数据结构。")
    else:
        print("请求失败，状态码：", response.status_code)
    # 每次请求间隔2秒，防止被封
    time.sleep(2)

# 6. 关闭数据库连接
cursor.close()
conn.close()
print("所有商品信息已成功存入 MySQL 数据库！") 