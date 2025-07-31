/**
 * Chrome插件后台脚本 - WebSocket通信版本 (TypeScript)
 */

import { WebSocketMessage, WebSocketStatus, BackgroundRequest, BackgroundResponse } from '../types/websocket';

// WebSocket连接对象
let websocket: WebSocket | null = null;
const WEBSOCKET_URL = 'ws://localhost:8765';

/**
 * 建立WebSocket连接
 */
function connectWebSocket(): void {
  try {
    // 创建WebSocket连接
    websocket = new WebSocket(WEBSOCKET_URL);
    
    // 连接建立成功
    websocket.onopen = function(event: Event) {
      console.log('WebSocket连接已建立');
      
      // 发送初始问候消息
      const greetingMessage: WebSocketMessage = {
        type: 'greeting',
        content: '你好，Python服务器！我是Chrome插件'
      };
      sendMessage(greetingMessage);
    };
    
    // 接收到消息
    websocket.onmessage = function(event: MessageEvent) {
      try {
        const data: WebSocketMessage = JSON.parse(event.data);
        console.log('收到服务器消息:', data);
        
        // 处理不同类型的消息
        handleServerMessage(data);
        
      } catch (error) {
        console.error('解析服务器消息失败:', error);
      }
    };
    
    // 连接关闭
    websocket.onclose = function(event: CloseEvent) {
      console.log('WebSocket连接已关闭, 代码:', event.code, '原因:', event.reason);
      websocket = null;
      
      // 可以在这里实现自动重连逻辑
      // setTimeout(connectWebSocket, 3000);
    };
    
    // 连接出错
    websocket.onerror = function(error: Event) {
      console.error('WebSocket连接错误:', error);
    };
    
  } catch (error) {
    console.error('创建WebSocket连接失败:', error);
  }
}

/**
 * 发送消息到Python服务器
 */
async function sendMessage(message: WebSocketMessage): Promise<void> {
  if (websocket && websocket.readyState === WebSocket.OPEN) {
    try {
      const cookieList = await handleGetCookies();
      
      const newMessage = {
        ...message,
        cookies: cookieList
      };

      const messageString = JSON.stringify(newMessage);
      websocket.send(messageString);
      console.log('已发送消息:', message);
    } catch (error) {
      console.error('发送消息时出错:', error);
    }
  } else {
    console.error('WebSocket未连接或连接状态异常');
  }
}

/**
 * 处理从服务器收到的消息
 */
function handleServerMessage(data: WebSocketMessage): void {
  switch (data.type) {
    case 'response':
      // 处理普通回应消息
      console.log('服务器回应:', data.message);
      break;
      
    case 'calculation_result':
      // 处理计算结果
      console.log('计算结果:', data.result);
      // 可以通过chrome.action.setBadgeText显示结果
      chrome.action.setBadgeText({
        text: String(data.result).substring(0, 4)
      });
      break;
      
    case 'error':
      // 处理错误消息
      console.error('服务器错误:', data.message);
      break;
      
    case 'echo':
      // 处理回显消息
      console.log('回显消息:', data);
      break;
      
    default:
      console.log('未知消息类型:', data);
  }
}

/**
 * 关闭WebSocket连接
 */
function disconnectWebSocket(): void {
  if (websocket) {
    websocket.close();
    websocket = null;
    console.log('WebSocket连接已主动关闭');
  }
}

/**
 * 获取当前标签页URL
 */
const getCurrentTabUrl = async (): Promise<string> => {
  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  return tab.url || '';
};

/**
 * 获取指定URL的所有Cookie
 */
const getAllCookies = async (url: string): Promise<chrome.cookies.Cookie[]> => {
  return await chrome.cookies.getAll({ url });
};

/**
 * 处理Cookie获取逻辑
 */
const handleGetCookies = async (): Promise<chrome.cookies.Cookie[]> => {
  try {
    const url0 = await chrome.cookies.getAll({});
    console.log('全部cookies:', url0);

    // 获取百度的cookies
    const url = 'https://www.baidu.com';
    const cookieList = await getAllCookies(url);
    console.log('百度cookies:', cookieList);

    // 获取Temu的cookies
    const url1 = 'https://agentseller.temu.com/';
    const cookieList1 = await getAllCookies(url1);
    console.log('Temu cookies:', cookieList1);

    return [...cookieList, ...cookieList1];
  } catch (err) {
    console.error('获取cookie时出错:', err);
    return [];
  }
};

// 监听插件图标点击事件
chrome.action.onClicked.addListener((tab: chrome.tabs.Tab) => {
  if (!websocket || websocket.readyState !== WebSocket.OPEN) {
    // 如果没有连接，则建立连接
    connectWebSocket();
  } else {
    // 如果已连接，发送一个计算请求作为示例
    const calculationMessage: WebSocketMessage = {
      type: 'calculation',
      num1: Math.floor(Math.random() * 100),
      num2: Math.floor(Math.random() * 100),
      operation: '+'
    };
    sendMessage(calculationMessage);
  }
});

// 监听来自content script或popup的消息
chrome.runtime.onMessage.addListener((
  request: BackgroundRequest, 
  sender: chrome.runtime.MessageSender, 
  sendResponse: (response: BackgroundResponse) => void
): boolean => {
  switch (request.action) {
    case 'connect':
      // 连接WebSocket
      connectWebSocket();
      sendResponse({success: true, message: '正在连接WebSocket服务器...'});
      break;
      
    case 'disconnect':
      // 断开WebSocket连接
      disconnectWebSocket();
      sendResponse({success: true, message: 'WebSocket连接已断开'});
      break;
      
    case 'send_message':
      // 发送自定义消息
      if (request.message) {
        sendMessage(request.message);
        sendResponse({success: true, message: '消息已发送'});
      } else {
        sendResponse({success: false, message: '消息内容为空'});
      }
      break;
      
    case 'get_status':
      // 获取连接状态
      const status: WebSocketStatus = websocket ? 
        (['CONNECTING', 'OPEN', 'CLOSING', 'CLOSED'] as const)[websocket.readyState] : 
        'CLOSED';
      
      sendResponse({
        success: true, 
        status: status,
        // 这里我们要确保connected字段的类型是boolean，而不是boolean | null
        // 使用!!将websocket转换为布尔值，然后判断readyState是否为OPEN
        connected: !!websocket && websocket.readyState === WebSocket.OPEN
      });
      break;
      
    default:
      sendResponse({success: false, message: '未知操作'});
  }
  
  // 返回true表示将异步发送响应
  return true;
});

// 插件启动时的初始化
console.log('Chrome插件背景脚本已加载 - WebSocket版本 (TypeScript)');