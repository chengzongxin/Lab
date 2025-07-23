import React, { useState, useRef } from 'react';
import axios from 'axios';
import './CrawlerControl.css';

interface CrawlerControlProps {
  onCrawlComplete: () => void;
}

const CrawlerControl: React.FC<CrawlerControlProps> = ({ onCrawlComplete }) => {
  const [keyword, setKeyword] = useState('');
  const [pages, setPages] = useState(1);
  const [isCrawling, setIsCrawling] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState<'success' | 'error' | 'info'>('info');
  const [crawlStatus, setCrawlStatus] = useState<any>(null);
  const statusTimer = useRef<NodeJS.Timeout | null>(null);

  const startPollingStatus = () => {
    if (statusTimer.current) clearInterval(statusTimer.current);
    console.log('开始轮询爬虫状态...');
    statusTimer.current = setInterval(async () => {
      try {
        console.log('正在请求爬虫状态...');
        const res = await axios.get('http://localhost:8000/api/crawl_status');
        console.log('收到爬虫状态:', res.data);
        setCrawlStatus(res.data);
        
        // 只有当爬虫真正完成时才停止轮询和重置状态
        if (res.data.step === '完成' || res.data.step === '空闲') {
          console.log('爬虫完成，停止轮询');
          clearInterval(statusTimer.current!);
          statusTimer.current = null;
          setIsCrawling(false);
          setMessage('爬取完成！');
          setMessageType('success');
          onCrawlComplete();
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
    if (!keyword.trim()) {
      setMessage('请输入搜索关键词');
      setMessageType('error');
      return;
    }

    setIsCrawling(true);
    setMessage('正在启动爬虫...');
    setMessageType('info');
    setCrawlStatus(null);
    
    // 先启动轮询
    startPollingStatus();

    try {
      const response = await axios.post('http://localhost:8000/api/crawl', {
        keyword: keyword.trim(),
        pages: pages
      });
      
      // 启动成功，但不要立即停止轮询
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

  const handleClearData = async () => {
    if (!window.confirm('确定要清空所有商品数据吗？此操作不可恢复。')) {
      return;
    }

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

  // 组件卸载时清理定时器
  React.useEffect(() => {
    return () => {
      stopPollingStatus();
    };
  }, []);

  return (
    <div className="crawler-control">
      <div className="crawler-form">
        <div className="form-group">
          <label htmlFor="keyword">搜索关键词：</label>
          <input
            id="keyword"
            type="text"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            placeholder="例如：cats, dogs, nature..."
            disabled={isCrawling}
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="pages">爬取页数：</label>
          <select
            id="pages"
            value={pages}
            onChange={(e) => setPages(Number(e.target.value))}
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
            disabled={isCrawling || !keyword.trim()}
          >
            {isCrawling ? '爬取中...' : '开始爬取'}
          </button>
          
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
        <div className={`message ${messageType}`}>
          {message}
        </div>
      )}

      {/* 进度条与状态显示 */}
      {crawlStatus && crawlStatus.step !== '空闲' && (
        <div className="crawl-status-bar">
          <div className="crawl-status-text">
            {crawlStatus.step} {crawlStatus.title && `：${crawlStatus.title}`}
          </div>
          <div className="crawl-status-progress">
            <span>{crawlStatus.current}/{crawlStatus.total}</span>
            <progress value={crawlStatus.current} max={crawlStatus.total} style={{ width: 200, marginLeft: 8, marginRight: 8 }} />
            <span>{Math.round((crawlStatus.current / (crawlStatus.total || 1)) * 100)}%</span>
          </div>
        </div>
      )}
      
      {isCrawling && (
        <div className="crawling-status">
          <div className="spinner"></div>
          <span>正在爬取数据，请稍候...</span>
        </div>
      )}
    </div>
  );
};

export default CrawlerControl; 