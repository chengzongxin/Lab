# 医生主页爬虫脚本

这是一个用于爬取百度健康医生信息的Python爬虫脚本，可以获取医生列表、构建健康页面URL，并获取医生的个人主页URL。

## 功能特点

### 🎯 核心功能
1. **获取医生列表** - 根据科室关键词搜索医生
2. **构建健康页面URL** - 生成医生在百度健康的页面链接
3. **获取个人主页** - 获取医生的百度作者主页URL

### 🚀 技术特性
- 使用配置文件管理参数
- 内置反爬虫机制（随机延迟、重试机制）
- 完整的日志记录
- 统计信息收集
- 错误处理和重试
- 支持批量处理多个科室

## 文件结构

```
scrap_doctor/
├── doctor_scraper.py          # 基础版爬虫脚本
├── doctor_scraper_v2.py       # 改进版爬虫脚本（推荐）
├── config.py                  # 配置文件
├── example_usage.py           # 使用示例
├── requirements.txt            # 依赖包列表
├── README.md                  # 说明文档
├── flow.md                    # 爬虫流程说明
├── expertlist.json            # 医生列表数据示例
└── applets.json               # 应用数据示例
```

## 安装和配置

### 1. 安装依赖
```bash
pip install -r requirements.txt
```

### 2. 基本配置
配置文件 `config.py` 包含了所有可配置的参数：

```python
# 搜索配置
SEARCH_CONFIG = {
    'default_keyword': '妇产科',  # 默认搜索关键词
    'max_pages': 3,              # 最大爬取页数
    'page_size': 20,             # 每页数量
    'delay_range': (1, 3),       # 请求间隔范围（秒）
}

# 反爬配置
ANTI_CRAWL_CONFIG = {
    'timeout': 30,           # 请求超时时间
    'max_retries': 3,        # 最大重试次数
    'retry_delay': 5,        # 重试延迟（秒）
}
```

## 使用方法

### 基本使用

```python
from doctor_scraper_v2 import DoctorScraperV2

# 创建爬虫实例
scraper = DoctorScraperV2()

# 爬取医生信息
doctors = scraper.scrape_doctors(
    search_keyword="妇产科",  # 搜索关键词
    max_pages=2,             # 爬取页数
    page_size=10             # 每页数量
)

# 保存结果
scraper.save_results(doctors, "妇产科医生.json")
```

### 高级使用

```python
# 获取医生列表
doctors = scraper.get_doctor_list("内科", page=1, page_size=20)

# 构建健康页面URL
health_url = scraper.build_doctor_home_url(doctor['doc_id'])

# 获取个人主页URL
author_url = scraper.get_doctor_author_home(doctor['doc_id'], doctor['expert_id'])

# 查看统计信息
scraper.print_statistics()
```

### 批量处理

```python
# 批量搜索多个科室
departments = ["妇产科", "内科", "外科", "儿科"]
all_results = {}

for dept in departments:
    doctors = scraper.scrape_doctors(
        search_keyword=dept,
        max_pages=1,
        page_size=10
    )
    all_results[dept] = doctors

# 保存所有结果
scraper.save_results(all_results, "所有科室医生.json")
```

## 爬虫流程说明

根据 `flow.md` 文件，爬虫的主要流程如下：

### 第一步：获取医生列表
```
URL: https://jiankang.baidu.com/wzcui/uiservice/expert/expertlist
参数: 科室关键词、页码、每页数量等
返回: 医生基本信息列表（包含expert_id和doc_id）
```

### 第二步：构建健康页面URL
```
URL: https://jiankang.baidu.com/decision/pages/expert/newHome/index
参数: doc_id（医生文档ID）
返回: 医生在百度健康的页面URL
```

### 第三步：获取医生个人主页
```
URL: https://author.baidu.com/home
参数: context（包含来源和app_id）、lid、referlid
返回: 医生的百度作者主页URL
```

## 输出数据格式

爬取到的医生数据包含以下字段：

```json
{
  "expert_id": "1458741",
  "doc_id": "pgbr3gb3qog4t33f10bg",
  "name": "孙云燕",
  "level": "主治医师",
  "hospital": "复旦大学附属中山医院",
  "department": "妇产科",
  "good_at": ["擅长: 子宫肌瘤、痛经、阴道炎..."],
  "pic": "https://...",
  "core_id": "53618",
  "health_page_url": "https://jiankang.baidu.com/decision/pages/expert/newHome/index?doc_id=...",
  "author_home_url": "https://author.baidu.com/home?..."
}
```

## 注意事项

### ⚠️ 反爬虫策略
1. **请求频率控制** - 内置随机延迟机制
2. **请求头伪装** - 模拟真实浏览器请求
3. **会话保持** - 使用Session保持连接
4. **重试机制** - 失败请求自动重试

### 🔒 合规使用
- 请遵守网站的robots.txt规则
- 不要过于频繁地请求，避免对服务器造成压力
- 仅用于学习和研究目的
- 遵守相关法律法规

### 🚨 风险提示
- 网站可能会更新反爬虫机制
- 请求过于频繁可能被限制访问
- 建议在测试环境中先验证功能

## 故障排除

### 常见问题

1. **请求失败**
   - 检查网络连接
   - 确认URL是否有效
   - 查看日志文件了解详细错误

2. **数据解析失败**
   - 检查返回的JSON格式
   - 确认网站结构是否发生变化
   - 查看日志中的错误信息

3. **被反爬虫拦截**
   - 增加延迟时间
   - 更换User-Agent
   - 使用代理IP（需要配置）

### 日志文件
脚本会生成 `scraper.log` 日志文件，包含详细的运行信息，可用于调试和监控。

## 扩展功能

### 可能的改进方向
1. **代理支持** - 添加代理池轮换
2. **数据存储** - 集成数据库存储
3. **Web界面** - 添加简单的Web管理界面
4. **定时任务** - 支持定时爬取
5. **多线程** - 提高爬取效率

### 第三方库集成
```python
# 数据处理
import pandas as pd
df = pd.DataFrame(doctors)

# 数据库存储
import sqlite3
# 或使用其他数据库驱动

# 异步处理
import asyncio
import aiohttp
```

## 许可证

本项目仅供学习和研究使用，请遵守相关法律法规和网站使用条款。

## 联系方式

如有问题或建议，请通过以下方式联系：
- 提交Issue
- 发送邮件
- 参与讨论

---

**免责声明**：本脚本仅供学习和研究使用，使用者需自行承担使用风险，开发者不承担任何法律责任。
