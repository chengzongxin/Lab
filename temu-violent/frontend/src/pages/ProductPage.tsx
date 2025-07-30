import React, { useState } from "react";
import { Card, Input, Button, Table, Space, Image, Tag } from "antd";
import { CopyOutlined } from "@ant-design/icons";
import { useGlobalNotification } from './GlobalNotification';
import { useUnpublishedRecords } from '../contexts/UnpublishedRecordsContext';
import { useProductSearchContext } from './ProductSearchContext';

interface Product {
  productId: string;
  productName: string;
  mainImageUrl?: string;
  productSkcId?: string;
  skcStatus?: number;
  skcSiteStatus?: number;
  leafCat?: { catId: number; catName: string };
  productSkuSummaries?: any[];
  createdAt?: string;
  price?: number;
  virtualStock?: number;
  categories?: any;
}

const ProductPage: React.FC = () => {
  const {
    searchName, setSearchName,
    searchIds, setSearchIds,
    products, setProducts,
    selectedRowKeys, setSelectedRowKeys
  } = useProductSearchContext();
  const [loading, setLoading] = useState(false);
  const [offlineResults, setOfflineResults] = useState<{[key: string]: {success: boolean, message: string}}>({}); // 下架结果缓存

  const notify = useGlobalNotification();
  const { addRecords } = useUnpublishedRecords();

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
      notify({
        type: 'error',
        message: "输入提示",
        description: "请输入商品ID或名称"
      });
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

      if (data.data.length === 0) {
        notify({
          type: 'info',
          message: "查询提示",
          description: "未找到商品"
        });
      }
    } else {
      notify({
        type: 'error',
        message: "查询失败",
        description: data.msg || "查询商品信息失败，请检查输入或稍后重试"
      });
    }
    setLoading(false);
  };

  // 复制文本到剪贴板
  const handleCopy = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      notify({
        type: 'success',
        message: "复制成功",
        description: `已复制"${text}"到剪贴板`
      });
    } catch (err) {
      // 降级方案
      const textArea = document.createElement('textarea');
      textArea.value = text;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      notify({
        type: 'success',
        message: "复制成功",
        description: `已复制"${text}"到剪贴板`
      });
    }
  };

  // 判断商品发布状态的函数
  function getProductStatus(skcStatus: number, skcSiteStatus: number) {
    if ((skcStatus === 1 || skcStatus === 7 || skcStatus === 10) && skcSiteStatus === 0) {
      return "未发布";
    }
    if (skcStatus === 11 && skcSiteStatus === 1) {
      return "在售中";
    }
    if (skcStatus === 11 && skcSiteStatus === 0) {
      return "已下架";
    }
    return "未知状态";
  }

  // 批量下架函数
  const handleBatchOffline = async () => {
    if (selectedRowKeys.length === 0) {
      notify({
        type: 'error',
        message: "操作提示",
        description: "请先选择要下架的商品"
      });
      return;
    }
    setLoading(true);
    try {
      const res = await fetch("/api/temu/seller/offline", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          productIds: selectedRowKeys.map(id => parseInt(id.toString())),
          max_threads: 8
        }),
      });
      const data = await res.json();
      if (data.success) {
        // 更新下架结果缓存
        const newResults = { ...offlineResults };
        if (data.results) {
          data.results.forEach((item: any) => {
            newResults[item.productSkcId?.toString() || item.productId?.toString()] = {
              success: item.success,
              message: item.message
            };
          });
        }
        setOfflineResults(newResults);

        // 收集未发布SKC
        const unpublishedSkcs = selectedRowKeys
          .map(key => {
            const product = products.find(r => r.productSkcId === key);
            if (product) {
              const status = getProductStatus(product.skcStatus ?? 0, product.skcSiteStatus ?? 0);
              if (status === '未发布') {
                return {
                  skcId: product.productSkcId,
                  productId: product.productId,
                  productName: product.productName,
                  mainImageUrl: product.mainImageUrl,
                  category: product.leafCat || { catId: 0, catName: '未知类目' },
                  source: 'product-page'
                };
              }
            }
            return null;
          })
          .filter(Boolean);
        if (unpublishedSkcs.length > 0) {
          addRecords(unpublishedSkcs);
        }

        // 弹窗通知
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
              {unpublishedSkcs.length > 0 && (
                <div style={{ marginBottom: 12, padding: '8px', backgroundColor: '#f6ffed', borderRadius: '4px', border: '1px solid #b7eb8f' }}>
                  <span style={{ color: '#52c41a', fontWeight: 'bold' }}>
                    ✓ 已收集 {unpublishedSkcs.length} 个未发布SKC到记录中
                  </span>
                </div>
              )}
              {data.results && data.results.map((item: any) => (
                <div key={item.productSkcId || item.productId} style={{ marginBottom: 8 }}>
                  SKC ID: {item.productSkcId || item.productId} - {item.success ? (
                    <span style={{ color: 'green' }}>{item.message}</span>
                  ) : (
                    <span style={{ color: 'red' }}>{item.message}</span>
                  )}
                </div>
              ))}
            </div>
          ) as any,
        });
        // 刷新商品列表
        handleSearch();
        setSelectedRowKeys([]);
      } else {
        notify({
          type: 'error',
          message: "下架失败",
          description: data.msg || data.message || "下架失败"
        });
      }
    } catch (error) {
      notify({
        type: 'error',
        message: "下架失败",
        description: `网络错误: ${error}`
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <Card
      title="商品搜索"
      style={{ height: 'calc(100vh - 64px - 48px)' }}
    >
      <Space style={{ marginBottom: 16 }}>
        <Input
          placeholder="输入商品ID，支持多个用逗号分隔"
          value={searchIds}
          onChange={e => setSearchIds(e.target.value)}
          style={{ width: 260 }}
          onPressEnter={handleSearch}
        />
        <Input
          placeholder="输入商品名称"
          value={searchName}
          onChange={e => setSearchName(e.target.value)}
          style={{ width: 200 }}
          onPressEnter={handleSearch}
        />
        <Button type="primary" onClick={handleSearch} loading={loading}>搜索</Button>
        <Button
          type="primary"
          danger
          disabled={selectedRowKeys.length === 0}
          loading={loading}
          onClick={handleBatchOffline}
        >
          批量下架({selectedRowKeys.length})
        </Button>
      </Space>
      <Table
        rowKey="productSkcId"
        rowSelection={{
          selectedRowKeys,
          onChange: setSelectedRowKeys,
          columnWidth: 60,
        }}
        columns={[
          {
            title: "SKC ID",
            dataIndex: "productSkcId",
            render: (text: string) => (
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '16px' }}>{text}</span>
                <Button
                  type="text"
                  size="small"
                  icon={<CopyOutlined />}
                  onClick={() => handleCopy(text)}
                  style={{ padding: '2px 4px', minWidth: 'auto' }}
                  title="复制SKC ID"
                />
              </div>
            )
          },
          {
            title: "商品ID",
            dataIndex: "productId",
            render: (text: string) => (
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                <span style={{ fontSize: '16px' }}>{text}</span>
                <Button
                  type="text"
                  size="small"
                  icon={<CopyOutlined />}
                  onClick={() => handleCopy(text)}
                  style={{ padding: '2px 4px', minWidth: 'auto' }}
                  title="复制商品ID"
                />
              </div>
            )
          },
          {
            title: "商品名称",
            dataIndex: "productName",
            render: (text: string) => <span style={{ fontSize: '16px' }}>{text}</span>
          },
          {
            title: "价格",
            dataIndex: "price",
            width: 120,
            render: (_: any, record: any) => {
              const skuSummaries = record.productSkuSummaries;
              if (!skuSummaries || skuSummaries.length === 0) {
                return <span style={{ fontSize: '16px', color: '#999' }}>-</span>;
              }
              const skuWithPrice = skuSummaries.find((sku: any) => sku.supplierPrice && sku.supplierPrice > 0);
              if (!skuWithPrice) {
                return <span style={{ fontSize: '16px', color: '#999' }}>-</span>;
              }
              return (
                <span style={{ fontSize: '16px', fontWeight: 'bold', color: '#52c41a' }}>
                  ${(skuWithPrice.supplierPrice / 100).toFixed(2)}
                </span>
              );
            },
          },
          {
            title: "创建时间",
            dataIndex: "createdAt",
            width: 160,
            render: (createdAt: string) => {
              if (!createdAt) {
                return <span style={{ fontSize: '16px', color: '#999' }}>-</span>;
              }
              return (
                <span style={{ fontSize: '16px' }}>
                  {new Date(createdAt).toLocaleString('zh-CN')}
                </span>
              );
            },
          },
          {
            title: "主图",
            dataIndex: "mainImageUrl",
            render: (url: string) => (url ? <Image width={150} src={url} /> : null),
          },
          {
            title: "发布状态",
            width: 120,
            render: (_: any, record: any) => {
              const status = getProductStatus(record.skcStatus ?? 0, record.skcSiteStatus ?? 0);
              let color = '#666';
              let backgroundColor = '#f5f5f5';
              switch (status) {
                case '在售中':
                  color = '#52c41a';
                  backgroundColor = '#f6ffed';
                  break;
                case '已下架':
                  color = '#ff4d4f';
                  backgroundColor = '#fff2f0';
                  break;
                case '未发布':
                  color = '#faad14';
                  backgroundColor = '#fffbe6';
                  break;
                default:
                  color = '#666';
                  backgroundColor = '#f5f5f5';
              }
              return (
                <span style={{ fontSize: '16px', color: color, padding: '4px 8px', borderRadius: '4px', fontWeight: 'bold', display: 'inline-block', minWidth: '60px', textAlign: 'center' }}>
                  {status}
                </span>
              );
            },
          },
          {
            title: "虚拟库存",
            dataIndex: "virtualStock",
            render: (_: number, record: any) => {
              const skuSummaries = record.productSkuSummaries;
              if (!skuSummaries || skuSummaries.length === 0) {
                return <span style={{ fontSize: '16px', color: '#999' }}>-</span>;
              }
              const totalVirtualStock = skuSummaries.reduce((sum: number, sku: any) => sum + (sku.virtualStock || 0), 0);
              let color = '#52c41a';
              if (totalVirtualStock <= 10) {
                color = '#ff4d4f';
              } else if (totalVirtualStock <= 50) {
                color = '#faad14';
              }
              return (
                <span style={{ fontSize: '16px', color: color, fontWeight: 'bold' }}>
                  {totalVirtualStock.toLocaleString()}
                </span>
              );
            },
          },
          {
            title: "下架结果",
            dataIndex: "productSkcId",
            render: (productSkcId: string) => {
              const result = offlineResults[productSkcId];
              if (!result) return null;
              return (
                <div style={{ maxWidth: '200px', wordBreak: 'break-word', whiteSpace: 'pre-wrap', lineHeight: '1.4' }}>
                  <Tag color={result.success ? 'green' : 'red'} style={{ marginBottom: '4px', fontSize: '15px' }}>
                    {result.success ? '成功' : '失败'}
                  </Tag>
                  <div style={{ fontSize: '15px', color: result.success ? '#52c41a' : '#ff4d4f', marginTop: '4px' }}>
                    {result.message}
                  </div>
                </div>
              );
            },
          },
        ]}
        dataSource={products}
        loading={loading}
        pagination={{
          pageSize: 50,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条记录`,
          pageSizeOptions: ['20', '50', '100'],
        }}
        scroll={{ y: 'calc(100vh - 64px - 48px - 168px)' }}
      />
    </Card>
  );
};

export default ProductPage; 