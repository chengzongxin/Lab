import React, { useState, useEffect, useRef } from 'react';
import './styles.css';
import {
    WebSocketStatus,
    WebSocketMessage,
    BackgroundRequest,
    BackgroundResponse,
    MessageLog,
    MessageLogType,
    CookieInfo,
    InterceptedRequest,
    RequestFilter,
    RequestStatistics
} from '../types/websocket';

const App: React.FC = () => {
    // 状态管理
    const [connectionStatus, setConnectionStatus] = useState<WebSocketStatus>('CLOSED');
    const [isConnected, setIsConnected] = useState<boolean>(false);
    const [messages, setMessages] = useState<MessageLog[]>([]);
    const [num1, setNum1] = useState<number>(10);
    const [num2, setNum2] = useState<number>(5);
    const [operation, setOperation] = useState<'+' | '-' | '*' | '/'>('+');
    const [customMessage, setCustomMessage] = useState<string>('');

    // Cookie管理状态
    const [cookies, setCookies] = useState<CookieInfo[]>([]);
    const [cookieDomain, setCookieDomain] = useState<string>('');
    const [showCookies, setShowCookies] = useState<boolean>(false);

    // 请求拦截管理状态
    const [isIntercepting, setIsIntercepting] = useState<boolean>(false);
    const [interceptedRequests, setInterceptedRequests] = useState<InterceptedRequest[]>([]);
    const [showRequests, setShowRequests] = useState<boolean>(false);
    const [searchHeaderName, setSearchHeaderName] = useState<string>('');
    const [searchHeaderValue, setSearchHeaderValue] = useState<string>('');
    const [searchDomain, setSearchDomain] = useState<string>('');
    const [requestStats, setRequestStats] = useState<RequestStatistics | null>(null);

    // 业务Cookie状态
    const [temuCookies, setTemuCookies] = useState<CookieInfo[]>([]);
    const [kuajingCookies, setKuajingCookies] = useState<CookieInfo[]>([]);
    const [copyStatus, setCopyStatus] = useState<string>('');
    
    // Temu请求头MailID状态
    const [temuRequestMailIds, setTemuRequestMailIds] = useState<{
        mailId: string;
        domain: string;
        timestamp: string;
        url: string;
    }[]>([]);

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
        loadInterceptionStatus();
        loadBusinessCookies(); // 加载业务Cookie
        setupTemuMailIdListener(); // 设置Temu MailID监听
        addMessage('WebSocket通信测试界面已加载', 'system');
        addMessage('请先点击"连接服务器"按钮建立连接', 'system');
    }, []);

    /**
     * 加载拦截状态
     */
    const loadInterceptionStatus = async () => {
        try {
            const response = await sendToBackground({ action: 'get_interception_status' });
            if (response.success) {
                setIsIntercepting(response.isIntercepting || false);
            }
        } catch (error) {
            console.error('加载拦截状态失败:', error);
        }
    };

    // ========== Cookie管理功能 ==========

    /**
     * 获取所有Cookie
     */
    const getAllCookies = async () => {
        try {
            addMessage('正在获取所有Cookie...', 'system');
            const response = await sendToBackground({ action: 'get_all_cookies' });
            if (response.success && response.cookies) {
                setCookies(response.cookies);
                setShowCookies(true);
                addMessage(`获取到 ${response.cookies.length} 个Cookie`, 'system');
            } else {
                addMessage('获取Cookie失败', 'error');
            }
        } catch (error) {
            addMessage('获取Cookie失败: ' + (error as Error).message, 'error');
        }
    };

    /**
     * 根据域名获取Cookie
     */
    const getCookiesByDomain = async () => {
        if (!cookieDomain.trim()) {
            addMessage('请输入域名', 'error');
            return;
        }

        try {
            addMessage(`正在获取域名 ${cookieDomain} 的Cookie...`, 'system');
            const response = await sendToBackground({
                action: 'get_cookies_by_domain',
                domain: cookieDomain
            });
            if (response.success && response.cookies) {
                setCookies(response.cookies);
                setShowCookies(true);
                addMessage(`获取到 ${response.cookies.length} 个Cookie`, 'system');
            } else {
                addMessage('获取Cookie失败', 'error');
            }
        } catch (error) {
            addMessage('获取Cookie失败: ' + (error as Error).message, 'error');
        }
    };

    /**
     * 获取当前标签页Cookie
     */
    const getCurrentTabCookies = async () => {
        try {
            addMessage('正在获取当前标签页Cookie...', 'system');
            const response = await sendToBackground({ action: 'get_current_tab_cookies' });
            if (response.success && response.cookies) {
                setCookies(response.cookies);
                setShowCookies(true);
                addMessage(`获取到 ${response.cookies.length} 个Cookie`, 'system');
            } else {
                addMessage('获取Cookie失败', 'error');
            }
        } catch (error) {
            addMessage('获取Cookie失败: ' + (error as Error).message, 'error');
        }
    };

    // ========== 请求拦截管理功能 ==========

    /**
     * 启动请求拦截
     */
    const startInterception = async () => {
        try {
            const response = await sendToBackground({ action: 'start_interception' });
            if (response.success) {
                setIsIntercepting(true);
                addMessage('开始拦截网络请求', 'system');
            } else {
                addMessage(response.message || '启动拦截失败', 'error');
            }
        } catch (error) {
            addMessage('启动拦截失败: ' + (error as Error).message, 'error');
        }
    };

    /**
     * 停止请求拦截
     */
    const stopInterception = async () => {
        try {
            const response = await sendToBackground({ action: 'stop_interception' });
            if (response.success) {
                setIsIntercepting(false);
                addMessage('停止拦截网络请求', 'system');
            } else {
                addMessage(response.message || '停止拦截失败', 'error');
            }
        } catch (error) {
            addMessage('停止拦截失败: ' + (error as Error).message, 'error');
        }
    };

    /**
     * 获取拦截的请求列表
     */
    const loadInterceptedRequests = async () => {
        try {
            addMessage('正在加载拦截的请求...', 'system');
            const response = await sendToBackground({
                action: 'get_recent_requests',
                limit: 50
            });
            if (response.success && response.requests) {
                setInterceptedRequests(response.requests);
                setShowRequests(true);
                addMessage(`加载了 ${response.requests.length} 个拦截的请求`, 'system');
            } else {
                addMessage('加载请求失败', 'error');
            }
        } catch (error) {
            addMessage('加载请求失败: ' + (error as Error).message, 'error');
        }
    };

    /**
     * 根据请求头名称和值搜索
     */
    const searchByHeader = async () => {
        if (!searchHeaderName.trim()) {
            addMessage('请输入要搜索的请求头名称', 'error');
            return;
        }

        try {
            addMessage(`搜索包含请求头 "${searchHeaderName}" 的请求...`, 'system');
            const response = await sendToBackground({
                action: 'find_requests_by_header',
                headerName: searchHeaderName,
                headerValue: searchHeaderValue || undefined
            });

            if (response.success && response.requests) {
                setInterceptedRequests(response.requests);
                setShowRequests(true);
                addMessage(`找到 ${response.requests.length} 个匹配的请求`, 'system');
            } else {
                addMessage('搜索请求失败', 'error');
            }
        } catch (error) {
            addMessage('搜索请求失败: ' + (error as Error).message, 'error');
        }
    };

    /**
     * 根据域名搜索
     */
    const searchByDomain = async () => {
        if (!searchDomain.trim()) {
            addMessage('请输入要搜索的域名', 'error');
            return;
        }

        try {
            addMessage(`搜索域名 "${searchDomain}" 的请求...`, 'system');
            const response = await sendToBackground({
                action: 'get_requests_by_domain',
                domain: searchDomain
            });

            if (response.success && response.requests) {
                setInterceptedRequests(response.requests);
                setShowRequests(true);
                addMessage(`找到 ${response.requests.length} 个匹配的请求`, 'system');
            } else {
                addMessage('搜索请求失败', 'error');
            }
        } catch (error) {
            addMessage('搜索请求失败: ' + (error as Error).message, 'error');
        }
    };

    /**
     * 获取请求统计信息
     */
    const loadRequestStatistics = async () => {
        try {
            const response = await sendToBackground({ action: 'get_request_statistics' });
            if (response.success && response.statistics) {
                setRequestStats(response.statistics);
                addMessage('统计信息已加载', 'system');
            } else {
                addMessage('加载统计信息失败', 'error');
            }
        } catch (error) {
            addMessage('加载统计信息失败: ' + (error as Error).message, 'error');
        }
    };

    /**
     * 导出拦截的请求数据
     */
    const exportRequests = async () => {
        try {
            const response = await sendToBackground({ action: 'export_requests' });
            if (response.success && response.exportData) {
                // 创建下载链接
                const blob = new Blob([response.exportData], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = `intercepted-requests-${new Date().toISOString().slice(0, 10)}.json`;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);

                addMessage('拦截数据已导出', 'system');
            } else {
                addMessage('导出失败', 'error');
            }
        } catch (error) {
            addMessage('导出失败: ' + (error as Error).message, 'error');
        }
    };

    /**
     * 清除所有拦截的请求数据
     */
    const clearAllRequests = async () => {
        if (!confirm('确定要清除所有拦截的请求数据吗？')) {
            return;
        }

        try {
            const response = await sendToBackground({ action: 'clear_all_requests' });
            if (response.success) {
                addMessage('所有拦截数据已清除', 'system');
                setInterceptedRequests([]);
                setRequestStats(null);
            } else {
                addMessage(response.message || '清除失败', 'error');
            }
        } catch (error) {
            addMessage('清除数据失败: ' + (error as Error).message, 'error');
        }
    };

    // ========== 业务Cookie功能 ==========
    const loadBusinessCookies = async () => {
        try {
            // 加载Temu的Cookie
            const temuResponse = await sendToBackground({ 
                action: 'get_cookies_by_domain', 
                domain: 'https://agentseller.temu.com/' 
            });
            if (temuResponse.success) {
                setTemuCookies(temuResponse.cookies || []);
            }

            // 加载跨境猫的Cookie
            const kuajingResponse = await sendToBackground({ 
                action: 'get_cookies_by_domain', 
                domain: 'https://seller.kuajingmaihuo.com/' 
            });
            if (kuajingResponse.success) {
                setKuajingCookies(kuajingResponse.cookies || []);
            }
        } catch (error) {
            console.error('加载业务Cookie失败:', error);
        }
    };

    const copyToClipboard = async (text: string, type: string) => {
        try {
            await navigator.clipboard.writeText(text);
            setCopyStatus(`${type}已复制到剪贴板`);
            setTimeout(() => setCopyStatus(''), 2000);
        } catch (error) {
            console.error('复制失败:', error);
            setCopyStatus('复制失败');
            setTimeout(() => setCopyStatus(''), 2000);
        }
    };

    const formatCookiesForCopy = (cookies: CookieInfo[]): string => {
        return cookies.map(cookie => `${cookie.name}=${cookie.value}`).join('; ');
    };

    const getMailIdFromCookies = (cookies: CookieInfo[]): string => {
        const mailIdCookie = cookies.find(cookie => 
            cookie.name.toLowerCase().includes('mail') || 
            cookie.name.toLowerCase().includes('id') ||
            cookie.name.toLowerCase().includes('user')
        );
        return mailIdCookie ? mailIdCookie.value : '未找到MailID';
    };

    // ========== Temu请求头MailID功能 ==========
    const setupTemuMailIdListener = () => {
        // 监听来自background的Temu MailID消息
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            if (message.type === 'temu_mailid_detected') {
                console.log('收到Temu MailID:', message);
                
                // 添加到状态中
                setTemuRequestMailIds(prev => {
                    const newMailId = {
                        mailId: message.mailId,
                        domain: message.domain,
                        timestamp: message.timestamp,
                        url: message.url
                    };
                    
                    // 避免重复添加相同的MailID
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

    const copyTemuRequestMailId = async (mailId: string) => {
        await copyToClipboard(mailId, 'Temu请求头MailID');
    };

    const clearTemuRequestMailIds = () => {
        setTemuRequestMailIds([]);
        addMessage('已清除Temu请求头MailID记录', 'system');
    };

    // 当消息更新时自动滚动到底部
    useEffect(() => {
        scrollToBottom();
    }, [messages]);

    return (
        <div className="container">
            <h1>🔗 WebSocket通信插件</h1>

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

            {/* 业务Cookie显示 */}
            <div className="input-group">
                <label>🍪 业务Cookie</label>
                
                {/* 复制状态提示 */}
                {copyStatus && (
                    <div className="copy-status">
                        {copyStatus}
                    </div>
                )}

                {/* Temu Cookie */}
                <div className="cookie-section">
                    <div className="cookie-header">
                        <span className="cookie-title">🛒 Temu (agentseller.temu.com)</span>
                        <button 
                            className="btn btn-small" 
                            onClick={() => copyToClipboard(formatCookiesForCopy(temuCookies), 'Temu Cookie')}
                        >
                            复制Cookie
                        </button>
                    </div>
                    <div className="cookie-content">
                        <div className="cookie-count">Cookie数量: {temuCookies.length}</div>
                        {temuCookies.length > 0 && (
                            <div className="cookie-preview">
                                {temuCookies.slice(0, 3).map((cookie, index) => (
                                    <div key={index} className="cookie-item">
                                        <span className="cookie-name">{cookie.name}:</span>
                                        <span className="cookie-value">{cookie.value.substring(0, 30)}...</span>
                                    </div>
                                ))}
                                {temuCookies.length > 3 && (
                                    <div className="cookie-more">... 还有 {temuCookies.length - 3} 个Cookie</div>
                                )}
                            </div>
                        )}
                    </div>
                </div>

                {/* 跨境猫 Cookie */}
                <div className="cookie-section">
                    <div className="cookie-header">
                        <span className="cookie-title">🐱 跨境猫 (seller.kuajingmaihuo.com)</span>
                        <button 
                            className="btn btn-small" 
                            onClick={() => copyToClipboard(formatCookiesForCopy(kuajingCookies), '跨境猫 Cookie')}
                        >
                            复制Cookie
                        </button>
                    </div>
                    <div className="cookie-content">
                        <div className="cookie-count">Cookie数量: {kuajingCookies.length}</div>
                        {kuajingCookies.length > 0 && (
                            <div className="cookie-preview">
                                {kuajingCookies.slice(0, 3).map((cookie, index) => (
                                    <div key={index} className="cookie-item">
                                        <span className="cookie-name">{cookie.name}:</span>
                                        <span className="cookie-value">{cookie.value.substring(0, 30)}...</span>
                                    </div>
                                ))}
                                {kuajingCookies.length > 3 && (
                                    <div className="cookie-more">... 还有 {kuajingCookies.length - 3} 个Cookie</div>
                                )}
                            </div>
                        )}
                    </div>
                </div>

                {/* MailID 显示 */}
                <div className="mailid-section">
                    <div className="mailid-header">
                        <span className="mailid-title">📧 MailID</span>
                        <button 
                            className="btn btn-small" 
                            onClick={() => copyToClipboard(getMailIdFromCookies(temuCookies), 'Temu MailID')}
                        >
                            复制Temu MailID
                        </button>
                    </div>
                    <div className="mailid-content">
                        <div className="mailid-value">
                            Temu: {getMailIdFromCookies(temuCookies)}
                        </div>
                    </div>
                </div>

                {/* Temu请求头MailID显示 */}
                {temuRequestMailIds.length > 0 && (
                    <div className="mailid-section">
                        <div className="mailid-header">
                            <span className="mailid-title">🔍 Temu请求头MailID</span>
                            <div className="mailid-buttons">
                                <button 
                                    className="btn btn-small" 
                                    onClick={clearTemuRequestMailIds}
                                >
                                    清除
                                </button>
                            </div>
                        </div>
                        <div className="mailid-content">
                            <div className="mailid-list">
                                {temuRequestMailIds.map((item, index) => (
                                    <div key={index} className="mailid-item">
                                        <div className="mailid-info">
                                            <div className="mailid-value">
                                                {item.mailId}
                                            </div>
                                            <div className="mailid-meta">
                                                {item.domain} | {new Date(item.timestamp).toLocaleTimeString()}
                                            </div>
                                        </div>
                                        <button 
                                            className="btn btn-small" 
                                            onClick={() => copyTemuRequestMailId(item.mailId)}
                                        >
                                            复制
                                        </button>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}
            </div>
            {/* 请求拦截管理 */}
            <div className="input-group">
                <label>🕵️ 请求拦截器</label>
                <div className="form-row">
                    <button
                        className={`btn ${isIntercepting ? 'btn-danger' : 'btn-success'}`}
                        onClick={isIntercepting ? stopInterception : startInterception}
                    >
                        {isIntercepting ? '停止拦截' : '开始拦截'}
                    </button>
                    <span className="status-text">
                        状态: {isIntercepting ? '🔴 拦截中' : '⚪ 未拦截'}
                    </span>
                </div>

                {/* 拦截控制 */}
                <div className="form-row">
                    <button className="btn" onClick={loadInterceptedRequests}>
                        查看拦截请求
                    </button>
                    <button className="btn" onClick={loadRequestStatistics}>
                        统计信息
                    </button>
                </div>

                {/* 搜索功能 */}
                <div className="search-section">
                    <label>🔍 搜索拦截的请求:</label>

                    {/* 按请求头搜索 */}
                    <div className="form-row">
                        <input
                            type="text"
                            className="form-control"
                            placeholder="请求头名称 (如: Authorization)"
                            value={searchHeaderName}
                            onChange={(e) => setSearchHeaderName(e.target.value)}
                        />
                        <input
                            type="text"
                            className="form-control"
                            placeholder="请求头值 (可选)"
                            value={searchHeaderValue}
                            onChange={(e) => setSearchHeaderValue(e.target.value)}
                        />
                        <button className="btn" onClick={searchByHeader}>
                            搜索
                        </button>
                    </div>

                    {/* 按域名搜索 */}
                    <div className="form-row">
                        <input
                            type="text"
                            className="form-control"
                            placeholder="域名 (如: api.example.com)"
                            value={searchDomain}
                            onChange={(e) => setSearchDomain(e.target.value)}
                            onKeyPress={(e) => handleKeyPress(e, searchByDomain)}
                        />
                        <button className="btn" onClick={searchByDomain}>
                            按域名搜索
                        </button>
                    </div>
                </div>

                {/* 统计信息显示 */}
                {requestStats && (
                    <div className="stats-section">
                        <h4>📊 拦截统计</h4>
                        <div className="stats-grid">
                            <div>总请求数: {requestStats.total}</div>
                            <div>涉及域名: {requestStats.domains.length}</div>
                            <div>请求头类型: {requestStats.headerNames.length}</div>
                        </div>
                        <div className="stats-details">
                            <strong>请求方法:</strong> {Object.entries(requestStats.methods).map(([method, count]) => `${method}(${count})`).join(', ')}
                        </div>
                    </div>
                )}

                {/* 拦截请求列表 */}
                {showRequests && interceptedRequests.length > 0 && (
                    <div className="requests-list">
                        <h4>📋 拦截的请求 ({interceptedRequests.length})</h4>
                        <div className="message-area" style={{ maxHeight: '200px' }}>
                            {interceptedRequests.slice(0, 20).map((request, index) => (
                                <div key={index} className="message request-item">
                                    <div>
                                        <strong>{request.method}</strong> {request.domain}{request.path}
                                    </div>
                                    <div className="message-time">
                                        {new Date(request.timestamp).toLocaleString('zh-CN')} |
                                        请求头: {request.headers.length}个 |
                                        类型: {request.type}
                                    </div>
                                    <div className="headers-preview">
                                        {request.headers.slice(0, 3).map((header, idx) => (
                                            <span key={idx} className="header-tag">
                                                {header.name}: {header.value.substring(0, 20)}{header.value.length > 20 ? '...' : ''}
                                            </span>
                                        ))}
                                        {request.headers.length > 3 && (
                                            <span className="header-tag">+{request.headers.length - 3}更多</span>
                                        )}
                                    </div>
                                </div>
                            ))}
                            {interceptedRequests.length > 20 && (
                                <div className="message">
                                    <div>还有 {interceptedRequests.length - 20} 个请求...</div>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* 管理操作 */}
                <div className="form-row">
                    <button className="btn" onClick={exportRequests}>
                        导出数据
                    </button>
                    <button className="btn btn-danger" onClick={clearAllRequests}>
                        清空数据
                    </button>
                </div>
            </div>

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

            {/* Cookie管理 */}
            <div className="input-group">
                <label>🍪 Cookie管理</label>
                <div className="form-row">
                    <button className="btn" onClick={getAllCookies}>
                        获取所有Cookie
                    </button>
                    <button className="btn" onClick={getCurrentTabCookies}>
                        当前页面Cookie
                    </button>
                </div>
                <div className="form-row">
                    <input
                        type="text"
                        className="form-control"
                        placeholder="输入域名 (如: baidu.com)"
                        value={cookieDomain}
                        onChange={(e) => setCookieDomain(e.target.value)}
                        onKeyPress={(e) => handleKeyPress(e, getCookiesByDomain)}
                    />
                    <button className="btn" onClick={getCookiesByDomain}>
                        获取域名Cookie
                    </button>
                </div>

                {showCookies && cookies.length > 0 && (
                    <div className="cookie-list">
                        <h4>Cookie列表 ({cookies.length}个)</h4>
                        <div className="message-area" style={{ maxHeight: '120px' }}>
                            {cookies.slice(0, 10).map((cookie, index) => (
                                <div key={index} className="message">
                                    <div><strong>{cookie.name}</strong>: {cookie.value.substring(0, 50)}{cookie.value.length > 50 ? '...' : ''}</div>
                                    <div className="message-time">
                                        域名: {cookie.domain} | 路径: {cookie.path} | {cookie.secure ? '安全' : '普通'} | {cookie.httpOnly ? 'HttpOnly' : '可JS访问'}
                                    </div>
                                </div>
                            ))}
                            {cookies.length > 10 && (
                                <div className="message">
                                    <div>还有 {cookies.length - 10} 个Cookie...</div>
                                </div>
                            )}
                        </div>
                    </div>
                )}
            </div>


        </div>
    );
};

export default App;