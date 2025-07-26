import React, { useEffect, useState } from "react";
import { Card, Table, Button, message, Image, Switch, Drawer, Select, InputNumber, Space } from "antd";
import { useNavigate } from "react-router-dom";
import { useProductListContext } from './ProductListContext';
import ProductDetail from './ProductDetail';
import { useGlobalNotification } from './GlobalNotification';
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
  const [filterRange, setFilterRange] = useState<string>("80+"); // 默认筛选80以上
  const [customMin, setCustomMin] = useState<number>(80); // 自定义最小值
  const [customMax, setCustomMax] = useState<number>(999); // 自定义最大值
  const [showUSViolation, setShowUSViolation] = useState<boolean>(false); // 美国站违规筛选
  const notify = useGlobalNotification();

  // 获取违规商品列表
  const fetchProducts = async (pageNum = page, size = pageSize) => {
    setLoading(true);
    // 清理选择状态，避免缓存问题
    setSelectedRowKeys([]);
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
    
    try {
      // 第一步：获取选中商品的详情，获取所有对应的skcId
      message.loading("正在获取商品详情...", 0);
      const productRes = await fetch("/api/temu/seller/product", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ productIds: selectedRowKeys.map(String) }),
      });
      const productData = await productRes.json();
      message.destroy(); // 清除loading消息
      
      if (!productData.success) {
        message.error(productData.msg || "获取商品详情失败");
        return;
      }

      // 提取所有skcId
      const allSkcIds: string[] = [];
      if (Array.isArray(productData.data)) {
        productData.data.forEach((product: any) => {
          if (product.productSkcId) {
            allSkcIds.push(product.productSkcId);
          }
        });
      }

      if (allSkcIds.length === 0) {
        message.warning("未找到可下架的SKC");
        return;
      }

      // 第二步：批量下架这些skcId
      message.loading(`正在下架 ${allSkcIds.length} 个SKC...`, 0);
      const res = await fetch("/api/temu/seller/offline", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          productIds: allSkcIds,  // 传递skcId列表
          max_threads: 8  // 批量下架使用更多线程
        }),
      });
      const data = await res.json();
      message.destroy(); // 清除loading消息

      if (data.success) {
        // 显示详细的下架结果
        const successCount = data.summary?.success || 0;
        const failCount = data.summary?.failed || 0;
        const totalCount = data.summary?.total || 0;
        
        notify({
          type: 'info',
          message: "批量下架完成",
          description: (
            <div>
              <div style={{ marginBottom: 12 }}>
                <span style={{ color: 'green' }}>下架成功：{successCount} 个</span>
                <span style={{ color: 'red', marginLeft: 16 }}>下架失败：{failCount} 个</span>
                <span style={{ color: 'blue', marginLeft: 16 }}>总计：{totalCount} 个</span>
              </div>
              {data.results && data.results.map((item: any) => (
                <div key={item.productId} style={{ marginBottom: 8, fontSize: '13px' }}>
                  SKC ID: {item.productId} - {item.success ? (
                    <span style={{ color: 'green' }}>{item.message}</span>
                  ) : (
                    <span style={{ color: 'red' }}>{item.message}</span>
                  )}
                </div>
              ))}
            </div>
          ) as any,
        });
        
        // 刷新列表并清空选择
        fetchProducts(page, pageSize);
        setSelectedRowKeys([]);
              } else {
          notify({
            type: 'error',
            message: "下架失败",
            description: data.msg || data.message || "下架失败"
          });
        }
      } catch (error) {
        message.destroy(); // 确保清除所有loading消息
        notify({
          type: 'error',
          message: "下架失败",
          description: `网络错误: ${error}`
        });
    } finally {
      setLoading(false);
    }
  };

  // 违规筛选逻辑
  const filteredProducts = products.filter(record => {
    // 美国站违规筛选
    if (showUSViolation) {
      const hasUSViolation = Array.isArray(record.punish_detail_list) &&
        record.punish_detail_list.some((d: any) => d.site_id === 100);
      if (!hasUSViolation) return false;
    }

    // 违规站点数量筛选
    if (showMajorViolation) {
      const isAllSite = record.site_num === 1 &&
        Array.isArray(record.punish_detail_list) &&
        record.punish_detail_list.some((d: any) => d.site_id === -1);

      // 根据筛选范围进行过滤
      if (filterRange === "80+") {
        // 80以上：包括全站违规 + 80站以上
        return isAllSite || record.site_num >= 80;
      } else if (filterRange === "custom") {
        // 自定义范围：只包括指定范围，不包括全站违规
        if (isAllSite) {
          return customMax >= 999;
        } else {
          return record.site_num >= customMin && record.site_num <= customMax;
        }
      }

      return false;
    }

    return true;
  });

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
            }} loading={loading}>
              刷新
            </Button>
            <Button 
              type="primary" 
              danger 
              onClick={handleOffline}
              disabled={selectedRowKeys.length === 0}
              loading={loading}
              style={{ marginLeft: 8 }}
            >
              批量下架 ({selectedRowKeys.length})
            </Button>
          </div>
          <Space>
            <Switch checked={showUSViolation} onChange={setShowUSViolation} />
            <span style={{ marginLeft: 8 }}>
              美国站违规
            </span>
            <Switch checked={showMajorViolation} onChange={setShowMajorViolation} />
            <span style={{ marginLeft: 8 }}>
              违规筛选
            </span>
            {showMajorViolation && (
              <Space>
                <Select
                  value={filterRange}
                  onChange={setFilterRange}
                  style={{ width: 120 }}
                  options={[
                    { label: "80站以上(含全站)", value: "80+" },
                    { label: "自定义范围", value: "custom" }
                  ]}
                />
                {filterRange === "custom" && (
                  <Space>
                    <InputNumber
                      min={0}
                      max={999}
                      value={customMin}
                      onChange={(value) => setCustomMin(value || 0)}
                      placeholder="最小值"
                      style={{ width: 100 }}
                    />
                    <span>-</span>
                    <InputNumber
                      min={0}
                      max={999}
                      value={customMax}
                      onChange={(value) => setCustomMax(value || 999)}
                      placeholder="最大值"
                      style={{ width: 100 }}
                    />
                  </Space>
                )}
              </Space>
            )}
          </Space>
        </div>
      }
      style={{ height: 'calc(100vh - 64px - 48px)' }}
    >
      <Table
        rowKey={(record) => record.spu_id}
        rowSelection={{
          selectedRowKeys,
          onChange: setSelectedRowKeys,
        }}
        size='large'
        key={`table-${page}-${pageSize}`}
        columns={[
          {
            title: "违规描述",
            dataIndex: "violation_desc",
            width: 150,
            render: (desc: string) => (
              <div style={{ 
                maxWidth: 150, 
                wordBreak: 'break-word',
                lineHeight: '1.4',
                fontSize: '13px'
              }}>
                {desc || "-"}
              </div>
            )
          },
          { 
            title: "图片", 
            dataIndex: "goods_img_url", 
            width: 160,
            render: (url: string) => url ? <Image width={120} src={url} /> : null 
          },
          {
            title: "商品ID",
            dataIndex: "spu_id",
            width: 120,
            render: (text: string) => <span style={{ fontSize: '16px', fontWeight: 'bold' }}>{text}</span>
          },
          { 
            title: "商品名称", 
            dataIndex: "goods_name",
            width: 300,
            render: (name: string) => (
              <div style={{ 
                maxWidth: 300, 
                wordBreak: 'break-word',
                lineHeight: '1.4',
                display: '-webkit-box',
                WebkitLineClamp: 2,
                WebkitBoxOrient: 'vertical',
                overflow: 'hidden',
                textOverflow: 'ellipsis'
              }}>
                {name}
              </div>
            )
          },
          {
            title: "违规信息",
            dataIndex: "site_num",
            width: 160,
            render: (_, record) => {
              const isAllSite = record.site_num === 1 &&
                Array.isArray(record.punish_detail_list) &&
                record.punish_detail_list.some((d: any) => d.site_id === -1);
              
              // 检查是否包含美国站违规
              const hasUSViolation = Array.isArray(record.punish_detail_list) &&
                record.punish_detail_list.some((d: any) => d.site_id === 100);
              
              const punishNum = (record as any).punish_num || 0;
              
              return (
                <div style={{ fontSize: '14px' }}>
                  {/* 违规站点数 */}
                  <div style={{ marginBottom: '4px' }}>
                    {isAllSite ? (
                      <span style={{ fontWeight: 'bold', color: '#ff4d4f' }}>
                        全部站点违规
                      </span>
                    ) : (
                      <span style={{ fontWeight: 'bold' }}>
                        {record.site_num} 个站点
                      </span>
                    )}
                  </div>
                  
                  {/* 违规记录数 */}
                  <div style={{ marginBottom: '2px', color: '#666' }}>
                    {punishNum} 条记录
                  </div>
                  
                  {/* 美国站标识 */}
                  {hasUSViolation && (
                    <div>
                      <span style={{ 
                        backgroundColor: '#ff4d4f',
                        color: '#fff',
                        padding: '2px 6px',
                        borderRadius: '3px',
                        fontSize: '12px',
                        fontWeight: 'bold'
                      }}>
                        含美国站
                      </span>
                    </div>
                  )}
                </div>
              );
            }
          },
          {
            title: "操作",
            width: 100,
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
        rowClassName={record => viewedIds.includes(record.spu_id) ? "viewed-row" : ""}
      />
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