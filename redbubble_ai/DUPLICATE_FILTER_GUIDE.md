# 🔄 重复过滤功能使用指南

## 📖 功能介绍

自动检测并跳过已经爬取过的店铺和类目，避免重复爬取浪费时间和资源。

---

## 🎯 功能特性

### 1. **TEMU卖家店铺过滤** 🏪

- ✅ 自动检测 `mall_id` 是否已存在
- ✅ 显示店铺已有商品数量
- ✅ 显示上次爬取时间
- ✅ 跳过已存在的店铺，继续处理下一个

### 2. **TEMU类目过滤** 📦

- ✅ 自动检测类目URL是否已爬取
- ✅ 显示类目已有商品数量
- ✅ 显示上次爬取时间
- ✅ 跳过已存在的类目，继续处理下一个

---

## 💡 工作原理

### TEMU卖家店铺过滤

```
用户输入店铺URL
    ↓
提取 mall_id
    ↓
查询数据库：SELECT COUNT(*) FROM temu_products WHERE mall_id = ?
    ↓
判断是否存在
    ├─ 是 → ⏭️ 跳过，显示已有商品数量
    └─ 否 → 🚀 开始爬取
```

**数据库检查SQL**：
```sql
SELECT COUNT(DISTINCT goods_id) as product_count, 
       MAX(created_at) as last_crawl_time
FROM temu_products 
WHERE mall_id = '634418212334809'
```

---

### TEMU类目过滤

```
用户输入类目URL
    ↓
生成 URL Hash (MD5)
    ↓
查询数据库：SELECT * FROM temu_categories WHERE category_url_hash = ?
    ↓
判断是否存在
    ├─ 是 → ⏭️ 跳过，显示已有商品数量
    └─ 否 → 🚀 开始爬取
```

**数据库检查SQL**：
```sql
SELECT 
    id,
    category_name,
    total_products,
    status,
    created_at,
    updated_at
FROM temu_categories 
WHERE category_url_hash = MD5('类目URL')
```

---

## 🚀 使用示例

### 示例1：批量爬取多个店铺（有重复）

**输入**：
```
https://www.temu.com/mall.html?mall_id=634418212334809  ← 新店铺
https://www.temu.com/mall.html?mall_id=123456789  ← 已存在
https://www.temu.com/mall.html?mall_id=987654321  ← 新店铺
```

**输出**：
```
[1/3] 正在处理: https://www.temu.com/mall.html?mall_id=634418212334809
✅ [1/3] 成功爬取50个商品，保存到数据库！

[2/3] 正在处理: https://www.temu.com/mall.html?mall_id=123456789
⏭️ [2/3] 跳过（店铺ID: 123456789）
   └─ 店铺已存在！该店铺已有 120 个商品，上次爬取时间: 2025-11-27 10:30:00

[3/3] 正在处理: https://www.temu.com/mall.html?mall_id=987654321
✅ [3/3] 成功爬取80个商品，保存到数据库！

🎉 批量爬取完成！
   成功: 2 | 跳过: 1 | 失败: 0 | 总计: 3
```

---

### 示例2：批量爬取多个类目（有重复）

**输入**：
```
https://www.temu.com/channel/women-clothing.html  ← 新类目
https://www.temu.com/channel/men-shoes.html       ← 已存在
```

**输出**：
```
[1/2] 正在处理: https://www.temu.com/channel/women-clothing.html
✅ [1/2] 成功爬取200个商品

[2/2] 正在处理: https://www.temu.com/channel/men-shoes.html
⏭️ [2/2] 跳过（类目已存在）
   └─ 类目已存在！该类目已有 350 个商品，上次爬取时间: 2025-11-26 15:20:00

🎉 批量爬取完成！
   成功: 1 | 跳过: 1 | 失败: 0 | 总计: 2
```

---

## 📊 前端显示效果

### 成功爬取
```
✅ [1/3] 成功爬取50个商品，保存到数据库！
```

### 跳过（店铺已存在）
```
⏭️ [2/3] 跳过（店铺ID: 123456789）
   └─ 店铺已存在！该店铺已有 120 个商品，上次爬取时间: 2025-11-27 10:30:00
```

### 跳过（类目已存在）
```
⏭️ [2/3] 跳过（类目已存在）
   └─ 类目已存在！该类目已有 350 个商品，上次爬取时间: 2025-11-26 15:20:00
```

### 最终统计
```
🎉 批量爬取完成！
   成功: 2 | 跳过: 1 | 失败: 0 | 总计: 3
```

---

## 🔧 技术实现

### 后端实现（api_server.py）

#### 店铺检查代码
```python
# 检查店铺是否已存在
conn = get_db_conn()
cursor = conn.cursor()
cursor.execute("""
    SELECT COUNT(DISTINCT goods_id) as product_count, 
           MAX(created_at) as last_crawl_time
    FROM temu_products 
    WHERE mall_id = %s
""", (request.mall_id,))
result = cursor.fetchone()

if result and result[0] > 0:
    # 店铺已存在，返回跳过信息
    return {
        "success": False,
        "skipped": True,
        "message": f"店铺已存在！该店铺已有 {product_count} 个商品",
        "mall_id": request.mall_id,
        "existing_products": product_count,
        "last_crawl_time": str(last_crawl_time)
    }
```

#### 类目检查代码
```python
# 生成URL哈希
import hashlib
category_url_hash = hashlib.md5(request.category_url.encode()).hexdigest()

# 检查类目是否已存在
cursor.execute("""
    SELECT id, category_name, total_products, updated_at
    FROM temu_categories 
    WHERE category_url_hash = %s
""", (category_url_hash,))
existing_category = cursor.fetchone()

if existing_category:
    # 类目已存在，返回跳过信息
    return {
        "success": False,
        "skipped": True,
        "message": f"类目已存在！该类目已有 {product_count} 个商品",
        # ...
    }
```

---

### 前端实现（TemuSellerCrawler.tsx / TemuCategoryCrawler.tsx）

```typescript
// 处理跳过的店铺（已存在）
if (response.data.skipped) {
  const skipMsg = `⏭️ [${currentIndex}/${urls.length}] 跳过（店铺ID: ${mallId}）\n   └─ ${response.data.message}`;
  setProgressLogs(prev => [...prev, skipMsg]);
  skippedCount++;
} else if (response.data.success) {
  // 成功爬取
  successCount++;
} else {
  // 失败
  failCount++;
}
```

---

## 🎓 优势与好处

### ✅ 节省时间
- 避免重复爬取已有店铺/类目
- 批量处理时自动跳过重复项
- 专注于新数据的获取

### ✅ 节省资源
- 减少网络请求
- 降低服务器负载
- 避免触发反爬机制

### ✅ 数据清晰
- 清楚知道哪些是新数据
- 清楚知道哪些已存在
- 统计信息一目了然

### ✅ 用户体验
- 实时反馈跳过原因
- 显示已有数据情况
- 批量处理更智能

---

## 🤔 常见问题

### Q1: 如果我想重新爬取已存在的店铺怎么办？

**方法1：删除店铺数据**
```sql
-- 删除指定店铺的所有商品
DELETE FROM temu_products WHERE mall_id = '123456789';
```

**方法2：删除后重新爬取**
1. 在AI工作流页面手动删除店铺商品
2. 重新在卖家爬取页面输入店铺URL
3. 系统会检测到店铺不存在，开始爬取

---

### Q2: 如果店铺商品有更新，我想重新爬取怎么办？

**建议**：
- 定期清理旧数据
- 或者修改代码，添加"强制重新爬取"选项

**未来改进方向**：
- 添加"强制重新爬取"复选框
- 或者根据时间间隔自动重新爬取（如：超过7天自动重新爬取）

---

### Q3: 跳过的店铺/类目会影响统计吗？

**不会！** 统计信息会清晰显示：
- ✅ 成功爬取的数量
- ⏭️ 跳过的数量
- ❌ 失败的数量
- 📊 总计数量

---

### Q4: 如何查看已存在的店铺/类目列表？

**查看所有店铺**：
```sql
SELECT 
    mall_id,
    COUNT(DISTINCT goods_id) as product_count,
    MAX(created_at) as last_crawl_time
FROM temu_products
GROUP BY mall_id
ORDER BY last_crawl_time DESC;
```

**查看所有类目**：
```sql
SELECT 
    category_name,
    category_url,
    total_products,
    status,
    created_at,
    updated_at
FROM temu_categories
ORDER BY updated_at DESC;
```

---

## 🚀 未来增强功能

### 计划中的功能：

1. **强制重新爬取选项** ✨
   - 添加"忽略已存在检查"复选框
   - 即使店铺/类目存在也强制爬取

2. **智能更新策略** 🧠
   - 检测数据时间，超过N天自动重新爬取
   - 增量更新（只爬取新商品）

3. **可视化管理界面** 📊
   - 显示所有已爬取的店铺/类目列表
   - 可以选择删除或重新爬取

4. **爬取历史记录** 📝
   - 记录每次爬取的详细信息
   - 查看爬取历史和统计

---

## ✅ 总结

重复过滤功能：
- ✅ 自动检测重复店铺和类目
- ✅ 智能跳过已存在的数据
- ✅ 清晰的进度反馈
- ✅ 完整的统计信息
- ✅ 节省时间和资源

**使用建议**：
- 批量爬取前，不用担心重复
- 系统会自动处理重复项
- 专注于收集新数据
- 定期清理过时数据

**开心爬取，不怕重复！** 🎉

