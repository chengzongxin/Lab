/**
 * Chrome插件后台脚本 - WebSocket通信版本 (TypeScript)
 */

import { WebSocketMessage, WebSocketStatus, BackgroundRequest, BackgroundResponse } from '../types/websocket';
import { CookieUtils } from '../utils/cookieUtils';
import { RequestInterceptor, InterceptedRequest } from '../utils/headersUtils';

// WebSocket连接对象
let websocket: WebSocket | null = null;
const WEBSOCKET_URL = 'ws://localhost:8765';

// 请求拦截状态
let isIntercepting = false;

// 初始化时打印日志
console.log('Background script started at:', new Date().toISOString());

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
      // const cookieList = await handleGetCookies();
      
      // const newMessage = {
      //   ...message,
      //   cookies: cookieList
      // };

      const messageString = JSON.stringify(message);
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
      
    case 'backend_command':
      // 处理来自后端的命令
      handleBackendCommand(data);
      break;
      
    default:
      console.log('未知消息类型:', data);
  }
}

/**
 * 处理来自后端的命令
 */
async function handleBackendCommand(command: any): Promise<void> {
  console.log('收到后端命令:', command);
  
  const { command: action, params, command_id } = command;
  
  try {
    let response: BackgroundResponse;
    
    // 根据命令类型执行相应操作
    switch (action) {
      case 'get_cookies_by_domain':
        if (params.domain) {
          const cookies = await CookieUtils.getCookiesByDomain(params.domain);
          response = { success: true, cookies };
        } else {
          response = { success: false, message: '域名参数缺失' };
        }
        break;
        
      case 'get_requests_by_domain':
        if (params.domain) {
          const requests = await RequestInterceptor.getRequestsByDomain(params.domain);
          response = { success: true, requests };
        } else {
          response = { success: false, message: '域名参数缺失' };
        }
        break;
        
      case 'find_requests_by_header':
        if (params.headerName) {
          const requests = await RequestInterceptor.findRequestsByHeader(
            params.headerName, 
            params.headerValue
          );
          response = { success: true, requests };
        } else {
          response = { success: false, message: '请求头名称缺失' };
        }
        break;
        
      case 'get_request_statistics':
        const stats = await RequestInterceptor.getRequestStatistics();
        response = { success: true, statistics: stats };
        break;
        
      case 'get_all_cookies':
        const allCookies = await CookieUtils.getAllCookies();
        response = { success: true, cookies: allCookies };
        break;
        
      default:
        response = { success: false, message: `未知命令: ${action}` };
    }
    
    // 发送响应回后端
    const responseMessage = {
      type: 'command_response' as const,
      command_id,
      data: response
    };
    
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      websocket.send(JSON.stringify(responseMessage));
      console.log('已发送命令响应:', responseMessage);
    }
    
  } catch (error) {
    // 发送错误响应
    const errorResponse = {
      type: 'command_response' as const,
      command_id,
      data: { success: false, message: `执行命令失败: ${(error as Error).message}` }
    };
    
    if (websocket && websocket.readyState === WebSocket.OPEN) {
      websocket.send(JSON.stringify(errorResponse));
    }
    
    console.error('处理后端命令失败:', error);
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

/**
 * 初始化请求拦截功能
 */
function initializeRequestInterception(): void {
  // 监听网络请求
  chrome.webRequest.onBeforeSendHeaders.addListener(
    (details) => {
      if (!isIntercepting) return;
      
      console.log('拦截到请求:', details.url);
      
      // 检查所有请求
      const headers = details.requestHeaders || [];
      const timestamp = new Date().toISOString();
      const { domain, path } = RequestInterceptor.parseUrl(details.url);
      
      // 创建请求记录
      const interceptedRequest: InterceptedRequest = {
        id: RequestInterceptor.createRequestId(details.url, timestamp),
        url: details.url,
        method: details.method,
        type: details.type,
        headers: headers.map(header => ({
          name: header.name,
          value: header.value || ''
        })),
        timestamp,
        domain,
        path
      };
      
      // 异步保存到storage（不阻塞请求）
      RequestInterceptor.saveInterceptedRequest(interceptedRequest).catch(error => {
        console.error('保存拦截请求失败:', error);
      });
      
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
          console.log('发现Temu MailID:', mailIdHeader.value);
          
          // 通知popup显示MailID
          chrome.runtime.sendMessage({
            type: 'temu_mailid_detected',
            mailId: mailIdHeader.value,
            domain: domain,
            timestamp: timestamp,
            url: details.url
          }).catch(error => {
            console.log('发送MailID到popup失败:', error);
          });
        }
      }
      
      console.log('捕获到请求:', {
        url: details.url,
        method: details.method,
        type: details.type,
        headers: interceptedRequest.headers,
        timestamp: timestamp
      });
    },
    { urls: ["<all_urls>"] },
    ["requestHeaders", "extraHeaders"]
  );
  
  console.log('请求拦截器已初始化');
}

/**
 * 启动请求拦截
 */
function startInterception(): void {
  isIntercepting = true;
  console.log('开始拦截请求');
}

/**
 * 停止请求拦截
 */
function stopInterception(): void {
  isIntercepting = false;
  console.log('停止拦截请求');
}

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
  // 使用async函数处理异步操作
  const handleRequest = async () => {
    try {
      switch (request.action) {
        // ========== WebSocket相关操作 ==========
        case 'connect':
          connectWebSocket();
          sendResponse({success: true, message: '正在连接WebSocket服务器...'});
          break;
          
        case 'disconnect':
          disconnectWebSocket();
          sendResponse({success: true, message: 'WebSocket连接已断开'});
          break;
          
        case 'send_message':
          if (request.message) {
            sendMessage(request.message);
            sendResponse({success: true, message: '消息已发送'});
          } else {
            sendResponse({success: false, message: '消息内容为空'});
          }
          break;
          
        case 'get_status':
          const status: WebSocketStatus = websocket ? 
            (['CONNECTING', 'OPEN', 'CLOSING', 'CLOSED'] as const)[websocket.readyState] : 
            'CLOSED';
          
          sendResponse({
            success: true, 
            status: status,
            connected: !!websocket && websocket.readyState === WebSocket.OPEN
          });
          break;

        // ========== Cookie相关操作 ==========
        case 'get_all_cookies':
          const allCookies = await CookieUtils.getAllCookies();
          sendResponse({success: true, cookies: allCookies});
          break;

        case 'get_cookies_by_domain':
          if (request.domain) {
            const domainCookies = await CookieUtils.getCookiesByDomain(request.domain);
            sendResponse({success: true, cookies: domainCookies});
          } else {
            sendResponse({success: false, message: '域名参数缺失'});
          }
          break;

        case 'get_current_tab_cookies':
          const currentTabCookies = await CookieUtils.getCurrentTabCookies();
          sendResponse({success: true, cookies: currentTabCookies});
          break;

        case 'get_cookies_by_domains':
          if (request.domains && Array.isArray(request.domains)) {
            const cookieMap = await CookieUtils.getCookiesByDomains(request.domains);
            const cookieMapObject: Record<string, any[]> = {};
            cookieMap.forEach((cookies, domain) => {
              cookieMapObject[domain] = cookies;
            });
            sendResponse({success: true, cookieMap: cookieMapObject});
          } else {
            sendResponse({success: false, message: '域名列表参数缺失'});
          }
          break;

        case 'clear_domain_cookies':
          if (request.domain) {
            const clearedCount = await CookieUtils.clearDomainCookies(request.domain);
            sendResponse({success: true, clearedCount, message: `已清除 ${clearedCount} 个Cookie`});
          } else {
            sendResponse({success: false, message: '域名参数缺失'});
          }
          break;

        // ========== 请求拦截相关操作 ==========
        case 'start_interception':
          startInterception();
          sendResponse({success: true, message: '开始拦截请求'});
          break;

        case 'stop_interception':
          stopInterception();
          sendResponse({success: true, message: '停止拦截请求'});
          break;

        case 'get_interception_status':
          sendResponse({success: true, isIntercepting});
          break;

        case 'get_intercepted_requests':
          const allRequests = await RequestInterceptor.getInterceptedRequests();
          sendResponse({success: true, requests: allRequests});
          break;

        case 'get_recent_requests':
          const limit = request.limit || 50;
          const recentRequests = await RequestInterceptor.getRecentRequests(limit);
          sendResponse({success: true, requests: recentRequests});
          break;

        case 'search_requests':
          if (request.filter) {
            const searchResults = await RequestInterceptor.searchRequests(request.filter);
            sendResponse({success: true, requests: searchResults});
          } else {
            sendResponse({success: false, message: '搜索条件缺失'});
          }
          break;

        case 'find_requests_by_header':
          if (request.headerName) {
            const headerRequests = await RequestInterceptor.findRequestsByHeader(
              request.headerName, 
              request.headerValue
            );
            sendResponse({success: true, requests: headerRequests});
          } else {
            sendResponse({success: false, message: '请求头名称缺失'});
          }
          break;

        case 'get_request_by_id':
          if (request.requestId) {
            const requestData = await RequestInterceptor.getRequestById(request.requestId);
            sendResponse({success: !!requestData, request: requestData || undefined});
          } else {
            sendResponse({success: false, message: '请求ID缺失'});
          }
          break;

        case 'get_requests_by_domain':
          if (request.domain) {
            const domainRequests = await RequestInterceptor.getRequestsByDomain(request.domain);
            sendResponse({success: true, requests: domainRequests});
          } else {
            sendResponse({success: false, message: '域名参数缺失'});
          }
          break;

        case 'get_request_statistics':
          const stats = await RequestInterceptor.getRequestStatistics();
          sendResponse({success: true, statistics: stats});
          break;

        case 'export_requests':
          const exportData = await RequestInterceptor.exportRequests();
          sendResponse({success: !!exportData, exportData, message: exportData ? '导出成功' : '导出失败'});
          break;

        case 'clear_all_requests':
          const clearSuccess = await RequestInterceptor.clearAllRequests();
          sendResponse({success: clearSuccess, message: clearSuccess ? '数据已清除' : '清除失败'});
          break;
          
        default:
          sendResponse({success: false, message: '未知操作'});
      }
    } catch (error) {
      console.error('处理请求时发生错误:', error);
      sendResponse({success: false, message: '操作失败: ' + (error as Error).message});
    }
  };

  // 执行异步处理
  handleRequest();
  
  // 返回true表示将异步发送响应
  return true;
});

// 监听扩展安装或更新
chrome.runtime.onInstalled.addListener((details) => {
  if (details.reason === 'install') {
    console.log('插件已安装');
    // 初始化存储
    chrome.storage.local.set({ intercepted_requests: {} });
  } else if (details.reason === 'update') {
    console.log('插件已更新');
  }
  
  // 初始化请求拦截功能
  initializeRequestInterception();
});

// 插件启动时的初始化
console.log('Chrome插件背景脚本已加载 - WebSocket版本 (TypeScript)');

// 立即初始化请求拦截功能（用于开发调试）
initializeRequestInterception();