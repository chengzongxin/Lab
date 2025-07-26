/**
 * Popup页面脚本 - 处理用户交互和与background script通信
 */

// DOM元素引用
const elements = {
    statusDot: document.getElementById('statusDot'),
    statusText: document.getElementById('statusText'),
    connectBtn: document.getElementById('connectBtn'),
    disconnectBtn: document.getElementById('disconnectBtn'),
    greetingBtn: document.getElementById('greetingBtn'),
    calculateBtn: document.getElementById('calculateBtn'),
    sendCustomBtn: document.getElementById('sendCustomBtn'),
    clearBtn: document.getElementById('clearBtn'),
    num1: document.getElementById('num1'),
    num2: document.getElementById('num2'),
    operation: document.getElementById('operation'),
    customMessage: document.getElementById('customMessage'),
    messageArea: document.getElementById('messageArea')
};

/**
 * 向background script发送消息
 * @param {Object} message - 要发送的消息对象
 * @returns {Promise} - 返回响应的Promise
 */
function sendToBackground(message) {
    return new Promise((resolve, reject) => {
        chrome.runtime.sendMessage(message, (response) => {
            if (chrome.runtime.lastError) {
                reject(chrome.runtime.lastError);
            } else {
                resolve(response);
            }
        });
    });
}

/**
 * 更新连接状态显示
 * @param {string} status - 连接状态
 * @param {string} text - 状态文本
 */
function updateConnectionStatus(status, text) {
    // 移除所有状态类
    elements.statusDot.classList.remove('status-connected', 'status-disconnected', 'status-connecting');
    
    // 添加对应的状态类
    switch (status) {
        case 'OPEN':
            elements.statusDot.classList.add('status-connected');
            elements.statusText.textContent = '已连接';
            elements.connectBtn.classList.add('hidden');
            elements.disconnectBtn.classList.remove('hidden');
            enableControls(true);
            break;
        case 'CONNECTING':
            elements.statusDot.classList.add('status-connecting');
            elements.statusText.textContent = '连接中...';
            elements.connectBtn.disabled = true;
            enableControls(false);
            break;
        case 'CLOSED':
        case 'UNKNOWN':
        default:
            elements.statusDot.classList.add('status-disconnected');
            elements.statusText.textContent = text || '未连接';
            elements.connectBtn.classList.remove('hidden');
            elements.disconnectBtn.classList.add('hidden');
            elements.connectBtn.disabled = false;
            enableControls(false);
            break;
    }
}

/**
 * 启用或禁用控制按钮
 * @param {boolean} enabled - 是否启用
 */
function enableControls(enabled) {
    elements.greetingBtn.disabled = !enabled;
    elements.calculateBtn.disabled = !enabled;
    elements.sendCustomBtn.disabled = !enabled;
}

/**
 * 添加消息到消息区域
 * @param {string} content - 消息内容
 * @param {string} type - 消息类型 ('sent', 'received', 'system')
 */
function addMessage(content, type = 'system') {
    const messageDiv = document.createElement('div');
    messageDiv.className = 'message';
    
    const timeDiv = document.createElement('div');
    timeDiv.className = 'message-time';
    timeDiv.textContent = new Date().toLocaleTimeString();
    
    const contentDiv = document.createElement('div');
    
    let prefix = '';
    switch (type) {
        case 'sent':
            prefix = '📤 发送: ';
            break;
        case 'received':
            prefix = '📥 接收: ';
            break;
        case 'system':
            prefix = '🔧 系统: ';
            break;
        case 'error':
            prefix = '❌ 错误: ';
            break;
    }
    
    contentDiv.textContent = prefix + content;
    
    messageDiv.appendChild(timeDiv);
    messageDiv.appendChild(contentDiv);
    
    elements.messageArea.appendChild(messageDiv);
    
    // 滚动到底部
    elements.messageArea.scrollTop = elements.messageArea.scrollHeight;
    
    // 限制消息数量，避免过多消息占用内存
    const messages = elements.messageArea.children;
    if (messages.length > 50) {
        elements.messageArea.removeChild(messages[0]);
    }
}

/**
 * 获取并更新连接状态
 */
async function updateStatus() {
    try {
        const response = await sendToBackground({ action: 'get_status' });
        if (response.success) {
            updateConnectionStatus(response.status, response.status);
        }
    } catch (error) {
        console.error('获取状态失败:', error);
        updateConnectionStatus('CLOSED', '获取状态失败');
    }
}

/**
 * 连接到WebSocket服务器
 */
async function connectToServer() {
    try {
        updateConnectionStatus('CONNECTING');
        addMessage('正在连接WebSocket服务器...', 'system');
        
        const response = await sendToBackground({ action: 'connect' });
        if (response.success) {
            addMessage(response.message, 'system');
            // 稍等一下再检查状态，因为连接是异步的
            setTimeout(updateStatus, 1000);
        } else {
            addMessage(response.message, 'error');
            updateConnectionStatus('CLOSED');
        }
    } catch (error) {
        console.error('连接失败:', error);
        addMessage('连接失败: ' + error.message, 'error');
        updateConnectionStatus('CLOSED');
    }
}

/**
 * 断开WebSocket连接
 */
async function disconnectFromServer() {
    try {
        const response = await sendToBackground({ action: 'disconnect' });
        addMessage(response.message, 'system');
        updateConnectionStatus('CLOSED');
    } catch (error) {
        console.error('断开连接失败:', error);
        addMessage('断开连接失败: ' + error.message, 'error');
    }
}

/**
 * 发送问候消息
 */
async function sendGreeting() {
    const message = {
        type: 'greeting',
        content: '你好，Python服务器！这是来自Popup的问候消息！'
    };
    
    await sendMessage(message);
}

/**
 * 发送计算请求
 */
async function sendCalculation() {
    const num1 = parseFloat(elements.num1.value) || 0;
    const num2 = parseFloat(elements.num2.value) || 0;
    const operation = elements.operation.value;
    
    const message = {
        type: 'calculation',
        num1: num1,
        num2: num2,
        operation: operation
    };
    
    await sendMessage(message);
}

/**
 * 发送自定义消息
 */
async function sendCustomMessage() {
    const messageText = elements.customMessage.value.trim();
    if (!messageText) {
        addMessage('请输入消息内容', 'error');
        return;
    }
    
    try {
        // 尝试解析为JSON
        const message = JSON.parse(messageText);
        await sendMessage(message);
    } catch (error) {
        // 如果不是有效JSON，作为普通文本发送
        const message = {
            type: 'text',
            content: messageText
        };
        await sendMessage(message);
    }
}

/**
 * 发送消息到background script
 * @param {Object} message - 要发送的消息
 */
async function sendMessage(message) {
    try {
        addMessage(JSON.stringify(message, null, 2), 'sent');
        
        const response = await sendToBackground({
            action: 'send_message',
            message: message
        });
        
        if (response.success) {
            addMessage(response.message, 'system');
        } else {
            addMessage(response.message, 'error');
        }
    } catch (error) {
        console.error('发送消息失败:', error);
        addMessage('发送消息失败: ' + error.message, 'error');
    }
}

/**
 * 清空消息记录
 */
function clearMessages() {
    elements.messageArea.innerHTML = '<div class="message"><div class="message-time">消息记录已清空</div></div>';
}

/**
 * 初始化事件监听器
 */
function initializeEventListeners() {
    // 连接按钮
    elements.connectBtn.addEventListener('click', connectToServer);
    
    // 断开连接按钮
    elements.disconnectBtn.addEventListener('click', disconnectFromServer);
    
    // 发送问候消息按钮
    elements.greetingBtn.addEventListener('click', sendGreeting);
    
    // 计算按钮
    elements.calculateBtn.addEventListener('click', sendCalculation);
    
    // 发送自定义消息按钮
    elements.sendCustomBtn.addEventListener('click', sendCustomMessage);
    
    // 清空消息按钮
    elements.clearBtn.addEventListener('click', clearMessages);
    
    // 回车键发送自定义消息
    elements.customMessage.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendCustomMessage();
        }
    });
    
    // 数字输入框回车键计算
    [elements.num1, elements.num2].forEach(input => {
        input.addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                sendCalculation();
            }
        });
    });
}

/**
 * 监听来自background script的消息
 */
function setupMessageListener() {
    // 注意：在popup中通常不需要监听runtime.onMessage
    // 因为popup主要是主动向background发送消息
    // 如果需要接收background的主动推送，可以使用以下代码：
    
    /*
    chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
        if (message.type === 'websocket_message') {
            addMessage(JSON.stringify(message.data), 'received');
        }
    });
    */
}

/**
 * 页面初始化
 */
function initialize() {
    console.log('Popup页面初始化');
    
    // 初始化事件监听器
    initializeEventListeners();
    
    // 设置消息监听器
    setupMessageListener();
    
    // 更新初始状态
    updateStatus();
    
    // 添加欢迎消息
    addMessage('WebSocket通信测试界面已加载', 'system');
    addMessage('请先点击"连接服务器"按钮建立连接', 'system');
}

// 当DOM加载完成时初始化
document.addEventListener('DOMContentLoaded', initialize); 