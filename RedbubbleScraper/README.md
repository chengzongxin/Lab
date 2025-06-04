# Redbubble 商品爬虫

这是一个用于爬取 Redbubble 网站商品数据的爬虫项目。

## 功能特点

- 支持分页爬取商品数据
- 自动处理请求头和 User-Agent
- 数据保存为 CSV 和 JSON 格式
- 内置重试机制和异常处理
- 支持断点续爬

## 环境要求

- Python 3.8+
- 依赖包见 requirements.txt

## 安装步骤

1. 克隆项目
```bash
git clone [项目地址]
cd RedbubbleScraper
```

2. 创建虚拟环境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
.\venv\Scripts\activate  # Windows
```

3. 安装依赖
```bash
pip install -r requirements.txt
```

## 使用方法

1. 运行爬虫
```bash
python spiders/product_spider.py
```

2. 查看结果
- CSV 文件保存在 `data/products/` 目录下
- JSON 文件保存在 `data/products/` 目录下

## 配置说明

配置文件位于 `config/config.py`，可以修改以下参数：
- 请求超时时间
- 重试次数
- 延迟时间
- 数据保存路径

## 注意事项

- 请遵守网站的robots.txt规则
- 建议适当调整爬取间隔，避免对目标网站造成压力
- 定期检查网站结构变化，及时更新选择器

## 许可证

MIT License 