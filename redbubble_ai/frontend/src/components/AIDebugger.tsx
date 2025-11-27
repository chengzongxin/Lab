import React, { useState, useEffect, useRef } from 'react';
import axios from 'axios';
import './AIDebugger.css';

interface Message {
  role: 'system' | 'user' | 'assistant';
  content: string;
}

interface Preset {
  name: string;
  description: string;
  system_prompt: string;
  user_prompt: string;
  model: string;
  temperature: number;
  max_tokens: number;
}

interface ChatResponse {
  success: boolean;
  message?: string;
  error?: string;
  model?: string;
  usage?: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
  };
}

const AIDebugger: React.FC = () => {
  // 状态管理
  const [presets, setPresets] = useState<Preset[]>([]);
  const [selectedPreset, setSelectedPreset] = useState<string>('');
  
  // 对话参数
  const [systemPrompt, setSystemPrompt] = useState<string>('');
  const [userMessage, setUserMessage] = useState<string>('');
  const [model, setModel] = useState<string>('gpt-4o-mini');
  const [temperature, setTemperature] = useState<number>(0.7);
  const [maxTokens, setMaxTokens] = useState<number>(500);
  
  // 对话历史
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState<boolean>(false);
  const [lastUsage, setLastUsage] = useState<any>(null);
  
  // 聊天容器引用（用于自动滚动）
  const chatContainerRef = useRef<HTMLDivElement>(null);

  // 加载预设
  useEffect(() => {
    loadPresets();
  }, []);

  // 自动滚动到底部
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const loadPresets = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/ai-debugger/presets');
      if (response.data.success) {
        setPresets(response.data.presets);
      }
    } catch (error) {
      console.error('加载预设失败:', error);
      alert('加载预设失败，请检查后端服务');
    }
  };

  const applyPreset = (presetName: string) => {
    const preset = presets.find(p => p.name === presetName);
    if (preset) {
      setSystemPrompt(preset.system_prompt);
      setUserMessage(preset.user_prompt);
      setModel(preset.model);
      setTemperature(preset.temperature);
      setMaxTokens(preset.max_tokens);
      setSelectedPreset(presetName);
      
      // 重置对话历史
      setMessages([]);
      setLastUsage(null);
    }
  };

  const sendMessage = async () => {
    if (!userMessage.trim()) {
      alert('请输入用户消息');
      return;
    }

    setIsLoading(true);

    // 构建消息列表
    const newMessages: Message[] = [];
    
    // 添加系统提示词（如果有）
    if (systemPrompt.trim()) {
      newMessages.push({
        role: 'system',
        content: systemPrompt
      });
    }
    
    // 添加历史对话
    messages.forEach(msg => {
      if (msg.role !== 'system') {
        newMessages.push(msg);
      }
    });
    
    // 添加当前用户消息
    newMessages.push({
      role: 'user',
      content: userMessage
    });

    try {
      const response = await axios.post<ChatResponse>(
        'http://localhost:8000/api/ai-debugger/chat',
        {
          messages: newMessages,
          model: model,
          temperature: temperature,
          max_tokens: maxTokens
        }
      );

      if (response.data.success && response.data.message) {
        // 更新对话历史
        setMessages([
          ...messages,
          { role: 'user', content: userMessage },
          { role: 'assistant', content: response.data.message }
        ]);
        
        // 更新token使用情况
        if (response.data.usage) {
          setLastUsage(response.data.usage);
        }
        
        // 清空用户输入
        setUserMessage('');
      } else {
        alert(`AI响应失败: ${response.data.error || '未知错误'}`);
      }
    } catch (error: any) {
      console.error('发送消息失败:', error);
      alert(`发送失败: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const clearChat = () => {
    if (window.confirm('确定要清空对话历史吗？')) {
      setMessages([]);
      setLastUsage(null);
      setUserMessage('');
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    // Ctrl+Enter 或 Cmd+Enter 发送消息
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="ai-debugger">
      <div className="debugger-header">
        <h1>🤖 AI 对话调试器</h1>
        <p className="subtitle">测试和调试AI功能，支持自定义提示词和参数</p>
      </div>

      <div className="debugger-layout">
        {/* 左侧：参数配置区 */}
        <div className="config-panel">
          <div className="panel-section">
            <h3>📋 预设模板</h3>
            <select 
              className="preset-select"
              value={selectedPreset}
              onChange={(e) => applyPreset(e.target.value)}
            >
              <option value="">-- 选择预设 --</option>
              {presets.map(preset => (
                <option key={preset.name} value={preset.name}>
                  {preset.name}
                </option>
              ))}
            </select>
            {selectedPreset && (
              <div className="preset-description">
                {presets.find(p => p.name === selectedPreset)?.description}
              </div>
            )}
          </div>

          <div className="panel-section">
            <h3>⚙️ 模型参数</h3>
            
            <label>
              <span className="label-text">模型</span>
              <input
                type="text"
                className="param-input"
                value={model}
                onChange={(e) => setModel(e.target.value)}
                placeholder="gpt-4o-mini"
              />
            </label>

            <label>
              <span className="label-text">
                温度 (Temperature): {temperature}
              </span>
              <input
                type="range"
                className="param-slider"
                min="0"
                max="2"
                step="0.1"
                value={temperature}
                onChange={(e) => setTemperature(parseFloat(e.target.value))}
              />
              <small className="param-hint">越高越随机，越低越确定</small>
            </label>

            <label>
              <span className="label-text">最大Tokens: {maxTokens}</span>
              <input
                type="range"
                className="param-slider"
                min="50"
                max="2000"
                step="50"
                value={maxTokens}
                onChange={(e) => setMaxTokens(parseInt(e.target.value))}
              />
              <small className="param-hint">控制响应长度</small>
            </label>
          </div>

          <div className="panel-section">
            <h3>💬 系统提示词 (System Prompt)</h3>
            <textarea
              className="system-prompt-input"
              value={systemPrompt}
              onChange={(e) => setSystemPrompt(e.target.value)}
              placeholder="设置AI的角色和行为..."
              rows={10}
            />
          </div>

          {lastUsage && (
            <div className="panel-section usage-info">
              <h3>📊 Token 使用</h3>
              <div className="usage-stats">
                <div className="usage-item">
                  <span className="usage-label">提示词:</span>
                  <span className="usage-value">{lastUsage.prompt_tokens}</span>
                </div>
                <div className="usage-item">
                  <span className="usage-label">响应:</span>
                  <span className="usage-value">{lastUsage.completion_tokens}</span>
                </div>
                <div className="usage-item total">
                  <span className="usage-label">总计:</span>
                  <span className="usage-value">{lastUsage.total_tokens}</span>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* 右侧：对话区 */}
        <div className="chat-panel">
          <div className="chat-header">
            <h3>💭 对话历史</h3>
            <button 
              className="btn-clear"
              onClick={clearChat}
              disabled={messages.length === 0}
            >
              🗑️ 清空
            </button>
          </div>

          <div className="chat-container" ref={chatContainerRef}>
            {messages.length === 0 ? (
              <div className="empty-chat">
                <p>👋 还没有对话记录</p>
                <p className="hint">在下方输入消息开始对话</p>
              </div>
            ) : (
              messages.map((msg, index) => (
                <div key={index} className={`message message-${msg.role}`}>
                  <div className="message-header">
                    <span className="message-role">
                      {msg.role === 'user' ? '👤 用户' : '🤖 AI助手'}
                    </span>
                  </div>
                  <div className="message-content">
                    {msg.content}
                  </div>
                </div>
              ))
            )}
            
            {isLoading && (
              <div className="message message-assistant loading">
                <div className="message-header">
                  <span className="message-role">🤖 AI助手</span>
                </div>
                <div className="message-content">
                  <span className="loading-dots">思考中</span>
                </div>
              </div>
            )}
          </div>

          <div className="chat-input-area">
            <textarea
              className="chat-input"
              value={userMessage}
              onChange={(e) => setUserMessage(e.target.value)}
              onKeyDown={handleKeyPress}
              placeholder="输入消息... (Ctrl+Enter 或 Cmd+Enter 发送)"
              rows={3}
              disabled={isLoading}
            />
            <div className="input-actions">
              <small className="input-hint">
                ⌨️ 快捷键: Ctrl/Cmd + Enter 发送
              </small>
              <button
                className="btn-send"
                onClick={sendMessage}
                disabled={isLoading || !userMessage.trim()}
              >
                {isLoading ? '发送中...' : '📤 发送'}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AIDebugger;

