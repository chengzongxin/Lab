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
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body { background: #f5f6fa; margin: 0; font-family: 'Segoe UI', Arial, sans-serif; }
            .header { background: #fff; box-shadow: 0 2px 8px #0001; padding: 24px 0 16px 0; text-align: center; margin-bottom: 24px; }
            .header h2 { margin: 0; font-size: 2.2rem; color: #222; letter-spacing: 2px; }
            .container {
                display: grid;
                grid-template-columns: repeat(6, 1fr);
                gap: 18px;
                max-width: 100vw;
                margin: 0 auto;
                padding: 0 2px 24px 2px;
            }
            @media (max-width: 1400px) {
                .container { grid-template-columns: repeat(5, 1fr); }
            }
            @media (max-width: 1200px) {
                .container { grid-template-columns: repeat(4, 1fr); }
            }
            @media (max-width: 900px) {
                .container { grid-template-columns: repeat(3, 1fr); }
            }
            @media (max-width: 700px) {
                .container { grid-template-columns: repeat(2, 1fr); }
            }
            @media (max-width: 480px) {
                .container { grid-template-columns: 1fr; }
            }
            .card {
                background: #fff;
                border-radius: 12px;
                box-shadow: 0 2px 12px #0002;
                overflow: hidden;
                display: flex;
                flex-direction: column;
                transition: box-shadow 0.2s, transform 0.2s;
                position: relative;
            }
            .card:hover {
                box-shadow: 0 8px 24px #0003;
                transform: translateY(-4px) scale(1.02);
            }
            .card-img-box {
                width: 100%;
                aspect-ratio: 1/1;
                background: #f0f0f0;
                display: flex;
                align-items: center;
                justify-content: center;
            }
            .card-img {
                max-width: 100%;
                max-height: 100%;
                object-fit: cover;
                border-radius: 0;
                transition: transform 0.2s;
            }
            .card:hover .card-img {
                transform: scale(1.05);
            }
            .card-content {
                flex: 1;
                display: flex;
                flex-direction: column;
                padding: 12px 10px 10px 10px;
            }
            .title {
                font-size: 1.02rem;
                font-weight: 500;
                color: #222;
                margin-bottom: 8px;
                min-height: 36px;
                line-height: 1.3;
                overflow: hidden;
                text-overflow: ellipsis;
                display: -webkit-box;
                -webkit-line-clamp: 2;
                -webkit-box-orient: vertical;
            }
            .score {
                font-size: 1rem;
                color: #e67e22;
                font-weight: bold;
                margin-bottom: 6px;
            }
            .link {
                margin-top: auto;
                display: inline-block;
                background: #3498db;
                color: #fff;
                font-size: 0.95rem;
                padding: 6px 14px;
                border-radius: 6px;
                text-decoration: none;
                font-weight: 500;
                box-shadow: 0 2px 8px #3498db33;
                transition: background 0.2s;
            }
            .link:hover {
                background: #217dbb;
            }
        </style>
    </head>
    <body>
        <div class="header">
            <h2>Redbubble 商品美学评分展示</h2>
        </div>
        <div class="container">
    '''

    for item in items:
        img_src = item.get('local_img') or item['img']
        html += f'''
        <div class="card">
            <div class="card-img-box">
                <a href="{item['link']}" target="_blank">
                    <img class="card-img" src="{img_src}" alt="{item['title']}">
                </a>
            </div>
            <div class="card-content">
                <div class="title">{item['title']}</div>
                <div class="score">美学评分：{item.get('score', '无')}</div>
                <a class="link" href="{item['link']}" target="_blank">查看商品</a>
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