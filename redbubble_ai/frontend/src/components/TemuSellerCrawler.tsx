import React, { useState } from 'react';
import axios from 'axios';
import './TemuSellerCrawler.css';

const TemuSellerCrawler: React.FC = () => {
    const [sellerUrls, setSellerUrls] = useState(''); // 改为复数，支持多个URL
    const [maxPages, setMaxPages] = useState(10);
    const [minSales, setMinSales] = useState(200); // 默认最小销量改为200
    const [debugPort, setDebugPort] = useState<number>(9222); // 默认端口9222
    const [usePersistentContext, setUsePersistentContext] = useState(false);
    const [isRunning, setIsRunning] = useState(false);
    const [message, setMessage] = useState('');
    const [progressLogs, setProgressLogs] = useState<string[]>([]); // 进度日志

    const extractMallId = (url: string): string | null => {
        // 从URL中提取mall_id
        const match = url.match(/mall_id[=:](\d+)/);
        return match ? match[1] : null;
    };

    const startCrawl = async () => {
        if (!sellerUrls.trim()) {
            setMessage('❌ 请输入卖家店铺URL（支持多个，一行一个）');
            return;
        }

        // 解析多个URL（按行分割，过滤空行）
        const urls = sellerUrls.split('\n')
            .map(url => url.trim())
            .filter(url => url.length > 0);

        if (urls.length === 0) {
            setMessage('❌ 请输入至少一个有效的URL');
            return;
        }

        setIsRunning(true);
        setProgressLogs([]);
        setMessage(`📋 准备批量爬取 ${urls.length} 个店铺...`);

        let successCount = 0;
        let failCount = 0;
        let skippedCount = 0;

        // 依次处理每个URL
        for (let i = 0; i < urls.length; i++) {
            const url = urls[i];
            const currentIndex = i + 1;
            
            // 添加进度日志
            const progressMsg = `\n[${currentIndex}/${urls.length}] 正在处理: ${url.substring(0, 60)}...`;
            setProgressLogs(prev => [...prev, progressMsg]);
            setMessage(`🔄 [${currentIndex}/${urls.length}] 正在爬取...`);

            try {
                const mallId = extractMallId(url);
                if (!mallId) {
                    const errorMsg = `❌ [${currentIndex}/${urls.length}] 无法提取店铺ID`;
                    setProgressLogs(prev => [...prev, errorMsg]);
                    failCount++;
                    continue;
                }

                const response = await axios.post('http://localhost:8000/api/crawl/temu/seller', {
                    mall_id: mallId,
                    max_pages: maxPages,
                    min_sales: minSales,
                    use_persistent_context: usePersistentContext,
                    debug_port: debugPort
                }, {
                    timeout: 1800000  // 30分钟超时（爬取可能需要较长时间）
                });

                // 处理跳过的店铺（已存在）
                if (response.data.skipped) {
                    const skipMsg = `⏭️ [${currentIndex}/${urls.length}] 跳过（店铺ID: ${mallId}）\n   └─ ${response.data.message}`;
                    setProgressLogs(prev => [...prev, skipMsg]);
                    skippedCount++;
                } else if (response.data.success) {
                    const successMsg = `✅ [${currentIndex}/${urls.length}] ${response.data.message}`;
                    setProgressLogs(prev => [...prev, successMsg]);
                    successCount++;
                } else {
                    const errorMsg = `❌ [${currentIndex}/${urls.length}] 爬取失败`;
                    setProgressLogs(prev => [...prev, errorMsg]);
                    failCount++;
                }
            } catch (error: any) {
                const errorMsg = `❌ [${currentIndex}/${urls.length}] 错误: ${error.response?.data?.detail || error.message}`;
                setProgressLogs(prev => [...prev, errorMsg]);
                failCount++;
            }
        }

        // 显示最终结果
        const finalMsg = `\n🎉 批量爬取完成！\n   成功: ${successCount} | 跳过: ${skippedCount} | 失败: ${failCount} | 总计: ${urls.length}`;
        setProgressLogs(prev => [...prev, finalMsg]);
        setMessage(`✅ 批量爬取完成！成功 ${successCount}, 跳过 ${skippedCount}, 失败 ${failCount}`);
        setIsRunning(false);
    };

    return (
        <div className="temu-seller-crawler">
            <div className="temu-header">
                <h2>🏪 TEMU卖家店铺爬取</h2>
                <p className="subtitle">爬取指定卖家店铺的所有商品，包含卖家信息</p>
            </div>

            <div className="form-container">
                <div className="form-group">
                    <label>卖家店铺URL（支持批量，一行一个）</label>
                    <textarea
                        value={sellerUrls}
                        onChange={(e) => setSellerUrls(e.target.value)}
                        placeholder="https://www.temu.com/mall.html?mall_id=634418218462973&...&#10;https://www.temu.com/mall.html?mall_id=123456789&...&#10;（可输入多个链接，每行一个）"
                        className="input-url textarea-url"
                        rows={5}
                    />
                    <span className="hint">粘贴完整的TEMU卖家店铺链接，支持批量输入（每行一个）</span>
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

                {progressLogs.length > 0 && (
                    <div className="progress-logs">
                        <h4>📊 爬取进度</h4>
                        <div className="log-content">
                            {progressLogs.map((log, index) => (
                                <div key={index} className="log-item">
                                    {log}
                                </div>
                            ))}
                        </div>
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
