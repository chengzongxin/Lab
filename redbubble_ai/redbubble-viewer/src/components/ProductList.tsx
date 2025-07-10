import React from "react";
import { Product } from "../types/product";
import "./ProductList.css";

interface Props {
  products: Product[];
}

const ProductList: React.FC<Props> = ({ products }) => (
  <div className="container">
    {products.map((item, idx) => (
      <div className="card" key={idx}>
        <div className="card-img-box">
          <a href={item.link} target="_blank" rel="noopener noreferrer">
            <img className="card-img" src={item.local_img || item.img} alt={item.title} />
          </a>
        </div>
        <div className="card-content">
          <div className="title">{item.title}</div>
          <div className="score">美学评分：{item.score || "无"}</div>
        </div>
      </div>
    ))}
  </div>
);

export default ProductList; 