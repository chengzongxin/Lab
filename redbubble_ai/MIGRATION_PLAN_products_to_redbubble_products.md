# 📋 数据库表重命名评估报告

## 🎯 目标

将 `products` 表重命名为 `redbubble_products`，因为该表实际存储的是 Redbubble 商品数据。

## 📊 影响范围评估

### 1. **数据库层面** (需修改)

#### 文件：`backend/api_server.py`
- **行 115-125**: 创建 `products` 表
- **行 876**: 查询 `products` 表（带 category 过滤）
- **行 878**: 查询 `products` 表（全部）
- **行 1126**: 统计 `products` 表总数
- **行 1130**: 计算 `products` 表平均分数
- **行 1134**: 统计 `products` 表高分商品
- **行 1158**: 删除 `products` 表所有数据

#### 文件：`backend/download_utils.py`
- **行 244-253**: 创建 `products` 表
- **行 261**: 插入 `products` 表

#### 文件：`backend/temu_ai_workflow.py`
- **行 140**: 查询 `products` 表检查是否存在
- **行 149**: 插入 `products` 表

### 2. **API 端点层面** (保持不变或可选调整)

#### 当前端点：
- `GET /api/products` - 获取 Redbubble 商品列表
- `DELETE /api/products` - 清空所有商品数据

#### 建议：
**保持端点名称不变**，只修改后端 SQL 查询。前端无需改动。

### 3. **前端层面** (无需改动)

前端只调用 API 端点，不直接涉及表名：
- `frontend/src/components/RedbubblePage.tsx` - 调用 `/api/products`
- `frontend/src/components/CrawlerControl.tsx` - 调用 `/api/products` (DELETE)
- `frontend/src/App.tsx` - 调用 `/api/products`

✅ **前端无需任何改动**

### 4. **文档层面** (需更新)

- `backend/README.md` - 数据库表结构说明
- `README.md` - API 文档
- 其他相关文档

---

## ✅ 改造方案

### 方案选择：**渐进式改造**

1. ✅ **修改所有 SQL 语句**：将 `products` 改为 `redbubble_products`
2. ✅ **保持 API 端点不变**：`/api/products` 继续使用
3. ✅ **前端零改动**：完全不需要修改前端代码
4. ✅ **数据迁移**：提供 SQL 脚本迁移现有数据

---

## 🔧 具体改动清单

### **数据库改动** (7个文件，约15处)

#### 1. `backend/api_server.py` (8处)
- [ ] 行 113: 注释改为"创建商品表（Redbubble）"
- [ ] 行 115: `CREATE TABLE IF NOT EXISTS redbubble_products`
- [ ] 行 876: `SELECT ... FROM redbubble_products WHERE`
- [ ] 行 878: `SELECT ... FROM redbubble_products ORDER BY`
- [ ] 行 1126: `SELECT COUNT(*) FROM redbubble_products`
- [ ] 行 1130: `SELECT AVG(score) FROM redbubble_products WHERE`
- [ ] 行 1134: `SELECT COUNT(*) FROM redbubble_products WHERE`
- [ ] 行 1158: `DELETE FROM redbubble_products`

#### 2. `backend/download_utils.py` (2处)
- [ ] 行 242: 注释改为"创建redbubble_products表"
- [ ] 行 244: `CREATE TABLE IF NOT EXISTS redbubble_products`
- [ ] 行 261: `INSERT INTO redbubble_products`

#### 3. `backend/temu_ai_workflow.py` (2处)
- [ ] 行 140: `SELECT id FROM redbubble_products WHERE`
- [ ] 行 149: `INSERT INTO redbubble_products`

---

## 📝 数据迁移 SQL

```sql
-- 方案1: 重命名表（推荐，保留现有数据）
RENAME TABLE products TO redbubble_products;

-- 方案2: 创建新表并迁移数据
CREATE TABLE redbubble_products LIKE products;
INSERT INTO redbubble_products SELECT * FROM products;
-- 确认数据无误后
DROP TABLE products;
```

---

## ⚠️ 风险评估

| 风险 | 等级 | 缓解措施 |
|------|------|----------|
| 数据丢失 | 🟡 中 | 执行前备份数据库 |
| API 中断 | 🟢 低 | API 端点保持不变 |
| 前端报错 | 🟢 极低 | 前端不涉及表名 |
| 回滚困难 | 🟢 低 | 保留旧表备份 |

---

## 🎯 执行步骤

### 步骤1: 备份数据库（重要！）
```bash
mysqldump -u root -p redbubble_ai products > products_backup.sql
```

### 步骤2: 重命名数据库表
```sql
USE redbubble_ai;
RENAME TABLE products TO redbubble_products;
```

### 步骤3: 修改代码
- 修改 `backend/api_server.py`
- 修改 `backend/download_utils.py`
- 修改 `backend/temu_ai_workflow.py`

### 步骤4: 测试验证
```bash
# 重启后端
cd backend
python api_server.py

# 测试 API
curl http://localhost:8000/api/products
```

### 步骤5: 回滚方案（如需要）
```sql
RENAME TABLE redbubble_products TO products;
# 恢复代码到之前版本
```

---

## 📈 预期收益

1. ✅ **语义更清晰**：表名明确表示存储的是 Redbubble 商品
2. ✅ **避免混淆**：与 `temu_products`、`temu_seller_products` 形成统一命名规范
3. ✅ **易于维护**：新开发者更容易理解数据库结构
4. ✅ **零前端影响**：前端完全不受影响

---

## 🚀 执行建议

**推荐执行时间**：开发环境测试通过后，选择业务低峰期执行

**总工时估算**：
- 代码修改：30分钟
- 测试验证：30分钟
- 数据迁移：5分钟
- **总计**：约1小时

**难度评级**：⭐⭐☆☆☆（较简单）

---

## ✅ 结论

**评估结果**：✅ **改造可行且风险低**

- 影响范围明确（3个后端文件，约12处修改）
- 前端零改动
- 数据迁移简单（一条 RENAME 语句）
- 回滚方案清晰

**建议立即执行改造！**

