# TEMU完整爬取功能说明

## 📋 功能概述

实现了完整的TEMU爆款商品爬取系统，包括：
1. **类目商品爬取**：爬取指定类目下的所有爆款商品（销量≥1000）
2. **商品详情爬取**：获取商品详情页信息，提取卖家店铺链接
3. **卖家店铺爬取**：爬取卖家店铺的所有商品

## 🗄️ 数据库表结构

### 1. temu_categories - 类目表
存储TEMU类目信息
```sql
- id: 主键
- category_url: 类目URL（唯一）
- category_name: 类目名称
- status: 状态（pending/crawling/completed/failed）
- total_products: 总商品数
- crawled_products: 已爬取商品数
```

### 2. temu_products - 商品表（从类目页爬取）
存储从类目页爬取的爆款商品
```sql
- id: 主键
- goods_id: 商品ID（唯一）
- title: 商品标题
- img: 商品图片URL
- link: 商品链接
- price: 价格
- original_price: 原价
- sales_count: 销量（数字）
- sales_text: 销量文本（如"100K+sold"）
- rating: 评分（1-5分）
- review_count: 评论数
- category_id: 关联类目ID
- mall_id: 卖家店铺ID
- seller_url: 卖家店铺URL
- detail_crawled: 是否已爬取详情
```

### 3. temu_product_details - 商品详情表
存储商品详情页信息
```sql
- id: 主键
- goods_id: 商品ID（唯一）
- product_id: 关联商品ID
- description: 商品描述
- specifications: 规格信息
- images: 商品图片列表（JSON）
- video_url: 视频URL
- mall_id: 卖家店铺ID
- seller_name: 卖家名称
- seller_url: 卖家店铺URL
```

### 4. temu_sellers - 卖家店铺表
存储卖家店铺信息
```sql
- id: 主键
- mall_id: 店铺ID（唯一）
- seller_name: 卖家名称
- seller_url: 店铺URL
- total_products: 总商品数
- crawled_products: 已爬取商品数
- status: 状态（pending/crawling/completed/failed）
```

### 5. temu_seller_products - 店铺商品表
存储从店铺页面爬取的商品
```sql
- id: 主键
- goods_id: 商品ID
- seller_id: 关联卖家ID
- mall_id: 店铺ID
- title: 商品标题
- img: 商品图片
- link: 商品链接
- price: 价格
```

## 🔧 核心函数

### 1. crawl_temu_category()
爬取TEMU类目下的所有商品，筛选销量大于指定值的爆款商品

**参数**：
- `category_url`: 类目URL
- `min_sales`: 最小销量（默认1000）
- `use_persistent_context`: 是否使用持久化上下文
- `user_data_dir`: 用户数据目录
- `debug_port`: 调试端口

**返回**：商品列表，包含goods_id, title, img, link, price, sales_count等

### 2. crawl_temu_product_detail()
爬取商品详情页，提取卖家店铺信息

**参数**：
- `product_url`: 商品详情页URL
- `use_persistent_context`: 是否使用持久化上下文
- `user_data_dir`: 用户数据目录
- `debug_port`: 调试端口

**返回**：商品详情信息，包含mall_id, seller_url等

### 3. crawl_temu_mall()
爬取卖家店铺的所有商品（已实现）

### 4. crawl_temu_category_full_workflow()
完整的爬取工作流，整合所有步骤

**工作流程**：
1. 保存类目信息
2. 爬取类目下的爆款商品并入库
3. 爬取每个商品的详情页，获取卖家信息
4. 爬取每个卖家的店铺所有商品并入库

## 📡 API接口

### POST /api/crawl/temu/category

启动TEMU类目完整爬取工作流

**请求体**：
```json
{
  "category_url": "https://www.temu.com/ca/mens-hats-caps-o3-800.html?...",
  "min_sales": 1000,
  "crawl_details": true,
  "crawl_seller_products": true,
  "use_persistent_context": false,
  "user_data_dir": null,
  "debug_port": 9222
}
```

**响应**：
```json
{
  "success": true,
  "task_id": "uuid",
  "message": "已启动TEMU类目爬取工作流..."
}
```

## 🚀 使用示例

### 方式1：通过API调用

```bash
curl -X POST "http://localhost:8000/api/crawl/temu/category" \
  -H "Content-Type: application/json" \
  -d '{
    "category_url": "https://www.temu.com/ca/mens-hats-caps-o3-800.html?opt_level=2&title=Men%27s%20Hats%20%26%20Caps",
    "min_sales": 1000,
    "crawl_details": true,
    "crawl_seller_products": true,
    "debug_port": 9222
  }'
```

### 方式2：通过API文档

1. 访问：http://localhost:8000/docs
2. 找到 `POST /api/crawl/temu/category` 端点
3. 填写参数并执行

### 方式3：直接调用函数

```python
from temu_category_crawler import crawl_temu_category_full_workflow

stats = crawl_temu_category_full_workflow(
    category_url="https://www.temu.com/ca/mens-hats-caps-o3-800.html?...",
    min_sales=1000,
    crawl_details=True,
    crawl_seller_products=True,
    debug_port=9222
)

print(f"统计信息: {stats}")
```

## 📊 数据流程

```
类目URL
  ↓
[步骤1] 保存类目信息到 temu_categories
  ↓
[步骤2] 爬取类目商品 → 筛选销量≥1000 → 保存到 temu_products
  ↓
[步骤3] 遍历商品 → 爬取详情页 → 提取mall_id → 保存到 temu_product_details 和 temu_sellers
  ↓
[步骤4] 遍历卖家 → 爬取店铺商品 → 保存到 temu_seller_products
  ↓
完成
```

## 🔍 关键特性

1. **销量筛选**：自动筛选销量大于等于指定值的爆款商品
2. **销量解析**：支持"100K+sold"、"1M+sold"等格式的销量文本解析
3. **去重机制**：使用goods_id避免重复爬取
4. **状态跟踪**：每个步骤都有状态跟踪
5. **错误处理**：完善的异常处理和日志记录
6. **浏览器复用**：支持使用已登录的浏览器

## 📝 注意事项

1. **销量解析**：
   - "100K+sold" → 100000
   - "1M+sold" → 1000000
   - 如果解析失败，sales_count为0

2. **商品ID提取**：
   - 从商品链接中提取：`/g-601099517407518.html` → `601099517407518`

3. **卖家ID提取**：
   - 从详情页链接或页面内容中提取mall_id

4. **浏览器配置**：
   - 推荐使用调试端口方式，保持登录状态
   - 确保Chrome浏览器以调试模式启动

## 🎯 使用场景

1. **市场调研**：分析某个类目的爆款商品
2. **竞品分析**：了解热门卖家的商品策略
3. **选品参考**：根据销量数据选择潜力商品
4. **数据挖掘**：收集商品和卖家数据进行分析

## 📈 性能优化建议

1. **批量处理**：商品详情爬取可以批量处理
2. **并发控制**：避免过于频繁的请求
3. **缓存机制**：已爬取的商品不再重复爬取
4. **增量更新**：只爬取新增或更新的商品

## 🐛 故障排除

### 问题1：销量解析失败
- 检查HTML结构是否变化
- 查看日志中的销量文本格式

### 问题2：找不到卖家链接
- 检查详情页是否正常加载
- 尝试手动访问商品详情页确认结构

### 问题3：数据库连接失败
- 确认MySQL服务正在运行
- 检查数据库配置是否正确

## 📚 相关文件

- `crawler_utils.py`: 爬虫核心函数
- `temu_db_utils.py`: 数据库操作函数
- `api_server.py`: API接口定义
- `TEMU_爬虫使用说明.md`: 浏览器配置说明

