import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './CrawlerControl.css';

interface CrawlerControlProps {
  onCrawlComplete: () => void;
}

interface TaskStatus {
  id: string;
  keyword: string;
  pages: number;
  status: 'pending' | 'running' | 'completed' | 'failed';
  progress: {
    current: number;
    total: number;
  };
  step: string;
  title: string;
  created_at: string;
  updated_at: string;
  current_score?: number;
  category?: string;
}

const categoryOptions = [
  { value: 'u-clothing', label: '衣服' },
  { value: 'u-bags', label: '包' },
  { value: 'u-socks', label: '袜子' },
  { value: 'u-masks', label: '口罩' },
  { value: 'u-cases', label: '手机壳' },
  { value: 'u-stickers', label: '贴纸' },
  { value: 'u-wall-art', label: '墙饰' },
  { value: 'u-home-decor', label: '家居' },
  { value: 'u-stationery', label: '文具' },
  { value: 'u-kids-babies', label: '儿童婴儿' },
];

const CrawlerControl: React.FC<CrawlerControlProps> = ({ onCrawlComplete }) => {
  const [keyword, setKeyword] = useState('');
  const [category, setCategory] = useState('u-clothing');
  const [pages, setPages] = useState(1);
  const [isCrawling, setIsCrawling] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState<'success' | 'error' | 'info'>('info');
  const [currentTask, setCurrentTask] = useState<TaskStatus | null>(null);
  const statusTimer = useRef<NodeJS.Timeout | null>(null);

  // 页面加载时检查是否有正在运行的任务
  useEffect(() => {
    checkRunningTask();
  }, []);

  const checkRunningTask = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/crawl/status');
      if (response.data.has_running_task) {
        setCurrentTask(response.data.current_task);
        setIsCrawling(true);
        startPollingStatus();
        setMessage('检测到正在运行的任务，正在监控进度...');
        setMessageType('info');
      }
    } catch (error) {
      console.error('检查运行中任务失败:', error);
    }
  };

  const startPollingStatus = () => {
    if (statusTimer.current) clearInterval(statusTimer.current);
    statusTimer.current = setInterval(async () => {
      try {
        const res = await axios.get('http://localhost:8000/api/crawl/status');
        if (res.data.has_running_task) {
          setCurrentTask(res.data.current_task);
          setIsCrawling(true);
          if (res.data.current_task.status === 'completed' || res.data.current_task.status === 'failed') {
            clearInterval(statusTimer.current!);
            statusTimer.current = null;
            setIsCrawling(false);
            if (res.data.current_task.status === 'completed') {
              setMessage('爬取完成！');
              setMessageType('success');
              onCrawlComplete();
              setTimeout(() => window.location.reload(), 1000);
            } else {
              setMessage('爬取失败，请重试');
              setMessageType('error');
            }
            setCurrentTask(null);
          }
        } else {
          setCurrentTask(null);
          setIsCrawling(false);
          clearInterval(statusTimer.current!);
          statusTimer.current = null;
        }
      } catch (e) {
        console.error('轮询状态失败:', e);
      }
    }, 1000);
  };

  const stopPollingStatus = () => {
    if (statusTimer.current) {
      clearInterval(statusTimer.current);
      statusTimer.current = null;
    }
  };

  const handleCrawl = async () => {
    setIsCrawling(true);
    setMessage('正在启动爬虫...');
    setMessageType('info');
    setCurrentTask(null);
    startPollingStatus();
    try {
      const response = await axios.post('http://localhost:8000/api/crawl', {
        keyword: keyword.trim(),
        pages,
        category
      });
      setMessage('爬虫已启动，正在后台运行...');
      setMessageType('info');
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || '爬虫启动失败，请检查后端服务';
      setMessage(errorMessage);
      setMessageType('error');
      setIsCrawling(false);
      stopPollingStatus();
    }
  };

  const handleCancelTask = async () => {
    if (!currentTask) return;
    if (!window.confirm('确定要取消当前任务吗？')) return;
    try {
      await axios.delete(`http://localhost:8000/api/crawl/tasks/${currentTask.id}`);
      setMessage('任务已取消');
      setMessageType('info');
      setIsCrawling(false);
      setCurrentTask(null);
      stopPollingStatus();
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || '取消任务失败';
      setMessage(errorMessage);
      setMessageType('error');
    }
  };

  const handleClearData = async () => {
    if (!window.confirm('确定要清空所有商品数据吗？此操作不可恢复。')) return;
    try {
      await axios.delete('http://localhost:8000/api/products');
      setMessage('已清空所有商品数据');
      setMessageType('success');
      onCrawlComplete();
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || '清空数据失败';
      setMessage(errorMessage);
      setMessageType('error');
    }
  };

  useEffect(() => {
    return () => {
      stopPollingStatus();
    };
  }, []);

  const getProgressPercentage = () => {
    if (!currentTask || currentTask.progress.total === 0) return 0;
    return Math.round((currentTask.progress.current / currentTask.progress.total) * 100);
  };

  return (
    <div className="crawler-control">
      <div className="crawler-form">
        <div className="form-group">
          <label htmlFor="category">类目：</label>
          <select
            id="category"
            value={category}
            onChange={e => setCategory(e.target.value)}
            disabled={isCrawling}
          >
            {categoryOptions.map(opt => (
              <option value={opt.value} key={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
        <div className="form-group">
          <label htmlFor="keyword">关键词（可选）：</label>
          <input
            id="keyword"
            type="text"
            value={keyword}
            onChange={e => setKeyword(e.target.value)}
            placeholder="如：cats, dogs, nature..."
            disabled={isCrawling}
          />
        </div>
        <div className="form-group">
          <label htmlFor="pages">爬取页数：</label>
          <select
            id="pages"
            value={pages}
            onChange={e => setPages(Number(e.target.value))}
            disabled={isCrawling}
          >
            <option value={1}>1 页</option>
            <option value={2}>2 页</option>
            <option value={3}>3 页</option>
            <option value={5}>5 页</option>
            <option value={10}>10 页</option>
          </select>
        </div>
        <div className="form-actions">
          <button
            className="crawl-button"
            onClick={handleCrawl}
            disabled={isCrawling}
          >
            {isCrawling ? '爬取中...' : '开始爬取'}
          </button>
          {isCrawling && currentTask && (
            <button className="cancel-button" onClick={handleCancelTask}>取消任务</button>
          )}
          <button
            className="clear-button"
            onClick={handleClearData}
            disabled={isCrawling}
          >
            清空数据
          </button>
        </div>
      </div>
      {message && (
        <div className={`message ${messageType}`}>{message}</div>
      )}
      {currentTask && (
        <div className="task-status">
          <div className="task-info">
            <h4>当前任务</h4>
            <p><strong>类目:</strong> {categoryOptions.find(opt => opt.value === currentTask.category)?.label || currentTask.category}</p>
            <p><strong>关键词:</strong> {currentTask.keyword}</p>
            <p><strong>页数:</strong> {currentTask.pages}</p>
            <p><strong>状态:</strong> {currentTask.status}</p>
            <p><strong>步骤:</strong> {currentTask.step}</p>
            {currentTask.title && (
              <p><strong>当前商品:</strong> {currentTask.title}</p>
            )}
            <p><strong>当前商品评分:</strong> {currentTask.current_score ?? '--'}</p>
          </div>
          <div className="task-progress">
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${getProgressPercentage()}%` }}></div>
            </div>
            <div className="progress-text">
              {currentTask.progress.current}/{currentTask.progress.total} ({getProgressPercentage()}%)
            </div>
          </div>
        </div>
      )}
      {isCrawling && !currentTask && (
        <div className="crawling-status">
          <div className="spinner"></div>
          <span>正在爬取数据，请稍候...</span>
        </div>
      )}
    </div>
  );
};

export default CrawlerControl; 