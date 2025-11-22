import React, { useEffect, useState } from "react";
import axios from "axios";
import { Product } from "./types/product";
import ProductList from "./components/ProductList";
import SortFilter, { SortOption } from "./components/SortFilter";
import CrawlerControl from "./components/CrawlerControl";
import TemuCategoryCrawler from "./components/TemuCategoryCrawler";
import TemuAIWorkflow from "./components/TemuAIWorkflow";
import "./App.css";

const categoryOptions = [
  { value: 'all', label: '全部' },
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

const App: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sortOption, setSortOption] = useState<SortOption>('default');
  const [showCrawlerControl, setShowCrawlerControl] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('all');
  const [activeTab, setActiveTab] = useState<'redbubble' | 'temu' | 'ai-workflow'>('ai-workflow');

  const fetchProducts = async (category: string = 'all') => {
    try {
      setLoading(true);
      setError(null);
      const url = category === 'all'
        ? "http://localhost:8000/api/products"
        : `http://localhost:8000/api/products?category=${category}`;
      const response = await axios.get<Product[]>(url);
      setProducts(response.data);
      setFilteredProducts(response.data);
    } catch (err) {
      setError("无法连接到后端服务器，请确保后端服务正在运行");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts(selectedCategory);
  }, [selectedCategory]);

  useEffect(() => {
    let sorted = [...products].sort((a, b) => {
      switch (sortOption) {
        case 'score-high':
          const scoreA = typeof a.score === 'number' ? a.score : parseFloat(a.score || '0');
          const scoreB = typeof b.score === 'number' ? b.score : parseFloat(b.score || '0');
          return scoreB - scoreA;
        case 'score-low':
          const scoreA2 = typeof a.score === 'number' ? a.score : parseFloat(a.score || '0');
          const scoreB2 = typeof b.score === 'number' ? b.score : parseFloat(b.score || '0');
          return scoreA2 - scoreB2;
        case 'title':
          return a.title.localeCompare(b.title);
        default:
          return 0;
      }
    });
    setFilteredProducts(sorted);
  }, [sortOption, products]);

  const handleSortChange = (sort: SortOption) => {
    setSortOption(sort);
  };

  const handleRetry = () => {
    fetchProducts(selectedCategory);
  };

  const handleCrawlComplete = () => {
    fetchProducts(selectedCategory);
  };

  return (
    <div className="app">
      <div className="header">
        <h2>商品爬取与分析平台</h2>
        {/* 标签页切换 */}
        <div className="tab-switcher">
          <button
            className={`tab-button ${activeTab === 'ai-workflow' ? 'active' : ''}`}
            onClick={() => setActiveTab('ai-workflow')}
          >
            🤖 AI工作流
          </button>
          <button
            className={`tab-button ${activeTab === 'temu' ? 'active' : ''}`}
            onClick={() => setActiveTab('temu')}
          >
            TEMU
          </button>
          <button
            className={`tab-button ${activeTab === 'redbubble' ? 'active' : ''}`}
            onClick={() => setActiveTab('redbubble')}
          >
            Redbubble
          </button>
        </div>
      </div>

      {/* Redbubble 标签页内容 */}
      {activeTab === 'redbubble' && (
        <>
          <button
            className="toggle-crawler-btn"
            onClick={() => setShowCrawlerControl(!showCrawlerControl)}
          >
            {showCrawlerControl ? '隐藏爬虫控制' : '显示爬虫控制'}
          </button>
          {showCrawlerControl && (
            <CrawlerControl onCrawlComplete={handleCrawlComplete} />
          )}
          <div className="filter-bar" style={{ display: 'flex', alignItems: 'center', gap: 24, padding: '12px 24px', background: '#fff', borderBottom: '1px solid #e1e5e9' }}>
            <div className="category-filter-bar" style={{ margin: 0, padding: 0, border: 'none', background: 'none' }}>
              <label htmlFor="category-filter">筛选类目：</label>
              <select
                id="category-filter"
                value={selectedCategory}
                onChange={e => setSelectedCategory(e.target.value)}
              >
                {categoryOptions.map(opt => (
                  <option value={opt.value} key={opt.value}>{opt.label}</option>
                ))}
              </select>
            </div>
            <SortFilter currentSort={sortOption} onSortChange={handleSortChange} />
          </div>
          <div className="main-content">
            {loading ? (
              <div className="loading">正在加载商品数据...</div>
            ) : error ? (
              <div className="error">{error} <button onClick={handleRetry}>重试</button></div>
            ) : (
              <ProductList products={filteredProducts} loading={loading} error={error} onRetry={handleRetry} />
            )}
          </div>
        </>
      )}

      {/* TEMU 标签页内容 */}
      {activeTab === 'temu' && (
        <TemuCategoryCrawler onCrawlComplete={handleCrawlComplete} />
      )}

      {/* AI工作流标签页内容 */}
      {activeTab === 'ai-workflow' && (
        <TemuAIWorkflow />
      )}
    </div>
  );
};

export default App;
