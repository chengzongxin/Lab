# Selenium百度健康爬虫使用说明

## 📋 概述

`selenium_baidu_health_scraper.py` 是基于Selenium WebDriver的百度健康爬虫程序，完全模拟真实浏览器行为，避免了使用requests直接发送HTTP请求可能遇到的反爬虫问题。

## 🔄 主要改动

### 1. **搜索方式改变**
- **原方式**：使用 `requests.get()` 直接发送HTTP请求到百度搜索URL
- **新方式**：使用Selenium打开浏览器，导航到百度首页，在搜索框中输入关键词并点击搜索按钮

### 2. **页面获取方式改变**
- **原方式**：使用 `requests.get()` 获取页面HTML内容
- **新方式**：使用 `driver.get()` 导航到页面，然后通过 `driver.page_source` 获取HTML内容

### 3. **元素查找方式**
- **原方式**：完全依赖BeautifulSoup解析HTML
- **新方式**：结合使用Selenium的WebDriver API和BeautifulSoup，更灵活可靠

## 🚀 使用方法

### 基本使用

```bash
python selenium_baidu_health_scraper.py
```

### 程序运行流程

1. **选择Excel文件**：程序会自动扫描当前目录下的Excel文件，让你选择要处理的文件
2. **选择浏览器模式**：
   - 是否使用现有浏览器实例（如果已有Chrome在调试模式下运行）
   - 是否使用无头模式（不显示浏览器窗口）
3. **开始爬取**：程序会逐个处理Excel文件中的标题

### 使用现有浏览器实例

如果你已经有一个Chrome浏览器在调试模式下运行，可以连接到它：

1. **启动Chrome调试模式**：
   ```bash
   # macOS/Linux
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222
   
   # Windows
   chrome.exe --remote-debugging-port=9222
   ```

2. **运行程序时选择使用现有浏览器**：
   - 输入 `y` 使用现有浏览器
   - 输入调试端口（默认9222）

### 无头模式

如果不想看到浏览器窗口，可以使用无头模式：
- 运行程序时输入 `y` 启用无头模式

## 📁 输出文件

- **结果文件**：`Selenium百度健康爬取结果_YYYYMMDD.xlsx`
- **日志文件**：`selenium_scraper.log`

## 🔧 技术特点

### 1. **反反爬虫措施**
- 禁用自动化检测特征
- 模拟真实浏览器行为
- 随机延迟避免被识别为机器人
- 隐藏webdriver特征

### 2. **错误处理**
- 自动检测验证码
- 超时重试机制
- 详细的日志记录

### 3. **页面加载等待**
- 使用WebDriverWait等待元素加载
- 智能判断页面是否加载完成

## ⚠️ 注意事项

1. **Chrome浏览器**：需要安装Chrome浏览器，程序会自动下载匹配的ChromeDriver
2. **网络连接**：需要稳定的网络连接
3. **运行时间**：由于使用真实浏览器，运行速度会比requests方式稍慢，但更稳定
4. **资源占用**：浏览器会占用一定的内存和CPU资源

## 🆚 与原版本对比

| 特性 | requests版本 | Selenium版本 |
|------|-------------|-------------|
| 速度 | 快 | 稍慢 |
| 稳定性 | 可能被反爬 | 更稳定 |
| 资源占用 | 低 | 较高 |
| 反爬能力 | 较弱 | 强 |
| 调试难度 | 简单 | 中等 |

## 📝 代码示例

### 初始化爬虫

```python
# 基本使用
scraper = SeleniumBaiduHealthScraper()

# 使用无头模式
scraper = SeleniumBaiduHealthScraper(headless=True)

# 连接到现有浏览器
scraper = SeleniumBaiduHealthScraper(
    use_existing_browser=True,
    debug_port=9222
)
```

### 运行爬虫

```python
result_file = scraper.run('宠物种子词.xlsx')
```

## 🐛 常见问题

### 1. ChromeDriver版本不匹配
**解决方法**：程序使用webdriver_manager自动管理ChromeDriver，会自动下载匹配的版本

### 2. 页面加载超时
**解决方法**：检查网络连接，或增加等待时间

### 3. 找不到搜索框
**解决方法**：百度页面结构可能变化，需要更新选择器

## 📚 依赖库

- selenium
- webdriver-manager
- pandas
- beautifulsoup4
- openpyxl

所有依赖都在 `requirements.txt` 中，使用以下命令安装：

```bash
pip install -r requirements.txt
```
