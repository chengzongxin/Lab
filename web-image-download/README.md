# 网页图片下载工具

一个基于Python的GUI工具，可以从指定网站下载图片到本地磁盘。支持现代网站的动态内容加载。

## 🚀 功能特性

- 🖥️ 简洁的图形用户界面
- 🌐 支持输入任意网站URL
- 📸 自动提取网页中的图片链接
- 💾 批量下载图片到本地
- 📊 实时显示下载进度
- 🎯 支持多种图片格式（jpg, png, gif, webp等）
- 🔄 **双模式下载**：简单模式（Requests）+ 高级模式（Playwright）
- 🤖 **智能检测**：自动识别网站类型，推荐合适的下载方式
- 📱 **现代网站支持**：支持JavaScript动态加载的网站（如Redbubble、Pinterest等）

## 📦 快速安装

### 方法一：自动安装（推荐）

```bash
python install.py
```

### 方法二：手动安装

```bash
# 1. 安装Python依赖
pip install -r requirements.txt

# 2. 安装Playwright浏览器（可选，用于高级模式）
playwright install
```

## 🎮 使用方法

```bash
python main.py
```

## 🔧 下载模式

### 简单模式（Requests）
- **适用场景**：传统静态网站
- **特点**：速度快，资源占用少
- **支持网站**：Wikipedia、GitHub、Stack Overflow等

### 高级模式（Playwright）
- **适用场景**：现代动态网站
- **特点**：支持JavaScript渲染，功能强大
- **支持网站**：Redbubble、Pinterest、Instagram、Facebook等

### 自动模式
- **智能检测**：根据网站类型自动选择最佳下载方式
- **推荐使用**：适合大多数用户

## 🛠️ 技术栈

- **GUI**: tkinter (Python内置)
- **网络请求**: requests
- **HTML解析**: BeautifulSoup4
- **浏览器自动化**: Playwright
- **图片处理**: Pillow
- **进度显示**: tqdm

## 📁 项目结构

```
web-image-download/
├── main.py                    # 🚀 主程序入口
├── gui.py                     # 🖥️ GUI界面实现
├── downloader.py              # ⬇️ 简单模式下载器
├── playwright_downloader.py   # 🌐 高级模式下载器
├── site_detector.py           # 🔍 网站类型检测
├── utils.py                   # 🔧 工具函数
├── install.py                 # 📦 安装脚本
├── test_downloader.py         # 🧪 测试脚本
├── requirements.txt           # 📋 项目依赖
└── README.md                  # 📖 项目说明
```

## 🎯 使用示例

### Redbubble网站下载
1. 启动程序：`python main.py`
2. 输入URL：`https://www.redbubble.com/people/paisleydrawrns/explore`
3. 选择模式：自动模式（推荐）
4. 设置下载数量：留空下载所有图片
5. 点击开始下载

### 其他现代网站
- **Pinterest**: 支持无限滚动加载
- **Instagram**: 支持动态内容
- **Facebook**: 支持懒加载图片
- **Twitter**: 支持实时内容

## ⚠️ 注意事项

1. **网络连接**：确保网络连接稳定
2. **网站访问**：某些网站可能有访问限制
3. **下载速度**：高级模式需要启动浏览器，首次使用较慢
4. **资源占用**：高级模式占用更多内存和CPU资源

## 🔧 故障排除

### 常见问题

**Q: 高级模式无法启动？**
A: 请确保已安装Playwright浏览器：`playwright install`

**Q: 下载速度很慢？**
A: 可以尝试使用简单模式，或减少最大下载数量

**Q: 某些图片下载失败？**
A: 可能是网络问题或图片链接失效，程序会自动跳过

### 手动安装Playwright

```bash
# 安装Playwright包
pip install playwright

# 安装浏览器
playwright install chromium
```

## 📄 许可证

本项目仅供学习和个人使用，请遵守相关网站的使用条款。 