# Crawler 模块

Redbubble AI 项目的数据采集模块，负责爬取商品信息、下载图片、进行 AI 美学评分。

## 🎯 功能概述

- 🔍 **智能爬取**：自动搜索 Redbubble 商品
- 📥 **图片下载**：批量下载商品主图
- 🤖 **AI 评分**：使用 NIMA 模型进行美学评分
- 💾 **数据存储**：保存到 CSV 和 MySQL 数据库

## 📁 文件结构

```
crawler/
├── crawler.py        # Redbubble 爬虫核心
├── download.py       # 图片下载工具
├── scorer.py         # AI 美学评分模块
├── main.py          # 主程序入口
├── generate_html.py  # 静态HTML生成
├── results/         # 图片存储目录
├── requirements.txt  # Python 依赖
└── README.md        # 本文件
```

## 🛠️ 技术栈

- **Playwright** - 浏览器自动化
- **TensorFlow/Keras** - NIMA AI 模型
- **Pillow** - 图像处理
- **MySQL Connector** - 数据库连接
- **Requests** - HTTP 请求

## 🚀 快速开始

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 下载 NIMA 模型
确保 `weights_mobilenet_aesthetic_0.07.hdf5` 文件在 crawler 目录下。

### 3. 运行爬虫
```bash
python main.py
```

## 📖 使用说明

### 运行流程

1. **输入搜索关键词**
   ```
   请输入搜索关键词：cat
   ```

2. **设置爬取页数**
   ```
   请输入要爬取的页数（回车默认1）：2
   ```

3. **自动处理**
   - 爬取商品信息
   - 下载商品图片
   - AI 美学评分
   - 保存到数据库

### 配置参数

在 `main.py` 中可以调整：

```python
limit = 20              # 每页爬取商品数量
score_threshold = 1     # 美学评分阈值
```

## 🔧 模块说明

### crawler.py
- **功能**：Redbubble 网站爬虫
- **核心方法**：`crawl_redbubble(keyword, pages=1)`
- **返回**：商品信息列表

### download.py
- **功能**：图片下载工具
- **核心方法**：`download_image(url, filename)`
- **特性**：支持反爬虫头部

### scorer.py
- **功能**：AI 美学评分
- **模型**：NIMA (Neural Image Assessment)
- **评分范围**：1-10 分
- **核心方法**：`nima_score(img_path)`

### main.py
- **功能**：主程序入口
- **流程**：爬取 → 下载 → 评分 → 保存
- **输出**：CSV 文件 + MySQL 数据库

## 📊 输出文件

### CSV 文件
- **文件名**：`products.csv`
- **字段**：title, img, score, link, local_img

### 图片文件
- **目录**：`results/`
- **格式**：JPG
- **命名**：商品标题（安全化处理）

### HTML 文件
- **文件名**：`products.html`
- **功能**：静态商品展示页面

## 🐛 故障排除

### 常见问题

1. **爬虫超时**
   - 检查网络连接
   - 增加超时时间
   - 使用代理（如需要）

2. **图片下载失败**
   - 检查反爬虫头部
   - 确认图片 URL 有效
   - 检查磁盘空间

3. **AI 评分失败**
   - 确认 NIMA 权重文件存在
   - 检查 TensorFlow 版本
   - 验证图片格式

4. **数据库连接失败**
   - 确认 MySQL 服务运行
   - 检查连接参数
   - 确认数据库权限

### 调试技巧

1. **启用详细日志**
   ```python
   import logging
   logging.basicConfig(level=logging.DEBUG)
   ```

2. **检查浏览器状态**
   ```python
   # 在 crawler.py 中设置
   browser = p.chromium.launch(headless=False)  # 显示浏览器
   ```

3. **验证图片下载**
   ```python
   # 检查文件大小
   if os.path.getsize(filename) < 1000:
       print(f"图片可能下载失败: {filename}")
   ```

## 🔒 注意事项

1. **反爬虫机制**
   - Redbubble 有反爬虫保护
   - 建议控制爬取频率
   - 遵守网站使用条款

2. **资源使用**
   - AI 模型需要 GPU 内存
   - 大量图片下载需要磁盘空间
   - 建议在性能较好的机器上运行

3. **版权问题**
   - 下载的图片仅供个人使用
   - 请遵守版权规定
   - 不要用于商业用途

## 📈 性能优化

### 爬取优化
- 使用异步请求
- 实现请求队列
- 添加重试机制

### 评分优化
- 批量处理图片
- 使用 GPU 加速
- 缓存评分结果

### 存储优化
- 压缩图片存储
- 数据库索引优化
- 定期清理临时文件

## 🔄 扩展功能

### 可能的改进
1. **多线程爬取**
2. **代理池支持**
3. **更多 AI 模型**
4. **实时监控**
5. **数据可视化**

### 自定义开发
1. 修改 `crawler.py` 适配其他网站
2. 在 `scorer.py` 中添加新的评分模型
3. 扩展 `main.py` 支持更多输出格式

---

**Happy Crawling!** 🕷️✨ 