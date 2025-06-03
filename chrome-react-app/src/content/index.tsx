import React, { useState, useEffect } from 'react';
import { createRoot } from 'react-dom/client';
import './content.css';

interface Header {
  name: string;
  value: string;
}

interface RequestData {
  url: string;
  method: string;
  type: string;
  headers: Header[];
  timeStamp: number;
  requestId: string;
}

// 创建一个 React 组件
const ContentOverlay: React.FC = () => {
  const [requests, setRequests] = useState<RequestData[]>([]);
  const [isVisible, setIsVisible] = useState(true);
  const [expandedRequests, setExpandedRequests] = useState<Set<number>>(new Set());

  useEffect(() => {
    // 监听来自后台脚本的消息
    chrome.runtime.onMessage.addListener((message) => {
      if (message.type === 'NEW_REQUEST' || message.type === 'NEW_HEADERS') {
        setRequests(prev => {
          const newRequests = [...prev];
          const index = newRequests.findIndex(req => req.requestId === message.data.requestId);
          
          if (index !== -1) {
            newRequests[index] = message.data;
          } else {
            newRequests.push(message.data);
          }
          
          // 只保留最近的 20 个请求
          return newRequests.slice(-20);
        });
      } else if (message.type === 'EXECUTE_REQUEST') {
        executeRequest(message.data);
      }
    });

    // 获取历史请求数据
    chrome.runtime.sendMessage({ type: 'GET_REQUESTS' }, (response) => {
      if (response) {
        setRequests(response.slice(-20));
      }
    });
  }, []);

  // 格式化时间戳
  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  // 格式化 URL
  const formatUrl = (url: string) => {
    try {
      const urlObj = new URL(url);
      return urlObj.pathname + urlObj.search;
    } catch {
      return url;
    }
  };

  // 获取请求类型的显示名称
  const getRequestTypeName = (type: string) => {
    const typeMap: { [key: string]: string } = {
      'xmlhttprequest': 'XHR',
      'fetch': 'Fetch',
      'script': 'Script',
      'stylesheet': 'CSS',
      'image': 'Image',
      'font': 'Font',
      'media': 'Media',
      'websocket': 'WebSocket',
      'main_frame': 'Main Frame',
      'sub_frame': 'Sub Frame',
      'other': 'Other'
    };
    return typeMap[type] || type;
  };

  // 切换请求展开状态
  const toggleRequest = (index: number) => {
    setExpandedRequests(prev => {
      const newSet = new Set(prev);
      if (newSet.has(index)) {
        newSet.delete(index);
      } else {
        newSet.add(index);
      }
      return newSet;
    });
  };

  // 复制请求头值
  const copyHeaderValue = (value: string) => {
    navigator.clipboard.writeText(value);
  };

  // 重放请求
  const replayRequest = (request: RequestData) => {
    chrome.runtime.sendMessage({
      type: 'REPLAY_REQUEST',
      data: request
    });
  };

  // 执行请求
  const executeRequest = (request: RequestData) => {
    // 将请求头转换为对象
    const headers: { [key: string]: string } = {};
    request.headers.forEach(header => {
      headers[header.name] = header.value;
    });

    // 使用 fetch API 执行请求
    fetch(request.url, {
      method: request.method,
      headers: headers,
      credentials: 'include' // 包含 cookies
    }).then(response => {
      console.log('请求重放成功:', response);
    }).catch(error => {
      console.error('请求重放失败:', error);
    });
  };

  return (
    <div className={`chrome-extension-overlay ${isVisible ? 'visible' : 'hidden'}`}>
      <div className="chrome-extension-content">
        <div className="header">
          <h1>请求监控</h1>
          <button 
            className="toggle-button"
            onClick={() => setIsVisible(!isVisible)}
          >
            {isVisible ? '隐藏' : '显示'}
          </button>
        </div>
        <div className="requests-list">
          {requests.map((request, index) => (
            <div key={request.requestId} className="request-item">
              <div 
                className="request-header"
                onClick={() => toggleRequest(index)}
              >
                <div className="request-info">
                  <span className="request-method">{request.method}</span>
                  <span className="request-type">{getRequestTypeName(request.type)}</span>
                  <span className="request-time">{formatTime(request.timeStamp)}</span>
                </div>
                <div className="request-url">{formatUrl(request.url)}</div>
                <div className="request-actions">
                  <button 
                    className="replay-button"
                    onClick={(e) => {
                      e.stopPropagation();
                      replayRequest(request);
                    }}
                    title="重放请求"
                  >
                    重放
                  </button>
                  <span className="request-count">
                    {request.headers.length} 个请求头
                  </span>
                </div>
              </div>
              {expandedRequests.has(index) && (
                <div className="request-headers">
                  {request.headers.map((header, i) => (
                    <div key={i} className="header-item">
                      <span className="header-name">{header.name}</span>
                      <div className="header-value-container">
                        <span className="header-value">{header.value}</span>
                        <button 
                          className="copy-button"
                          onClick={() => copyHeaderValue(header.value)}
                          title="复制值"
                        >
                          复制
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
          {requests.length === 0 && (
            <div className="no-requests">
              暂无请求数据
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// 注入 React 组件到页面
const injectReactApp = () => {
  const container = document.createElement('div');
  container.id = 'chrome-extension-root';
  document.body.appendChild(container);

  const root = createRoot(container);
  root.render(
    <React.StrictMode>
      <ContentOverlay />
    </React.StrictMode>
  );

  console.log('React app injected');
};

// 确保在页面加载完成后注入
if (document.readyState === 'complete') {
  injectReactApp();
} else {
  window.addEventListener('load', injectReactApp);
} 