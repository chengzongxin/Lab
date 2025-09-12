# Excel商品名称处理工具

这是一个用于处理Excel文件中商品名称的Python脚本，可以根据正则表达式匹配特定的商品模式并进行重命名。

## 功能特点

- 🔍 **智能匹配**：使用正则表达式匹配包含数字+Drawstring的商品名称
- ✏️ **自动重命名**：在匹配的数字后添加"th"后缀
- 📅 **时间命名**：输出文件以时间戳命名，避免覆盖
- 📊 **详细统计**：显示处理前后的数据统计信息
- 🎯 **示例数据**：内置示例Excel文件用于测试

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 方法1：处理现有Excel文件
```bash
python excel_processor.py your_file.xlsx
```

### 方法2：使用示例文件测试
```bash
python excel_processor.py
```

## 匹配规则

脚本会匹配以下模式的商品名称：
- 包含数字（如：1, 2, 3, 4, 5, 6等）
- 数字后面紧跟"Drawstring"（不区分大小写）

**示例匹配：**
- ✅ `Fishes 3 Drawstring Bags` → `Fishes 3th Drawstring Bags`
- ✅ `Cats 5 Drawstring Bags` → `Cats 5th Drawstring Bags`
- ✅ `Dogs 2 Drawstring Bags` → `Dogs 2th Drawstring Bags`
- ❌ `Regular T-Shirt` (不匹配)
- ❌ `Normal Backpack` (不匹配)

## 输出文件

处理后的文件将保存为：`processed_products_YYYYMMDD_HHMMSS.xlsx`

## 注意事项

- 确保Excel文件的第一列包含商品名称
- 脚本会保留所有匹配的行，包括其他列的数据
- 如果文件不存在或为空，脚本会显示相应的错误信息
