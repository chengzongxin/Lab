import React, { useEffect, useState } from "react";
import { Card, Table, Button, message, Image, Switch, Modal } from "antd";
import { useNavigate } from "react-router-dom";
import { useProductListContext } from './ProductListContext';

const ProductList: React.FC = () => {
  const { products, setProducts, page, setPage, pageSize, setPageSize, total, setTotal } = useProductListContext();
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [loading, setLoading] = useState(false);
  const [showMajorViolation, setShowMajorViolation] = useState(false);
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

  // 首次挂载时自动加载一次数据
  useEffect(() => {
    if (products.length === 0) {
      fetchProducts(page, pageSize);
    }
    // eslint-disable-next-line
  }, []);

  // 批量下架
  const handleOffline = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning("请先选择要下架的商品");
      return;
    }
    setLoading(true);
    const res = await fetch("/api/temu/seller/offline", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ productIds: selectedRowKeys.map(String) }),
    });
    const data = await res.json();
    if (data.success) {
      // 处理批量下架结果
      if (Array.isArray(data.results)) {
        setTimeout(() => {
          Modal.info({
            title: "下架结果",
            width: 600,
            content: (
              <div>
                {data.results.map((item: any) => (
                  <div key={item.dataId} style={{ marginBottom: 8 }}>
                    商品ID: {item.dataId} - {item.result.success ? (
                      <span style={{ color: 'green' }}>下架成功</span>
                    ) : (
                      <span style={{ color: 'red' }}>
                        下架失败{item.result.errorMsg ? `: ${item.result.errorMsg}` : ""}
                      </span>
                    )}
                  </div>
                ))}
              </div>
            ),
          });
        }, 0);
      } else {
        message.success("下架成功");
      }
      fetchProducts(page, pageSize);
      setSelectedRowKeys([]);
    } else {
      message.error(data.msg || "下架失败");
    }
    setLoading(false);
  };

  // 违规筛选逻辑
  const filteredProducts = showMajorViolation
    ? products.filter(record => {
        const isAllSite = record.site_num === 1 &&
          Array.isArray(record.punish_detail_list) &&
          record.punish_detail_list.some((d: any) => d.site_id === -1);
        return isAllSite || record.site_num >= 80;
      })
    : products;

  return (
    <Card title="违规商品列表"
      extra={
        <span>
          <Switch checked={showMajorViolation} onChange={setShowMajorViolation} />
          <span style={{ marginLeft: 8 }}>
            只看全栈违规/80站以上
          </span>
        </span>
      }
    >
      <Button type="primary" onClick={() => fetchProducts(page, pageSize)} loading={loading} style={{ marginBottom: 16 }}>
        刷新
      </Button>
      <Button type="primary" style={{ marginLeft: 8, marginBottom: 16 }} onClick={handleOffline} loading={loading}>
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
            title: "违规描述",
            dataIndex: "violation_desc",
            render: (desc: string) => desc || "-"
          },
          {
            title: "违规站点",
            dataIndex: "site_num",
            render: (_, record) => {
              const isAllSite = record.site_num === 1 &&
                Array.isArray(record.punish_detail_list) &&
                record.punish_detail_list.some((d: any) => d.site_id === -1);
              if (isAllSite) return "全部站点违规";
              return record.site_num;
            }
          },
          {
            title: "操作",
            render: (_, record) => (
              <Button type="link" onClick={() => navigate(`/compliance/${record.spu_id}`, { state: record })}>
                详情
              </Button>
            ),
          },
        ]}
        dataSource={filteredProducts}
        loading={loading}
        pagination={{
          current: page,
          pageSize: pageSize,
          total: total,
          showSizeChanger: true,
          onChange: (p, ps) => {
            setPage(p);
            setPageSize(ps);
            fetchProducts(p, ps); // 分页时主动刷新
          },
        }}
      />
    </Card>
  );
};

export default ProductList; 