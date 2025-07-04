# 批量下架多线程优化

## 功能概述

为了提高批量下架商品的处理速度，我们实现了多线程并发处理功能。通过使用线程池，可以同时处理多个商品的下架操作，显著提升处理效率。

## 主要特性

### 1. 智能线程管理
- **动态线程数调整**：根据商品数量和用户设置自动调整线程数
- **最大线程限制**：默认最大8个线程，避免过度并发
- **线程池管理**：使用 `ThreadPoolExecutor` 进行线程管理

### 2. 缓存优化
- **parentMsgId 缓存**：避免每次都重新获取对话ID
- **toolId 缓存**：缓存商品下架工具ID
- **缓存过期机制**：24小时自动过期，确保数据有效性

### 3. 错误处理
- **异常隔离**：单个商品处理失败不影响其他商品
- **详细错误信息**：提供具体的错误原因和处理状态
- **线程安全**：确保多线程环境下的数据一致性

## API 接口

### 批量下架接口

```http
POST /api/temu/seller/offline
Content-Type: application/json

{
  "productIds": [123456, 789012, 345678],
  "max_threads": 8
}
```

#### 参数说明
- `productIds`: 商品ID列表（必需）
- `max_threads`: 最大线程数（可选，默认8）

#### 返回示例

```json
{
  "success": true,
  "message": "批量下架完成，共处理 3 个商品，2 个下架成功",
  "parentMsgId": "448421445119357",
  "toolId": "2406230000031",
  "cacheUsed": true,
  "threadInfo": {
    "maxThreads": 8,
    "actualThreads": 3,
    "productCount": 3
  },
  "results": [
    {
      "productId": 123456,
      "success": true,
      "message": "下架成功",
      "details": {
        "productName": "商品名称",
        "productImg": "图片URL",
        "offlineMsgId": "消息ID",
        "retryCount": 2
      }
    }
  ],
  "summary": {
    "total": 3,
    "success": 2,
    "failed": 1
  }
}
```

## 性能优化建议

### 1. 线程数配置
- **少量商品（1-4个）**：建议使用 2-4 个线程
- **中等数量（5-10个）**：建议使用 4-6 个线程
- **大量商品（10+个）**：建议使用 6-8 个线程

### 2. 网络环境考虑
- **网络较慢**：减少线程数，避免请求超时
- **网络稳定**：可以适当增加线程数
- **服务器负载**：根据服务器性能调整线程数

### 3. 缓存策略
- **首次使用**：会自动获取并缓存必要信息
- **后续使用**：直接使用缓存，大幅提升速度
- **配置更改**：会自动清除缓存并重新获取

## 使用示例

### 前端调用示例

```javascript
// 单个商品下架
const res = await fetch("/api/temu/seller/offline", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ 
    productIds: [123456],
    max_threads: 4
  }),
});

// 批量下架
const res = await fetch("/api/temu/seller/offline", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({ 
    productIds: [123456, 789012, 345678],
    max_threads: 8
  }),
});
```

### 性能测试

运行性能测试脚本：

```bash
cd backend
python test_performance.py
```

测试脚本会对比不同线程数的性能表现，并给出推荐配置。

## 注意事项

1. **请求频率限制**：虽然使用多线程，但仍需注意API的请求频率限制
2. **内存使用**：大量并发可能增加内存使用，建议监控系统资源
3. **错误处理**：单个商品失败不会影响整体流程，但需要关注错误日志
4. **缓存管理**：定期检查缓存有效性，必要时手动清除缓存

## 故障排除

### 常见问题

1. **线程数过多导致超时**
   - 解决方案：减少 `max_threads` 参数

2. **缓存失效**
   - 解决方案：检查配置文件，重新获取缓存

3. **部分商品处理失败**
   - 解决方案：查看详细错误信息，针对性处理

### 调试信息

接口返回的 `threadInfo` 字段包含详细的线程使用信息，可用于性能分析和问题诊断。

## 更新日志

- **v1.0.0**: 初始版本，支持基本的多线程处理
- **v1.1.0**: 添加缓存优化，提升处理速度
- **v1.2.0**: 增加线程数配置，支持动态调整 