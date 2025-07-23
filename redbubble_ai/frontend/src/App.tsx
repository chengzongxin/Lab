import React, { useEffect, useState } from "react";
import axios from "axios";
import { Product } from "./types/product";
import ProductList from "./components/ProductList";
import SearchBar from "./components/SearchBar";
import SortFilter, { SortOption } from "./components/SortFilter";
import "./App.css";

const App: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [filteredProducts, setFilteredProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [sortOption, setSortOption] = useState<SortOption>('default');

  const fetchProducts = async () => {
    try {
      setLoading(true);
      setError(null);
      const response = await axios.get<Product[]>("http://localhost:8000/api/products");
      setProducts(response.data);
      setFilteredProducts(response.data);
    } catch (err) {
      console.error("获取商品数据失败", err);
      setError("无法连接到后端服务器，请确保后端服务正在运行");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchProducts();
  }, []);

  // 搜索和排序功能
  useEffect(() => {
    let filtered = products;
    
    // 搜索过滤
    if (searchQuery.trim()) {
      filtered = products.filter(product =>
        product.title.toLowerCase().includes(searchQuery.toLowerCase())
      );
    }
    
    // 排序
    const sorted = [...filtered].sort((a, b) => {
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
  }, [searchQuery, sortOption, products]);

  const handleSearch = (query: string) => {
    setSearchQuery(query);
  };

  const handleSortChange = (sort: SortOption) => {
    setSortOption(sort);
  };

  const handleRetry = () => {
    fetchProducts();
  };

  return (
    <div className="app">
      <div className="header">
        <h2>Redbubble AI 商品美学平台</h2>
        <p className="subtitle">基于 AI 的美学评分，发现优质设计商品</p>
      </div>
      
      <SearchBar onSearch={handleSearch} placeholder="搜索商品名称..." />
      
      {!loading && !error && products.length > 0 && (
        <SortFilter 
          currentSort={sortOption}
          onSortChange={handleSortChange}
        />
      )}
      
      <ProductList 
        products={filteredProducts}
        loading={loading}
        error={error}
        onRetry={handleRetry}
      />
      
      {!loading && !error && products.length > 0 && (
        <div className="stats">
          <div className="stat-item">
            <span className="stat-number">{filteredProducts.length}</span>
            <span className="stat-label">
              {searchQuery ? '搜索结果' : '个商品'}
            </span>
          </div>
          <div className="stat-item">
            <span className="stat-number">
              {filteredProducts.length > 0 
                ? (filteredProducts.reduce((sum, p) => sum + (typeof p.score === 'number' ? p.score : parseFloat(p.score || '0')), 0) / filteredProducts.length).toFixed(1)
                : '0.0'
              }
            </span>
            <span className="stat-label">平均评分</span>
          </div>
          <div className="stat-item">
            <span className="stat-number">
              {filteredProducts.filter(p => {
                const score = typeof p.score === 'number' ? p.score : parseFloat(p.score || '0');
                return score >= 7;
              }).length}
            </span>
            <span className="stat-label">高分商品</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default App;
