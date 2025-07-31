import React, { useState, useEffect, useRef } from 'react';
import './styles.css';
import { WebSocketStatus, WebSocketMessage, BackgroundRequest, BackgroundResponse, MessageLog, MessageLogType } from '../types/websocket';

const App: React.FC = () => {
  // 状态管理
  const [connectionStatus, setConnectionStatus] = useState<WebSocketStatus>('CLOSED');
  const [isConnected, setIsConnected] = useState<boolean>(false);
  const [messages, setMessages] = useState<MessageLog[]>([]);
  const [num1, setNum1] = useState<number>(10);
  const [num2, setNum2] = useState<number>(5);
  const [operation, setOperation] = useState<'+' | '-' | '*' | '/'>('+');
  const [customMessage, setCustomMessage] = useState<string>('');

  // Refs
  const messageAreaRef = useRef<HTMLDivElement>(null);

  /**
   * 向background script发送消息
   */
  const sendToBackground = (request: BackgroundRequest): Promise<BackgroundResponse> => {
    return new Promise((resolve, reject) => {
      chrome.runtime.sendMessage(request, (response: BackgroundResponse) => {
        if (chrome.runtime.lastError) {
          reject(chrome.runtime.lastError);
        } else {
          resolve(response);
        }
      });
    });
  };

  /**
   * 添加消息到消息记录
   */
  const addMessage = (content: string, type: MessageLogType = 'system') => {
    const newMessage: MessageLog = {
      id: Date.now().toString(),
      content,
      type,
      timestamp: new Date()
    };

    setMessages(prev => {
      const newMessages = [...prev, newMessage];
      // 限制消息数量
      return newMessages.length > 50 ? newMessages.slice(1) : newMessages;
    });
  };

  /**
   * 滚动到消息区域底部
   */
  const scrollToBottom = () => {
    if (messageAreaRef.current) {
      messageAreaRef.current.scrollTop = messageAreaRef.current.scrollHeight;
    }
  };

  /**
   * 更新连接状态
   */
  const updateStatus = async () => {
    try {
      const response = await sendToBackground({ action: 'get_status' });
      if (response.success && response.status) {
        setConnectionStatus(response.status);
        setIsConnected(response.connected || false);
      }
    } catch (error) {
      console.error('获取状态失败:', error);
      setConnectionStatus('CLOSED');
      setIsConnected(false);
    }
  };

  /**
   * 连接到WebSocket服务器
   */
  const connectToServer = async () => {
    try {
      setConnectionStatus('CONNECTING');
      addMessage('正在连接WebSocket服务器...', 'system');
      
      const response = await sendToBackground({ action: 'connect' });
      if (response.success) {
        addMessage(response.message || '连接请求已发送', 'system');
        // 稍等一下再检查状态，因为连接是异步的
        setTimeout(updateStatus, 1000);
      } else {
        addMessage(response.message || '连接失败', 'error');
        setConnectionStatus('CLOSED');
        setIsConnected(false);
      }
    } catch (error) {
      console.error('连接失败:', error);
      addMessage('连接失败: ' + (error as Error).message, 'error');
      setConnectionStatus('CLOSED');
      setIsConnected(false);
    }
  };

  /**
   * 断开WebSocket连接
   */
  const disconnectFromServer = async () => {
    try {
      const response = await sendToBackground({ action: 'disconnect' });
      addMessage(response.message || '连接已断开', 'system');
      setConnectionStatus('CLOSED');
      setIsConnected(false);
    } catch (error) {
      console.error('断开连接失败:', error);
      addMessage('断开连接失败: ' + (error as Error).message, 'error');
    }
  };

  /**
   * 发送消息到background script
   */
  const sendMessage = async (message: WebSocketMessage) => {
    try {
      addMessage(JSON.stringify(message, null, 2), 'sent');
      
      const response = await sendToBackground({
        action: 'send_message',
        message: message
      });
      
      if (response.success) {
        addMessage(response.message || '消息已发送', 'system');
      } else {
        addMessage(response.message || '发送失败', 'error');
      }
    } catch (error) {
      console.error('发送消息失败:', error);
      addMessage('发送消息失败: ' + (error as Error).message, 'error');
    }
  };

  /**
   * 发送问候消息
   */
  const sendGreeting = () => {
    const message: WebSocketMessage = {
      type: 'greeting',
      content: '你好，Python服务器！这是来自React组件的问候消息！'
    };
    sendMessage(message);
  };

  /**
   * 发送计算请求
   */
  const sendCalculation = () => {
    const message: WebSocketMessage = {
      type: 'calculation',
      num1,
      num2,
      operation
    };
    sendMessage(message);
  };

  /**
   * 发送自定义消息
   */
  const sendCustomMessage = () => {
    const messageText = customMessage.trim();
    if (!messageText) {
      addMessage('请输入消息内容', 'error');
      return;
    }

    try {
      // 尝试解析为JSON
      const message = JSON.parse(messageText);
      sendMessage(message);
    } catch (error) {
      // 如果不是有效JSON，作为普通文本发送
      const message: WebSocketMessage = {
        type: 'text',
        content: messageText
      };
      sendMessage(message);
    }
  };

  /**
   * 清空消息记录
   */
  const clearMessages = () => {
    setMessages([]);
    addMessage('消息记录已清空', 'system');
  };

  /**
   * 处理回车键事件
   */
  const handleKeyPress = (event: React.KeyboardEvent, action: () => void) => {
    if (event.key === 'Enter') {
      action();
    }
  };

  /**
   * 获取状态样式类名
   */
  const getStatusClassName = () => {
    switch (connectionStatus) {
      case 'OPEN':
        return 'status-connected';
      case 'CONNECTING':
        return 'status-connecting';
      default:
        return 'status-disconnected';
    }
  };

  /**
   * 获取状态文本
   */
  const getStatusText = () => {
    switch (connectionStatus) {
      case 'OPEN':
        return '已连接';
      case 'CONNECTING':
        return '连接中...';
      default:
        return '未连接';
    }
  };

  /**
   * 获取消息类型前缀
   */
  const getMessagePrefix = (type: MessageLogType) => {
    switch (type) {
      case 'sent':
        return '📤 发送: ';
      case 'received':
        return '📥 接收: ';
      case 'system':
        return '🔧 系统: ';
      case 'error':
        return '❌ 错误: ';
      default:
        return '';
    }
  };

  // 组件挂载时的初始化
  useEffect(() => {
    console.log('React Popup组件已加载');
    updateStatus();
    addMessage('WebSocket通信测试界面已加载', 'system');
    addMessage('请先点击"连接服务器"按钮建立连接', 'system');
  }, []);

  // 当消息更新时自动滚动到底部
  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  return (
    <div className="container">
      <h1>🔗 WebSocket通信测试</h1>
      
      {/* 连接状态 */}
      <div className="status-indicator">
        <div className={`status-dot ${getStatusClassName()}`}></div>
        <span>{getStatusText()}</span>
      </div>

      {/* 连接控制 */}
      {!isConnected ? (
        <button 
          className="btn btn-primary" 
          onClick={connectToServer}
          disabled={connectionStatus === 'CONNECTING'}
        >
          连接服务器
        </button>
      ) : (
        <button className="btn btn-danger" onClick={disconnectFromServer}>
          断开连接
        </button>
      )}

      {/* 快速测试 */}
      <div className="input-group">
        <label>📤 快速测试消息</label>
        <button 
          className="btn" 
          onClick={sendGreeting}
          disabled={!isConnected}
        >
          发送问候消息
        </button>
      </div>

      {/* 计算器测试 */}
      <div className="input-group">
        <label>🧮 计算器测试</label>
        <div className="form-row">
          <input 
            type="number" 
            className="form-control" 
            placeholder="数字1" 
            value={num1}
            onChange={(e) => setNum1(parseFloat(e.target.value) || 0)}
            onKeyPress={(e) => handleKeyPress(e, sendCalculation)}
          />
          <select 
            className="form-control" 
            value={operation}
            onChange={(e) => setOperation(e.target.value as '+' | '-' | '*' | '/')}
          >
            <option value="+">+</option>
            <option value="-">-</option>
            <option value="*">×</option>
            <option value="/">/</option>
          </select>
          <input 
            type="number" 
            className="form-control" 
            placeholder="数字2" 
            value={num2}
            onChange={(e) => setNum2(parseFloat(e.target.value) || 0)}
            onKeyPress={(e) => handleKeyPress(e, sendCalculation)}
          />
        </div>
        <button 
          className="btn" 
          onClick={sendCalculation}
          disabled={!isConnected}
        >
          计算
        </button>
      </div>

      {/* 自定义消息 */}
      <div className="input-group">
        <label>✏️ 自定义消息</label>
        <textarea 
          className="form-control" 
          rows={2} 
          placeholder='{"type": "custom", "content": "你的消息"}'
          value={customMessage}
          onChange={(e) => setCustomMessage(e.target.value)}
          onKeyPress={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault();
              sendCustomMessage();
            }
          }}
        />
        <button 
          className="btn" 
          onClick={sendCustomMessage}
          disabled={!isConnected}
        >
          发送
        </button>
      </div>

      {/* 消息记录 */}
      <div className="input-group">
        <label>📋 消息记录</label>
        <div className="message-area" ref={messageAreaRef}>
          {messages.map((message) => (
            <div key={message.id} className="message">
              <div className="message-time">
                {message.timestamp.toLocaleTimeString()}
              </div>
              <div>
                {getMessagePrefix(message.type)}{message.content}
              </div>
            </div>
          ))}
        </div>
        <button className="btn" onClick={clearMessages}>
          清空记录
        </button>
      </div>
    </div>
  );
};

export default App;