import React, { useState } from 'react';
import axios from 'axios';
import './TemuSellerCrawler.css';

const TemuSellerCrawler: React.FC = () => {
    const [sellerUrl, setSellerUrl] = useState('');
    const [maxPages, setMaxPages] = useState(10);
    const [minSales, setMinSales] = useState(200); // 默认最小销量改为200
    const [debugPort, setDebugPort] = useState<number>(9222); // 默认端口9222
    const [usePersistentContext, setUsePersistentContext] = useState(false);
    const [isRunning, setIsRunning] = useState(false);
    const [message, setMessage] = useState('');

    const extractMallId = (url: string): string | null => {
        // 从URL中提取mall_id
        const match = url.match(/mall_id[=:](\d+)/);
        return match ? match[1] : null;
    };

    const startCrawl = async () => {
        if (!sellerUrl.trim()) {
            setMessage('❌ 请输入卖家店铺URL');
            return;
        }

        const mallId = extractMallId(sellerUrl);
        if (!mallId) {
            setMessage('❌ 无法从URL中提取店铺ID，请检查URL格式');
            return;
        }

        setIsRunning(true);
        setMessage(`正在启动爬取卖家店铺 (ID: ${mallId})...`);

        try {
            const response = await axios.post('http://localhost:8000/api/crawl/temu/seller', {
                mall_id: mallId,
                max_pages: maxPages,
                min_sales: minSales,
                use_persistent_context: usePersistentContext,
                debug_port: debugPort
            });

            if (response.data.success) {
                setMessage(`✅ ${response.data.message}`);
            }
        } catch (error: any) {
            setMessage(`❌ 启动失败: ${error.response?.data?.detail || error.message}`);
        } finally {
            setIsRunning(false);
        }
    };

    return (
        <div className="temu-seller-crawler">
            <div className="header">
                <h2>🏪 TEMU卖家店铺爬取</h2>
                <p className="subtitle">爬取指定卖家店铺的所有商品，包含卖家信息</p>
            </div>

            <div className="form-container">
                <div className="form-group">
                    <label>卖家店铺URL</label>
                    <input
                        type="text"
                        value={sellerUrl}
                        onChange={(e) => setSellerUrl(e.target.value)}
                        placeholder="https://www.temu.com/mall.html?mall_id=634418218462973&..."
                        className="input-url"
                    />
                    <span className="hint">粘贴完整的TEMU卖家店铺链接</span>
                </div>

                <div className="form-row">
                    <div className="form-group">
                        <label>滚动次数</label>
                        <input
                            type="number"
                            value={maxPages}
                            onChange={(e) => setMaxPages(parseInt(e.target.value))}
                            min="1"
                            max="30"
                            className="input-number"
                        />
                        <span className="hint">页面滚动加载次数</span>
                    </div>

                    <div className="form-group">
                        <label>最小销量</label>
                        <input
                            type="number"
                            value={minSales}
                            onChange={(e) => setMinSales(parseInt(e.target.value))}
                            min="0"
                            className="input-number"
                        />
                        <span className="hint">只保存销量大于此值的商品</span>
                    </div>
                </div>

                <div className="form-row">
                    <div className="form-group">
                        <label>调试端口</label>
                        <input
                            type="number"
                            value={debugPort}
                            onChange={(e) => setDebugPort(parseInt(e.target.value))}
                            className="input-number"
                        />
                        <span className="hint">连接已打开的浏览器（默认9222）</span>
                    </div>
                </div>

                <div className="checkbox-group">
                    <label className="checkbox-label">
                        <input
                            type="checkbox"
                            checked={usePersistentContext}
                            onChange={(e) => setUsePersistentContext(e.target.checked)}
                        />
                        <span>使用持久化上下文（保持登录状态）</span>
                    </label>
                </div>

                <button
                    className="btn-start"
                    onClick={startCrawl}
                    disabled={isRunning}
                >
                    {isRunning ? '⏳ 爬取中...' : '🚀 开始爬取'}
                </button>

                {message && (
                    <div className={`message ${message.startsWith('❌') ? 'error' : 'success'}`}>
                        {message}
                    </div>
                )}
            </div>

            <div className="info-box">
                <h3>📖 使用说明</h3>
                <ol>
                    <li>访问TEMU，找到目标卖家店铺</li>
                    <li>复制店铺页面的完整URL（包含mall_id参数）</li>
                    <li>粘贴到上方输入框，设置参数后点击"开始爬取"</li>
                    <li>爬取完成后，商品会自动保存到数据库的 <code>temu_products</code> 表</li>
                    <li>每个商品都会包含卖家信息：卖家名称、头像、店铺ID</li>
                </ol>
            </div>
        </div>
    );
};

export default TemuSellerCrawler;
