import React from "react";

// 商品详情页，后续可通过路由参数获取商品ID
const ProductDetail: React.FC = () => {
  // 这里可以通过useParams获取商品ID，实际开发中再完善
  return (
    <div>
      <h2>商品详情页</h2>
      <p>这里显示商品的详细信息。</p>
    </div>
  );
};

export default ProductDetail; 