# 🚀 Chrome插件后端命令系统

## 📖 概述

这个系统实现了**非阻塞WebSocket服务器**，支持从Python后端主动向Chrome插件发送命令，获取Cookie和请求头数据。

## 🔧 系统架构

```
Python后端 ←→ WebSocket服务器 ←→ Chrome插件
    ↓              ↓                 ↓
命令行界面    非阻塞监听         拦截网络请求
```

## 🚀 启动步骤

### 1. 启动WebSocket服务器

```bash
python websocket_server.py
```

你会看到：
```
🚀 WebSocket服务器启动中...
📡 监听地址: ws://localhost:8765
✅ WebSocket服务器已在后台启动

============================================================
🎮 Chrome插件后端控制台
============================================================
可用命令:
  1. cookie <域名>          - 获取指定域名的Cookie
  2. requests <域名>        - 获取指定域名的拦截请求
  3. header <请求头名称>     - 查询包含指定请求头的请求
  4. status                - 查看连接状态
  5. quit/exit             - 退出程序
============================================================

💬 请输入命令:
```

### 2. 启动Chrome插件

1. 在Chrome插件中点击"连接服务器"
2. 确保请求拦截功能已开启

## 📝 使用示例

### 获取域名Cookie

```bash
💬 请输入命令: cookie baidu.com

🍪 获取域名 'baidu.com' 的Cookie...
📤 发送命令: get_cookies_by_domain
⏳ 等待插件响应...
✅ 收到响应:
📊 找到 15 个Cookie:
  - BAIDUID: BAD8F7E4C92C4B5F8F1234567890ABCD...
  - BIDUPSID: 1234567890ABCDEF1234567890ABCDEF...
  - PSTM: 1640995200...
```

### 获取域名请求

```bash
💬 请输入命令: requests api.github.com

🕵️ 获取域名 'api.github.com' 的拦截请求...
📤 发送命令: get_requests_by_domain
⏳ 等待插件响应...
✅ 收到响应:
📊 找到 8 个请求:
  - GET /user | 请求头: 12个
  - POST /repos | 请求头: 15个
  - GET /notifications | 请求头: 10个
```

### 查询特定请求头

```bash
💬 请输入命令: header Authorization

🔍 查询包含请求头 'Authorization' 的请求...
📤 发送命令: find_requests_by_header
⏳ 等待插件响应...
✅ 收到响应:
📊 找到 25 个匹配的请求:
  - GET api.github.com | 2024-01-15 14:30:25
  - POST api.openai.com | 2024-01-15 14:32:15
```

### 查看连接状态

```bash
💬 请输入命令: status
📊 连接状态: 1 个Chrome插件已连接
```

## 🔧 技术实现

### Python后端特性

- **非阻塞运行**：WebSocket服务器在后台线程运行
- **命令队列**：主线程与WebSocket线程通过队列通信
- **响应等待**：支持发送命令并等待Chrome插件响应
- **错误处理**：完善的错误处理和超时机制

### Chrome插件特性

- **命令监听**：监听`backend_command`类型消息
- **自动响应**：接收命令后自动执行并返回结果
- **支持的命令**：
  - `get_cookies_by_domain` - 获取域名Cookie
  - `get_requests_by_domain` - 获取域名请求
  - `find_requests_by_header` - 按请求头查询
  - `get_request_statistics` - 获取统计信息
  - `get_all_cookies` - 获取所有Cookie

### 消息协议

**后端 → 插件 (命令)**
```json
{
  "type": "backend_command",
  "command": "get_cookies_by_domain",
  "params": {"domain": "example.com"},
  "command_id": "cmd_1640995200"
}
```

**插件 → 后端 (响应)**
```json
{
  "type": "command_response",
  "command_id": "cmd_1640995200",
  "data": {
    "success": true,
    "cookies": [...]
  }
}
```

## 🎯 应用场景

1. **调试和监控**：实时获取网站Cookie和请求头
2. **数据分析**：收集特定域名的网络请求信息
3. **安全测试**：检查网站的认证机制和请求头
4. **自动化工具**：集成到Python脚本中进行批量操作

## ⚡ 性能优化

- 后台线程处理WebSocket连接，不阻塞主程序
- 队列机制确保线程安全
- 异步保存拦截数据，不影响网络请求速度
- 支持多个Chrome插件同时连接

## 🔒 安全考虑

- 仅监听localhost，不对外暴露
- 命令执行限制在预定义的安全操作
- Cookie和请求头数据仅在本地处理
- 支持完整的错误处理和日志记录

现在你可以通过Python后端轻松控制Chrome插件，获取任何网站的Cookie和请求头信息！🎉