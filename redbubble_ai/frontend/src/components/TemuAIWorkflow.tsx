import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './TemuAIWorkflow.css';

interface AIWorkflowStats {
  cleaning: {
    total: number;
    completed: number;
  };
  matches: {
    matched_products: number;
    total_matches: number;
  };
}

interface RedbubbleResult {
  id: number;
  redbubble_title: string;
  redbubble_img: string;
  redbubble_link: string;
  redbubble_score: number;
  match_score: number;
  rank_position: number;
  created_at: string;
}

interface TemuProduct {
  id: number;
  goods_id: string;
  title: string;
  img: string;
  price: string;
  sales_count: number;
  category_id: number;
}

interface ProductWithMatches {
  temu_product: TemuProduct;
  cleaned_keywords: string;
  cleaning_status: string;
  cleaned_at: string | null;
  redbubble_results: RedbubbleResult[];
}

const TemuAIWorkflow: React.FC = () => {
  const [categoryId, setCategoryId] = useState<string>('');
  const [batchSize, setBatchSize] = useState<number>(10);
  const [redbubblePages, setRedbubblePages] = useState<number>(2);
  const [isRunning, setIsRunning] = useState(false);
  const [message, setMessage] = useState('');
  const [stats, setStats] = useState<AIWorkflowStats | null>(null);
  const [products, setProducts] = useState<ProductWithMatches[]>([]);
  const [isLoadingProducts, setIsLoadingProducts] = useState(false);

  // 加载统计信息
  const loadStats = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/temu/ai-workflow/stats');
      setStats(response.data);
    } catch (error) {
      console.error('加载统计失败:', error);
    }
  };

  // 加载TEMU商品及其匹配结果
  const loadProducts = async () => {
    setIsLoadingProducts(true);
    try {
      const response = await axios.get('http://localhost:8000/api/temu/products-with-matches', {
        params: {
          limit: 20,
          offset: 0,
          min_match_score: 0.3
        }
      });
      setProducts(response.data.products || []);
    } catch (error) {
      console.error('加载商品数据失败:', error);
      setProducts([]);
    } finally {
      setIsLoadingProducts(false);
    }
  };

  // 页面加载时获取统计和商品数据
  useEffect(() => {
    loadStats();
    loadProducts();
    const interval = setInterval(() => {
      loadStats();
    }, 5000); // 每5秒刷新统计

    return () => clearInterval(interval);
  }, []);

  // 启动AI工作流
  const startWorkflow = async () => {
    if (isRunning) {
      setMessage('工作流正在运行中，请稍候...');
      return;
    }

    setIsRunning(true);
    setMessage('正在启动AI标题清洗工作流...');

    try {
      const response = await axios.post('http://localhost:8000/api/temu/ai-workflow', {
        category_id: categoryId ? parseInt(categoryId) : null,
        batch_size: batchSize,
        redbubble_pages: redbubblePages
      });

      if (response.data.success) {
        setMessage(`✅ ${response.data.message} (任务ID: ${response.data.task_id})`);
        // 启动后等待一段时间再刷新数据
        setTimeout(() => {
          loadStats();
          loadProducts();
        }, 3000);
      } else {
        setMessage('❌ 启动失败');
      }
    } catch (error: any) {
      console.error('启动工作流失败:', error);
      setMessage(`❌ 启动失败: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  return (
    <div className="temu-ai-workflow">
      <div className="workflow-header">
        <h2>🤖 TEMU商品 AI标题清洗 + Redbubble搜索</h2>
        <p className="workflow-description">
          使用AI清洗TEMU商品标题，提取核心关键词，然后在Redbubble搜索相似设计
        </p>
      </div>

      {/* 统计信息 */}
      {stats && (
        <div className="stats-container">
          <div className="stat-card">
            <div className="stat-label">已清洗标题</div>
            <div className="stat-value">{stats.cleaning.completed} / {stats.cleaning.total}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">已匹配商品</div>
            <div className="stat-value">{stats.matches.matched_products}</div>
          </div>
          <div className="stat-card">
            <div className="stat-label">总搜索结果</div>
            <div className="stat-value">{stats.matches.total_matches}</div>
          </div>
        </div>
      )}

      {/* 控制面板 */}
      <div className="control-panel">
        <div className="form-group">
          <label htmlFor="categoryId">
            类目ID（可选）
            <span className="help-text">留空处理所有类目</span>
          </label>
          <input
            id="categoryId"
            type="text"
            value={categoryId}
            onChange={(e) => setCategoryId(e.target.value)}
            placeholder="例如: 1"
            disabled={isRunning}
          />
        </div>

        <div className="form-group">
          <label htmlFor="batchSize">
            批量处理数量
            <span className="help-text">每次处理多少个商品</span>
          </label>
          <input
            id="batchSize"
            type="number"
            value={batchSize}
            onChange={(e) => setBatchSize(parseInt(e.target.value))}
            min="1"
            max="50"
            disabled={isRunning}
          />
        </div>

        <div className="form-group">
          <label htmlFor="redbubblePages">
            Redbubble搜索页数
            <span className="help-text">每个关键词搜索几页</span>
          </label>
          <input
            id="redbubblePages"
            type="number"
            value={redbubblePages}
            onChange={(e) => setRedbubblePages(parseInt(e.target.value))}
            min="1"
            max="5"
            disabled={isRunning}
          />
        </div>

        <button
          className={`start-button ${isRunning ? 'disabled' : ''}`}
          onClick={startWorkflow}
          disabled={isRunning}
        >
          {isRunning ? '⏳ 运行中...' : '🚀 启动AI工作流'}
        </button>

        {message && (
          <div className={`message ${message.startsWith('❌') ? 'error' : 'success'}`}>
            {message}
          </div>
        )}
      </div>

      {/* TEMU商品列表 */}
      <div className="products-section">
        <div className="section-header">
          <h3>📦 TEMU商品及Redbubble搜索结果</h3>
          <button onClick={loadProducts} disabled={isLoadingProducts} className="refresh-button">
            {isLoadingProducts ? '⏳ 加载中...' : '🔄 刷新'}
          </button>
        </div>

        {isLoadingProducts ? (
          <div className="loading">加载中...</div>
        ) : products.length === 0 ? (
          <div className="empty-state">
            <p>暂无数据</p>
            <p className="hint">启动AI工作流后，系统将清洗TEMU商品标题并搜索Redbubble设计</p>
          </div>
        ) : (
          <div className="products-list">
            {products.map((item) => (
              <div key={item.temu_product.id} className="product-card">
                {/* TEMU商品信息 */}
                <div className="temu-section">
                  <div className="temu-product">
                    <img
                      src={item.temu_product.img}
                      alt={item.temu_product.title}
                      className="temu-img"
                    />
                    <div className="temu-info">
                      <h4 className="temu-title">{item.temu_product.title}</h4>
                      <div className="temu-meta">
                        <span className="price">{item.temu_product.price}</span>
                        <span className="sales">销量: {item.temu_product.sales_count}</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* AI清洗关键词 */}
                <div className="keywords-section">
                  {item.cleaning_status === 'completed' && item.cleaned_keywords ? (
                    <>
                      <div className="keywords-label">🤖 AI提取关键词:</div>
                      <div className="keywords-value">{item.cleaned_keywords}</div>
                    </>
                  ) : (
                    <>
                      <div className="keywords-label">⏳ 待处理</div>
                      <div className="keywords-value" style={{ color: '#95a5a6', fontStyle: 'italic' }}>
                        点击上方"🚀 启动AI工作流"按钮来清洗标题并搜索Redbubble设计
                      </div>
                    </>
                  )}
                </div>

                {/* Redbubble搜索结果 */}
                <div className="redbubble-section">
                  <h5 className="redbubble-title">
                    🎨 Redbubble搜索结果 ({item.redbubble_results.length})
                  </h5>
                  {item.redbubble_results.length === 0 ? (
                    <div className="no-results">
                      {item.cleaning_status === 'completed' ? '暂无搜索结果' : '需要先运行AI工作流'}
                    </div>
                  ) : (
                    <div className="redbubble-results">
                      {item.redbubble_results.map((result) => (
                        <div key={result.id} className="redbubble-card">
                          <img
                            src={result.redbubble_img}
                            alt={result.redbubble_title}
                            className="redbubble-img"
                          />
                          <div className="redbubble-info">
                            <p className="redbubble-product-title">{result.redbubble_title}</p>
                            <div className="redbubble-meta">
                              <span className="score">评分: {result.redbubble_score.toFixed(1)}</span>
                              <span className="rank">#{result.rank_position}</span>
                            </div>
                            <a
                              href={result.redbubble_link}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="view-link"
                            >
                              查看 →
                            </a>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default TemuAIWorkflow;
