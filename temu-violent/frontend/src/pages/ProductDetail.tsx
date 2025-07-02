import React, { useEffect, useState } from "react";
import { useParams, useLocation, useNavigate } from "react-router-dom";
import { Card, Button, Table, message, Image, Descriptions, Input } from "antd";

// 商品详情页组件
const ProductDetail: React.FC = () => {
  const { spu_id } = useParams(); // 从路由参数获取spu_id
  const location = useLocation(); // 获取路由传递的state
  const navigate = useNavigate(); // 用于页面跳转
  const violationData = location.state; // 违规商品原始数据
  const [product, setProduct] = useState<any>(null); // 商品详情数据
  const [related, setRelated] = useState<any[]>([]); // 关联商品列表
  const [detailLoading, setDetailLoading] = useState(false); // 详情页loading
  const [relatedLoading, setRelatedLoading] = useState(false); // 关联商品loading
  const [searchName, setSearchName] = useState(""); // 关联搜索输入框内容
  const [selectedRelatedKeys, setSelectedRelatedKeys] = useState<React.Key[]>([]); // 关联商品多选

  // 查询商品详情，并自动用前三个单词做关联搜索
  useEffect(() => {
    if (!spu_id) return;
    setDetailLoading(true);
    fetch("/api/temu/seller/product", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ productIds: [spu_id] }),
    })
      .then(res => res.json())
      .then(data => {
        if (data.success && data.data.length > 0) {
          setProduct(data.data[0]);
          // 自动用商品名称前三个单词做关联搜索
          const name = data.data[0].productName || "";
          const words = name.split(/\s+/).slice(0, 3).join(" ");
          if (words) {
            setSearchName(words); // 设置输入框内容
            handleRelatedSearch(words);
          }
        } else message.error(data.msg || "商品详情获取失败");
      })
      .finally(() => setDetailLoading(false));
    // eslint-disable-next-line
  }, [spu_id]);

  // 关联搜索函数，支持自动和手动触发
  const handleRelatedSearch = async (name?: string) => {
    const keyword = typeof name === "string" ? name : searchName;
    if (!keyword) return;
    setRelatedLoading(true);
    const res = await fetch("/api/temu/seller/product", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ productName: keyword }),
    });
    const data = await res.json();
    if (data.success) setRelated(data.data);
    else message.error(data.msg || "关联搜索失败");
    setRelatedLoading(false);
  };

  // 下架当前商品
  const handleOffline = async () => {
    setDetailLoading(true);
    const res = await fetch("/api/seller/offline", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ productIds: [spu_id] }),
    });
    const data = await res.json();
    if (data.success) message.success("下架成功");
    else message.error(data.msg || "下架失败");
    setDetailLoading(false);
  };

  // 一键下架关联商品
  const handleOfflineRelated = async () => {
    if (selectedRelatedKeys.length === 0) {
      message.warning("请先选择要下架的关联商品");
      return;
    }
    setRelatedLoading(true);
    const res = await fetch("/api/seller/offline", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ productIds: selectedRelatedKeys }),
    });
    const data = await res.json();
    if (data.success) {
      message.success("关联商品下架成功");
      handleRelatedSearch(); // 下架后刷新关联商品列表
      setSelectedRelatedKeys([]); // 清空多选
    } else message.error(data.msg || "下架失败");
    setRelatedLoading(false);
  };

  return (
    <Card
      title="违规商品详情"
      loading={detailLoading}
      extra={<Button onClick={() => navigate(-1)}>返回</Button>}
    >
      {/* 违规商品原始信息 */}
      <Descriptions title="违规商品信息" bordered column={1} size="small">
        <Descriptions.Item label="商品ID">{violationData?.spu_id}</Descriptions.Item>
        <Descriptions.Item label="商品名称">{violationData?.goods_name}</Descriptions.Item>
        <Descriptions.Item label="主图">
          {violationData?.goods_img_url && <Image width={80} src={violationData.goods_img_url} />}
        </Descriptions.Item>
        {/* 展示所有原始字段 */}
        {violationData &&
          Object.entries(violationData).map(([k, v]) => (
            <Descriptions.Item key={k} label={k}>
              {String(v)}
            </Descriptions.Item>
          ))}
      </Descriptions>
      <br />
      {/* 商品详情 */}
      <Descriptions title="商品详情" bordered column={1} size="small">
        <Descriptions.Item label="商品ID">{product?.productId}</Descriptions.Item>
        <Descriptions.Item label="商品名称">{product?.productName}</Descriptions.Item>
        <Descriptions.Item label="主图">
          {product?.mainImageUrl && <Image width={80} src={product.mainImageUrl} />}
        </Descriptions.Item>
        {/* 可补充更多字段 */}
      </Descriptions>
      {/* 下架按钮 */}
      <Button type="primary" danger style={{ marginTop: 16 }} onClick={handleOffline}>
        下架该商品
      </Button>
      {/* 一键下架关联商品按钮 */}
      <Button
        type="primary"
        danger
        style={{ marginLeft: 16, marginTop: 16 }}
        onClick={handleOfflineRelated}
        disabled={selectedRelatedKeys.length === 0}
        loading={relatedLoading}
      >
        一键下架关联商品
      </Button>
      <br />
      <br />
      {/* 关联搜索输入框 */}
      <Input.Search
        placeholder="输入商品名称进行关联搜索"
        value={searchName}
        onChange={e => setSearchName(e.target.value)}
        onSearch={v => handleRelatedSearch(v)}
        style={{ width: 300, marginBottom: 16 }}
        enterButton="关联搜索"
        loading={relatedLoading}
      />
      {/* 关联商品表格，支持多选 */}
      <Table
        rowKey="productId"
        columns={[
          { title: "商品ID", dataIndex: "productId" },
          { title: "商品名称", dataIndex: "productName" },
          {
            title: "主图",
            dataIndex: "mainImageUrl",
            render: (url: string) => (url ? <Image width={60} src={url} /> : null),
          },
        ]}
        dataSource={related}
        loading={relatedLoading}
        title={() => "关联商品列表"}
        rowSelection={{
          selectedRowKeys: selectedRelatedKeys,
          onChange: setSelectedRelatedKeys,
        }}
      />
    </Card>
  );
};

export default ProductDetail; 