import React, { useEffect, useState } from "react";
import axios from "axios";
import { Product } from "./types/product";
import ProductList from "./components/ProductList";
import "./App.css";

const App: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchProducts = async () => {
      try {
        setLoading(true);
        const response = await axios.get<Product[]>("http://localhost:8000/api/products");
        setProducts(response.data);
        setError(null);
      } catch (err) {
        console.error("获取商品数据失败", err);
        setError("无法连接到后端服务器，请确保后端服务正在运行");
      } finally {
        setLoading(false);
      }
    };

    fetchProducts();
  }, []);

  if (loading) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '1.2rem',
        color: '#666'
      }}>
        正在加载商品数据...
      </div>
    );
  }

  if (error) {
    return (
      <div style={{ 
        display: 'flex', 
        justifyContent: 'center', 
        alignItems: 'center', 
        height: '100vh',
        fontSize: '1.2rem',
        color: '#e74c3c',
        textAlign: 'center',
        padding: '20px'
      }}>
        <div>
          <div style={{ marginBottom: '10px' }}>⚠️ 连接错误</div>
          <div>{error}</div>
          <div style={{ marginTop: '20px', fontSize: '1rem', color: '#666' }}>
            请确保后端服务在 http://localhost:8000 运行
          </div>
        </div>
      </div>
    );
  }

  return (
    <div>
      <div className="header">
        <h2>Redbubble 商品美学评分展示（数据库版）</h2>
      </div>
      <ProductList products={products} />
    </div>
  );
};

export default App;
