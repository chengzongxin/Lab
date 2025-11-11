import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './TemuCategoryCrawler.css';

interface TemuCategoryCrawlerProps {
  onCrawlComplete?: () => void;
}

const TemuCategoryCrawler: React.FC<TemuCategoryCrawlerProps> = ({ onCrawlComplete }) => {
  const [categoryUrl, setCategoryUrl] = useState('');
  const [minSales, setMinSales] = useState(1000);
  const [crawlDetails, setCrawlDetails] = useState(true);
  const [crawlSellerProducts, setCrawlSellerProducts] = useState(true);
  const [usePersistentContext, setUsePersistentContext] = useState(false);
  const [userDataDir, setUserDataDir] = useState('');
  const [debugPort, setDebugPort] = useState<number | null>(9222);
  const [isCrawling, setIsCrawling] = useState(false);
  const [message, setMessage] = useState('');
  const [messageType, setMessageType] = useState<'success' | 'error' | 'info'>('info');
  const [taskId, setTaskId] = useState<string | null>(null);
  const statusTimer = useRef<NodeJS.Timeout | null>(null);

  // 示例URL
  const exampleUrls = [
    {
      label: '男士帽子',
      url: 'https://www.temu.com/ca/mens-hats-caps-o3-800.html?opt_level=2&title=Men%27s%20Hats%20%26%20Caps&_x_enter_scene_type=cate_tab'
    },
    {
      label: '女士服装',
      url: 'https://www.temu.com/ca/womens-clothing-o3-800.html?opt_level=2&title=Women%27s%20Clothing&_x_enter_scene_type=cate_tab'
    }
  ];

  const stopPollingStatus = () => {
    if (statusTimer.current) {
      clearInterval(statusTimer.current);
      statusTimer.current = null;
    }
  };

  const startPollingStatus = () => {
    if (statusTimer.current) clearInterval(statusTimer.current);
    statusTimer.current = setInterval(async () => {
      try {
        // 检查任务状态（这里可以扩展为检查TEMU任务状态）
        const res = await axios.get('http://localhost:8000/api/crawl/status');
        // 注意：这里需要根据实际API调整
        // 目前先简单检查，后续可以添加专门的TEMU任务状态接口
      } catch (e) {
        console.error('轮询状态失败:', e);
      }
    }, 2000);
  };

  const handleCrawl = async () => {
    if (!categoryUrl.trim()) {
      setMessage('请输入类目URL');
      setMessageType('error');
      return;
    }

    setIsCrawling(true);
    setMessage('正在启动TEMU类目爬取工作流...');
    setMessageType('info');
    setTaskId(null);
    
    try {
      const requestData: any = {
        category_url: categoryUrl.trim(),
        min_sales: minSales,
        crawl_details: crawlDetails,
        crawl_seller_products: crawlSellerProducts,
        use_persistent_context: usePersistentContext,
      };

      if (userDataDir) {
        requestData.user_data_dir = userDataDir;
      }

      if (debugPort) {
        requestData.debug_port = debugPort;
      }

      const response = await axios.post('http://localhost:8000/api/crawl/temu/category', requestData);
      
      setTaskId(response.data.task_id);
      setMessage(response.data.message || '工作流已启动，正在后台运行...');
      setMessageType('info');
      startPollingStatus();
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || '工作流启动失败，请检查后端服务';
      setMessage(errorMessage);
      setMessageType('error');
      setIsCrawling(false);
      stopPollingStatus();
    }
  };

  const handleUseExample = (url: string) => {
    setCategoryUrl(url);
  };

  useEffect(() => {
    return () => {
      stopPollingStatus();
    };
  }, []);

  return (
    <div className="temu-category-crawler">
      <div className="crawler-header">
        <h3>TEMU 类目爆款商品爬取</h3>
        <p className="subtitle">爬取指定类目下的所有爆款商品（销量≥1000），并自动爬取商品详情和卖家店铺商品</p>
      </div>

      <div className="crawler-form">
        <div className="form-section">
          <h4>基本设置</h4>
          
          <div className="form-group">
            <label htmlFor="category-url">
              类目URL <span className="required">*</span>
            </label>
            <input
              id="category-url"
              type="text"
              value={categoryUrl}
              onChange={e => setCategoryUrl(e.target.value)}
              placeholder="https://www.temu.com/ca/mens-hats-caps-o3-800.html?..."
              disabled={isCrawling}
              className="url-input"
            />
            <div className="example-urls">
              <span className="example-label">示例URL：</span>
              {exampleUrls.map((example, idx) => (
                <button
                  key={idx}
                  type="button"
                  className="example-btn"
                  onClick={() => handleUseExample(example.url)}
                  disabled={isCrawling}
                >
                  {example.label}
                </button>
              ))}
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="min-sales">
              最小销量 <span className="required">*</span>
            </label>
            <input
              id="min-sales"
              type="number"
              value={minSales}
              onChange={e => setMinSales(Number(e.target.value))}
              min="0"
              disabled={isCrawling}
            />
            <span className="form-hint">只爬取销量大于等于此值的爆款商品</span>
          </div>
        </div>

        <div className="form-section">
          <h4>爬取选项</h4>
          
          <div className="form-group checkbox-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={crawlDetails}
                onChange={e => setCrawlDetails(e.target.checked)}
                disabled={isCrawling}
              />
              <span>爬取商品详情（获取卖家店铺信息）</span>
            </label>
          </div>

          <div className="form-group checkbox-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={crawlSellerProducts}
                onChange={e => setCrawlSellerProducts(e.target.checked)}
                disabled={isCrawling}
              />
              <span>爬取卖家店铺商品</span>
            </label>
          </div>
        </div>

        <div className="form-section">
          <h4>浏览器设置（可选）</h4>
          
          <div className="form-group checkbox-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={usePersistentContext}
                onChange={e => setUsePersistentContext(e.target.checked)}
                disabled={isCrawling}
              />
              <span>使用持久化上下文（保持登录状态）</span>
            </label>
          </div>

          {usePersistentContext && (
            <div className="form-group">
              <label htmlFor="user-data-dir">用户数据目录：</label>
              <input
                id="user-data-dir"
                type="text"
                value={userDataDir}
                onChange={e => setUserDataDir(e.target.value)}
                placeholder="/tmp/chrome_debug"
                disabled={isCrawling}
              />
              <span className="form-hint">留空则使用临时目录</span>
            </div>
          )}

          <div className="form-group">
            <label htmlFor="debug-port">调试端口：</label>
            <input
              id="debug-port"
              type="number"
              value={debugPort || ''}
              onChange={e => setDebugPort(e.target.value ? Number(e.target.value) : null)}
              placeholder="9222"
              disabled={isCrawling}
            />
            <span className="form-hint">连接到已打开的Chrome浏览器（推荐）</span>
          </div>
        </div>

        <div className="form-actions">
          <button
            className="crawl-button"
            onClick={handleCrawl}
            disabled={isCrawling || !categoryUrl.trim()}
          >
            {isCrawling ? '爬取中...' : '开始爬取'}
          </button>
        </div>
      </div>

      {message && (
        <div className={`message ${messageType}`}>{message}</div>
      )}

      {isCrawling && (
        <div className="crawling-status">
          <div className="spinner"></div>
          <div className="status-info">
            <span className="status-text">工作流正在运行中...</span>
            <span className="status-detail">请保持浏览器打开，任务在后台执行</span>
          </div>
        </div>
      )}

      {taskId && (
        <div className="task-info">
          <p><strong>任务ID:</strong> {taskId}</p>
          <p className="info-hint">任务正在后台执行，完成后会自动保存到数据库</p>
        </div>
      )}

      <div className="workflow-steps">
        <h4>工作流程</h4>
        <ol>
          <li>保存类目信息到数据库</li>
          <li>爬取类目下的所有商品，筛选销量≥{minSales}的爆款商品</li>
          {crawlDetails && <li>爬取每个商品的详情页，提取卖家店铺信息</li>}
          {crawlSellerProducts && <li>爬取每个卖家的店铺所有商品</li>}
          <li>所有数据自动保存到数据库</li>
        </ol>
      </div>
    </div>
  );
};

export default TemuCategoryCrawler;

