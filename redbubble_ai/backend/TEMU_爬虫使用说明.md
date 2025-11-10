# TEMU 爬虫使用说明

## 问题：需要登录

TEMU网站需要登录才能访问某些内容。为了解决这个问题，我们提供了两种方式：

## 方式1：使用调试端口（推荐）⭐

连接到已经打开并登录的浏览器，这样就不需要每次都登录了。

### 步骤：

1. **打开Chrome浏览器（已登录TEMU）**

2. **以调试模式启动Chrome**：
   ```bash
   # macOS/Linux
   /Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="/tmp/chrome_debug"
   
   # Windows
   "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\temp\chrome_debug"
   ```

3. **在打开的Chrome浏览器中登录TEMU**

4. **调用API时指定调试端口**：
   ```bash
   curl -X POST "http://localhost:8000/api/crawl/temu" \
     -H "Content-Type: application/json" \
     -d '{
       "mall_id": "23225409861",
       "max_pages": 10,
       "debug_port": 9222
     }'
   ```

   或者在API文档中：
   - `mall_id`: "23225409861"
   - `max_pages`: 10
   - `debug_port`: 9222
   - `use_persistent_context`: false
   - `user_data_dir`: null

### 优点：
- ✅ 使用你已经登录的浏览器
- ✅ 不需要额外配置
- ✅ 可以手动操作浏览器（如果需要）

### 注意事项：
- 确保Chrome浏览器在调用API时保持打开状态
- 调试端口默认是9222，可以改为其他端口（如9223, 9224等）

---

## 方式2：使用持久化上下文

使用持久化的用户数据目录，浏览器会自动保存登录状态。

### 步骤：

1. **第一次使用**：
   ```bash
   curl -X POST "http://localhost:8000/api/crawl/temu" \
     -H "Content-Type: application/json" \
     -d '{
       "mall_id": "23225409861",
       "max_pages": 10,
       "use_persistent_context": true,
       "user_data_dir": "/path/to/browser/data"
     }'
   ```

2. **浏览器会自动打开，手动登录TEMU**

3. **关闭浏览器后，下次使用相同的`user_data_dir`，会自动保持登录状态**

### 优点：
- ✅ 自动保存登录状态
- ✅ 不需要每次都手动登录

### 注意事项：
- 第一次需要手动登录
- 需要指定一个固定的`user_data_dir`路径
- 如果不指定`user_data_dir`，会使用临时目录（每次都会丢失登录状态）

---

## 快速开始（推荐方式1）

### 1. 打开Chrome调试模式

**macOS:**
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 --user-data-dir="/tmp/chrome_debug"
```

**Windows:**
```bash
"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222 --user-data-dir="C:\temp\chrome_debug"
```

### 2. 在打开的Chrome中登录TEMU

访问 https://www.temu.com 并登录你的账号

### 3. 调用API

```bash
curl -X POST "http://localhost:8000/api/crawl/temu" \
  -H "Content-Type: application/json" \
  -d '{
    "mall_id": "23225409861",
    "max_pages": 10,
    "debug_port": 9222
  }'
```

### 4. 查看结果

访问 http://localhost:8000/api/products?category=temu 查看爬取的商品

---

## 参数说明

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `mall_id` | string | ✅ | TEMU店铺ID（从URL中提取） |
| `max_pages` | int | ❌ | 最大爬取页数（默认10，最大20） |
| `debug_port` | int | ❌ | 调试端口（连接到已打开的浏览器） |
| `use_persistent_context` | bool | ❌ | 是否使用持久化上下文（默认false） |
| `user_data_dir` | string | ❌ | 用户数据目录路径（仅在使用持久化上下文时需要） |

---

## 如何获取店铺ID

从TEMU店铺URL中提取`mall_id`参数：

```
https://www.temu.com/mall.html?mall_id=23225409861&...
                                    ↑
                                这就是店铺ID
```

---

## 常见问题

### Q: 连接调试端口失败怎么办？

A: 确保：
1. Chrome浏览器已经以调试模式启动
2. 调试端口号正确（默认9222）
3. 浏览器没有关闭

### Q: 使用持久化上下文后，还是需要登录？

A: 第一次使用需要登录，之后会自动保持登录状态。确保每次都使用相同的`user_data_dir`。

### Q: 可以同时使用两种方式吗？

A: 不可以。如果指定了`debug_port`，会优先使用调试端口方式。

---

## 技术说明

### 调试端口方式（connect_over_cdp）
- 使用Chrome DevTools Protocol (CDP)
- 连接到已存在的浏览器实例
- 共享浏览器的所有状态（包括登录状态）

### 持久化上下文方式（launch_persistent_context）
- 使用用户数据目录保存浏览器状态
- 自动保存cookies、localStorage等
- 下次启动时自动恢复状态


