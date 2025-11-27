import React, { useEffect, useState } from "react";
import axios from "axios";
import { Product } from "../types/product";
import ProductList from "./ProductList";
import SortFilter, { SortOption } from "./SortFilter";
import CrawlerControl from "./CrawlerControl";
import Pagination from "./Pagination";
import { API_BASE_URL } from '../config';
import "./RedbubblePage.css";

const categoryOptions = [
  { value: 'all', label: '全部' },
  { value: 'u-socks', label: '袜子' },
  { value: 'u-clothing', label: '衣服' },
  { value: 'u-bags', label: '包' },
  { value: 'u-masks', label: '口罩' },
  { value: 'u-cases', label: '手机壳' },
  { value: 'u-stickers', label: '贴纸' },
  { value: 'u-wall-art', label: '墙饰' },
  { value: 'u-home-decor', label: '家居' },
  { value: 'u-stationery', label: '文具' },
  { value: 'u-kids-babies', label: '儿童婴儿' },
];

interface RedbubblePageProps {
  onCrawlComplete?: () => void;
}

const RedbubblePage: React.FC<RedbubblePageProps> = ({ onCrawlComplete }) => {
  const [products, setProducts] = useState<Product[]>([]);
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [sortOption, setSortOption] = useState<SortOption>('default');
  const [showCrawlerControl, setShowCrawlerControl] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState('all');

  // 分页相关状态
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 100; // 每页显示100个商品

  const fetchProducts = async (category: string = 'all') => {
    try {
      setLoading(true);
      setError(null);
      const url = category === 'all'
        ? `${API_BASE_URL}/api/products`
        : `${API_BASE_URL}/api/products?category=${category}`;
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
    // 切换筛选条件时重置到第一页
    setCurrentPage(1);
  }, [sortOption, products]);

  const handleSortChange = (sort: SortOption) => {
    setSortOption(sort);
  };

  const handleRetry = () => {
    fetchProducts(selectedCategory);
  };

  const handleCrawlComplete = () => {
    fetchProducts(selectedCategory);
    onCrawlComplete?.();
  };

  // 计算分页数据
  const totalPages = Math.ceil(filteredProducts.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const endIndex = startIndex + itemsPerPage;
  const currentPageProducts = filteredProducts.slice(startIndex, endIndex);

  // 分页处理函数
  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    // 滚动到页面顶部
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <>
      
      {showCrawlerControl && (
        <CrawlerControl onCrawlComplete={handleCrawlComplete} />
      )}
      <div className="filter-bar" style={{ display: 'flex', alignItems: 'center', gap: 24, padding: '12px 24px', background: '#fff', borderBottom: '1px solid #e1e5e9' }}>
        
        <div className="category-filter-bar" style={{ margin: 0, padding: 0, border: 'none', background: 'none' }}>
          <label htmlFor="category-filter">筛选类目：</label>
          <select
            id="category-filter"
            value={selectedCategory}
            onChange={e => {
              setSelectedCategory(e.target.value);
              setCurrentPage(1); // 切换类别时重置到第一页
            }}
          >
            {categoryOptions.map(opt => (
              <option value={opt.value} key={opt.value}>{opt.label}</option>
            ))}
          </select>
        </div>
        <SortFilter currentSort={sortOption} onSortChange={handleSortChange} />

        <div className="spacer" style={{ flex: 1 }}></div>

        <div className="toggle-crawler-btn-container">
      <button
        className="toggle-crawler-btn"
        style={{ margin: 10 }}
        onClick={() => setShowCrawlerControl(!showCrawlerControl)}
      >
        {showCrawlerControl ? '隐藏爬虫控制' : '显示爬虫控制'}
      </button>
      </div>
      </div>
      <div className="main-content">
        {loading ? (
          <div className="loading">正在加载商品数据...</div>
        ) : error ? (
          <div className="error">{error} <button onClick={handleRetry}>重试</button></div>
        ) : (
          <>
            <ProductList products={currentPageProducts} loading={loading} error={error} onRetry={handleRetry} />
            {totalPages > 1 && (
              <Pagination
                currentPage={currentPage}
                totalPages={totalPages}
                onPageChange={handlePageChange}
              />
            )}
          </>
        )}
      </div>
    </>
  );
};

export default RedbubblePage;
