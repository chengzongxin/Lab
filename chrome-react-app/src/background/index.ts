// 后台脚本
chrome.runtime.onInstalled.addListener(() => {
  console.log('Extension installed');
});

// 存储当前页面的请求数据
let currentPageRequests: any[] = [];
let currentTabId: number | null = null;

// 监听标签页更新
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === 'complete' && tab.active) {
    currentTabId = tabId;
    currentPageRequests = []; // 清空之前的请求数据
  }
});

// 监听标签页激活
chrome.tabs.onActivated.addListener((activeInfo) => {
  currentTabId = activeInfo.tabId;
  currentPageRequests = []; // 清空之前的请求数据
});

// 获取请求的 Cookie 信息
function getRequestCookies(url: string, callback: (cookies: chrome.cookies.Cookie[]) => void) {
  try {
    const urlObj = new URL(url);
    // 获取所有 Cookie，包括 HttpOnly 和 Secure Cookie
    chrome.cookies.getAll({
      url: url,
      domain: urlObj.hostname
    }, (cookies) => {
      // 如果没有找到 Cookie，尝试获取所有域名的 Cookie
      if (cookies.length === 0) {
        chrome.cookies.getAll({}, (allCookies) => {
          // 过滤出与当前域名相关的 Cookie
          const domainCookies = allCookies.filter(cookie => {
            return urlObj.hostname.endsWith(cookie.domain) || 
                   cookie.domain.endsWith(urlObj.hostname);
          });
          callback(domainCookies);
        });
      } else {
        callback(cookies);
      }
    });
  } catch (error) {
    console.error('获取 Cookie 失败:', error);
    callback([]);
  }
}

// 重放请求
function replayRequest(request: any) {
  // 获取当前标签页
  chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
    if (tabs[0]?.id) {
      // 在内容脚本中执行请求
      chrome.tabs.sendMessage(tabs[0].id, {
        type: 'EXECUTE_REQUEST',
        data: request
      });
    }
  });
}

// 监听所有请求
chrome.webRequest.onBeforeRequest.addListener(
  (details) => {
    if (details.tabId === currentTabId) {
      const requestData = {
        url: details.url,
        method: details.method,
        type: details.type,
        timeStamp: details.timeStamp,
        requestId: details.requestId,
        headers: []
      };
      
      currentPageRequests.push(requestData);
      
      // 通知内容脚本
      chrome.tabs.sendMessage(details.tabId, {
        type: 'NEW_REQUEST',
        data: requestData
      });
    }
  },
  { urls: ["<all_urls>"] }
);

// 监听请求头
chrome.webRequest.onBeforeSendHeaders.addListener(
  (details) => {
    if (details.tabId === currentTabId) {
      // 获取 Cookie 信息
      getRequestCookies(details.url, (cookies) => {
        // 将 Cookie 信息添加到请求头中
        const cookieHeader = cookies.map(cookie => `${cookie.name}=${cookie.value}`).join('; ');
        
        const headersData = {
          url: details.url,
          method: details.method,
          type: details.type,
          headers: [
            ...(details.requestHeaders || []),
            { name: 'Cookie', value: cookieHeader }
          ],
          timeStamp: details.timeStamp,
          requestId: details.requestId
        };
        
        // 更新请求数据
        const requestIndex = currentPageRequests.findIndex(req => req.requestId === details.requestId);
        if (requestIndex !== -1) {
          currentPageRequests[requestIndex] = headersData;
        } else {
          currentPageRequests.push(headersData);
        }
        
        // 通知内容脚本
        chrome.tabs.sendMessage(details.tabId, {
          type: 'NEW_HEADERS',
          data: headersData
        });
      });
    }
  },
  { urls: ["<all_urls>"] },
  ["requestHeaders"]
);

// 监听来自内容脚本的消息
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  if (message.type === 'GET_REQUESTS') {
    sendResponse(currentPageRequests);
  } else if (message.type === 'REPLAY_REQUEST') {
    replayRequest(message.data);
  }
}); 