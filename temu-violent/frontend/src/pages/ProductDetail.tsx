import React, { useEffect, useState } from "react";
import { useParams, useLocation, useNavigate } from "react-router-dom";
import { Card, Button, Table, message, Image, Descriptions, Input, Modal, notification, Tag, Space } from "antd";
import { CopyOutlined } from "@ant-design/icons";
import { useGlobalNotification } from './GlobalNotification';
import { useUnpublishedRecords } from '../contexts/UnpublishedRecordsContext';

// 支持通过props传递spu_id、violationData和onClose
const ProductDetail: React.FC<{ spu_id?: string, violationData?: any, onClose?: () => void }> = ({ spu_id: propSpuId, violationData: propViolationData, onClose }) => {
  const params = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const spu_id = propSpuId || params.spu_id;
  const violationData = propViolationData || location.state;
  const notify = useGlobalNotification();
  const { addRecords } = useUnpublishedRecords();
  const [product, setProduct] = useState<any>(null); // 商品详情
  const [related, setRelated] = useState<any[]>([]); // 关联商品列表
  const [detailLoading, setDetailLoading] = useState(false); // 详情页loading
  const [relatedLoading, setRelatedLoading] = useState(false); // 关联商品loading
  const [searchName, setSearchName] = useState(""); // 关联搜索输入框内容
  const [selectedRelatedKeys, setSelectedRelatedKeys] = useState<React.Key[]>([]); // 关联商品多选
  const [offlineResults, setOfflineResults] = useState<{[key: string]: {success: boolean, message: string}}>({}); // 下架结果缓存

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
            setSearchName(words);
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
    try {
      const res = await fetch("/api/temu/seller/offline", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          productIds: [parseInt(spu_id || "0")],
          max_threads: 4  // 单个商品使用较少线程
        }),
      });
      const data = await res.json();
      if (data.success) {
        // 新的返回格式处理
        const successCount = data.summary?.success || 0;
        const failCount = data.summary?.failed || 0;
        const totalCount = data.summary?.total || 0;
        
        // 更新下架结果缓存
        const newResults = { ...offlineResults };
        if (data.results) {
          data.results.forEach((item: any) => {
            newResults[item.productId.toString()] = {
              success: item.success,
              message: item.message
            };
          });
        }
        setOfflineResults(newResults);
        
        notify({
          type: 'info',
          message: "下架结果",
          description: (
            <div>
              <div style={{ marginBottom: 12 }}>
                <span style={{ color: 'green' }}>下架成功：{successCount} 个</span>
                <span style={{ color: 'red', marginLeft: 16 }}>下架失败：{failCount} 个</span>
                <span style={{ color: 'blue', marginLeft: 16 }}>总计：{totalCount} 个</span>
              </div>
              {data.results && data.results.map((item: any) => (
                <div key={item.productId} style={{ marginBottom: 8 }}>
                  商品ID: {item.productId} - {item.success ? (
                    <span style={{ color: 'green' }}>{item.message}</span>
                  ) : (
                    <span style={{ color: 'red' }}>{item.message}</span>
                  )}
                </div>
              ))}
            </div>
          ) as any,
        });
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
      setDetailLoading(false);
    }
  };

  // 一键下架关联商品
  const handleOfflineRelated = async () => {
    if (selectedRelatedKeys.length === 0) {
      message.warning("请先选择要下架的关联商品");
      return;
    }
    setRelatedLoading(true);
    try {
      const res = await fetch("/api/temu/seller/offline", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
          productIds: selectedRelatedKeys.map(key => parseInt(key.toString())),
          max_threads: 8  // 批量下架使用更多线程
        }),
      });
      const data = await res.json();
      if (data.success) {
        // 新的返回格式处理
        const successCount = data.summary?.success || 0;
        const failCount = data.summary?.failed || 0;
        const totalCount = data.summary?.total || 0;
        
        // 更新下架结果缓存
        const newResults = { ...offlineResults };
        if (data.results) {
          data.results.forEach((item: any) => {
            newResults[item.productId.toString()] = {
              success: item.success,
              message: item.message
            };
          });
        }
        setOfflineResults(newResults);
        
        // 收集未发布的SKC
        const unpublishedSkcs = selectedRelatedKeys
          .map(key => {
            const product = related.find(r => r.productSkcId === key);
            console.log('检查商品:', product); // 调试信息
            if (product) {
              const status = getProductStatus(product.skcStatus, product.skcSiteStatus);
              console.log('商品状态:', status, 'SKC状态:', product.skcStatus, '站点状态:', product.skcSiteStatus); // 调试信息
              if (status === '未发布') {
                const record = {
                  skcId: product.productSkcId,
                  productId: product.productId,
                  productName: product.productName,
                  mainImageUrl: product.mainImageUrl,
                  category: product.leafCat || { catId: 0, catName: '未知类目' },
                  source: 'product-detail'
                };
                console.log('收集未发布SKC:', record); // 调试信息
                return record;
              }
            }
            return null;
          })
          .filter(Boolean);

        console.log('最终收集的未发布SKC:', unpublishedSkcs); // 调试信息

        if (unpublishedSkcs.length > 0) {
          addRecords(unpublishedSkcs);
        } else {
          console.log('没有找到未发布的SKC'); // 调试信息
        }

        // 合并显示下架结果和SKC收集结果
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
                <div key={item.productId} style={{ marginBottom: 8 }}>
                  商品ID: {item.productId} - {item.success ? (
                    <span style={{ color: 'green' }}>{item.message}</span>
                  ) : (
                    <span style={{ color: 'red' }}>{item.message}</span>
                  )}
                </div>
              ))}
            </div>
          ) as any,
        });
        
        handleRelatedSearch(); // 下架后刷新关联商品列表
        setSelectedRelatedKeys([]); // 清空多选
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
      setRelatedLoading(false);
    }
  };

  // 复制文本到剪贴板
  const handleCopy = async (text: string) => {
    try {
      await navigator.clipboard.writeText(text);
      notify({
        type: 'success',
        message: '复制成功',
        description: `已复制"${text}"到剪贴板`
      });
    } catch (err) {
      // 降级方案：使用传统方法
      const textArea = document.createElement('textarea');
      textArea.value = text;
      document.body.appendChild(textArea);
      textArea.select();
      document.execCommand('copy');
      document.body.removeChild(textArea);
      notify({
        type: 'success',
        message: '复制成功',
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

  return (
    <Card
      title="违规商品详情"
      loading={detailLoading}
      extra={<Button onClick={onClose ? onClose : () => navigate(-1)}>返回</Button>}
      style={{ fontSize: '18px' }}
    >
      {/* 商品信息区域 - 左右排列 */}
      <div style={{ display: 'flex', gap: '16px', marginBottom: '16px' }}>
        {/* 违规商品原始信息 - 左侧 */}
        <div style={{ flex: 1 }}>
          <Descriptions title="违规商品信息" bordered column={1} size="default" style={{ fontSize: '17px' }}>
            <Descriptions.Item label="商品ID">{violationData?.spu_id}</Descriptions.Item>
            <Descriptions.Item label="商品名称">{violationData?.goods_name}</Descriptions.Item>
            <Descriptions.Item label="主图">
              {violationData?.goods_img_url && <Image width={120} src={violationData.goods_img_url} />}
            </Descriptions.Item>
            <Descriptions.Item label="违规站点">
              {(() => {
                const isAllSite = violationData?.site_num === 1 &&
                  Array.isArray(violationData?.punish_detail_list) &&
                  violationData.punish_detail_list.some((d: any) => d.site_id === -1);
                if (isAllSite) return "全部站点违规";
                return violationData?.site_num;
              })()}
            </Descriptions.Item>
            <Descriptions.Item label="违规描述">{violationData?.violation_desc || '-'}</Descriptions.Item>
            {/* 展示所有原始字段 */}
            {/* {violationData &&
              Object.entries(violationData).map(([k, v]) => (
                <Descriptions.Item key={k} label={k}>
                  {String(v)}
                </Descriptions.Item>
              ))} */}
          </Descriptions>
        </div>
        
        {/* 商品详情 - 右侧 */}
        <div style={{ flex: 1 }}>
          <Descriptions title="商品详情" bordered column={1} size="default" style={{ fontSize: '17px' }}>
            {/* <Descriptions.Item label="商品ID">{product?.productId}</Descriptions.Item> */}
            <Descriptions.Item label="商品名称">{product?.productName}</Descriptions.Item>
            <Descriptions.Item label="创建时间">
              {product?.createdAt ? new Date(product.createdAt).toLocaleString('zh-CN') : '-'}
            </Descriptions.Item>
            <Descriptions.Item label="主图">
              {product?.mainImageUrl && <Image width={120} src={product.mainImageUrl} />}
            </Descriptions.Item>
            {/* 可补充更多字段 */}
          </Descriptions>
        </div>
      </div>

      {/* 关联搜索输入框 */}
      <Space style={{ margin: 16 }}>
        <Input.Search
          placeholder="输入商品名称进行关联搜索"
          value={searchName}
          onChange={e => setSearchName(e.target.value)}
          onSearch={v => handleRelatedSearch(v)}
          style={{ width: 300, fontSize: '17px' }}
          enterButton="关联搜索"
          loading={relatedLoading}
        />
        <Button
          icon={<CopyOutlined />}
          onClick={() => handleCopy(searchName)}
          disabled={!searchName.trim()}
          title="复制搜索内容"
          style={{ fontSize: '17px' }}
        >
          复制
        </Button>
      </Space>
      {/* 关联商品表格，支持多选 */}
      <Table
        rowKey="productSkcId"
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
                <span style={{ 
                  color: text === spu_id ? 'red' : 'inherit', 
                  fontSize: '16px' 
                }}>
                  {text}
                </span>
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
            render: (price: number, record: any) => {
              // 从 productSkuSummaries 数组中获取 supplierPrice
              const skuSummaries = record.productSkuSummaries;
              if (!skuSummaries || skuSummaries.length === 0) {
                return <span style={{ fontSize: '16px', color: '#999' }}>-</span>;
              }
              
              // 查找第一个有 supplierPrice 值的 SKU
              const skuWithPrice = skuSummaries.find((sku: any) => sku.supplierPrice && sku.supplierPrice > 0);
              if (!skuWithPrice) {
                return <span style={{ fontSize: '16px', color: '#999' }}>-</span>;
              }
              
              return (
                <span style={{ 
                  fontSize: '16px', 
                  fontWeight: 'bold',
                  color: '#52c41a'
                }}>
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
              const status = getProductStatus(record.skcStatus, record.skcSiteStatus);
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
                <span style={{ 
                  fontSize: '16px',
                  color: color,
                  padding: '4px 8px',
                  borderRadius: '4px',
                  fontWeight: 'bold',
                  display: 'inline-block',
                  minWidth: '60px',
                  textAlign: 'center'
                }}>
                  {status}
                </span>
              );
            },
          },
          {
            title: "虚拟库存",
            dataIndex: "virtualStock",
            render: (virtualStock: number, record: any) => {
              // 从 productSkuSummaries 中获取虚拟库存信息
              const skuSummaries = record.productSkuSummaries;
              if (!skuSummaries || skuSummaries.length === 0) {
                return <span style={{ fontSize: '16px', color: '#999' }}>-</span>;
              }
              
              // 计算总虚拟库存
              const totalVirtualStock = skuSummaries.reduce((sum: number, sku: any) => {
                return sum + (sku.virtualStock || 0);
              }, 0);
              
              // 根据库存数量显示不同颜色
              let color = '#52c41a'; // 绿色 - 库存充足
              if (totalVirtualStock <= 10) {
                color = '#ff4d4f'; // 红色 - 库存不足
              } else if (totalVirtualStock <= 50) {
                color = '#faad14'; // 橙色 - 库存警告
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
                <div style={{ 
                  maxWidth: '200px',
                  wordBreak: 'break-word',
                  whiteSpace: 'pre-wrap',
                  lineHeight: '1.4'
                }}>
                  <Tag color={result.success ? 'green' : 'red'} style={{ marginBottom: '4px', fontSize: '15px' }}>
                    {result.success ? '成功' : '失败'}
                  </Tag>
                  <div style={{ 
                    fontSize: '15px',
                    color: result.success ? '#52c41a' : '#ff4d4f',
                    marginTop: '4px'
                  }}>
                    {result.message}
                  </div>
                </div>
              );
            },
          },
        ]}
        dataSource={related}
        loading={relatedLoading}
        title={() => <div style={{ fontSize: 20, fontWeight: 'bold' }}>关联商品列表</div>}
        rowSelection={{
          selectedRowKeys: selectedRelatedKeys,
          onChange: setSelectedRelatedKeys,
          columnWidth: 60,
        }}
        pagination={{
          pageSize: 50,
          showSizeChanger: true,
          showQuickJumper: true,
          showTotal: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条记录`,
          pageSizeOptions: ['20', '50', '100'],
        }}
      />
      
      {/* 固定在抽屉底部的下架按钮区域 */}
      <div style={{
        position: 'sticky',
        bottom: 0,
        backgroundColor: '#fff',
        padding: '16px 24px',
        margin: '16px 0 0 0',
        display: 'inline-flex',
        justifyContent: 'flex-start',
        gap: '16px',
        borderRadius: '8px',
        boxShadow: '0 2px 8px rgba(0, 0, 0, 0.1)',
      }}>
        <Button
          type="primary"
          danger
          size="large"
          onClick={handleOfflineRelated}
          disabled={selectedRelatedKeys.length === 0}
          loading={relatedLoading}
          style={{ fontSize: '17px' }}
        >
          一键下架关联商品 ({selectedRelatedKeys.length})
        </Button>
      </div>
    </Card>
  );
};

export default ProductDetail; 