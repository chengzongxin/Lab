# Redbubble AI 商品美学筛选器

## 项目简介
本项目可以自动在 Redbubble 网站上批量搜索商品，下载商品主图，并用 AI（NIMA 模型）对图片进行美学评分，筛选出“好看”的商品，并生成可视化网页方便浏览和筛选。

## 主要功能
- 自动化爬取 Redbubble 商品信息（主图、标题、链接）
- 使用 NIMA 美学评分模型对商品图片进行 1~10 分美学打分
- 支持多页批量爬取
- 下载高分商品主图并保存信息到 CSV
- 自动生成网页（products.html），可直观浏览图片、名称、评分和商品链接

## 技术原理
- **爬虫**：使用 Playwright 自动化浏览器抓取商品信息
- **图片下载**：requests 下载主图
- **美学评分**：Keras 加载 NIMA（MobileNet）模型和权重，对图片打分
- **网页生成**：Python 脚本自动生成 HTML 展示页面

## 依赖环境
- Python 3.8 及以上
- 依赖包见 requirements.txt
- 需准备 NIMA 权重文件：`weights_mobilenet_aesthetic_0.07.hdf5`（放在项目根目录）

## 安装依赖
```bash
pip install -r requirements.txt
python -m playwright install
```

## 权重文件准备
请自行下载 NIMA 权重文件 `weights_mobilenet_aesthetic_0.07.hdf5`，放在项目根目录。

## 使用方法
```bash
python main.py
```
- 按提示输入关键词和页数，程序会自动爬取、评分、筛选并生成网页。
- 运行结束后会自动打开 `products.html`，可在浏览器中查看所有高分商品。

## 目录结构
```
redbubble_ai/
├── crawler.py         # 网页爬虫
├── scorer.py          # NIMA美学评分
├── download.py        # 下载图像和保存CSV
├── generate_html.py   # 生成网页
├── main.py            # 主程序
├── requirements.txt   # 依赖列表
├── products.csv       # 保存结果数据
├── products.html      # 结果网页
├── results/           # 保存图片
└── weights_mobilenet_aesthetic_0.07.hdf5  # NIMA权重
```

## 依赖说明
- playwright
- requests
- pillow
- tensorflow
- keras
- numpy

## 常见问题
- 权重文件未找到：请确保 `weights_mobilenet_aesthetic_0.07.hdf5` 在项目根目录。
- 分数分布窄：NIMA模型本身分数多集中在4~6分，建议用排序或归一化方式筛选。
- 运行慢：Playwright首次运行会自动下载浏览器，耐心等待。

---
如有问题，欢迎随时提问！ 