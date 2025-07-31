# 🔍 Temu MailID 实时检测功能

## 📖 功能概述

Chrome插件现在支持**实时检测Temu域名请求中的MailID**，当页面进行网络请求时，自动解析请求头中的MailID字段并在popup中显示。

## 🎯 检测机制

### 触发条件
- **域名匹配**: 请求URL包含 `temu.com`
- **请求头检测**: 自动查找包含以下关键词的请求头：
  - `mailid`
  - `mail-id` 
  - `mail_id`
  - `userid`
  - `user-id`
  - `user_id`

### 实时通知
- **Background监听**: 在background script中实时监听网络请求
- **Popup显示**: 检测到MailID后立即通知popup显示
- **消息记录**: 在消息区域显示检测到的MailID

## 🚀 使用方法

### 1. 启动检测
1. 打开Chrome插件popup
2. 点击"开始拦截"按钮
3. 访问任何Temu相关网站
4. 当页面发起包含MailID的请求时，插件会自动检测并显示

### 2. 查看结果
- **实时显示**: 检测到的MailID会立即显示在popup中
- **历史记录**: 保留最近10个不同的MailID记录
- **详细信息**: 显示域名、时间戳和完整URL

### 3. 复制功能
- **单个复制**: 点击每个MailID记录旁的"复制"按钮
- **状态反馈**: 复制成功后会显示绿色提示信息

## 🔧 技术实现

### Background Script 检测逻辑
```typescript
// 检查是否是temu.com域名的请求，并提取MailID
if (domain.includes('temu.com')) {
  const mailIdHeader = headers.find(header => 
    header.name.toLowerCase().includes('mailid') ||
    header.name.toLowerCase().includes('mail-id') ||
    header.name.toLowerCase().includes('mail_id') ||
    header.name.toLowerCase().includes('userid') ||
    header.name.toLowerCase().includes('user-id') ||
    header.name.toLowerCase().includes('user_id')
  );
  
  if (mailIdHeader && mailIdHeader.value) {
    // 通知popup显示MailID
    chrome.runtime.sendMessage({
      type: 'temu_mailid_detected',
      mailId: mailIdHeader.value,
      domain: domain,
      timestamp: timestamp,
      url: details.url
    });
  }
}
```

### Popup 监听处理
```typescript
const setupTemuMailIdListener = () => {
  chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.type === 'temu_mailid_detected') {
      // 添加到状态中，避免重复
      setTemuRequestMailIds(prev => {
        const exists = prev.some(item => item.mailId === message.mailId);
        if (!exists) {
          return [newMailId, ...prev.slice(0, 9)]; // 保留最近10个
        }
        return prev;
      });
      
      // 显示消息
      addMessage(`发现Temu MailID: ${message.mailId}`, 'received');
    }
  });
};
```

## 🎨 界面特性

### 显示区域
```
🔍 Temu请求头MailID
├── [清除] 按钮
└── MailID列表
    ├── user123@example.com
    │   agentseller.temu.com | 14:30:25
    │   [复制] 按钮
    ├── user456@example.com  
    │   api.temu.com | 14:32:15
    │   [复制] 按钮
    └── ...
```

### 视觉设计
- **独立卡片**: 只在检测到MailID时显示
- **时间信息**: 显示检测时间和域名
- **复制按钮**: 每个MailID都有独立的复制按钮
- **清除功能**: 一键清除所有历史记录

## 📊 数据格式

### 检测到的MailID信息
```typescript
interface TemuMailIdInfo {
  mailId: string;      // MailID值
  domain: string;      // 请求域名
  timestamp: string;   // 检测时间戳
  url: string;         // 完整请求URL
}
```

### 消息格式
```typescript
// Background发送给Popup的消息
{
  type: 'temu_mailid_detected',
  mailId: 'user123@example.com',
  domain: 'agentseller.temu.com',
  timestamp: '2024-01-15T14:30:25.123Z',
  url: 'https://agentseller.temu.com/api/user/info'
}
```

## 🔒 安全考虑

- **本地处理**: 所有检测和处理都在本地进行
- **数据保护**: MailID信息不会上传到任何服务器
- **权限控制**: 仅监听网络请求，不修改请求内容
- **隐私保护**: 检测到的数据仅在插件内部使用

## 🚀 应用场景

1. **开发调试**: 快速获取Temu API请求中的用户ID
2. **API测试**: 复制MailID用于API接口测试
3. **用户追踪**: 监控特定用户的请求活动
4. **数据分析**: 收集用户ID用于数据分析

## ⚡ 性能优化

- **智能过滤**: 只检测temu.com域名的请求
- **去重机制**: 避免重复显示相同的MailID
- **数量限制**: 最多保留10个历史记录
- **异步处理**: 不阻塞网络请求的正常进行

## 🔧 扩展性

### 添加新域名
修改background.ts中的域名检测条件：
```typescript
if (domain.includes('temu.com') || domain.includes('newsite.com')) {
  // 检测逻辑
}
```

### 自定义关键词
修改请求头检测的关键词：
```typescript
const mailIdHeader = headers.find(header => 
  header.name.toLowerCase().includes('customid') ||
  header.name.toLowerCase().includes('userid')
);
```

现在你可以实时监控Temu网站的MailID，提高开发和调试效率！🎉 