# Redbubble AI 商品筛选器

## 项目简介
本项目可以自动在 Redbubble 网站上搜索商品，利用AI模型判断商品图片是否“好看”，并下载主图和商品链接保存到本地。

## 主要功能
- 自动化爬取 Redbubble 商品信息（主图、标题、链接）
- 使用AI模型对商品图片进行美学评分
- 下载高分商品主图并保存信息到CSV

## 目录结构
```
redbubble_ai/
├── crawler.py         # 网页爬虫
├── scorer.py          # 图像评分
├── download.py        # 下载图像
├── main.py            # 主程序
├── results/           # 保存图片
└── products.csv       # 保存结果数据
```

## 安装依赖
```bash
pip install -r requirements.txt
python -m playwright install
```

## 使用方法
```bash
python main.py
```

## 依赖说明
- playwright
- requests
- pillow
- tensorflow/keras（用于AI评分，可选）

## 进阶
- 可自定义关键词、评分阈值
- 支持多关键词批量搜索
- 可扩展为Web界面

---
如有问题，欢迎随时提问！ 