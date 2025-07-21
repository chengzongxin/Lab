// 内容脚本 - 在网页中执行自动勾选逻辑
// 防止重复声明
if (typeof window.autoCheckManager === 'undefined') {
    class AutoCheckManager {
        constructor() {
            this.isRunning = false;
            this.categories = [];
            this.observer = null;
            this.checkInterval = null;
            this.processedRows = new Set();
            this.checkedCount = 0; // 已勾选的商品数量
            this.maxCheckedItems = 200; // 最大勾选数量限制
            this.lastCheckTime = 0; // 上次检查时间
            this.checkThrottle = 1000; // 检查间隔（毫秒）
            this.scrollInterval = null; // 滚动定时器
            this.scrollTimeoutId = null; // 滚动后的延迟检查定时器
            this.lastScrollTime = 0; // 上次滚动时间
            this.scrollThrottle = 2000; // 滚动间隔（毫秒）
            this.noMatchCount = 0; // 连续无匹配次数
            this.maxNoMatchCount = 3; // 最大连续无匹配次数，超过后开始滚动
            this.pageType = '未知页面'; // 添加页面类型属性
            this.init();
        }

    // 初始化
    init() {
        this.bindMessageListener();
        console.log('🎯 活动申报助手已加载');
    }

    // 绑定消息监听器
    bindMessageListener() {
        chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
            // console.log('🎯 收到消息:', message);
            
            try {
                switch (message.action) {
                    case 'startAutoCheck':
                        this.startAutoCheck(message.categories, message.pageType, message.maxCheckedItems);
                        sendResponse({ success: true, message: '自动勾选已开始' });
                        break;
                    case 'stopAutoCheck':
                        this.stopAutoCheck();
                        sendResponse({ success: true, message: '自动勾选已停止' });
                        break;

                    case 'updateMaxCheckedItems':
                        this.maxCheckedItems = message.maxCheckedItems || 200;
                        console.log('🔧 更新最大勾选数量为:', this.maxCheckedItems);
                        sendResponse({ success: true, message: '最大勾选数量已更新' });
                        break;
                    case 'getStatus':
                        const status = this.getStatus();
                        sendResponse({ success: true, data: status });
                        break;
                    case 'ping':
                        // 用于测试连接
                        sendResponse({ success: true, message: '内容脚本已连接' });
                        break;
                    default:
                        console.warn('未知消息类型:', message.action);
                        sendResponse({ success: false, message: '未知消息类型' });
                }
            } catch (error) {
                console.error('处理消息时出错:', error);
                sendResponse({ success: false, message: '处理消息时出错: ' + error.message });
            }
            
            // 返回true表示异步响应
            return true;
        });
    }

    // 开始自动勾选
    startAutoCheck(categories, pageType = '未知页面', maxCheckedItems = 200) {
        console.log('🚀 开始自动勾选，配置:', categories, '页面类型:', pageType, '最大勾选数量:', maxCheckedItems);
        this.categories = categories;
        this.pageType = pageType; // 保存页面类型
        this.maxCheckedItems = maxCheckedItems; // 设置最大勾选数量
        this.isRunning = true;
        this.processedRows.clear();
        this.checkedCount = 0;
        this.lastCheckTime = 0;
        this.lastScrollTime = 0;
        this.noMatchCount = 0;
        
        // 立即执行一次检查
        this.checkCurrentRows();
        
        // 设置定时检查（降低频率以减少卡顿）
        this.checkInterval = setInterval(async () => {
            if (this.isRunning) {
                await this.checkCurrentRows();
            }
        }, 3000); // 每3秒检查一次，减少频率
        
        // 设置定时滚动检查
        // this.scrollInterval = setInterval(() => {
        //     if (this.isRunning) {
        //         this.checkAndScroll();
        //     }
        // }, 5000); // 每5秒检查一次是否需要滚动
        
        // 监听DOM变化
        this.startObserving();
        
        // 初始化批量权益功能（仅限时秒杀页面）
        this.initBatchRightsFeature();
        
        this.showNotification(`自动勾选已开始 (${pageType})`, 'success');
    }

    // 停止自动勾选
    stopAutoCheck() {
        console.log('⏹️ 停止自动勾选');
        
        // 立即设置停止标志
        this.isRunning = false;
        
        // 清除所有定时器
        if (this.checkInterval) {
            clearInterval(this.checkInterval);
            this.checkInterval = null;
            console.log('✅ 已清除检查定时器');
        }
        
        if (this.scrollInterval) {
            clearInterval(this.scrollInterval);
            this.scrollInterval = null;
            console.log('✅ 已清除滚动定时器');
        }
        
        if (this.scrollTimeoutId) {
            clearTimeout(this.scrollTimeoutId);
            this.scrollTimeoutId = null;
            console.log('✅ 已清除滚动延迟检查定时器');
        }
        
        // 停止DOM监听
        if (this.observer) {
            this.observer.disconnect();
            this.observer = null;
            console.log('✅ 已停止DOM监听');
        }
        
        // 重置状态
        this.processedRows.clear();
        this.lastCheckTime = 0;
        this.lastScrollTime = 0;
        this.noMatchCount = 0;
        
        console.log('✅ 状态已重置');
        
        this.showNotification('自动勾选已停止', 'info');
        
        // 通知popup更新状态
        try {
            chrome.runtime.sendMessage({
                action: 'updateStatus',
                data: { isRunning: false, checkedCount: this.checkedCount }
            });
            console.log('✅ 已通知popup更新状态');
        } catch (error) {
            console.log('⚠️ 无法发送状态更新消息:', error);
        }
        
        console.log('🎯 停止操作完成');
    }

    // 获取当前状态
    getStatus() {
        return {
            isRunning: this.isRunning,
            checkedCount: this.checkedCount,
            maxCheckedItems: this.maxCheckedItems,
            categories: this.categories,
            processedRows: this.processedRows.size
        };
    }

    // 开始监听DOM变化（优化性能）
    startObserving() {
        const targetNode = document.body;
        const config = { 
            childList: true, 
            subtree: true,
            attributes: false,
            characterData: false
        };

        this.observer = new MutationObserver((mutations) => {
            if (!this.isRunning) return;
            
            // 节流处理，避免频繁触发
            const now = Date.now();
            if (now - this.lastCheckTime < this.checkThrottle) {
                return;
            }
            
            let hasNewRows = false;
            mutations.forEach((mutation) => {
                if (mutation.type === 'childList') {
                    mutation.addedNodes.forEach((node) => {
                        if (node.nodeType === Node.ELEMENT_NODE) {
                            // 检查是否添加了新的表格行
                            if (node.classList && node.classList.contains('TB_tr_5-118-0')) {
                                hasNewRows = true;
                            } else if (node.querySelector && node.querySelector('.TB_tr_5-118-0')) {
                                hasNewRows = true;
                            }
                        }
                    });
                }
            });
            
            if (hasNewRows) {
                this.lastCheckTime = now;
                // 延迟一点时间让DOM完全渲染
                setTimeout(async () => {
                    if (this.isRunning) {
                        await this.checkCurrentRows();
                    }
                }, 1000); // 增加延迟时间
            }
        });

        this.observer.observe(targetNode, config);
    }

    // 检查当前页面上的所有行
    async checkCurrentRows() {
        if (!this.isRunning) return;
        
        // 检查是否达到最大勾选数量
        if (this.checkedCount >= this.maxCheckedItems) {
            console.log(`⚠️ 已达到最大勾选数量限制 (${this.maxCheckedItems})，停止自动勾选`);
            this.showNotification(`已达到最大勾选数量限制 (${this.maxCheckedItems})，自动勾选已停止`, 'warning');
            this.stopAutoCheck();
            return;
        }

        const rows = this.getTableRows();
        let checkedCount = 0;
        let totalCount = 0;

        for (const row of rows) {
            // 每次循环都检查是否还在运行
            if (!this.isRunning) {
                console.log('🛑 检测到停止信号，中断检查');
                return;
            }
            
            if (this.processedRows.has(row)) continue;
            
            totalCount++;
            const shouldCheck = await this.shouldCheckRow(row);
            
            if (shouldCheck && this.checkedCount < this.maxCheckedItems) {
                const checkSuccess = this.checkRow(row);
                if (checkSuccess) {
                    checkedCount++;
                    this.checkedCount++;
                    
                    // 检查是否达到限制
                    if (this.checkedCount >= this.maxCheckedItems) {
                        console.log(`⚠️ 已达到最大勾选数量限制 (${this.maxCheckedItems})`);
                        this.showNotification(`已达到最大勾选数量限制 (${this.maxCheckedItems})，自动勾选已停止`, 'warning');
                        this.stopAutoCheck();
                        return;
                    }
                } else {
                    console.log('❌ 勾选失败，不计入计数');
                }
            }
            
            this.processedRows.add(row);
        }

        if (totalCount > 0) {
            console.log(`📊 检查了 ${totalCount} 行，勾选了 ${checkedCount} 行，总计 ${this.checkedCount}/${this.maxCheckedItems}`);
            this.showNotification(`已勾选 ${this.checkedCount}/${this.maxCheckedItems} 个商品`, 'info');
            
            // 更新无匹配计数
            if (checkedCount === 0) {
                this.noMatchCount++;
                console.log(`⚠️ 本次检查无匹配商品，连续无匹配次数: ${this.noMatchCount}`);
            } else {
                this.noMatchCount = 0; // 重置计数
            }

            // 检查是否还在运行，如果是则开始滚动
            if (this.isRunning) {
                console.log('🔄 开始滚动加载更多内容');
                this.scrollToBottom();
            } else {
                console.log('🛑 检测到停止信号，取消滚动操作');
            }
            
            // 通知popup更新状态
            try {
                chrome.runtime.sendMessage({
                    action: 'updateStatus',
                    data: { 
                        isRunning: this.isRunning, 
                        checkedCount: this.checkedCount,
                        maxCheckedItems: this.maxCheckedItems
                    }
                });
            } catch (error) {
                console.log('无法发送状态更新消息');
            }
        }
    }

    // 获取表格行
    getTableRows() {
        // 根据页面结构获取表格行
        const rows = document.querySelectorAll('tr[data-testid="beast-core-table-body-tr"]');
        return Array.from(rows);
    }

    // 检查是否需要滚动并执行滚动
    checkAndScroll() {
        if (!this.isRunning) return;
        
        // 检查是否达到最大勾选数量
        if (this.checkedCount >= this.maxCheckedItems) {
            console.log('✅ 已达到最大勾选数量，停止滚动');
            return;
        }
        
        // 节流处理，避免频繁滚动
        const now = Date.now();
        if (now - this.lastScrollTime < this.scrollThrottle) {
            return;
        }
        
        // 如果连续多次检查都没有匹配的商品，开始滚动
        if (this.noMatchCount >= this.maxNoMatchCount) {
            console.log(`🔄 连续 ${this.noMatchCount} 次无匹配商品，开始滚动加载更多内容`);
            this.scrollToBottom();
            this.lastScrollTime = now;
            this.noMatchCount = 0; // 重置计数
        }
    }

    // 滚动到页面底部
    scrollToBottom() {
        try {
            // 首先检查是否还在运行
            if (!this.isRunning) {
                console.log('🛑 检测到停止信号，取消滚动操作');
                return;
            }
            
            console.log('📜 滚动到页面底部...');
            
            // 方法1：查找表格容器并滚动
            const tableContainer = this.findTableContainer();
            if (tableContainer) {
                console.log('找到表格容器，执行滚动:', tableContainer);
                tableContainer.scrollTo({
                    top: tableContainer.scrollHeight,
                    behavior: 'smooth'
                });
            }
            
            // 方法2：查找所有可能的滚动容器
            const scrollContainers = document.querySelectorAll('[style*="overflow"], [class*="scroll"], [class*="table"], .ant-table-body, .el-table__body-wrapper');
            console.log('找到滚动容器数量:', scrollContainers.length);
            
            scrollContainers.forEach((container, index) => {
                if (container.scrollHeight > container.clientHeight) {
                    // console.log(`滚动容器 ${index}:`, container);
                    container.scrollTo({
                        top: container.scrollHeight,
                        behavior: 'smooth'
                    });
                }
            });
            
            // 方法3：直接滚动页面
            const currentScrollTop = window.pageYOffset || document.documentElement.scrollTop;
            const maxScrollTop = document.body.scrollHeight - window.innerHeight;
            
            console.log('页面滚动信息:', {
                currentScrollTop,
                maxScrollTop,
                documentHeight: document.body.scrollHeight,
                windowHeight: window.innerHeight
            });
            
            if (maxScrollTop > currentScrollTop) {
                window.scrollTo({
                    top: maxScrollTop,
                    behavior: 'smooth'
                });
            }
            
            // 方法4：模拟键盘End键（更完整的事件）
            const endEvent = new KeyboardEvent('keydown', {
                key: 'End',
                code: 'End',
                keyCode: 35,
                which: 35,
                bubbles: true,
                cancelable: true,
                composed: true
            });
            
            // 在多个元素上触发事件
            [document, document.body, document.documentElement].forEach(element => {
                element.dispatchEvent(endEvent);
            });
            
            // 方法5：查找并点击"加载更多"按钮
            const loadMoreButtons = document.querySelectorAll('button, .btn, [class*="load"], [class*="more"]');
            loadMoreButtons.forEach(button => {
                const text = button.textContent.toLowerCase();
                if (text.includes('加载') || text.includes('更多') || text.includes('load') || text.includes('more')) {
                    console.log('找到加载更多按钮:', button);
                    button.click();
                }
            });
            
            this.showNotification('正在加载更多商品...', 'info');
            
            // 延迟后重新检查 - 保存定时器ID以便能够取消
            this.scrollTimeoutId = setTimeout(async () => {
                // 再次检查是否还在运行
                if (!this.isRunning) {
                    console.log('🛑 检测到停止信号，取消滚动后的检查');
                    return;
                }
                console.log('🔄 滚动后重新检查商品');
                await this.checkCurrentRows();
            }, 3000); // 增加延迟时间
            
        } catch (error) {
            console.error('滚动时出错:', error);
        }
    }

    // 查找表格容器
    findTableContainer() {
        // 查找包含表格的容器
        const table = document.querySelector('table, [data-testid*="table"]');
        if (table) {
            // 向上查找可滚动的父容器
            let container = table.parentElement;
            while (container && container !== document.body) {
                const style = window.getComputedStyle(container);
                if (style.overflow === 'auto' || style.overflow === 'scroll' || style.overflowY === 'auto' || style.overflowY === 'scroll') {
                    return container;
                }
                container = container.parentElement;
            }
        }
        
        // 查找常见的表格容器类名
        const commonContainers = [
            '.ant-table-body',
            '.el-table__body-wrapper',
            '.table-container',
            '.scroll-container',
            '[class*="table"]',
            '[class*="scroll"]'
        ];
        
        for (const selector of commonContainers) {
            const container = document.querySelector(selector);
            if (container && container.scrollHeight > container.clientHeight) {
                return container;
            }
        }
        
        return null;
    }

    // 判断是否应该勾选某一行
    async shouldCheckRow(row) {
        try {
            // 检查是否已经处理过这一行
            if (row.hasAttribute('data-auto-check-processed')) {
                console.log('🔄 该行已处理过，跳过');
                return false;
            }
            
            // 标记为正在处理
            row.setAttribute('data-auto-check-processing', 'true');
            
            // 获取商品名称 - 尝试多种方式获取纯文本
            // 支持两种页面结构：活动申报页面和官方大促页面
            let titleElement = row.querySelector('.goods-info_title__yHBeG');
            if (!titleElement) {
                // 官方大促页面的商品名称选择器
                titleElement = row.querySelector('.beast-core-ellipsis-1');
            }
            
            if (!titleElement) {
                console.log('❌ 未找到商品名称元素');
                return false;
            }
            
            // 获取纯文本内容，排除样式代码
            let productName = '';
            
            // 方法1：获取所有文本节点，排除style标签
            const walker = document.createTreeWalker(
                titleElement,
                NodeFilter.SHOW_TEXT,
                {
                    acceptNode: function(node) {
                        // 排除style标签内的文本
                        let parent = node.parentElement;
                        while (parent && parent !== titleElement) {
                            if (parent.tagName === 'STYLE') {
                                return NodeFilter.FILTER_REJECT;
                            }
                            parent = parent.parentElement;
                        }
                        return NodeFilter.FILTER_ACCEPT;
                    }
                },
                false
            );
            
            const textNodes = [];
            let node;
            while (node = walker.nextNode()) {
                const text = node.textContent.trim();
                if (text && !text.includes('{') && !text.includes('}')) {
                    textNodes.push(text);
                }
            }
            
            if (textNodes.length > 0) {
                productName = textNodes.join(' ').trim();
            } else {
                // 方法2：直接获取textContent并清理
                productName = titleElement.textContent.trim();
                // 移除CSS样式代码和style标签内容
                productName = productName.replace(/\{[^}]*\}/g, '').trim();
                // 移除可能的style标签内容
                productName = productName.replace(/<style[^>]*>[\s\S]*?<\/style>/gi, '').trim();
            }
            
            if (!productName) {
                console.log('❌ 商品名称为空');
                return false;
            }

            // 获取申报价格 - 根据页面类型选择不同的列
            let priceElement = null;
            
            if (this.pageType === '限时秒杀') {
                // 限时秒杀页面：检查是否已经选择基础权益
                const basicRightsLabel = row.querySelector('label[data-testid="beast-core-radio"] .RD_textWrapper_5-118-0 span');
                let needToSelectBasicRights = true;
                
                if (basicRightsLabel) {
                    const allRadioLabels = row.querySelectorAll('label[data-testid="beast-core-radio"]');
                    for (const label of allRadioLabels) {
                        const textElement = label.querySelector('.RD_textWrapper_5-118-0 span');
                        if (textElement && textElement.textContent.includes('基础权益')) {
                            if (label.getAttribute('data-checked') === 'true') {
                                needToSelectBasicRights = false;
                                break;
                            }
                        }
                    }
                }
                
                if (needToSelectBasicRights) {
                    console.log('🔧 需要选择基础权益');
                    const shouldSelectBasicRights = await this.selectBasicRightsIfNeeded(row);
                    if (!shouldSelectBasicRights) {
                        console.log('❌ 无法选择基础权益，跳过该商品');
                        return false;
                    }
                    
                    // 等待价格刷新
                    await this.waitForPriceRefresh(row);
                } else {
                    console.log('✅ 基础权益已选择，直接获取价格');
                }
                
                // 获取基础权益的价格（第7个td）
                priceElement = row.querySelector('td:nth-child(7) span span:last-child');
                if (!priceElement) {
                    priceElement = row.querySelector('td:nth-child(7) span:last-child');
                }
                if (!priceElement) {
                    priceElement = row.querySelector('td:nth-child(7)');
                }
            } else if (this.pageType === '官方大促') {
                // 官方大促页面：价格在第7个td
                priceElement = row.querySelector('td:nth-child(7) span span:last-child');
                if (!priceElement) {
                    priceElement = row.querySelector('td:nth-child(7) span:last-child');
                }
                if (!priceElement) {
                    priceElement = row.querySelector('td:nth-child(7)');
                }
            } else if (
                this.pageType === '新品专区' ||
                this.pageType === '大流量扶持' ||
                this.pageType === '爆款冲刺' ||
                this.pageType === '营销热点'
            ) {
                // 新活动页面：价格在第6个td
                priceElement = row.querySelector('td:nth-child(6) span span:last-child');
                if (!priceElement) {
                    priceElement = row.querySelector('td:nth-child(6) span:last-child');
                }
                if (!priceElement) {
                    priceElement = row.querySelector('td:nth-child(6)');
                }
            } else {
                // 省心报页面：价格在第5个td
                priceElement = row.querySelector('td:nth-child(5) span span:last-child');
                if (!priceElement) {
                    priceElement = row.querySelector('td:nth-child(5) span:last-child');
                }
                if (!priceElement) {
                    priceElement = row.querySelector('td:nth-child(5)');
                }
            }
            
            if (!priceElement) {
                console.log(`❌ 未找到价格元素，商品: "${productName}"，页面类型: ${this.pageType}`);
                // 调试：尝试查找所有td元素
                const allTds = row.querySelectorAll('td');
                console.log(`🔍 该行共有 ${allTds.length} 个td元素`);
                allTds.forEach((td, index) => {
                    console.log(`  td[${index + 1}]: ${td.textContent.trim()}`);
                });
                return false;
            }
            
            const priceText = priceElement.textContent.trim();
            console.log(`💰 找到价格元素: "${priceText}" (页面类型: ${this.pageType})`);
            
            // 提取数字
            const priceMatch = priceText.match(/[\d.]+/);
            const price = priceMatch ? parseFloat(priceMatch[0]) : 0;
            
            if (isNaN(price) || price <= 0) {
                console.log(`❌ 价格无效: "${priceText}" -> ${price}，商品: "${productName}"`);
                return false;
            }

            // 调试：打印商品信息
            console.log(`🔍 检查商品: "${productName}" (¥${price}) [${this.pageType}]`);

            // 检查是否匹配任何品类
            let matchedAny = false;
            console.log(`🔍 开始检查商品匹配: "${productName}" (¥${price}) [${this.pageType}]`);
            
            for (const category of this.categories) {
                const isMatch = this.matchesCategory(productName, category.keyword);
                const priceOK = price >= category.minPrice;
                
                console.log(`🔍 品类检查: "${category.keyword}" | 关键词匹配: ${isMatch} | 价格检查: ¥${price} >= ¥${category.minPrice} = ${priceOK}`);
                
                if (isMatch && priceOK) {
                    console.log(`✅ 匹配成功: "${productName}" (¥${price}) 匹配品类 "${category.keyword}" (最低价¥${category.minPrice})`);
                    // 标记为已处理
                    row.setAttribute('data-auto-check-processed', 'true');
                    row.removeAttribute('data-auto-check-processing');
                    return true;
                }
                
                if (isMatch) {
                    matchedAny = true;
                    console.log(`⚠️ 关键词匹配但价格不足: "${productName}" (¥${price}) 匹配 "${category.keyword}" 但价格低于最低要求 ¥${category.minPrice}`);
                }
            }
            
            if (matchedAny) {
                console.log(`💰 价格不足的商品: "${productName}" (¥${price})`);
            } else {
                console.log(`❌ 未匹配任何品类: "${productName}" (¥${price})`);
                // 调试：显示所有配置的关键词
                console.log(`🔍 当前配置的关键词: ${this.categories.map(c => `${c.keyword}(≥¥${c.minPrice})`).join(', ')}`);
            }

            // 标记为已处理
            row.setAttribute('data-auto-check-processed', 'true');
            row.removeAttribute('data-auto-check-processing');
            return false;
        } catch (error) {
            console.error('检查行时出错:', error);
            // 清理标记
            row.removeAttribute('data-auto-check-processing');
            return false;
        }
    }

    // 检查商品名称是否匹配品类关键词
    matchesCategory(productName, keyword) {
        if (!productName || !keyword) return false;
        
        // 转换为小写进行比较
        const name = productName.toLowerCase();
        const key = keyword.toLowerCase();
        
        // 支持多个关键词（用逗号分隔）
        const keywords = key.split(',').map(k => k.trim());
        
        return keywords.some(k => {
            // 直接匹配
            if (name.includes(k)) return true;
            
            // 智能匹配：处理单复数形式
            if (k.endsWith('s')) {
                // 如果关键词以s结尾，也匹配去掉s的形式
                const singular = k.slice(0, -1);
                if (name.includes(singular)) return true;
            } else {
                // 如果关键词不以s结尾，也匹配加上s的形式
                const plural = k + 's';
                if (name.includes(plural)) return true;
            }
            
            // 处理特殊情况：Drawstring Bags -> Drawstring Bag
            if (k === 'drawstring bags') {
                if (name.includes('drawstring bag')) return true;
            }
            
            return false;
        });
    }

    // 勾选某一行
    checkRow(row) {
        try {
            // 找到label元素（这是自定义checkbox的容器）
            const label = row.querySelector('label[data-testid="beast-core-checkbox"]');
            if (!label) {
                console.log('❌ 未找到checkbox label');
                return false;
            }
            
            // 检查当前状态
            const isChecked = label.getAttribute('data-checked') === 'true';
            console.log('🔍 当前checkbox状态:', isChecked);
            
            if (!isChecked) {
                console.log('🔧 开始勾选操作...');
                
                // 步骤1：修改data-checked属性
                label.setAttribute('data-checked', 'true');
                label.setAttribute('data-indeterminate', 'false');
                
                // 步骤2：添加激活状态的CSS类
                label.classList.add('CBX_active_5-118-0');
                
                // 步骤3：找到并设置input元素
                const input = label.querySelector('input[type="checkbox"]');
                if (input) {
                    input.checked = true;
                    input.indeterminate = false;
                }
                
                // 步骤4：修改square元素的样式
                const squareElement = label.querySelector('.CBX_square_5-118-0');
                if (squareElement) {
                    squareElement.classList.add('CBX_active_5-118-0');
                }
                
                // 步骤5：修改icon元素的样式
                const iconElement = label.querySelector('.CBX_iconCheck_5-118-0');
                if (iconElement) {
                    iconElement.classList.add('CBX_active_5-118-0');
                }
                
                // 步骤6：触发必要的事件
                if (input) {
                    // 触发change事件
                    const changeEvent = new Event('change', { bubbles: true });
                    input.dispatchEvent(changeEvent);
                    
                    // 触发input事件
                    const inputEvent = new Event('input', { bubbles: true });
                    input.dispatchEvent(inputEvent);
                }
                
                // 步骤7：点击label元素
                label.click();
                
                // 步骤8：添加视觉反馈
                row.style.backgroundColor = '#e8f5e8';
                setTimeout(() => {
                    row.style.backgroundColor = '';
                }, 2000);
                
                console.log('✅ 勾选操作完成，当前状态:', label.getAttribute('data-checked'));
                
                // 立即验证勾选结果
                const finalState = label.getAttribute('data-checked');
                const hasActiveClass = label.classList.contains('CBX_active_5-118-0');
                
                if (finalState === 'true' && hasActiveClass) {
                    console.log('✅ 勾选成功确认');
                    return true;
                } else {
                    console.log('⚠️ 勾选可能没有完全生效，尝试补充操作');
                    this.supplementCheckRow(row);
                    
                    // 再次验证
                    setTimeout(() => {
                        const retryState = label.getAttribute('data-checked');
                        if (retryState === 'true') {
                            console.log('✅ 补充操作后勾选成功');
                        } else {
                            console.log('❌ 勾选最终失败');
                        }
                    }, 200);
                    
                    return finalState === 'true';
                }
            } else {
                console.log('ℹ️ 该行已经勾选');
                return true; // 已经勾选，算作成功
            }
        } catch (error) {
            console.error('勾选行时出错:', error);
            return false;
        }
    }

    // 显示通知
    showNotification(message, type = 'info') {
        // 创建通知元素
        const notification = document.createElement('div');
        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 12px 20px;
            border-radius: 6px;
            color: white;
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            font-size: 14px;
            z-index: 10000;
            max-width: 300px;
            word-wrap: break-word;
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
            transition: opacity 0.3s ease;
        `;

        // 根据类型设置样式
        switch (type) {
            case 'success':
                notification.style.backgroundColor = '#28a745';
                break;
            case 'error':
                notification.style.backgroundColor = '#dc3545';
                break;
            case 'warning':
                notification.style.backgroundColor = '#ffc107';
                notification.style.color = '#212529';
                break;
            default:
                notification.style.backgroundColor = '#17a2b8';
        }

        notification.textContent = message;
        document.body.appendChild(notification);

        // 3秒后自动移除
        setTimeout(() => {
            notification.style.opacity = '0';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    // 补充勾选操作（当主要勾选方法不完全生效时）
    supplementCheckRow(row) {
        try {
            console.log('🔧 执行补充勾选操作...');
            
            const label = row.querySelector('label[data-testid="beast-core-checkbox"]');
            if (!label) return;
            
            // 确保所有必要的属性都设置正确
            label.setAttribute('data-checked', 'true');
            label.setAttribute('data-indeterminate', 'false');
            
            // 确保所有必要的CSS类都存在
            label.classList.add('CBX_active_5-118-0');
            
            const input = label.querySelector('input[type="checkbox"]');
            const square = label.querySelector('.CBX_square_5-118-0');
            const icon = label.querySelector('.CBX_iconCheck_5-118-0');
            
            if (input) {
                input.checked = true;
                input.indeterminate = false;
            }
            
            if (square) {
                square.classList.add('CBX_active_5-118-0');
            }
            
            if (icon) {
                icon.classList.add('CBX_active_5-118-0');
            }
            
            // 再次触发事件
            if (input) {
                ['change', 'input', 'click'].forEach(eventType => {
                    const event = new Event(eventType, { bubbles: true, cancelable: true });
                    input.dispatchEvent(event);
                });
            }
            
            // 再次点击label
            label.click();
            
            console.log('🔧 补充勾选操作完成');
        } catch (error) {
            console.error('补充勾选出错:', error);
        }
    }

    // 强制勾选某一行（备用方法）
    forceCheckRow(row) {
        try {
            console.log('🔧 尝试强制勾选...');
            
            const label = row.querySelector('label[data-testid="beast-core-checkbox"]');
            if (!label) return;
            
            // 方法1：直接修改DOM属性
            label.setAttribute('data-checked', 'true');
            label.setAttribute('data-indeterminate', 'false');
            
            // 方法2：修改input属性
            const input = label.querySelector('input[type="checkbox"]');
            if (input) {
                input.checked = true;
                input.indeterminate = false;
                input.setAttribute('checked', 'checked');
            }
            
            // 方法3：修改视觉样式
            const square = label.querySelector('.CBX_square_5-118-0');
            if (square) {
                square.classList.add('CBX_active_5-118-0');
                square.style.backgroundColor = '#1890ff';
                square.style.borderColor = '#1890ff';
            }
            
            // 方法4：显示勾选图标
            const icon = label.querySelector('.CBX_iconCheck_5-118-0');
            if (icon) {
                icon.classList.add('CBX_active_5-118-0');
                icon.style.display = 'block';
                icon.style.opacity = '1';
            }
            
            // 方法5：使用Object.defineProperty强制设置属性
            if (input) {
                Object.defineProperty(input, 'checked', {
                    value: true,
                    writable: true,
                    configurable: true
                });
            }
            
            console.log('🔧 强制勾选完成');
        } catch (error) {
            console.error('强制勾选出错:', error);
        }
    }

    // 限时秒杀：选择基础权益
    async selectBasicRightsIfNeeded(row) {
        try {
            console.log('🔧 限时秒杀：检查并选择基础权益...');
            
            // 查找所有的radio选项
            const allRadioLabels = row.querySelectorAll('label[data-testid="beast-core-radio"]');
            console.log(`🔍 找到 ${allRadioLabels.length} 个权益选项`);
            
            let basicRightsLabel = null;
            let advancedRightsLabel = null;
            
            // 遍历所有选项，找到基础权益和进阶权益
            allRadioLabels.forEach((label, index) => {
                const textElement = label.querySelector('.RD_textWrapper_5-118-0 span');
                if (textElement) {
                    const text = textElement.textContent.trim();
                    console.log(`  选项 ${index + 1}: "${text}", 选中状态: ${label.getAttribute('data-checked')}`);
                    
                    if (text.includes('基础权益')) {
                        basicRightsLabel = label;
                    } else if (text.includes('进阶权益')) {
                        advancedRightsLabel = label;
                    }
                }
            });
            
            if (!basicRightsLabel) {
                console.log('❌ 未找到基础权益选项');
                return false;
            }
            
            // 检查基础权益当前状态
            const isBasicChecked = basicRightsLabel.getAttribute('data-checked') === 'true';
            console.log('🔍 基础权益当前状态:', isBasicChecked);
            
            if (!isBasicChecked) {
                console.log('🔧 需要选择基础权益，执行点击...');
                
                // 模拟点击基础权益
                basicRightsLabel.click();
                
                // 等待状态更新
                await new Promise(resolve => setTimeout(resolve, 800));
                
                // 验证是否选择成功
                const newBasicChecked = basicRightsLabel.getAttribute('data-checked') === 'true';
                const newAdvancedChecked = advancedRightsLabel ? advancedRightsLabel.getAttribute('data-checked') === 'true' : false;
                
                console.log('🔍 选择后状态:', {
                    基础权益: newBasicChecked,
                    进阶权益: newAdvancedChecked
                });
                
                if (newBasicChecked) {
                    console.log('✅ 基础权益选择成功');
                    return true;
                } else {
                    console.log('❌ 基础权益选择失败');
                    return false;
                }
            } else {
                console.log('✅ 基础权益已经选中');
                return true;
            }
        } catch (error) {
            console.error('选择基础权益时出错:', error);
            return false;
        }
    }

    // 限时秒杀：等待价格刷新
    async waitForPriceRefresh(row) {
        try {
            console.log('⏳ 等待价格刷新...');
            
            // 等待最多3秒让价格刷新
            const maxWaitTime = 3000;
            const checkInterval = 200;
            let waitedTime = 0;
            
            while (waitedTime < maxWaitTime) {
                // 检查价格是否已经刷新为基础权益价格（第7个td）
                const priceElement = row.querySelector('td:nth-child(7) span span:last-child');
                if (priceElement) {
                    const priceText = priceElement.textContent.trim();
                    const priceMatch = priceText.match(/[\d.]+/);
                    const price = priceMatch ? parseFloat(priceMatch[0]) : 0;
                    
                    if (price > 0) {
                        console.log('✅ 价格已刷新:', priceText);
                        return true;
                    }
                }
                
                await new Promise(resolve => setTimeout(resolve, checkInterval));
                waitedTime += checkInterval;
            }
            
            console.log('⚠️ 价格刷新超时');
            return false;
        } catch (error) {
            console.error('等待价格刷新时出错:', error);
            return false;
        }
    }

    // 分析价格分布（用于调试）
    analyzePriceDistribution() {
        const rows = this.getTableRows();
        const stats = {
            total: 0,
            min: Infinity,
            max: -Infinity,
            sum: 0,
            prices: []
        };
        
        const categoryStats = {};
        
        rows.forEach(row => {
            try {
                // 获取商品名称
                let titleElement = row.querySelector('.goods-info_title__yHBeG');
                if (!titleElement) {
                    titleElement = row.querySelector('.beast-core-ellipsis-1');
                }
                
                if (!titleElement) return;
                
                const productName = titleElement.textContent.trim().replace(/\{[^}]*\}/g, '').trim();
                
                // 获取价格
                let priceElement = null;
                if (this.pageType === '限时秒杀') {
                    priceElement = row.querySelector('td:nth-child(7) span span:last-child');
                } else if (this.pageType === '官方大促') {
                    priceElement = row.querySelector('td:nth-child(7) span span:last-child');
                } else {
                priceElement = row.querySelector('td:nth-child(5) span span:last-child');
                }
                
                if (!priceElement) return;
                
                const priceText = priceElement.textContent.trim();
                const priceMatch = priceText.match(/[\d.]+/);
                const price = priceMatch ? parseFloat(priceMatch[0]) : 0;
                
                if (isNaN(price) || price <= 0) return;
                
                // 更新总体统计
                stats.total++;
                stats.min = Math.min(stats.min, price);
                stats.max = Math.max(stats.max, price);
                stats.sum += price;
                stats.prices.push(price);
                
                // 按品类统计
                for (const category of this.categories) {
                    if (this.matchesCategory(productName, category.keyword)) {
                        if (!categoryStats[category.keyword]) {
                            categoryStats[category.keyword] = {
                                count: 0,
                                min: Infinity,
                                max: -Infinity,
                                sum: 0,
                                prices: []
                            };
                        }
                        
                        const catStats = categoryStats[category.keyword];
                        catStats.count++;
                        catStats.min = Math.min(catStats.min, price);
                        catStats.max = Math.max(catStats.max, price);
                        catStats.sum += price;
                        catStats.prices.push(price);
                    }
                }
            } catch (error) {
                console.error('分析价格时出错:', error);
            }
        });
        
        // 计算平均值
        if (stats.total > 0) {
            stats.avg = stats.sum / stats.total;
        }
        
        // 计算各品类平均值
        for (const keyword in categoryStats) {
            const catStats = categoryStats[keyword];
            if (catStats.count > 0) {
                catStats.avg = catStats.sum / catStats.count;
            }
        }
        
        return { stats, categoryStats };
    }

    // 获取页面统计信息
    getPageStats() {
        const rows = this.getTableRows();
        const checkedRows = rows.filter(row => {
            const label = row.querySelector('label[data-testid="beast-core-checkbox"]');
            return label && label.getAttribute('data-checked') === 'true';
        });

        return {
            total: rows.length,
            checked: checkedRows.length,
            processed: this.processedRows.size,
            autoChecked: this.checkedCount,
            maxChecked: this.maxCheckedItems
        };
    }

    // 批量选择基础权益功能
    async batchSelectBasicRights() {
        try {
            console.log('🔧 开始批量选择基础权益...');
            
            // 步骤1：找到并点击"批量选择"按钮
            console.log('🔍 查找批量选择按钮...');
            
            // 尝试多种方法找到批量选择按钮
            const allLinks = document.querySelectorAll('th a[data-testid="beast-core-button-link"]');
            let foundBatchBtn = null;
            
            console.log(`🔍 找到 ${allLinks.length} 个表头链接`);
            
            for (const link of allLinks) {
                console.log(`  检查链接: "${link.textContent}"`);
                if (link.textContent.includes('批量选择')) {
                    foundBatchBtn = link;
                    console.log('✅ 找到批量选择按钮');
                    break;
                }
            }
            
            if (!foundBatchBtn) {
                console.log('❌ 未找到批量选择按钮');
                this.showNotification('未找到批量选择按钮', 'error');
                return false;
            }
            
            console.log('🔧 点击批量选择按钮...');
            foundBatchBtn.click();
            
            // 步骤2：等待弹窗出现
            console.log('⏳ 等待弹窗出现...');
            await this.waitForElement('.PP_popoverContent_5-118-0', 3000);
            
            // 步骤3：在弹窗中选择基础权益
            console.log('🔧 在弹窗中查找基础权益选项...');
            const popover = document.querySelector('.PP_popoverContent_5-118-0');
            if (!popover) {
                console.log('❌ 未找到弹窗');
                this.showNotification('未找到权益选择弹窗', 'error');
                return false;
            }
            
            // 查找基础权益选项
            const radioLabels = popover.querySelectorAll('label[data-testid="beast-core-radio"]');
            let basicRightsLabel = null;
            
            for (const label of radioLabels) {
                const textElement = label.querySelector('.RD_textWrapper_5-118-0 span');
                if (textElement && textElement.textContent.includes('基础权益')) {
                    basicRightsLabel = label;
                    break;
                }
            }
            
            if (!basicRightsLabel) {
                console.log('❌ 未找到基础权益选项');
                this.showNotification('未找到基础权益选项', 'error');
                return false;
            }
            
            // 检查是否已经选中基础权益
            const isBasicChecked = basicRightsLabel.getAttribute('data-checked') === 'true';
            if (!isBasicChecked) {
                console.log('🔧 选择基础权益...');
                basicRightsLabel.click();
                await new Promise(resolve => setTimeout(resolve, 500));
            } else {
                console.log('✅ 基础权益已选中');
            }
            
            // 步骤4：点击确认按钮
            console.log('🔧 查找确认按钮...');
            
            // 在弹窗中查找确认按钮
            const footerButtons = popover.querySelectorAll('.body-module__footer___24uWB button[data-testid="beast-core-button"]');
            let confirmBtn = null;
            
            console.log(`🔍 弹窗底部找到 ${footerButtons.length} 个按钮`);
            
            for (const btn of footerButtons) {
                console.log(`  检查按钮: "${btn.textContent}"`);
                if (btn.textContent.includes('确认')) {
                    confirmBtn = btn;
                    console.log('✅ 找到确认按钮');
                    break;
                }
            }
            
            if (!confirmBtn) {
                console.log('❌ 未找到确认按钮');
                this.showNotification('未找到确认按钮', 'error');
                return false;
            }
            
            console.log('🔧 点击确认按钮...');
            confirmBtn.click();
            
            // 步骤5：等待弹窗关闭
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            console.log('✅ 批量选择基础权益完成');
            
            // 步骤6：自动点击"一键填入参考价"
            const fillPriceSuccess = await this.clickFillReferencePrice();
            
            if (fillPriceSuccess) {
                this.showNotification('批量权益选择和价格填入完成，现在可以提交了', 'success');
            } else {
                this.showNotification('批量选择基础权益完成，但一键填入参考价失败', 'warning');
            }
            
            // 激活提交按钮
            this.enableSubmitButton();
            
            return true;
            
        } catch (error) {
            console.error('批量选择基础权益失败:', error);
            this.showNotification('批量选择基础权益失败: ' + error.message, 'error');
            return false;
        }
    }

    // 等待元素出现
    async waitForElement(selector, timeout = 5000) {
        const startTime = Date.now();
        
        while (Date.now() - startTime < timeout) {
            const element = document.querySelector(selector);
            if (element) {
                return element;
            }
            await new Promise(resolve => setTimeout(resolve, 100));
        }
        
        throw new Error(`元素 ${selector} 在 ${timeout}ms 内未出现`);
    }

    // 点击一键填入参考价
    async clickFillReferencePrice() {
        try {
            console.log('🔧 开始查找一键填入参考价按钮...');
            
            // 查找表头中的"一键填入参考价"按钮
            const allThLinks = document.querySelectorAll('th a[data-testid="beast-core-button-link"]');
            let fillPriceBtn = null;
            
            console.log(`🔍 找到 ${allThLinks.length} 个表头链接`);
            
            for (const link of allThLinks) {
                const linkText = link.textContent.trim();
                console.log(`  检查表头链接: "${linkText}"`);
                
                if (linkText.includes('一键填入参考价')) {
                    fillPriceBtn = link;
                    console.log('✅ 找到一键填入参考价按钮');
                    break;
                }
            }
            
            if (!fillPriceBtn) {
                // 如果在th中没找到，尝试在整个页面查找
                console.log('🔍 在表头中未找到，尝试在整个页面查找...');
                
                const allLinks = document.querySelectorAll('a[data-testid="beast-core-button-link"]');
                console.log(`🔍 页面中找到 ${allLinks.length} 个链接`);
                
                for (const link of allLinks) {
                    const linkText = link.textContent.trim();
                    if (linkText.includes('一键填入参考价')) {
                        fillPriceBtn = link;
                        console.log('✅ 在页面中找到一键填入参考价按钮');
                        break;
                    }
                }
            }
            
            if (!fillPriceBtn) {
                console.log('❌ 未找到一键填入参考价按钮');
                return false;
            }
            
            console.log('🔧 点击一键填入参考价按钮...');
            fillPriceBtn.click();
            
            // 等待一下让操作完成
            await new Promise(resolve => setTimeout(resolve, 1500));
            
            console.log('✅ 一键填入参考价完成');
            return true;
            
        } catch (error) {
            console.error('点击一键填入参考价失败:', error);
            return false;
        }
    }

    // 激活提交按钮
    enableSubmitButton() {
        console.log('🔧 正在激活提交按钮...');
        
        // 尝试多种选择器找到提交按钮
        const selectors = [
            '.table-goods_footer__RXisB button[data-testid="beast-core-button"]',
            'button[data-testid="beast-core-button"]:not(#batch-rights-btn)',
            '.table-goods_footer__RXisB button:last-child'
        ];
        
        let submitBtn = null;
        for (const selector of selectors) {
            const btns = document.querySelectorAll(selector);
            for (const btn of btns) {
                if (btn && btn.textContent.includes('提交') && btn.id !== 'batch-rights-btn') {
                    submitBtn = btn;
                    console.log(`✅ 找到提交按钮: ${selector}`);
                    break;
                }
            }
            if (submitBtn) break;
        }
        
        if (!submitBtn) {
            // 如果还是找不到，尝试查找所有按钮
            const allButtons = document.querySelectorAll('button[data-testid="beast-core-button"]');
            console.log(`🔍 找到 ${allButtons.length} 个按钮`);
            
            allButtons.forEach((btn, index) => {
                console.log(`  按钮 ${index + 1}: "${btn.textContent}" - disabled: ${btn.disabled}`);
                if (btn.textContent.includes('提交') && btn.id !== 'batch-rights-btn') {
                    submitBtn = btn;
                    console.log(`✅ 通过内容匹配找到提交按钮`);
                }
            });
        }
        
        if (submitBtn) {
            console.log('🔧 激活提交按钮...');
            console.log('激活前状态:', {
                disabled: submitBtn.disabled,
                opacity: submitBtn.style.opacity,
                cursor: submitBtn.style.cursor
            });
            
            // 移除所有可能的禁用属性
            submitBtn.disabled = false;
            submitBtn.removeAttribute('disabled');
            
            // 恢复样式
            submitBtn.style.opacity = '1';
            submitBtn.style.cursor = 'pointer';
            submitBtn.style.pointerEvents = 'auto';
            
            // 移除禁用的CSS类（如果有的话）
            submitBtn.classList.remove('disabled', 'BTN_disabled_5-118-0');
            
            // 添加激活提示样式
            submitBtn.style.boxShadow = '0 0 0 2px #52c41a';
            submitBtn.style.borderColor = '#52c41a';
            
            console.log('激活后状态:', {
                disabled: submitBtn.disabled,
                opacity: submitBtn.style.opacity,
                cursor: submitBtn.style.cursor
            });
            
            console.log('✅ 提交按钮已激活');
            
            // 添加点击事件监听（如果需要的话）
            submitBtn.addEventListener('click', (e) => {
                console.log('🔥 提交按钮被点击');
            });
            
        } else {
            console.log('❌ 未找到提交按钮');
            
            // 打印页面上所有可能的按钮用于调试
            const allBtns = document.querySelectorAll('button');
            console.log(`📋 页面上所有按钮 (${allBtns.length} 个):`);
            allBtns.forEach((btn, index) => {
                if (btn.textContent.trim()) {
                    console.log(`  ${index + 1}. "${btn.textContent.trim()}" - class: ${btn.className}`);
                }
            });
        }
    }

    // 创建批量权益按钮
    createBatchRightsButton() {
        try {
            console.log('🔧 开始创建批量权益按钮...');
            console.log('📄 当前页面类型:', this.pageType);
            
            // 检查是否已经创建过按钮
            if (document.querySelector('#batch-rights-btn')) {
                console.log('⚠️ 批量权益按钮已存在，跳过创建');
                return;
            }
            
            // 找到提交按钮容器
            const submitBtnContainer = document.querySelector('.table-goods_footer__RXisB');
            console.log('📦 提交按钮容器:', submitBtnContainer ? '找到' : '未找到');
            if (!submitBtnContainer) {
                console.log('❌ 未找到提交按钮容器，尝试其他选择器...');
                
                // 尝试其他可能的选择器
                const alternativeContainers = [
                    '.table-goods_footer__RXisB',
                    '[class*="footer"]',
                    'button[data-testid="beast-core-button"]'
                ];
                
                for (const selector of alternativeContainers) {
                    const container = document.querySelector(selector);
                    if (container) {
                        console.log(`✅ 找到替代容器: ${selector}`);
                        break;
                    }
                }
                return;
            }
            
            // 找到原始提交按钮
            const originalSubmitBtn = submitBtnContainer.querySelector('button[data-testid="beast-core-button"]');
            console.log('🔘 原始提交按钮:', originalSubmitBtn ? '找到' : '未找到');
            if (!originalSubmitBtn) {
                console.log('❌ 未找到原始提交按钮');
                console.log('容器内容:', submitBtnContainer.innerHTML.substring(0, 500));
                return;
            }
            
            // 创建批量权益按钮
            const batchBtn = document.createElement('button');
            batchBtn.id = 'batch-rights-btn';
            batchBtn.className = 'BTN_outerWrapper_5-118-0 BTN_default_5-118-0 BTN_large_5-118-0 BTN_outerWrapperBtn_5-118-0';
            batchBtn.setAttribute('data-testid', 'beast-core-button');
            batchBtn.type = 'button';
            batchBtn.style.cssText = `
                margin-top: 12px; 
                margin-right: 12px; 
                width: 176px; 
                min-width: 176px; 
                padding: 0px;
                background-color: #1890ff;
                border-color: #1890ff;
                color: white;
            `;
            
            const batchBtnSpan = document.createElement('span');
            batchBtnSpan.textContent = '基础权益+填价';
            batchBtn.appendChild(batchBtnSpan);
            
            // 添加点击事件
            batchBtn.addEventListener('click', async () => {
                batchBtn.disabled = true;
                batchBtnSpan.textContent = '处理中...';
                
                const success = await this.batchSelectBasicRights();
                
                if (success) {
                    batchBtnSpan.textContent = '已完成';
                    batchBtn.style.backgroundColor = '#52c41a';
                    batchBtn.style.borderColor = '#52c41a';
                } else {
                    batchBtn.disabled = false;
                    batchBtnSpan.textContent = '基础权益+填价';
                }
            });
            
            // 将按钮插入到原提交按钮前面
            originalSubmitBtn.parentNode.insertBefore(batchBtn, originalSubmitBtn);
            
            // 初始时禁用提交按钮（但允许手动启用）
            console.log('🔧 设置提交按钮初始状态...');
            console.log('提交按钮当前状态:', {
                disabled: originalSubmitBtn.disabled,
                opacity: originalSubmitBtn.style.opacity,
                cursor: originalSubmitBtn.style.cursor
            });
            
            // 先保存原始状态
            originalSubmitBtn.setAttribute('data-original-disabled', originalSubmitBtn.disabled);
            originalSubmitBtn.setAttribute('data-original-opacity', originalSubmitBtn.style.opacity || '1');
            originalSubmitBtn.setAttribute('data-original-cursor', originalSubmitBtn.style.cursor || 'pointer');
            
            // 设置禁用状态
            originalSubmitBtn.disabled = true;
            originalSubmitBtn.style.opacity = '0.5';
            originalSubmitBtn.style.cursor = 'not-allowed';
            originalSubmitBtn.style.pointerEvents = 'none';
            
            console.log('✅ 批量权益按钮已创建，提交按钮已禁用');
            
        } catch (error) {
            console.error('创建批量权益按钮失败:', error);
        }
    }

    // 初始化批量权益功能
    initBatchRightsFeature() {
        console.log('🔧 初始化批量权益功能...');
        console.log('📄 当前页面类型:', this.pageType);
        
        // 检查是否在正确的页面 - 临时注释，让所有页面都尝试创建
        if (this.pageType !== '限时秒杀') {
            console.log('⚠️ 非限时秒杀页面，跳过批量权益功能');
            return;
        }
        
        // 等待页面加载完成后创建按钮
        console.log('⏳ 等待2秒后创建批量权益按钮...');
        setTimeout(() => {
            this.createBatchRightsButton();
        }, 2000);
        
        // 如果2秒后没有创建成功，再尝试几次
        setTimeout(() => {
            if (!document.querySelector('#batch-rights-btn')) {
                console.log('🔄 第二次尝试创建批量权益按钮...');
                this.createBatchRightsButton();
            }
        }, 5000);
        
        setTimeout(() => {
            if (!document.querySelector('#batch-rights-btn')) {
                console.log('🔄 第三次尝试创建批量权益按钮...');
                this.createBatchRightsButton();
            }
        }, 10000);
    }
}

    // 初始化自动勾选管理器
    const autoCheckManager = new AutoCheckManager();

    // 在控制台暴露一些有用的方法（用于调试）
    window.autoCheckManager = autoCheckManager;
} 