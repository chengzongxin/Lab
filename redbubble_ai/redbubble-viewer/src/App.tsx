import React, { useState } from "react";
import Papa from "papaparse";
import { Product } from "./types/product";
import ProductList from "./components/ProductList";

const App: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    Papa.parse(file, {
      header: true,
      skipEmptyLines: true,
      complete: (results: any) => {
        setProducts(results.data as Product[]);
      },
    });
  };

  return (
    <div>
      <div className="header">
        <h2>Redbubble 商品美学评分展示（React版）</h2>
      </div>
      <div style={{ textAlign: "center", marginBottom: 20 }}>
        <input type="file" accept=".csv" onChange={handleFileChange} />
        <p>请选择本地 products.csv 文件</p>
      </div>
      <ProductList products={products} />
    </div>
  );
};

export default App;
