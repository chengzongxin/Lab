import React, { useEffect, useState } from "react";
import { useParams, useLocation, useNavigate } from "react-router-dom";
import { Card, Button, Table, message, Image, Descriptions, Input, Modal, notification, Tag } from "antd";
import { useGlobalNotification } from './GlobalNotification';

// 支持通过props传递spu_id、violationData和onClose
const ProductDetail: React.FC<{ spu_id?: string, violationData?: any, onClose?: () => void }> = ({ spu_id: propSpuId, violationData: propViolationData, onClose }) => {
  const params = useParams();
  const location = useLocation();
  const navigate = useNavigate();
  const spu_id = propSpuId || params.spu_id;
  const violationData = propViolationData || location.state;
  const notify = useGlobalNotification();
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
    >
      {/* 违规商品原始信息 */}
      <Descriptions title="违规商品信息" bordered column={1} size="small">
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
      <br />
      {/* 商品详情 */}
      <Descriptions title="商品详情" bordered column={1} size="small">
        {/* <Descriptions.Item label="商品ID">{product?.productId}</Descriptions.Item> */}
        <Descriptions.Item label="商品名称">{product?.productName}</Descriptions.Item>
        <Descriptions.Item label="主图">
          {product?.mainImageUrl && <Image width={120} src={product.mainImageUrl} />}
        </Descriptions.Item>
        {/* 可补充更多字段 */}
      </Descriptions>

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
        rowKey="productSkcId"
        columns={[
          { title: "SKC ID", dataIndex: "productSkcId" },
          { title: "商品ID", dataIndex: "productId", render: (text: string) => text === spu_id ? <span style={{ color: 'red' }}>{text}</span> : text },
          { title: "商品名称", dataIndex: "productName" },
          {
            title: "主图",
            dataIndex: "mainImageUrl",
            render: (url: string) => (url ? <Image width={150} src={url} /> : null),
          },
          {
            title: "发布状态",
            render: (_: any, record: any) => getProductStatus(record.skcStatus, record.skcSiteStatus),
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
                    <Tag color={result.success ? 'green' : 'red'} style={{ marginBottom: '4px' }}>
                      {result.success ? '成功' : '失败'}
                    </Tag>
                    <div style={{ 
                      fontSize: '12px',
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
        title={() => "关联商品列表"}
        rowSelection={{
          selectedRowKeys: selectedRelatedKeys,
          onChange: setSelectedRelatedKeys,
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
          onClick={handleOffline}
          loading={detailLoading}
        >
          下架该商品
        </Button>
        <Button
          type="primary"
          danger
          size="large"
          onClick={handleOfflineRelated}
          disabled={selectedRelatedKeys.length === 0}
          loading={relatedLoading}
        >
          一键下架关联商品 ({selectedRelatedKeys.length})
        </Button>
      </div>
    </Card>
  );
};

export default ProductDetail; 