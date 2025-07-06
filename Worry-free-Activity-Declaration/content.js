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
            console.log('🎯 收到消息:', message);
            
            try {
                switch (message.action) {
                    case 'startAutoCheck':
                        this.startAutoCheck(message.categories, message.pageType);
                        sendResponse({ success: true, message: '自动勾选已开始' });
                        break;
                    case 'stopAutoCheck':
                        this.stopAutoCheck();
                        sendResponse({ success: true, message: '自动勾选已停止' });
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
    startAutoCheck(categories, pageType = '未知页面') {
        console.log('🚀 开始自动勾选，配置:', categories, '页面类型:', pageType);
        this.categories = categories;
        this.pageType = pageType; // 保存页面类型
        this.isRunning = true;
        this.processedRows.clear();
        this.checkedCount = 0;
        this.lastCheckTime = 0;
        this.lastScrollTime = 0;
        this.noMatchCount = 0;
        
        // 立即执行一次检查
        this.checkCurrentRows();
        
        // 设置定时检查（降低频率以减少卡顿）
        this.checkInterval = setInterval(() => {
            if (this.isRunning) {
                this.checkCurrentRows();
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
        
        this.showNotification(`自动勾选已开始 (${pageType})`, 'success');
    }

    // 停止自动勾选
    stopAutoCheck() {
        console.log('⏹️ 停止自动勾选');
        this.isRunning = false;
        
        // 清除定时器
        if (this.checkInterval) {
            clearInterval(this.checkInterval);
            this.checkInterval = null;
        }
        
        // 清除滚动定时器
        if (this.scrollInterval) {
            clearInterval(this.scrollInterval);
            this.scrollInterval = null;
        }
        
        // 停止DOM监听
        if (this.observer) {
            this.observer.disconnect();
            this.observer = null;
        }
        
        // 重置状态
        this.processedRows.clear();
        this.lastCheckTime = 0;
        this.lastScrollTime = 0;
        this.noMatchCount = 0;
        
        this.showNotification('自动勾选已停止', 'info');
        
        // 通知popup更新状态
        try {
            chrome.runtime.sendMessage({
                action: 'updateStatus',
                data: { isRunning: false, checkedCount: this.checkedCount }
            });
        } catch (error) {
            console.log('无法发送状态更新消息');
        }
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
                setTimeout(() => {
                    if (this.isRunning) {
                        this.checkCurrentRows();
                    }
                }, 1000); // 增加延迟时间
            }
        });

        this.observer.observe(targetNode, config);
    }

    // 检查当前页面上的所有行
    checkCurrentRows() {
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

        rows.forEach((row, index) => {
            if (this.processedRows.has(row)) return;
            
            totalCount++;
            const shouldCheck = this.shouldCheckRow(row);
            
            if (shouldCheck && this.checkedCount < this.maxCheckedItems) {
                this.checkRow(row);
                checkedCount++;
                this.checkedCount++;
                
                // 检查是否达到限制
                if (this.checkedCount >= this.maxCheckedItems) {
                    console.log(`⚠️ 已达到最大勾选数量限制 (${this.maxCheckedItems})`);
                    this.showNotification(`已达到最大勾选数量限制 (${this.maxCheckedItems})，自动勾选已停止`, 'warning');
                    this.stopAutoCheck();
                    return;
                }
            }
            
            this.processedRows.add(row);
        });

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

            console.log('🔄 开始滚动加载更多内容');
            this.scrollToBottom();
            
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
                    console.log(`滚动容器 ${index}:`, container);
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
            
            // 延迟后重新检查
            setTimeout(() => {
                if (this.isRunning) {
                    console.log('🔄 滚动后重新检查商品');
                    this.checkCurrentRows();
                }
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
    shouldCheckRow(row) {
        try {
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

            // 获取申报价格 - 尝试多种选择器
            // 支持两种页面结构
            let priceElement = row.querySelector('td:nth-child(7) span span:last-child');
            if (!priceElement) {
                // 备用选择器
                priceElement = row.querySelector('td:nth-child(7) span:last-child');
            }
            if (!priceElement) {
                // 再备用选择器
                priceElement = row.querySelector('td:nth-child(7)');
            }
            
            if (!priceElement) {
                console.log(`❌ 未找到价格元素，商品: "${productName}"`);
                return false;
            }
            
            const priceText = priceElement.textContent.trim();
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
            for (const category of this.categories) {
                const isMatch = this.matchesCategory(productName, category.keyword);
                const priceOK = price >= category.minPrice;
                
                console.log(`  - 品类 "${category.keyword}": 匹配=${isMatch}, 价格=${priceOK} (需要≥${category.minPrice})`);
                
                if (isMatch && priceOK) {
                    console.log(`✅ 匹配成功: "${productName}" (¥${price}) 匹配品类 "${category.keyword}" (最低价¥${category.minPrice})`);
                    return true;
                }
            }

            console.log(`❌ 未匹配任何品类: "${productName}" (¥${price})`);
            return false;
        } catch (error) {
            console.error('检查行时出错:', error);
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
        
        return keywords.some(k => name.includes(k));
    }

    // 勾选某一行
    checkRow(row) {
        try {
            // 找到label元素（这是自定义checkbox的容器）
            const label = row.querySelector('label[data-testid="beast-core-checkbox"]');
            if (!label) {
                console.log('❌ 未找到checkbox label');
                return;
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
                
                // 步骤9：验证勾选结果
                setTimeout(() => {
                    const finalState = label.getAttribute('data-checked');
                    const hasActiveClass = label.classList.contains('CBX_active_5-118-0');
                    console.log('🔍 验证结果:', {
                        dataChecked: finalState,
                        hasActiveClass: hasActiveClass,
                        inputChecked: input ? input.checked : 'N/A'
                    });
                    
                    if (finalState !== 'true' || !hasActiveClass) {
                        console.log('⚠️ 勾选可能没有完全生效，尝试补充操作');
                        this.supplementCheckRow(row);
                    }
                }, 200);
            } else {
                console.log('ℹ️ 该行已经勾选');
            }
        } catch (error) {
            console.error('勾选行时出错:', error);
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
}

    // 初始化自动勾选管理器
    const autoCheckManager = new AutoCheckManager();

    // 在控制台暴露一些有用的方法（用于调试）
    window.autoCheckManager = autoCheckManager;
} 