# 🍪 业务Cookie管理功能

## 📖 功能概述

Chrome插件现在支持**业务导向的Cookie管理**，默认显示两个重要网站的Cookie信息，并支持一键复制功能。

## 🎯 支持的网站

### 1. 🛒 Temu (agentseller.temu.com)
- **功能**: 显示Temu卖家平台的Cookie
- **复制**: 一键复制所有Cookie字符串
- **预览**: 显示前3个Cookie的键值对

### 2. 🐱 跨境猫 (seller.kuajingmaihuo.com)  
- **功能**: 显示跨境猫平台的Cookie
- **复制**: 一键复制所有Cookie字符串
- **预览**: 显示前3个Cookie的键值对

### 3. 📧 MailID 提取
- **功能**: 自动从Temu Cookie中提取MailID
- **智能识别**: 自动查找包含mail、id、user等关键词的Cookie
- **复制**: 一键复制MailID值

## 🚀 使用方法

### 自动加载
插件启动时会自动加载两个网站的Cookie，无需手动操作。

### 复制功能
1. **复制完整Cookie**: 点击对应网站的"复制Cookie"按钮
2. **复制MailID**: 点击"复制Temu MailID"按钮
3. **状态提示**: 复制成功后会显示绿色提示信息

### 界面布局
```
🍪 业务Cookie
├── 🛒 Temu (agentseller.temu.com)
│   ├── Cookie数量: X
│   ├── Cookie预览 (前3个)
│   └── [复制Cookie] 按钮
├── 🐱 跨境猫 (seller.kuajingmaihuo.com)
│   ├── Cookie数量: X  
│   ├── Cookie预览 (前3个)
│   └── [复制Cookie] 按钮
└── 📧 MailID
    ├── Temu: [提取的MailID值]
    └── [复制Temu MailID] 按钮
```

## 🔧 技术实现

### 自动加载机制
```typescript
const loadBusinessCookies = async () => {
    // 加载Temu的Cookie
    const temuResponse = await sendToBackground({ 
        action: 'get_cookies_by_domain', 
        domain: 'https://agentseller.temu.com/' 
    });
    
    // 加载跨境猫的Cookie
    const kuajingResponse = await sendToBackground({ 
        action: 'get_cookies_by_domain', 
        domain: 'https://seller.kuajingmaihuo.com/' 
    });
};
```

### 复制功能
```typescript
const copyToClipboard = async (text: string, type: string) => {
    await navigator.clipboard.writeText(text);
    setCopyStatus(`${type}已复制到剪贴板`);
};
```

### Cookie格式化
```typescript
const formatCookiesForCopy = (cookies: CookieInfo[]): string => {
    return cookies.map(cookie => `${cookie.name}=${cookie.value}`).join('; ');
};
```

### MailID智能提取
```typescript
const getMailIdFromCookies = (cookies: CookieInfo[]): string => {
    const mailIdCookie = cookies.find(cookie => 
        cookie.name.toLowerCase().includes('mail') || 
        cookie.name.toLowerCase().includes('id') ||
        cookie.name.toLowerCase().includes('user')
    );
    return mailIdCookie ? mailIdCookie.value : '未找到MailID';
};
```

## 🎨 UI特性

### 视觉设计
- **卡片式布局**: 每个网站独立卡片显示
- **颜色区分**: 不同网站使用不同颜色主题
- **状态反馈**: 复制操作有明确的视觉反馈

### 响应式设计
- **紧凑布局**: 适合popup窗口的有限空间
- **滚动支持**: Cookie预览区域支持滚动
- **文本截断**: 长Cookie值自动截断显示

### 交互体验
- **悬停效果**: 按钮有悬停状态变化
- **动画效果**: 复制状态提示有淡入动画
- **即时反馈**: 操作结果立即显示

## 📊 数据格式

### Cookie信息结构
```typescript
interface CookieInfo {
    name: string;           // Cookie名称
    value: string;          // Cookie值
    domain: string;         // 所属域名
    path: string;           // 路径
    httpOnly: boolean;      // 是否HttpOnly
    secure: boolean;        // 是否Secure
    sameSite: string;       // SameSite设置
    expirationDate?: number; // 过期时间
}
```

### 复制格式示例
```
// 完整Cookie字符串
BAIDUID=BAD8F7E4C92C4B5F8F1234567890ABCD; BIDUPSID=1234567890ABCDEF1234567890ABCDEF; PSTM=1640995200

// MailID值
user123456@example.com
```

## 🔒 安全考虑

- **本地存储**: Cookie数据仅在本地处理，不上传到服务器
- **权限控制**: 仅访问指定域名的Cookie
- **数据保护**: 复制操作使用系统剪贴板，数据安全可控

## 🚀 扩展性

### 添加新网站
只需在`loadBusinessCookies`函数中添加新的域名即可：

```typescript
// 添加新网站
const newSiteResponse = await sendToBackground({ 
    action: 'get_cookies_by_domain', 
    domain: 'https://newsite.com/' 
});
```

### 自定义提取规则
可以修改`getMailIdFromCookies`函数来适应不同网站的ID提取规则。

## 📝 使用场景

1. **开发调试**: 快速获取测试环境的Cookie
2. **API测试**: 复制Cookie用于API请求测试
3. **身份验证**: 提取用户ID进行身份验证
4. **数据迁移**: 在不同环境间迁移用户会话

现在你可以轻松管理业务相关的Cookie，提高工作效率！🎉 