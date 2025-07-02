import React, { useEffect, useState } from "react";
import { Card, Table, Button, message, Image } from "antd";
import { useNavigate } from "react-router-dom";

interface Product {
  spu_id: string;
  goods_name: string;
  goods_img_url?: string;
}

const ProductList: React.FC = () => {
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [loading, setLoading] = useState(false);
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [total, setTotal] = useState(0);
  const navigate = useNavigate();

  // 获取违规商品列表
  const fetchProducts = async (pageNum = page, size = pageSize) => {
    setLoading(true);
    const res = await fetch(`/api/temu/compliance/list?page=${pageNum}&page_size=${size}`);
    const data = await res.json();
    if (data.success) {
      setProducts(data.data.items || data.data); // 兼容返回结构
      setTotal(data.data.total || 3000);
    } else {
      message.error(data.msg || "获取商品失败");
    }
    setLoading(false);
  };

  useEffect(() => {
    fetchProducts(page, pageSize);
    // eslint-disable-next-line
  }, [page, pageSize]);

  // 批量下架
  const handleOffline = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning("请先选择要下架的商品");
      return;
    }
    setLoading(true);
    const res = await fetch("/api/seller/offline", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ productIds: selectedRowKeys }),
    });
    const data = await res.json();
    if (data.success) {
      message.success("下架成功");
      fetchProducts(page, pageSize);
      setSelectedRowKeys([]);
    } else {
      message.error(data.msg || "下架失败");
    }
    setLoading(false);
  };

  return (
    <Card title="违规商品列表">
      <Button type="primary" style={{ marginBottom: 16 }} onClick={handleOffline} loading={loading}>
        批量下架
      </Button>
      <Table
        rowKey="spu_id"
        rowSelection={{
          selectedRowKeys,
          onChange: setSelectedRowKeys,
        }}
        columns={[
          { title: "图片", dataIndex: "goods_img_url", render: (url: string) => url ? <Image width={60} src={url} /> : null },
          { title: "商品ID", dataIndex: "spu_id" },
          { title: "商品名称", dataIndex: "goods_name" },
          {
            title: "操作",
            render: (_, record) => (
              <Button type="link" onClick={() => navigate(`/compliance/${record.spu_id}`, { state: record })}>
                详情
              </Button>
            ),
          },
        ]}
        dataSource={products}
        loading={loading}
        pagination={{
          current: page,
          pageSize: pageSize,
          total: total,
          showSizeChanger: true,
          onChange: (p, ps) => {
            setPage(p);
            setPageSize(ps);
          },
        }}
      />
    </Card>
  );
};

export default ProductList; 