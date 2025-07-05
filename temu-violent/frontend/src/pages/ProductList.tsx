import React, { useEffect, useState } from "react";
import { Card, Table, Button, message, Image, Switch, Drawer } from "antd";
import { useNavigate } from "react-router-dom";
import { useProductListContext } from './ProductListContext';
import ProductDetail from './ProductDetail';
import './ProductList.css';

const ProductList: React.FC = () => {
  const { products, setProducts, page, setPage, pageSize, setPageSize, total, setTotal } = useProductListContext();
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const [loading, setLoading] = useState(false);
  const [showMajorViolation, setShowMajorViolation] = useState(false);
  const [drawerVisible, setDrawerVisible] = useState(false);
  const [currentProduct, setCurrentProduct] = useState<any>(null);
  const navigate = useNavigate();
  const [viewedIds, setViewedIds] = useState<React.Key[]>([]);

  // 获取违规商品列表
  const fetchProducts = async (pageNum = page, size = pageSize) => {
    setLoading(true);
    const res = await fetch(`/api/temu/compliance/list?page=${pageNum}&page_size=${size}`);
    const data = await res.json();
    if (data.success) {
      setProducts(data.data.items || data.data); // 兼容返回结构
    } else {
      message.error(data.msg || "获取商品失败");
    }
    setLoading(false);
  };

  const fetchTotal = async (pageNum = page, size = pageSize) => {
    const res = await fetch(`/api/temu/compliance/total?page=${pageNum}&page_size=${size}`);
    const data = await res.json();
    if (data.success) {
      setTotal(data.total || 8000);
    }
  };

  // 首次挂载时自动加载一次数据
  useEffect(() => {
    if (products.length === 0) {
      fetchProducts(page, pageSize);
      fetchTotal(page, pageSize);
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
      body: JSON.stringify({ 
        productIds: selectedRowKeys.map(String),
        max_threads: 8  // 批量下架使用更多线程
      }),
    });
    const data = await res.json();
    if (data.success) {
      // 处理批量下架结果
      if (Array.isArray(data.results)) {
        setTimeout(() => {
          message.info("下架结果已弹窗显示");
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

  // 打开详情抽屉
  const openDetail = (record: any) => {
    setCurrentProduct(record);
    setDrawerVisible(true);
    setViewedIds(prev => prev.includes(record.spu_id) ? prev : [...prev, record.spu_id]);
  };

  return (
    <Card title="违规商品列表"
      extra={
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 16 }}>
          <div>
            <Button type="primary" onClick={() => {
              fetchProducts(page, pageSize);
              fetchTotal(page, pageSize);
            }} loading={loading} style={{ marginRight: 8 }}>
              刷新
            </Button>
            <Button type="primary" onClick={handleOffline} loading={loading}>
              批量下架
            </Button>
          </div>
          <span>
            <Switch checked={showMajorViolation} onChange={setShowMajorViolation} />
            <span style={{ marginLeft: 8 }}>
              只看全栈违规/80站以上
            </span>
          </span>
        </div>
      }
      style={{ display: 'flex', flexDirection: 'column', height: 'auto', minHeight: 0 }}
    >

      <div style={{ flex: 1, height: '100%' }}>

        <Table
          rowKey="spu_id"
          rowSelection={{
            selectedRowKeys,
            onChange: setSelectedRowKeys,
          }}
          size='large'
          columns={[
            { title: "图片", dataIndex: "goods_img_url", render: (url: string) => url ? <Image width={160} src={url} /> : null },
            { 
              title: "商品ID", 
              dataIndex: "spu_id",
              render: (text: string) => <span style={{ fontSize: '16px', fontWeight: 'bold' }}>{text}</span>
            },
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
                if (isAllSite) return <span style={{ fontSize: '16px', fontWeight: 'bold', color: '#ff4d4f' }}>全部站点违规</span>;
                return <span style={{ fontSize: '16px', fontWeight: 'bold' }}>{record.site_num}</span>;
              }
            },
            {
              title: "操作",
              render: (_, record) => (
                <Button type="link" style={{ fontSize: 16, padding: 20, border: '1px solid #00f' }} onClick={() => openDetail(record)}>
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
            showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条违规记录`,
            onChange: (p, ps) => {
              setPage(p);
              setPageSize(ps);
              fetchProducts(p, ps); // 分页时主动刷新
            },
          }}
          scroll={{ y: 800 }}
          rowClassName={record => viewedIds.includes(record.spu_id) ? "viewed-row" : ""}
        />
      </div>
      <Drawer
        title="违规商品详情"
        width={1600}
        open={drawerVisible}
        onClose={() => setDrawerVisible(false)}
        destroyOnClose
      >
        {currentProduct && (
          <ProductDetail spu_id={currentProduct.spu_id} violationData={currentProduct} onClose={() => setDrawerVisible(false)} />
        )}
      </Drawer>
    </Card>
  );
};

export default ProductList; 