import React, { useState } from 'react';
import axios from 'axios';
import './TemuCategoryCrawler.css';

interface TemuCategoryCrawlerProps {
  onCrawlComplete?: () => void;
}

const TemuCategoryCrawler: React.FC<TemuCategoryCrawlerProps> = () => {
  const [categoryUrl, setCategoryUrl] = useState('');
  const [minSales, setMinSales] = useState(200);
  const [crawlDetails, setCrawlDetails] = useState(false);
  const [crawlSellerProducts, setCrawlSellerProducts] = useState(false);
  const [debugPort, setDebugPort] = useState<number | null>(null);
  const [usePersistentContext, setUsePersistentContext] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [message, setMessage] = useState('');

  const startCrawl = async () => {
    if (!categoryUrl.trim()) {
      setMessage('❌ 请输入类目URL');
      return;
    }

    setIsRunning(true);
    setMessage('正在启动TEMU类目爬取...');

    try {
      const response = await axios.post('http://localhost:8000/api/crawl/temu/category', {
        category_url: categoryUrl.trim(),
        min_sales: minSales,
        crawl_details: crawlDetails,
        crawl_seller_products: crawlSellerProducts,
        use_persistent_context: usePersistentContext,
        debug_port: debugPort
      });

      if (response.data.success) {
        setMessage(`✅ ${response.data.message}`);
      }
    } catch (error: any) {
      setMessage(`❌ 启动失败: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="temu-category-crawler">
      <div className="header">
        <h2>📦 TEMU类目商品爬取</h2>
        <p className="subtitle">爬取指定类目下的所有爆款商品，支持销量筛选</p>
      </div>

      <div className="form-container">
        <div className="form-group">
          <label>类目URL</label>
          <input
            type="text"
            value={categoryUrl}
            onChange={(e) => setCategoryUrl(e.target.value)}
            placeholder="https://www.temu.com/channel/xxxxx.html"
            className="input-url"
          />
          <span className="hint">粘贴TEMU类目页面的完整链接</span>
        </div>

        <div className="form-row">
          <div className="form-group">
            <label>最小销量</label>
            <input
              type="number"
              value={minSales}
              onChange={(e) => setMinSales(parseInt(e.target.value))}
              min="0"
              className="input-number"
            />
            <span className="hint">只保存销量大于此值的商品</span>
          </div>

          <div className="form-group">
            <label>调试端口（可选）</label>
            <input
              type="number"
              value={debugPort || ''}
              onChange={(e) => setDebugPort(e.target.value ? parseInt(e.target.value) : null)}
              placeholder="9222"
              className="input-number"
            />
            <span className="hint">连接已打开的浏览器（高级）</span>
          </div>
        </div>

        <div className="checkbox-group">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={crawlDetails}
              onChange={(e) => setCrawlDetails(e.target.checked)}
            />
            <span>爬取商品详情（获取卖家信息）</span>
          </label>
        </div>

        {crawlDetails && (
          <div className="checkbox-group" style={{ marginLeft: '24px' }}>
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={crawlSellerProducts}
                onChange={(e) => setCrawlSellerProducts(e.target.checked)}
              />
              <span>同时爬取卖家店铺所有商品</span>
            </label>
          </div>
        )}

        <div className="checkbox-group">
          <label className="checkbox-label">
            <input
              type="checkbox"
              checked={usePersistentContext}
              onChange={(e) => setUsePersistentContext(e.target.checked)}
            />
            <span>使用持久化上下文（保持登录状态）</span>
          </label>
        </div>

        <button
          className="btn-start"
          onClick={startCrawl}
          disabled={isRunning}
        >
          {isRunning ? '⏳ 爬取中...' : '🚀 开始爬取'}
        </button>

        {message && (
          <div className={`message ${message.startsWith('❌') ? 'error' : 'success'}`}>
            {message}
          </div>
        )}
      </div>

      <div className="info-box">
        <h3>📖 使用说明</h3>
        <ol>
          <li>访问TEMU，找到目标类目页面（如"袜子"、"T恤"等）</li>
          <li>复制类目页面的完整URL</li>
          <li>粘贴到上方输入框，设置最小销量筛选条件</li>
          <li>点击"开始爬取"，等待爬取完成</li>
          <li>爬取的商品会自动保存到数据库的 <code>temu_products</code> 表</li>
        </ol>
      </div>
    </div>
  );
};

export default TemuCategoryCrawler;
