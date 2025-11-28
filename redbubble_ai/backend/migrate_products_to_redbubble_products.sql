-- ======================================
-- 数据表重命名迁移脚本
-- 目标：将 products 表重命名为 redbubble_products
-- 日期：2025-11-28
-- ======================================

USE redbubble_ai;

-- 步骤1：备份现有数据（可选，建议在执行前先用 mysqldump 备份整个数据库）
-- mysqldump -u root -p redbubble_ai products > products_backup_20251128.sql

-- 步骤2：检查表是否存在
SELECT 
    TABLE_NAME,
    TABLE_ROWS,
    CREATE_TIME,
    UPDATE_TIME
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'redbubble_ai' 
  AND TABLE_NAME = 'products';

-- 步骤3：重命名表（推荐方式，速度快，保留所有数据和索引）
RENAME TABLE products TO redbubble_products;

-- 步骤4：验证表已成功重命名
SELECT 
    TABLE_NAME,
    TABLE_ROWS,
    CREATE_TIME,
    UPDATE_TIME
FROM information_schema.TABLES 
WHERE TABLE_SCHEMA = 'redbubble_ai' 
  AND TABLE_NAME = 'redbubble_products';

-- 步骤5：验证数据完整性
SELECT COUNT(*) as total_products FROM redbubble_products;
SELECT * FROM redbubble_products LIMIT 5;

-- ======================================
-- 回滚脚本（如需要恢复）
-- ======================================
-- RENAME TABLE redbubble_products TO products;

-- ======================================
-- 说明
-- ======================================
-- 1. RENAME TABLE 操作是原子性的，非常快速且安全
-- 2. 不会复制数据，只是修改元数据
-- 3. 所有索引、约束、触发器等都会保留
-- 4. 执行前建议先备份数据库
-- 5. 如果遇到外键约束，需要先处理外键引用

-- ======================================
-- 检查是否有外键引用
-- ======================================
SELECT 
    CONSTRAINT_NAME,
    TABLE_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE REFERENCED_TABLE_NAME = 'products'
  AND TABLE_SCHEMA = 'redbubble_ai';

-- 如果有外键引用，需要先删除外键，重命名后再重新创建
-- 示例：
-- ALTER TABLE temu_redbubble_matches DROP FOREIGN KEY fk_products;
-- RENAME TABLE products TO redbubble_products;
-- ALTER TABLE temu_redbubble_matches ADD CONSTRAINT fk_redbubble_products 
--   FOREIGN KEY (product_id) REFERENCES redbubble_products(id);

