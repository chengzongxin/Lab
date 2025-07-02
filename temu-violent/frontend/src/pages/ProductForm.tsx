import React, { useState } from "react";

// 商品表单页，支持新增和编辑
const ProductForm: React.FC = () => {
  const [name, setName] = useState("");
  const [status, setStatus] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // 这里可以将数据提交到后端
    alert(`提交商品：${name}, 状态：${status}`);
  };

  return (
    <div>
      <h2>新增/编辑商品</h2>
      <form onSubmit={handleSubmit}>
        <div>
          <label>商品名称：</label>
          <input value={name} onChange={e => setName(e.target.value)} required />
        </div>
        <div>
          <label>状态：</label>
          <input value={status} onChange={e => setStatus(e.target.value)} required />
        </div>
        <button type="submit">提交</button>
      </form>
    </div>
  );
};

export default ProductForm; 