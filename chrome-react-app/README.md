# Chrome React App

这是一个使用 React 和 TypeScript 构建的 Chrome 扩展程序。

## 开发环境设置

1. 安装依赖：
```bash
npm install
```

2. 开发模式：
```bash
npm start
```

3. 构建生产版本：
```bash
npm run build
```

## 项目结构

```
├── public/              # 静态资源
│   ├── manifest.json    # Chrome 扩展清单文件
│   └── icons/          # 扩展图标
├── src/                # 源代码
│   ├── popup/         # 弹出窗口相关代码
│   ├── background/    # 后台脚本
│   └── content/       # 内容脚本
├── package.json       # 项目配置
├── tsconfig.json     # TypeScript 配置
└── webpack.config.js # Webpack 配置
```

## 在 Chrome 中加载扩展

1. 打开 Chrome 浏览器
2. 访问 `chrome://extensions/`
3. 开启"开发者模式"
4. 点击"加载已解压的扩展程序"
5. 选择项目的 `dist` 目录

## 开发说明

- 使用 `npm start` 启动开发模式，webpack 会监视文件变化并自动重新构建
- 修改代码后，需要在 Chrome 扩展管理页面点击刷新按钮来更新扩展 