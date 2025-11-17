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

interface Match {
  id: number;
  temu_product_id: number;
  temu_goods_id: string;
  temu_title: string;
  temu_img: string;
  temu_price: string;
  sales_count: number;
  search_keywords: string;
  redbubble_title: string;
  redbubble_img: string;
  redbubble_link: string;
  redbubble_score: number;
  match_score: number;
  rank_position: number;
  created_at: string;
}

const TemuAIWorkflow: React.FC = () => {
  const [categoryId, setCategoryId] = useState<string>('');
  const [batchSize, setBatchSize] = useState<number>(10);
  const [redbubblePages, setRedbubblePages] = useState<number>(2);
  const [isRunning, setIsRunning] = useState(false);
  const [message, setMessage] = useState('');
  const [stats, setStats] = useState<AIWorkflowStats | null>(null);
  const [matches, setMatches] = useState<Match[]>([]);
  const [isLoadingMatches, setIsLoadingMatches] = useState(false);

  // 加载统计信息
  const loadStats = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/temu/ai-workflow/stats');
      setStats(response.data);
    } catch (error) {
      console.error('加载统计失败:', error);
    }
  };

  // 加载匹配结果
  const loadMatches = async () => {
    setIsLoadingMatches(true);
    try {
      const response = await axios.get('http://localhost:8000/api/temu/matches', {
        params: {
          limit: 20,
          offset: 0,
          min_match_score: 0.5
        }
      });
      setMatches(response.data.matches || []);
    } catch (error) {
      console.error('加载匹配结果失败:', error);
      setMatches([]);
    } finally {
      setIsLoadingMatches(false);
    }
  };

  // 页面加载时获取统计和匹配结果
  useEffect(() => {
    loadStats();
    loadMatches();
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
          loadMatches();
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
            <div className="stat-label">总匹配结果</div>
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

      {/* 匹配结果展示 */}
      <div className="matches-section">
        <div className="section-header">
          <h3>📊 匹配结果</h3>
          <button onClick={loadMatches} disabled={isLoadingMatches} className="refresh-button">
            {isLoadingMatches ? '⏳ 加载中...' : '🔄 刷新'}
          </button>
        </div>

        {isLoadingMatches ? (
          <div className="loading">加载中...</div>
        ) : matches.length === 0 ? (
          <div className="empty-state">
            <p>暂无匹配结果</p>
            <p className="hint">启动工作流后，AI将清洗TEMU商品标题并搜索Redbubble匹配设计</p>
          </div>
        ) : (
          <div className="matches-grid">
            {matches.map((match) => (
              <div key={match.id} className="match-card">
                <div className="match-header">
                  <span className="match-score">匹配度: {(match.match_score * 100).toFixed(0)}%</span>
                  <span className="sales-badge">销量: {match.sales_count}</span>
                </div>

                <div className="match-content">
                  {/* TEMU商品 */}
                  <div className="product-section temu-section">
                    <h4>🛍️ TEMU商品</h4>
                    <img src={match.temu_img} alt={match.temu_title} />
                    <p className="product-title">{match.temu_title}</p>
                    <p className="product-price">{match.temu_price}</p>
                  </div>

                  {/* 搜索关键词 */}
                  <div className="keywords-section">
                    <div className="arrow">→</div>
                    <div className="keywords">
                      <strong>AI提取关键词:</strong>
                      <p>{match.search_keywords}</p>
                    </div>
                  </div>

                  {/* Redbubble匹配 */}
                  <div className="product-section redbubble-section">
                    <h4>🎨 Redbubble匹配</h4>
                    <img src={match.redbubble_img} alt={match.redbubble_title} />
                    <p className="product-title">{match.redbubble_title}</p>
                    <p className="product-score">评分: {match.redbubble_score.toFixed(2)}</p>
                    <a href={match.redbubble_link} target="_blank" rel="noopener noreferrer" className="view-link">
                      查看商品 →
                    </a>
                  </div>
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

