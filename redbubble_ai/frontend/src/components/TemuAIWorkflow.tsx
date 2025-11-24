import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { API_BASE_URL } from '../config';
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
}

interface TemuProduct {
  id: number;
  goods_id: string;
  title: string;
  img: string;
  price: string;
  sales_count: number;
}

interface ProductWithMatches {
  temu_product: TemuProduct;
  cleaned_keywords: string;
  cleaning_status: string;
  redbubble_results: RedbubbleResult[];
}

const TemuAIWorkflow: React.FC = () => {
  // 控制参数
  const [batchSize, setBatchSize] = useState<number>(100);
  const [redbubblePages, setRedbubblePages] = useState<number>(1);
  const [redbubbleCategory, setRedbubbleCategory] = useState<string>('u-socks');
  const [isRunning, setIsRunning] = useState(false);
  const [message, setMessage] = useState('');
  const [showControls, setShowControls] = useState(false);

  // 数据
  const [stats, setStats] = useState<AIWorkflowStats | null>(null);
  const [products, setProducts] = useState<ProductWithMatches[]>([]);
  const [isLoadingProducts, setIsLoadingProducts] = useState(false);

  // 分页
  const [currentPage, setCurrentPage] = useState(1);
  const [totalProducts, setTotalProducts] = useState(0);
  const pageSize = 20;

  // 展开商品的Redbubble结果
  const [expandedProducts, setExpandedProducts] = useState<Set<number>>(new Set());

  // 切换展开/收起
  const toggleExpand = (productId: number) => {
    const newSet = new Set(expandedProducts);
    if (newSet.has(productId)) {
      newSet.delete(productId);
    } else {
      newSet.add(productId);
    }
    setExpandedProducts(newSet);
  };

  // 加载统计信息
  const loadStats = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/temu/ai-workflow/stats`);
      setStats(response.data);
    } catch (error) {
      console.error('加载统计失败:', error);
    }
  };

  // 加载商品数据（支持分页）
  const loadProducts = async (page: number = 1) => {
    setIsLoadingProducts(true);
    try {
      const offset = (page - 1) * pageSize;
      const response = await axios.get(`${API_BASE_URL}/api/temu/products-with-matches`, {
        params: {
          limit: pageSize,
          offset: offset,
          min_match_score: 0.1
        }
      });
      setProducts(response.data.products || []);
      setTotalProducts(response.data.total || 0);
      setCurrentPage(page);
    } catch (error) {
      console.error('加载商品数据失败:', error);
      setProducts([]);
    } finally {
      setIsLoadingProducts(false);
    }
  };

  // 页面加载时获取数据
  useEffect(() => {
    loadStats();
    loadProducts(1);
    const interval = setInterval(loadStats, 10000); // 每10秒刷新统计
    return () => clearInterval(interval);
  }, []);

  // 启动AI工作流
  const startWorkflow = async () => {
    if (isRunning) return;

    setIsRunning(true);
    setMessage('正在启动AI工作流...');

    try {
      const response = await axios.post(`${API_BASE_URL}/api/temu/ai-workflow`, {
        category_id: null,
        batch_size: batchSize,
        redbubble_pages: redbubblePages,
        redbubble_category: redbubbleCategory
      });

      if (response.data.success) {
        setMessage(`✅ ${response.data.message}`);
        setTimeout(() => {
          loadStats();
          loadProducts(currentPage);
        }, 3000);
      }
    } catch (error: any) {
      setMessage(`❌ 启动失败: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsRunning(false);
    }
  };

  const totalPages = Math.ceil(totalProducts / pageSize);

  return (
    <div className="temu-ai-workflow-compact">
      {/* 顶部：精简的统计和控制 */}
      <div className="compact-header">
        <div className="stats-mini">
          {stats && (
            <>
              <span className="stat-item">
                <strong>{stats.cleaning.completed}</strong>/{stats.cleaning.total} 已清洗
              </span>
              <span className="stat-item">
                <strong>{stats.matches.matched_products}</strong> 已匹配
              </span>
              <span className="stat-item">
                <strong>{stats.matches.total_matches}</strong> 搜索结果
              </span>
            </>
          )}
        </div>

        <div className="action-buttons">
          <button
            className="btn-start"
            onClick={startWorkflow}
            disabled={isRunning}
          >
            {isRunning ? '⏳ 运行中...' : '🚀 启动AI工作流'}
          </button>
          <button
            className="btn-settings"
            onClick={() => setShowControls(!showControls)}
          >
            ⚙️
          </button>
        </div>
      </div>

      {/* 可折叠的控制面板 */}
      {showControls && (
        <div className="controls-panel-compact">
          <label>
            批量处理:
            <input
              type="number"
              value={batchSize}
              onChange={(e) => setBatchSize(parseInt(e.target.value))}
              min="1" max="200"
            />
          </label>
          <label>
            搜索页数:
            <input
              type="number"
              value={redbubblePages}
              onChange={(e) => setRedbubblePages(parseInt(e.target.value))}
              min="1" max="5"
            />
          </label>
          <label>
            搜索类目:
            <select
              value={redbubbleCategory}
              onChange={(e) => setRedbubbleCategory(e.target.value)}
            >
              <option value="u-socks">袜子 (Socks)</option>
              <option value="u-clothing">衣服 (Clothing)</option>
              <option value="u-stickers">贴纸 (Stickers)</option>
              <option value="u-phone-cases">手机壳 (Phone Cases)</option>
              <option value="u-mugs">马克杯 (Mugs)</option>
              <option value="u-tshirts">T恤 (T-Shirts)</option>
              <option value="u-hoodies">卫衣 (Hoodies)</option>
              <option value="u-bags">包包 (Bags)</option>
            </select>
          </label>
        </div>
      )}

      {message && (
        <div className={`message-compact ${message.startsWith('❌') ? 'error' : 'success'}`}>
          {message}
        </div>
      )}

      {/* 分页控制 */}
      <div className="pagination-top">
        <span className="page-info">共 {totalProducts} 个商品，第 {currentPage}/{totalPages} 页</span>
        <div className="page-buttons">
          <button
            onClick={() => loadProducts(currentPage - 1)}
            disabled={currentPage === 1 || isLoadingProducts}
          >
            ← 上一页
          </button>
          <button
            onClick={() => loadProducts(currentPage + 1)}
            disabled={currentPage >= totalPages || isLoadingProducts}
          >
            下一页 →
          </button>
        </div>
      </div>

      {/* 主要内容区：左右分栏 */}
      {isLoadingProducts ? (
        <div className="loading-compact">加载中...</div>
      ) : products.length === 0 ? (
        <div className="empty-compact">
          <p>暂无数据</p>
          <p className="hint">点击"🚀 启动AI工作流"开始处理TEMU商品</p>
        </div>
      ) : (
        <div className="products-grid-compact">
          {products.map((item) => (
            <div key={item.temu_product.id} className="product-row-compact">
              {/* 左侧：TEMU商品 */}
              <div className="temu-card-compact">
                <img
                  src={item.temu_product.img}
                  alt={item.temu_product.title}
                  className="temu-img-compact"
                />
                <div className="temu-info-compact">
                  <h4 className="temu-title-compact">{item.temu_product.title}</h4>
                  <div className="temu-meta-compact">
                    <span className="price">{item.temu_product.price}</span>
                    <span className="sales">🔥 {item.temu_product.sales_count.toLocaleString()}</span>
                  </div>
                </div>
              </div>

              {/* 右侧：AI关键词 + Redbubble结果 */}
              <div className="results-card-compact">
                {/* AI关键词 */}
                <div className="keywords-compact">
                  {item.cleaning_status === 'completed' && item.cleaned_keywords ? (
                    <>
                      <span className="label">🤖 关键词:</span>
                      <span className="value">{item.cleaned_keywords}</span>
                    </>
                  ) : (
                    <span className="pending">⏳ 待处理</span>
                  )}
                </div>

                {/* Redbubble结果列表 - 九宫格 */}
                {item.redbubble_results.length > 0 ? (
                  <div className="redbubble-grid-container">
                    <div className="redbubble-grid-compact">
                      {(expandedProducts.has(item.temu_product.id)
                        ? item.redbubble_results
                        : item.redbubble_results.slice(0, 6)
                      ).map((result) => (
                        <a
                          key={result.id}
                          href={result.redbubble_link}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="rb-grid-item"
                          title={result.redbubble_title}
                        >
                          <img src={result.redbubble_img} alt="Item preview" />
                          <div className="rb-overlay">
                            <div className="rb-title-overlay">{result.redbubble_title}</div>
                          </div>
                        </a>
                      ))}
                    </div>
                    {item.redbubble_results.length > 6 && (
                      <button
                        className="expand-btn"
                        onClick={() => toggleExpand(item.temu_product.id)}
                      >
                        {expandedProducts.has(item.temu_product.id)
                          ? `收起 ▲`
                          : `查看全部 ${item.redbubble_results.length} 个结果 ▼`}
                      </button>
                    )}
                  </div>
                ) : (
                  <div className="no-results-compact">
                    {item.cleaning_status === 'completed' ? '无搜索结果' : '需要先运行AI工作流'}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* 底部分页 */}
      {products.length > 0 && (
        <div className="pagination-bottom">
          <button
            onClick={() => loadProducts(currentPage - 1)}
            disabled={currentPage === 1 || isLoadingProducts}
          >
            ← 上一页
          </button>
          <span>第 {currentPage}/{totalPages} 页</span>
          <button
            onClick={() => loadProducts(currentPage + 1)}
            disabled={currentPage >= totalPages || isLoadingProducts}
          >
            下一页 →
          </button>
        </div>
      )}
    </div>
  );
};

export default TemuAIWorkflow;
