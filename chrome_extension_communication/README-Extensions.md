# Cookie工具和请求头管理 - 功能扩展文档

我已经为你的React+TypeScript Chrome插件项目添加了两个强大的工具类：**Cookie管理工具**和**请求头存储管理工具**。这些工具提供了完整的Cookie获取和请求头管理功能。

## 🍪 Cookie管理工具 (`src/utils/cookieUtils.ts`)

### 主要功能

#### 1. Cookie获取功能
```typescript
// 获取所有Cookie
const allCookies = await CookieUtils.getAllCookies();

// 根据域名获取Cookie
const domainCookies = await CookieUtils.getCookiesByDomain('baidu.com');

// 获取当前标签页Cookie
const currentTabCookies = await CookieUtils.getCurrentTabCookies();

// 批量获取多个域名的Cookie
const cookieMap = await CookieUtils.getCookiesByDomains(['google.com', 'baidu.com']);
```

#### 2. Cookie过滤和格式化
```typescript
// 过滤Cookie
const filteredCookies = CookieUtils.filterCookies(cookies, {
  domain: 'example.com',
  httpOnly: true,
  secure: true
});

// 转换为HTTP请求头格式
const cookieString = CookieUtils.cookiesToString(cookies);
// 输出: "sessionId=abc123; userId=456"

// 转换为对象格式
const cookieObject = CookieUtils.cookiesToObject(cookies);
// 输出: { sessionId: 'abc123', userId: '456' }
```

#### 3. Cookie统计和管理
```typescript
// 获取Cookie统计信息
const stats = CookieUtils.getCookieStatistics(cookies);
console.log(stats);
// 输出: { total: 50, httpOnly: 20, secure: 30, expired: 5, uniqueDomains: 8 }

// 检查Cookie是否过期
const isExpired = CookieUtils.isCookieExpired(cookie);

// 获取过期时间文本
const expirationText = CookieUtils.getCookieExpirationText(cookie);
```

#### 4. Cookie删除功能
```typescript
// 删除指定Cookie
const success = await CookieUtils.deleteCookie(url, cookieName);

// 清除域名下所有Cookie
const clearedCount = await CookieUtils.clearDomainCookies('example.com');
```

## 📨 请求头管理工具 (`src/utils/headersUtils.ts`)

### 主要功能

#### 1. 请求头基础管理
```typescript
// 获取所有存储的请求头
const headers = await HeadersUtils.getStoredHeaders();

// 添加新请求头
await HeadersUtils.addHeader({
  key: 'Authorization',
  value: 'Bearer token123',
  description: 'API认证令牌'
});

// 更新请求头
await HeadersUtils.updateHeader('Authorization', {
  value: 'Bearer newToken456'
});

// 切换请求头启用状态
await HeadersUtils.toggleHeader('Authorization');

// 删除请求头
await HeadersUtils.removeHeader('Authorization');
```

#### 2. 请求头分组管理
```typescript
// 创建请求头分组
const group = await HeadersUtils.createHeaderGroup('API测试', '用于API测试的请求头集合');

// 保存当前请求头为分组
const savedGroup = await HeadersUtils.saveCurrentHeadersAsGroup('生产环境配置');

// 加载请求头分组
await HeadersUtils.loadHeaderGroup(groupId);

// 删除请求头分组
await HeadersUtils.deleteHeaderGroup(groupId);
```

#### 3. 预设模板系统
```typescript
// 获取所有模板
const templates = HeadersUtils.getHeaderTemplates();

// 应用预设模板
await HeadersUtils.applyTemplate('基础认证');
await HeadersUtils.applyTemplate('内容类型');
await HeadersUtils.applyTemplate('用户代理');
```

#### 4. 导入导出功能
```typescript
// 导出请求头数据
const exportData = await HeadersUtils.exportHeaders();

// 导入请求头数据 (替换模式)
await HeadersUtils.importHeaders(jsonData, false);

// 导入请求头数据 (合并模式)
await HeadersUtils.importHeaders(jsonData, true);
```

## 🎨 UI界面功能

### Cookie管理界面

- **获取所有Cookie**: 一键获取浏览器中的所有Cookie
- **当前页面Cookie**: 获取当前活动标签页的Cookie
- **域名Cookie查询**: 输入域名获取特定网站的Cookie
- **Cookie详情显示**: 显示Cookie的名称、值、域名、路径、安全属性等信息

### 请求头管理界面

- **添加请求头**: 可添加自定义的HTTP请求头
- **启用/禁用切换**: 支持单独启用或禁用特定请求头
- **预设模板**: 提供常用的请求头模板（认证、内容类型、用户代理等）
- **配置导出**: 支持将当前配置导出为JSON文件
- **批量管理**: 支持清空所有配置

### 预设模板说明

1. **基础认证**: `Authorization`, `X-API-Key`
2. **内容类型**: `Content-Type`, `Accept`
3. **用户代理**: `User-Agent`, `Accept-Language`
4. **缓存控制**: `Cache-Control`, `Pragma`
5. **CORS相关**: `Access-Control-*` 系列头部
6. **移动端**: 移动设备的User-Agent和Accept头部

## 🔧 Background Script API扩展

我已经在`background.ts`中添加了完整的API支持：

### Cookie相关API
- `get_all_cookies`: 获取所有Cookie
- `get_cookies_by_domain`: 获取指定域名Cookie
- `get_current_tab_cookies`: 获取当前标签页Cookie
- `get_cookies_by_domains`: 批量获取多域名Cookie
- `clear_domain_cookies`: 清除域名Cookie

### 请求头相关API
- `get_stored_headers`: 获取存储的请求头
- `save_headers`: 保存请求头列表
- `add_header`: 添加单个请求头
- `remove_header`: 删除请求头
- `update_header`: 更新请求头
- `toggle_header`: 切换请求头状态
- `get_enabled_headers`: 获取启用的请求头
- `apply_header_template`: 应用预设模板
- `export_headers`: 导出配置
- `import_headers`: 导入配置
- `clear_headers_data`: 清除所有数据

## 🚀 使用示例

### 在React组件中获取Cookie

```typescript
const getAllCookies = async () => {
  try {
    const response = await sendToBackground({ action: 'get_all_cookies' });
    if (response.success && response.cookies) {
      setCookies(response.cookies);
      console.log(`获取到 ${response.cookies.length} 个Cookie`);
    }
  } catch (error) {
    console.error('获取Cookie失败:', error);
  }
};
```

### 在React组件中管理请求头

```typescript
const addNewHeader = async () => {
  try {
    const response = await sendToBackground({
      action: 'add_header',
      header: {
        key: 'Custom-Header',
        value: 'custom-value',
        description: '自定义请求头'
      }
    });
    
    if (response.success) {
      console.log('请求头已添加');
      await loadStoredHeaders(); // 重新加载列表
    }
  } catch (error) {
    console.error('添加请求头失败:', error);
  }
};
```

## 📊 数据格式说明

### Cookie数据格式
```typescript
interface CookieInfo {
  name: string;           // Cookie名称
  value: string;          // Cookie值
  domain: string;         // 域名
  path: string;           // 路径
  httpOnly: boolean;      // 是否HttpOnly
  secure: boolean;        // 是否需要HTTPS
  sameSite: SameSiteStatus; // SameSite属性
  expirationDate?: number;  // 过期时间戳
}
```

### 请求头数据格式
```typescript
interface HeaderKeyValue {
  key: string;            // 请求头名称
  value: string;          // 请求头值
  enabled: boolean;       // 是否启用
  description?: string;   // 描述信息
}
```

## 🔒 安全性考虑

1. **Cookie访问**: 只能访问当前用户浏览器中的Cookie，无法访问其他用户的数据
2. **域名限制**: Cookie获取遵循浏览器的同源策略
3. **权限控制**: 需要在manifest.json中声明`cookies`和`storage`权限
4. **数据存储**: 请求头数据存储在本地，不会上传到服务器

## 🎯 实际应用场景

### Cookie管理场景
- **调试网站登录状态**: 查看会话Cookie是否正确设置
- **分析第三方Cookie**: 检查广告追踪Cookie
- **清理过期Cookie**: 批量清除特定域名的Cookie
- **迁移用户状态**: 导出Cookie用于测试环境

### 请求头管理场景
- **API接口测试**: 设置认证头、内容类型等
- **爬虫开发**: 模拟不同浏览器的User-Agent
- **跨域调试**: 设置CORS相关头部
- **性能优化**: 设置缓存控制头部

## 📈 性能优化

1. **异步操作**: 所有Cookie和存储操作都是异步的
2. **批量处理**: 支持批量获取多个域名的Cookie
3. **缓存机制**: 请求头数据本地缓存，减少重复查询
4. **内存管理**: 限制显示的Cookie数量，避免界面卡顿

## 🎉 总结

这两个工具类为你的Chrome插件项目添加了强大的Cookie管理和请求头管理功能：

- **完整的功能集**: 涵盖了Cookie和请求头管理的各个方面
- **类型安全**: 完整的TypeScript类型定义
- **用户友好**: 直观的React界面，支持快速操作
- **高度可扩展**: 模块化设计，易于添加新功能
- **企业级质量**: 完善的错误处理和日志记录

你可以基于这些工具继续扩展更多功能，比如：
- Cookie的自动清理任务
- 请求头的自动应用规则
- 更多的预设模板
- 数据导入导出的高级选项

## 🔄 WebSocket API 扩展

在 `websocket_server.py` 中添加了请求头查询API：

### 查询API格式

```python
# 查询包含特定请求头的请求
{
  "type": "query_headers",
  "query_type": "by_name",
  "header_name": "Authorization",
  "header_value": "Bearer" # 可选
}

# 查询特定域名的请求
{
  "type": "query_headers", 
  "query_type": "by_domain",
  "domain": "api.example.com"
}

# 获取统计信息
{
  "type": "query_headers",
  "query_type": "statistics"
}

# 获取所有请求
{
  "type": "query_headers",
  "query_type": "all"
}
```

### 响应格式

```python
{
  "type": "header_query_result",
  "query_type": "by_name",
  "header_name": "Authorization", 
  "message": "查询包含请求头 'Authorization' 的请求",
  "instructions": "请在Chrome插件中使用'搜索'功能查看结果"
}
```

这样你就可以通过WebSocket从Python后端直接查询Chrome插件拦截到的请求头数据了！

现在你的Chrome插件项目不仅具备了WebSocket通信功能，还拥有了专业级的Cookie管理和请求头拦截能力！🚀