import React, { useEffect, useState } from "react";
import { useParams, useLocation, useNavigate } from "react-router-dom";
import { Card, Button, Table, message, Image, Descriptions, Input } from "antd";

// 商品详情页，后续可通过路由参数获取商品ID
const ProductDetail: React.FC = () => {
  const { spu_id } = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const violationData = location.state;
  const [product, setProduct] = useState<any>(null);
  const [related, setRelated] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [searchName, setSearchName] = useState("");

  // 查询商品详情
  useEffect(() => {
    if (!spu_id) return;
    setLoading(true);
    fetch("/api/temu/seller/product", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ productIds: [spu_id] }),
    })
      .then(res => res.json())
      .then(data => {
        if (data.success && data.data.length > 0) setProduct(data.data[0]);
        else message.error(data.msg || "商品详情获取失败");
      })
      .finally(() => setLoading(false));
  }, [spu_id]);

  // 关联搜索
  const handleRelatedSearch = async () => {
    if (!searchName) return;
    setLoading(true);
    const res = await fetch("/api/temu/seller/product", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ productName: searchName }),
    });
    const data = await res.json();
    if (data.success) setRelated(data.data);
    else message.error(data.msg || "关联搜索失败");
    setLoading(false);
  };

  // 下架
  const handleOffline = async () => {
    setLoading(true);
    const res = await fetch("/api/seller/offline", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ productIds: [spu_id] }),
    });
    const data = await res.json();
    if (data.success) message.success("下架成功");
    else message.error(data.msg || "下架失败");
    setLoading(false);
  };

  return (
    <Card title="违规商品详情" loading={loading} extra={<Button onClick={() => navigate(-1)}>返回</Button>}>
      <Descriptions title="违规商品信息" bordered column={1} size="small">
        {violationData && Object.entries(violationData).map(([k, v]) => (
          <Descriptions.Item key={k} label={k}>{String(v)}</Descriptions.Item>
        ))}
      </Descriptions>
      <br />
      <Descriptions title="商品详情" bordered column={1} size="small">
        <Descriptions.Item label="商品ID">{product?.productId}</Descriptions.Item>
        <Descriptions.Item label="商品名称">{product?.productName}</Descriptions.Item>
        <Descriptions.Item label="主图">{product?.mainImageUrl && <Image width={80} src={product.mainImageUrl} />}</Descriptions.Item>
        {/* 可补充更多字段 */}
      </Descriptions>
      <Button type="primary" danger style={{ marginTop: 16 }} onClick={handleOffline}>下架该商品</Button>
      <br /><br />
      <Input.Search
        placeholder="输入商品名称进行关联搜索"
        value={searchName}
        onChange={e => setSearchName(e.target.value)}
        onSearch={handleRelatedSearch}
        style={{ width: 300, marginBottom: 16 }}
        enterButton="关联搜索"
        loading={loading}
      />
      <Table
        rowKey="productId"
        columns={[
          { title: "商品ID", dataIndex: "productId" },
          { title: "商品名称", dataIndex: "productName" },
          { title: "主图", dataIndex: "mainImageUrl", render: (url: string) => url ? <Image width={60} src={url} /> : null },
        ]}
        dataSource={related}
        loading={loading}
        title={() => "关联商品列表"}
      />
    </Card>
  );
};

export default ProductDetail; 