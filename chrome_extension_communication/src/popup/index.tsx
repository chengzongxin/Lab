import React from 'react';
import { createRoot } from 'react-dom/client';
import App from './App';

// 获取根元素
const container = document.getElementById('root');
if (!container) {
  throw new Error('Root element not found');
}

// 创建React根节点
const root = createRoot(container);

// 渲染应用
root.render(<App />);