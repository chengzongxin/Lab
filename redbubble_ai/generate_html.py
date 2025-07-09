import csv

def generate_html(csv_file, output_file="products.html"):
    items = []
    with open(csv_file, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            items.append(row)

    html = '''
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <title>商品美学评分展示</title>
        <style>
            body { font-family: Arial, sans-serif; background: #f8f8f8; }
            .container { display: flex; flex-wrap: wrap; gap: 20px; padding: 20px;}
            .card {
                background: #fff; border-radius: 8px; box-shadow: 0 2px 8px #0001;
                width: 320px; padding: 12px; text-align: left; transition: box-shadow 0.2s;
                display: flex; flex-direction: row; align-items: center; gap: 12px;
            }
            .card:hover { box-shadow: 0 4px 16px #0002; }
            .card-img { width: 120px; height: 120px; object-fit: cover; border-radius: 6px; }
            .card-content { flex: 1; display: flex; flex-direction: column; justify-content: center; }
            .title { font-size: 16px; margin: 0 0 8px 0; }
            .score { font-size: 18px; color: #e67e22; font-weight: bold; margin-bottom: 8px; }
            .link { font-size: 13px; color: #3498db; text-decoration: none; }
        </style>
    </head>
    <body>
        <h2 style="text-align:center;">Redbubble 商品美学评分展示</h2>
        <div class="container">
    '''

    for item in items:
        img_src = item.get('local_img') or item['img']
        html += f'''
        <div class="card">
            <a href="{item['link']}" target="_blank">
                <img class="card-img" src="{img_src}" alt="{item['title']}">
            </a>
            <div class="card-content">
                <div class="title">{item['title']}</div>
                <div class="score">评分：{item.get('score', '无')}</div>
                <a class="link" href="{item['link']}" target="_blank">商品链接</a>
            </div>
        </div>
        '''

    html += '''
        </div>
    </body>
    </html>
    '''

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    print(f"已生成网页：{output_file}")

if __name__ == "__main__":
    generate_html("products.csv") 