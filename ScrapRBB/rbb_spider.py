import requests  # 导入 requests 库，用于发送 HTTP 请求
import time      # 导入 time 库，用于设置请求间隔，防止被封
import pymysql   # 导入 pymysql 库，用于操作 MySQL 数据库
import os        # 导入 os 库，用于文件和路径操作

# 1. 设置基础 URL，注意 page 参数会变化
base_url = "https://www.redbubble.com/_next/data/qr3AX2kCj6c8e3xcak9ko/en/shop.json?country=TW&iaCode=u-bags&locale=en&page={page}&sortOrder=top+selling"

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
    url TEXT,
    local_image VARCHAR(255)   -- 新增字段，保存本地图片路径
)
'''
cursor.execute(create_table_sql)
conn.commit()

# 5. 确保图片保存目录存在
image_dir = 'images'
os.makedirs(image_dir, exist_ok=True)

# 6. 设置要爬取的页数
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

                # 1. 先查询数据库，若inventoryId已存在则跳过
                cursor.execute("SELECT 1 FROM products WHERE inventoryId=%s", (inventoryId,))
                if cursor.fetchone():
                    print(f"inventoryId {inventoryId} 已存在，跳过插入。")
                    continue

                # 2. 下载图片到本地
                image_ext = os.path.splitext(preview)[-1].split('?')[0]  # 获取图片扩展名
                image_filename = f'{inventoryId}{image_ext}'
                image_path = os.path.join(image_dir, image_filename)
                try:
                    img_resp = requests.get(preview, headers=send_headers, timeout=10)
                    if img_resp.status_code == 200:
                        with open(image_path, 'wb') as f:
                            f.write(img_resp.content)
                        print(f'图片已保存：{image_path}')
                    else:
                        print(f'图片下载失败：{preview}')
                        image_path = None
                except Exception as e:
                    print(f'图片下载异常：{e}')
                    image_path = None

                # 3. 插入数据到 MySQL，记录本地图片路径
                insert_sql = """
                INSERT INTO products (inventoryId, title, preview, url, local_image) VALUES (%s, %s, %s, %s, %s)
                """
                cursor.execute(insert_sql, (inventoryId, title, preview, url, image_path))
                conn.commit()  # 提交事务
        else:
            print(f"第 {page} 页未找到商品信息字段 'results'，请检查数据结构。")
    else:
        print("请求失败，状态码：", response.status_code)
    # 每次请求间隔2秒，防止被封
    time.sleep(2)

# 7. 关闭数据库连接
cursor.close()
conn.close()
print("所有商品信息已成功存入 MySQL 数据库！") 