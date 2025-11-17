cd /Users/chengzongxin/Desktop/Lab/redbubble_ai/backend && source .venv/bin/activate && python3 -c "
import mysql.connector

# 连接数据库
conn = mysql.connector.connect(
    host='localhost',
    port=3306,
    user='root',
    password='123456789',
    database='redbubble_ai'
)
cursor = conn.cursor()

# 添加缺失的字段
try:
    # 为 temu_products 表添加 link_hash 字段
    cursor.execute('ALTER TABLE temu_products ADD COLUMN link_hash VARCHAR(64) AFTER link')
    print('✅ 已添加 temu_products.link_hash 字段')
except Exception as e:
    if '1060' in str(e):  # Duplicate column name
        print('⚠️  temu_products.link_hash 字段已存在')
    else:
        print(f'❌ 添加 temu_products.link_hash 失败: {e}')

try:
    # 添加索引
    cursor.execute('ALTER TABLE temu_products ADD INDEX idx_link_hash (link_hash)')
    print('✅ 已添加 temu_products.link_hash 索引')
except Exception as e:
    if '1061' in str(e):  # Duplicate key name
        print('⚠️  temu_products.link_hash 索引已存在')
    else:
        print(f'❌ 添加索引失败: {e}')

try:
    # 为 temu_seller_products 表添加 link_hash 字段
    cursor.execute('ALTER TABLE temu_seller_products ADD COLUMN link_hash VARCHAR(64) AFTER link')
    print('✅ 已添加 temu_seller_products.link_hash 字段')
except Exception as e:
    if '1060' in str(e):
        print('⚠️  temu_seller_products.link_hash 字段已存在')
    else:
        print(f'❌ 添加 temu_seller_products.link_hash 失败: {e}')

try:
    # 添加索引
    cursor.execute('ALTER TABLE temu_seller_products ADD INDEX idx_link_hash (link_hash)')
    print('✅ 已添加 temu_seller_products.link_hash 索引')
except Exception as e:
    if '1061' in str(e):
        print('⚠️  temu_seller_products.link_hash 索引已存在')
    else:
        print(f'❌ 添加索引失败: {e}')

try:
    # 为 temu_product_details 表添加 seller_url_hash 字段
    cursor.execute('ALTER TABLE temu_product_details ADD COLUMN seller_url_hash VARCHAR(64) AFTER seller_url')
    print('✅ 已添加 temu_product_details.seller_url_hash 字段')
except Exception as e:
    if '1060' in str(e):
        print('⚠️  temu_product_details.seller_url_hash 字段已存在')
    else:
        print(f'❌ 添加 temu_product_details.seller_url_hash 失败: {e}')

try:
    # 添加索引
    cursor.execute('ALTER TABLE temu_product_details ADD INDEX idx_seller_url_hash (seller_url_hash)')
    print('✅ 已添加 temu_product_details.seller_url_hash 索引')
except Exception as e:
    if '1061' in str(e):
        print('⚠️  temu_product_details.seller_url_hash 索引已存在')
    else:
        print(f'❌ 添加索引失败: {e}')

try:
    # 为 temu_sellers 表添加 seller_url_hash 字段
    cursor.execute('ALTER TABLE temu_sellers ADD COLUMN seller_url_hash VARCHAR(64) AFTER seller_url')
    print('✅ 已添加 temu_sellers.seller_url_hash 字段')
except Exception as e:
    if '1060' in str(e):
        print('⚠️  temu_sellers.seller_url_hash 字段已存在')
    else:
        print(f'❌ 添加 temu_sellers.seller_url_hash 失败: {e}')

try:
    # 添加索引
    cursor.execute('ALTER TABLE temu_sellers ADD INDEX idx_seller_url_hash (seller_url_hash)')
    print('✅ 已添加 temu_sellers.seller_url_hash 索引')
except Exception as e:
    if '1061' in str(e):
        print('⚠️  temu_sellers.seller_url_hash 索引已存在')
    else:
        print(f'❌ 添加索引失败: {e}')

conn.commit()
cursor.close()
conn.close()

print('\\n✅ 数据库表结构更新完成！')
"