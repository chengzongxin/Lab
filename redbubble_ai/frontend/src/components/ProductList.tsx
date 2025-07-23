import React from "react";
import { Product } from "../types/product";
import "./ProductList.css";

interface Props {
  products: Product[];
  loading?: boolean;
  error?: string | null;
  onRetry?: () => void;
}

const ProductList: React.FC<Props> = ({ products, loading, error, onRetry }) => {
  // 格式化评分显示
  const formatScore = (score: string | number) => {
    const numScore = typeof score === 'string' ? parseFloat(score) : score;
    return numScore.toFixed(1);
  };

  // 获取评分等级
  const getScoreLevel = (score: string | number) => {
    const numScore = typeof score === 'string' ? parseFloat(score) : score;
    if (numScore >= 8) return 'excellent';
    if (numScore >= 6) return 'good';
    if (numScore >= 4) return 'average';
    return 'poor';
  };

  // 加载状态
  if (loading) {
    return (
      <div className="loading">
        正在加载商品数据...
      </div>
    );
  }

  // 错误状态
  if (error) {
    return (
      <div className="error">
        <div className="error-icon">⚠️</div>
        <div className="error-message">{error}</div>
        {onRetry && (
          <button className="error-retry" onClick={onRetry}>
            重试
          </button>
        )}
      </div>
    );
  }

  // 空状态
  if (!products || products.length === 0) {
    return (
      <div className="empty">
        <div className="empty-icon">🛍️</div>
        <div className="empty-message">暂无商品数据</div>
        <div className="empty-subtitle">请先运行爬虫程序获取商品数据</div>
      </div>
    );
  }

  return (
    <div className="container">
      {products.map((item) => {
        const scoreLevel = getScoreLevel(item.score || 0);
        const scoreValue = formatScore(item.score || 0);
        
        return (
          <div className="card" key={item.id || item.link}>
            {/* 评分标签 */}
            {item.score && (
              <div className="product-badge">
                {scoreValue} 分
              </div>
            )}
            
            <div className="card-img-box">
              <a href={item.link} target="_blank" rel="noopener noreferrer">
                <img 
                  className="card-img" 
                  src={item.img} 
                  alt={item.title}
                  onError={(e) => {
                    // 图片加载失败时的处理
                    const target = e.target as HTMLImageElement;
                    target.style.display = 'none';
                    const parent = target.parentElement;
                    if (parent) {
                      parent.innerHTML = '<div style="display: flex; align-items: center; justify-content: center; height: 100%; color: #999; font-size: 0.9rem;">图片加载失败</div>';
                    }
                  }}
                />
              </a>
            </div>
            
            <div className="card-content">
              <div className="title">{item.title}</div>
              
              {item.score && (
                <div className="score">
                  <span className="score-value">{scoreValue}</span>
                  <span>美学评分</span>
                </div>
              )}
              
              <a 
                className="link" 
                href={item.link} 
                target="_blank" 
                rel="noopener noreferrer"
              >
                查看商品
              </a>
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default ProductList; 