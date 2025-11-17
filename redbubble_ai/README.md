# Redbubble AI 商品美学平台

一个基于 AI 的 Redbubble 商品美学评分和展示平台，能够自动爬取商品、进行美学评分，并提供现代化的 Web 界面展示。

## 🎯 项目概述

本项目通过 AI 技术自动识别和评分 Redbubble 网站上的商品美学价值，帮助用户快速发现高质量的设计商品。

### 核心功能
- 🔍 **智能爬取**：自动搜索和爬取 Redbubble 商品信息
- 🤖 **AI 评分**：使用 NIMA 模型对商品图片进行美学评分（1-10分）
- 💾 **数据存储**：将商品信息存储到 MySQL 数据库
- 🖥️ **Web 展示**：现代化的 React 前端界面展示商品
- 🖼️ **本地图片**：支持本地图片存储和快速加载

## 🏗️ 项目架构

```
redbubble_ai/
├── crawler/              # 数据采集模块
│   ├── crawler.py        # Redbubble 爬虫
│   ├── download.py       # 图片下载工具
│   ├── scorer.py         # AI 美学评分
│   ├── main.py          # 爬虫主程序
│   ├── generate_html.py  # 静态HTML生成
│   ├── results/         # 下载的图片存储
│   └── requirements.txt  # Python 依赖
├── backend/             # 后端 API 服务
│   ├── api_server.py    # FastAPI 服务器
│   ├── requirements.txt # Python 依赖
│   └── README.md        # 后端说明
├── frontend/            # React 前端应用
│   ├── src/            # 源代码
│   ├── public/         # 静态资源
│   ├── package.json    # Node.js 依赖
│   └── README.md       # 前端说明
└── README.md           # 项目总说明
```

## 🛠️ 技术栈

### 后端技术
- **Python 3.8+**
- **FastAPI** - 现代化 Web API 框架
- **Uvicorn** - ASGI 服务器
- **MySQL** - 数据存储
- **Playwright** - 浏览器自动化
- **TensorFlow/Keras** - AI 模型 (NIMA)
- **Pillow** - 图像处理

### 前端技术
- **React 18** - 用户界面框架
- **TypeScript** - 类型安全
- **Axios** - HTTP 客户端
- **CSS Grid/Flexbox** - 响应式布局

### AI 模型
- **NIMA (Neural Image Assessment)** - 美学评分模型
- 基于 MobileNet 架构
- 输出 1-10 分的美学评分

## 📋 环境要求

- Python 3.8+
- Node.js 16+
- MySQL 5.7+ 或 8.0+
- 至少 2GB 可用内存

## 🚀 快速开始

### 方法一：一键启动（推荐）

```bash
# 1. 克隆项目
git clone <repository-url>
cd redbubble_ai

# 2. 确保 MySQL 服务运行
# macOS: brew services start mysql
# Ubuntu: sudo systemctl start mysql

# 3. 一键启动所有服务
./start.sh
```

### 方法二：手动启动

#### 1. 克隆项目
```bash
git clone <repository-url>
cd redbubble_ai
```

#### 2. 数据库配置
确保 MySQL 服务运行在 `localhost:3306`，用户名为 `root`，密码为 `123456789`。

如需修改数据库配置，请编辑 `backend/api_server.py` 中的连接参数。

#### 3. 安装依赖

**后端依赖**
```bash
cd backend
pip install -r requirements.txt
```

**前端依赖**
```bash
cd frontend
npm install
```

#### 4. 启动服务

**启动后端 API 服务**
```bash
cd backend
uvicorn api_server:app --reload --port 8000
```

**启动前端开发服务器**
```bash
cd frontend
npm start
```

#### 5. 访问应用
- 前端界面：http://localhost:3000
- 后端 API：http://localhost:8000
- API 文档：http://localhost:8000/docs

### 项目管理脚本

项目提供了便捷的管理脚本：

```bash
./start.sh    # 一键启动所有服务
./stop.sh     # 停止所有服务
./status.sh   # 检查服务状态
```

## 📖 使用指南

### 数据采集

1. **运行爬虫程序**
   ```bash
   cd crawler
   python main.py
   ```

2. **输入搜索参数**
   - 搜索关键词（如：cat, dog, anime 等）
   - 爬取页数（默认 1 页）

3. **等待处理完成**
   - 程序会自动下载图片
   - 使用 NIMA 模型进行美学评分
   - 将数据保存到 MySQL 数据库

### 查看结果

1. 确保后端和前端服务都在运行
2. 访问 http://localhost:3000
3. 查看商品列表和美学评分

## 🔧 配置说明

### 数据库配置
在 `backend/api_server.py` 中修改：
```python
def get_db_conn():
    return mysql.connector.connect(
        host="localhost",
        port=3306,
        user="root",
        password="123456789",
        database="redbubble_ai"
    )
```

### AI 模型配置
NIMA 模型权重文件应放置在 `crawler/` 目录下：
- 文件名：`weights_mobilenet_aesthetic_0.07.hdf5`
- 大小：约 13MB

### 爬虫配置
在 `crawler/main.py` 中可以调整：
- `limit`：每页爬取的商品数量
- `score_threshold`：美学评分阈值

## 📊 数据库结构

```sql
CREATE TABLE products (
  id INT PRIMARY KEY AUTO_INCREMENT,
  title VARCHAR(512),        -- 商品标题
  img VARCHAR(1024),         -- 网络图片URL
  score FLOAT,              -- 美学评分 (1-10)
  link VARCHAR(1024),        -- 商品链接
  local_img VARCHAR(1024)    -- 本地图片路径
);
```

## 🎨 前端特性

- **响应式设计**：支持桌面、平板、手机
- **6列网格布局**：高效展示商品
- **悬停效果**：增强用户体验
- **加载状态**：友好的加载提示
- **错误处理**：优雅的错误显示

## 🔍 API 接口

### 获取商品列表
```
GET /api/products
```

响应示例：
```json
[
  {
    "id": 1,
    "title": "Cute Cat Design",
    "img": "http://localhost:8000/images/cute_cat.jpg",
    "score": 7.5,
    "link": "https://www.redbubble.com/...",
    "local_img": "results/cute_cat.jpg"
  }
]
```

## 🐛 故障排除

### 常见问题

1. **图片无法显示**
   - 检查后端服务是否运行在 8000 端口
   - 确认 `crawler/results/` 目录存在图片文件

2. **数据库连接失败**
   - 确认 MySQL 服务正在运行
   - 检查用户名和密码是否正确
   - 确认数据库 `redbubble_ai` 已创建

3. **爬虫失败**
   - 检查网络连接
   - 确认 Redbubble 网站可访问
   - 可能需要调整浏览器配置

4. **AI 评分异常**
   - 确认 NIMA 权重文件存在
   - 检查 TensorFlow 版本兼容性

### 日志查看
- 后端日志：查看终端输出
- 前端日志：浏览器开发者工具 Console

## 🔒 注意事项

1. **反爬虫机制**：Redbubble 有反爬虫保护，建议适度使用
2. **图片版权**：下载的图片仅供个人使用，请遵守版权规定
3. **数据库备份**：定期备份重要数据
4. **资源使用**：AI 模型需要一定计算资源，建议在性能较好的机器上运行

## 📝 开发说明

### 添加新功能
1. 后端：在 `backend/` 目录下开发
2. 前端：在 `frontend/src/` 目录下开发
3. 爬虫：在 `crawler/` 目录下开发

### 代码规范
- Python：遵循 PEP 8 规范
- TypeScript：使用 ESLint 和 Prettier
- 提交信息：使用清晰的英文描述

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支
3. 提交更改
4. 推送到分支
5. 创建 Pull Request

## 📄 许可证

本项目仅供学习和研究使用。

## 📞 联系方式

如有问题或建议，请通过以下方式联系：
- 提交 Issue
- 发送邮件

---

**享受发现美好设计的乐趣！** 🎨✨ 



# Windows
set HTTP_PROXY=http://127.0.0.1:7897
set HTTPS_PROXY=http://127.0.0.1:7897

# macOS/Linux  
export HTTP_PROXY=http://127.0.0.1:7890
export HTTPS_PROXY=http://127.0.0.1:7890

# 或者在 .env 文件中配置
HTTP_PROXY=http://127.0.0.1:7897
HTTPS_PROXY=http://127.0.0.1:7897

## 启动命令

Windows:
```bash
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\selenum\ChromeProfile"
```

macOS:
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="$HOME/selenium/ChromeProfile"
```