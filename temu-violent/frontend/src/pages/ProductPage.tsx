import React, { useState } from "react";
import { Card, Input, Button, Table, message, Space, Image } from "antd";

interface Product {
  productId: string;
  productName: string;
  mainImageUrl?: string;
  goodsId?: string;
  categories?: any;
}

const ProductPage: React.FC = () => {
  const [searchName, setSearchName] = useState("");
  const [searchIds, setSearchIds] = useState("");
  const [products, setProducts] = useState<Product[]>([]);
  const [loading, setLoading] = useState(false);

  // 搜索功能，支持商品ID数组和商品名称
  const handleSearch = async () => {
    setLoading(true);
    let body: any = {};
    if (searchIds.trim()) {
      // 支持逗号、空格分隔
      const ids = searchIds.split(/[,\s]+/).filter(Boolean);
      body.productIds = ids.map(id => id.trim());
    } else if (searchName.trim()) {
      body.productName = searchName.trim();
    } else {
      message.warning("请输入商品ID或名称");
      setLoading(false);
      return;
    }
    const res = await fetch("/api/temu/seller/product", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    if (data.success) {
      setProducts(data.data);
    } else {
      message.error(data.msg || "查询失败");
    }
    setLoading(false);
  };

  return (
    <Card title="商品搜索">
      <Space style={{ marginBottom: 16 }}>
        <Input
          placeholder="输入商品ID，支持多个用逗号分隔"
          value={searchIds}
          onChange={e => setSearchIds(e.target.value)}
          style={{ width: 260 }}
        />
        <Input
          placeholder="输入商品名称"
          value={searchName}
          onChange={e => setSearchName(e.target.value)}
          style={{ width: 200 }}
        />
        <Button type="primary" onClick={handleSearch} loading={loading}>搜索</Button>
      </Space>
      <Table
        rowKey="productId"
        columns={[
          { title: "图片", dataIndex: "mainImageUrl", render: (url: string) => url ? <Image width={60} src={url} /> : null },
          { title: "商品ID", dataIndex: "productId" },
          { title: "商品名称", dataIndex: "productName" },
          { title: "操作", render: (_, record) => <Button>下架</Button> }
        ]}
        dataSource={products}
        loading={loading}
      />
    </Card>
  );
};

export default ProductPage; 