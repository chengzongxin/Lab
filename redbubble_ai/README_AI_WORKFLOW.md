# TEMU商品 AI标题清洗 + Redbubble搜索工作流

## 📖 功能说明

这是一个智能化的商品分析工作流，主要流程如下：

1. **获取TEMU爆款商品**: 从已爬取的TEMU商品数据库中获取待处理商品
2. **AI标题清洗**: 使用OpenAI API清洗商品标题，提取核心关键词（去除营销词汇、数量词等）
3. **Redbubble搜索**: 用清洗后的关键词在Redbubble搜索相似设计
4. **保存匹配结果**: 将TEMU商品与Redbubble商品的匹配关系保存到数据库

## 🎯 使用场景

- 分析TEMU爆款商品的核心卖点
- 为TEMU商品寻找Redbubble上的相似设计
- 发现设计趋势和市场机会

## 📋 前置条件

### 1. 数据准备

首先需要爬取TEMU类目商品：

```bash
# 方式1：通过前端界面
1. 打开前端页面
2. 切换到"TEMU"标签页
3. 输入类目URL和参数
4. 点击"启动爬取"

# 方式2：通过API
curl -X POST "http://localhost:8000/api/crawl/temu/category" \
  -H "Content-Type: application/json" \
  -d '{
    "category_url": "https://www.temu.com/ca/mens-hats-caps-o3-800.html",
    "min_sales": 1000,
    "debug_port": 9222
  }'
```

### 2. 配置OpenAI API

创建 `backend/.env` 文件：

```bash
cd backend
cp .env.example .env
```

编辑 `.env` 文件，添加你的OpenAI API密钥：

```env
OPENAI_API_KEY=sk-your-api-key-here
OPENAI_BASE_URL=https://api.openai.com/v1
```

**国内用户**：如果使用国内API服务（如Azure OpenAI、国内代理等），修改 `OPENAI_BASE_URL`：

```env
OPENAI_BASE_URL=https://your-custom-endpoint.com/v1
```

### 3. 启动服务

```bash
# 启动后端
cd backend
source .venv/bin/activate
uvicorn api_server:app --reload

# 启动前端（新终端）
cd frontend
npm install
npm start
```

## 🚀 使用方法

### 方式1：通过前端界面（推荐）

1. 打开浏览器访问 `http://localhost:3000`
2. 切换到 "🤖 AI工作流" 标签页
3. 配置参数：
   - **类目ID**：留空处理所有类目，或指定特定类目ID
   - **批量处理数量**：每次处理多少个商品（建议10-20个）
   - **Redbubble搜索页数**：每个关键词搜索几页（建议1-2页）
4. 点击 "🚀 启动AI工作流"
5. 查看实时统计和匹配结果

### 方式2：通过API

```bash
curl -X POST "http://localhost:8000/api/temu/ai-workflow" \
  -H "Content-Type: application/json" \
  -d '{
    "category_id": null,
    "batch_size": 10,
    "redbubble_pages": 2
  }'
```

### 方式3：通过Python代码

```python
from temu_ai_workflow import process_temu_to_redbubble_workflow

stats = process_temu_to_redbubble_workflow(
    category_id=None,  # 处理所有类目
    batch_size=10,     # 每次10个商品
    redbubble_pages=2  # 每个关键词搜索2页
)

print(f"处理结果: {stats}")
```

## 📊 数据库表结构

### temu_title_cleaning - 标题清洗记录

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| product_id | INT | TEMU商品ID |
| goods_id | VARCHAR(50) | TEMU商品goods_id |
| original_title | VARCHAR(1000) | 原始标题 |
| cleaned_keywords | TEXT | 清洗后的关键词 |
| keywords_json | JSON | 关键词列表（JSON格式） |
| ai_model | VARCHAR(50) | 使用的AI模型 |
| status | ENUM | 状态：pending/processing/completed/failed |
| error_message | TEXT | 错误信息 |
| created_at | TIMESTAMP | 创建时间 |
| updated_at | TIMESTAMP | 更新时间 |

### temu_redbubble_matches - 匹配关系表

| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| temu_product_id | INT | TEMU商品ID |
| temu_goods_id | VARCHAR(50) | TEMU商品goods_id |
| search_keywords | TEXT | 搜索关键词 |
| redbubble_product_id | INT | Redbubble商品ID |
| redbubble_title | VARCHAR(1000) | Redbubble商品标题 |
| redbubble_img | VARCHAR(1000) | Redbubble商品图片 |
| redbubble_link | VARCHAR(1000) | Redbubble商品链接 |
| redbubble_score | DECIMAL(3,2) | Redbubble商品评分 |
| match_score | DECIMAL(5,4) | 匹配分数 |
| rank_position | INT | 排名位置 |
| created_at | TIMESTAMP | 创建时间 |

## 🔍 API端点

### POST /api/temu/ai-workflow
启动AI工作流

**请求参数**：
```json
{
  "category_id": null,      // 类目ID（可选）
  "batch_size": 10,         // 批量处理数量
  "redbubble_pages": 2      // Redbubble搜索页数
}
```

**响应**：
```json
{
  "success": true,
  "task_id": "uuid",
  "message": "已启动TEMU AI清洗工作流，批量处理 10 个商品"
}
```

### GET /api/temu/ai-workflow/stats
获取工作流统计信息

**查询参数**：
- `category_id` (可选): 类目ID

**响应**：
```json
{
  "cleaning": {
    "total": 100,
    "completed": 80
  },
  "matches": {
    "matched_products": 75,
    "total_matches": 450
  }
}
```

### GET /api/temu/matches
获取匹配结果列表

**查询参数**：
- `limit`: 返回数量（默认50）
- `offset`: 偏移量（默认0）
- `category_id` (可选): 类目ID
- `min_match_score`: 最小匹配分数（默认0.5）

**响应**：
```json
{
  "total": 100,
  "matches": [
    {
      "id": 1,
      "temu_product_id": 123,
      "temu_title": "...",
      "search_keywords": "retro hat dive design",
      "redbubble_title": "...",
      "redbubble_img": "...",
      "match_score": 0.95
    }
  ],
  "limit": 50,
  "offset": 0
}
```

## 💡 AI标题清洗示例

### 示例1
**原标题**: `1pc Retro Brimless Hat With Deep Sea Dive Diving Design - Casual Stylish Accessory For Men & Women`

**清洗后**: `retro brimless hat deep sea dive design`

**说明**: 
- 去除了数量词 `1pc`
- 去除了营销词 `Casual`, `Stylish`, `Accessory`
- 去除了通用词 `For Men & Women`
- 保留了核心关键词 `retro`, `brimless hat`, `deep sea dive`, `design`

### 示例2
**原标题**: `Men's Winter Warm Knit Beanie - Premium Quality Soft Comfortable Hat`

**清洗后**: `men winter knit beanie`

**说明**:
- 去除了形容词 `Warm`, `Premium`, `Quality`, `Soft`, `Comfortable`
- 保留了核心特征 `men`, `winter`, `knit`, `beanie`

### 示例3
**原标题**: `Colorful Pullover Hat Ski Hat For Men Women Casual Neck Hair Hoop Skull Cap Hip Hop Hat Beanie Christmas Gift`

**清洗后**: `colorful pullover ski hat skull cap hip hop beanie`

## ⚙️ 配置选项

### AI模型选择

在 `ai_title_cleaner.py` 中可以选择不同的模型：

```python
# 使用 gpt-4o-mini（经济实惠，推荐）
result = clean_title_with_ai(title, model="gpt-4o-mini")

# 使用 gpt-4（更强大但更贵）
result = clean_title_with_ai(title, model="gpt-4")

# 使用 gpt-3.5-turbo（更便宜）
result = clean_title_with_ai(title, model="gpt-3.5-turbo")
```

### 降级策略

如果AI API调用失败，系统会自动使用基于规则的方法作为降级方案：

```python
# 带降级的清洗
result = clean_title_with_fallback(title)
# 如果AI失败，会自动使用规则方法
```

## 🐛 故障排除

### 问题1: OpenAI API调用失败

**错误信息**: `未设置OPENAI_API_KEY环境变量`

**解决方法**:
1. 确认 `backend/.env` 文件存在
2. 检查 `OPENAI_API_KEY` 是否正确设置
3. 重启后端服务

### 问题2: 没有待处理的商品

**错误信息**: `没有需要处理的商品`

**解决方法**:
1. 先运行TEMU类目爬虫获取商品数据
2. 检查数据库中是否有 `temu_products` 数据

### 问题3: Redbubble搜索失败

**可能原因**:
- 网络连接问题
- Redbubble网站结构变化
- 浏览器未启动（需要Playwright）

**解决方法**:
1. 检查网络连接
2. 更新 `crawler_utils.py` 中的选择器
3. 确保Playwright浏览器已安装

## 📝 注意事项

1. **API费用**: OpenAI API按调用次数收费，建议使用 `gpt-4o-mini` 模型降低成本
2. **处理速度**: AI清洗和Redbubble搜索需要时间，建议批量处理数量设为10-20
3. **数据去重**: 系统会自动跳过已清洗的商品
4. **匹配分数**: 匹配分数基于搜索排名，排名越靠前分数越高

## 📚 相关文档

- [TEMU爬虫使用说明](TEMU完整爬取功能说明.md)
- [Redbubble爬虫使用说明](../README.md)
- [OpenAI API文档](https://platform.openai.com/docs/api-reference)

## 🎉 功能特点

✅ AI智能清洗标题，提取核心关键词  
✅ 自动降级策略，API失败时使用规则方法  
✅ 批量处理，提高效率  
✅ 实时统计展示  
✅ 美观的前端界面  
✅ 完整的匹配结果展示  
✅ 支持类目过滤  
✅ 可配置的搜索参数

