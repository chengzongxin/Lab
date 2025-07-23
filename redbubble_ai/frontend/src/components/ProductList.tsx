import React from "react";
import { Product } from "../types/product";
import "./ProductList.css";

interface Props {
  products: Product[];
}

const ProductList: React.FC<Props> = ({ products }) => (
  <div className="container">
    {products.map((item) => (
      <div className="card" key={item.id || item.link}>
        <div className="card-img-box">
          <a href={item.link} target="_blank" rel="noopener noreferrer">
            <img 
              className="card-img" 
              src={item.img} 
              alt={item.title}
              onError={(e) => {
                // 如果本地图片加载失败，尝试使用网络图片
                const target = e.target as HTMLImageElement;
                if (target.src.includes('/images/')) {
                  target.src = item.img.replace('/images/', '/api/fallback/');
                }
              }}
            />
          </a>
        </div>
        <div className="card-content">
          <div className="title">{item.title}</div>
          <div className="score">美学评分：{item.score || "无"}</div>
          <a className="link" href={item.link} target="_blank" rel="noopener noreferrer">查看商品</a>
        </div>
      </div>
    ))}
  </div>
);

export default ProductList; 