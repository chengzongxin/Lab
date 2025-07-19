// 弹出窗口的主要逻辑
class PopupManager {
    constructor() {
        this.categories = [];
        this.isRunning = false;
        this.checkedCount = 0;
        this.maxCheckedItems = 200;
        this.statusUpdateInterval = null;
        this.init();
    }

    // 初始化弹出窗口
    init() {
        this.loadCategories();
        this.bindEvents();
        this.renderCategories();
        this.startStatusUpdates();
    }

    // 绑定事件监听器
    bindEvents() {
        document.getElementById('addCategoryBtn').addEventListener('click', () => {
            this.addCategory();
        });

        document.getElementById('startBtn').addEventListener('click', () => {
            this.startAutoCheck();
        });

        document.getElementById('stopBtn').addEventListener('click', () => {
            this.stopAutoCheck();
        });
    }

    // 开始状态更新
    startStatusUpdates() {
        // 每2秒更新一次状态
        this.statusUpdateInterval = setInterval(() => {
            this.updateStatus();
        }, 2000);
        
        // 立即更新一次
        this.updateStatus();
    }

    // 停止状态更新
    stopStatusUpdates() {
        if (this.statusUpdateInterval) {
            clearInterval(this.statusUpdateInterval);
            this.statusUpdateInterval = null;
        }
    }

    // 更新状态显示
    async updateStatus() {
        try {
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            const response = await chrome.tabs.sendMessage(tab.id, { action: 'getStatus' });
            
            if (response && response.success) {
                const status = response.data;
                this.isRunning = status.isRunning;
                this.checkedCount = status.checkedCount || 0;
                this.maxCheckedItems = status.maxCheckedItems || 200;
                
                this.updateButtonStates();
                this.updateStatusDisplay(status);
            }
        } catch (error) {
            // 如果无法获取状态，假设已停止
            this.isRunning = false;
            this.updateButtonStates();
            this.showStatus('无法获取插件状态', 'warning');
        }
    }

    // 更新状态显示
    updateStatusDisplay(status) {
        const statusEl = document.getElementById('status');
        const progressContainer = document.getElementById('progressContainer');
        const progressFill = document.getElementById('progress');
        const progressText = document.getElementById('progressText');
        
        if (status.isRunning) {
            const progress = Math.round((status.checkedCount / status.maxCheckedItems) * 100);
            statusEl.textContent = `正在运行中... 已勾选 ${status.checkedCount}/${status.maxCheckedItems}`;
            statusEl.className = 'status success';
            
            // 显示进度条
            if (progressContainer && progressFill && progressText) {
                progressContainer.style.display = 'block';
                progressFill.style.width = `${progress}%`;
                progressText.textContent = `${progress}%`;
            }
        } else {
            statusEl.textContent = `已停止 - 共勾选 ${status.checkedCount} 个商品`;
            statusEl.className = 'status info';
            
            // 隐藏进度条
            if (progressContainer) {
                progressContainer.style.display = 'none';
            }
        }
    }

    // 从存储中加载品类配置
    async loadCategories() {
        try {
            const result = await chrome.storage.sync.get(['categories']);
            this.categories = result.categories || [];
            if (this.categories.length === 0) {
                // 添加默认配置
                this.categories = [
                    { keyword: 'Sock', minPrice: 12 },
                    { keyword: 'Apron', minPrice: 11 },
                    { keyword: 'Tote Bag', minPrice: 12 },
                    { keyword: 'Drawstring Bags', minPrice: 14 },
                    { keyword: 'Hair', minPrice: 10 },
                    { keyword: 'Sleeve', minPrice: 13 },
                    { keyword: 'Scarf', minPrice: 10 }
                ];
            }
        } catch (error) {
            console.error('加载配置失败:', error);
            this.showStatus('加载配置失败', 'error');
        }
    }

    // 保存品类配置到存储
    async saveCategories() {
        try {
            await chrome.storage.sync.set({ categories: this.categories });
        } catch (error) {
            console.error('保存配置失败:', error);
            this.showStatus('保存配置失败', 'error');
        }
    }

    // 渲染品类列表
    renderCategories() {
        const container = document.getElementById('categoryList');
        container.innerHTML = '';

        this.categories.forEach((category, index) => {
            const item = this.createCategoryItem(category, index);
            container.appendChild(item);
        });
    }

    // 创建单个品类配置项
    createCategoryItem(category, index) {
        const item = document.createElement('div');
        item.className = 'category-item';
        item.innerHTML = `
            <div style="flex: 1;">
                <div class="label">品类关键词</div>
                <input type="text" class="category-input" 
                       value="${category.keyword}" 
                       placeholder="例如：袜子、围裙"
                       data-index="${index}" 
                       data-field="keyword">
            </div>
            <div style="margin-left: 8px;">
                <div class="label">最低价格</div>
                <input type="number" class="price-input" 
                       value="${category.minPrice}" 
                       placeholder="0.00"
                       step="0.01"
                       data-index="${index}" 
                       data-field="minPrice">
            </div>
            <button class="remove-btn" data-index="${index}">删除</button>
        `;

        // 绑定输入事件
        const inputs = item.querySelectorAll('input');
        inputs.forEach(input => {
            input.addEventListener('input', (e) => {
                this.updateCategory(index, e.target.dataset.field, e.target.value);
            });
        });

        // 绑定删除事件
        const removeBtn = item.querySelector('.remove-btn');
        removeBtn.addEventListener('click', () => {
            this.removeCategory(index);
        });

        return item;
    }

    // 添加新品类
    addCategory() {
        this.categories.push({ keyword: '', minPrice: 0 });
        this.renderCategories();
        this.saveCategories();
        this.showStatus('已添加新品类配置', 'success');
    }

    // 删除品类
    removeCategory(index) {
        this.categories.splice(index, 1);
        this.renderCategories();
        this.saveCategories();
        this.showStatus('已删除品类配置', 'success');
    }

    // 更新品类配置
    updateCategory(index, field, value) {
        if (this.categories[index]) {
            this.categories[index][field] = field === 'minPrice' ? parseFloat(value) || 0 : value;
            this.saveCategories();
        }
    }

    // 开始自动勾选
    async startAutoCheck() {
        if (this.categories.length === 0) {
            this.showStatus('请先配置至少一个品类', 'error');
            return;
        }

        // 验证配置
        const invalidCategories = this.categories.filter(cat => !cat.keyword || cat.minPrice <= 0);
        if (invalidCategories.length > 0) {
            this.showStatus('请完善品类配置：关键词不能为空，最低价格必须大于0', 'error');
            return;
        }

        try {
            // 获取当前活动标签页
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            // 检测页面类型
            const pageType = await this.detectPageType(tab.id);
            console.log('检测到页面类型:', pageType);
            
            // 首先尝试注入内容脚本
            try {
                await chrome.scripting.executeScript({
                    target: { tabId: tab.id },
                    files: ['content.js']
                });
                console.log('内容脚本注入成功');
            } catch (injectError) {
                console.log('内容脚本可能已经存在，继续执行...');
            }
            
            // 等待一小段时间确保脚本加载
            await new Promise(resolve => setTimeout(resolve, 1000));
            
            // 先测试连接
            try {
                const pingResponse = await chrome.tabs.sendMessage(tab.id, { action: 'ping' });
                console.log('连接测试成功:', pingResponse);
            } catch (pingError) {
                console.error('连接测试失败:', pingError);
                this.showStatus('无法连接到页面，请刷新页面后重试', 'error');
                return;
            }
            
            // 发送消息到内容脚本开始自动勾选
            const response = await chrome.tabs.sendMessage(tab.id, {
                action: 'startAutoCheck',
                categories: this.categories,
                pageType: pageType // 传递页面类型信息
            });

            this.isRunning = true;
            this.updateButtonStates();
            this.showStatus(`自动勾选已开始 (${pageType})，正在扫描页面...`, 'success');

        } catch (error) {
            console.error('启动自动勾选失败:', error);
            this.showStatus('启动失败，请刷新页面后重试', 'error');
        }
    }

    // 检测页面类型
    async detectPageType(tabId) {
        try {
            const results = await chrome.scripting.executeScript({
                target: { tabId: tabId },
                func: () => {
                    // 检测页面类型
                    const hasWorryFree = document.querySelector('.worry-free-detail_table__unQvk');
                    const hasOfficialPromotion = document.querySelector('.block-title-module__title___3MkQp');
                    const hasFlashSale = document.querySelector('.block-title-module__title___3MkQp');
                    
                    if (hasWorryFree) {
                        return '省心报';
                    } else if (hasOfficialPromotion && hasOfficialPromotion.textContent.includes('官方大促')) {
                        return '官方大促';
                    } else if (hasFlashSale && hasFlashSale.textContent.includes('限时秒杀')) {
                        return '限时秒杀';
                    } else {
                        return '未知页面';
                    }
                }
            });
            
            return results[0].result;
        } catch (error) {
            console.error('检测页面类型失败:', error);
            return '未知页面';
        }
    }

    // 停止自动勾选
    async stopAutoCheck() {
        try {
            console.log('🛑 开始停止自动勾选...');
            
            // 立即更新UI状态
            this.isRunning = false;
            this.updateButtonStates();
            this.showStatus('正在停止自动勾选...', 'info');
            
            const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
            
            // 发送停止消息到内容脚本
            try {
                const response = await chrome.tabs.sendMessage(tab.id, { action: 'stopAutoCheck' });
                console.log('✅ 停止消息发送成功:', response);
            } catch (messageError) {
                console.warn('⚠️ 发送停止消息失败，但继续执行停止操作:', messageError);
            }
            
            // 立即更新状态显示
            setTimeout(() => {
                this.updateStatus();
            }, 500);
            
            this.showStatus('自动勾选已停止', 'success');
            console.log('✅ 停止操作完成');
            
        } catch (error) {
            console.error('❌ 停止自动勾选失败:', error);
            // 即使停止失败，也要更新状态
            this.isRunning = false;
            this.updateButtonStates();
            this.showStatus('自动勾选已停止', 'info');
        }
    }

    // 更新按钮状态
    updateButtonStates() {
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        
        startBtn.disabled = this.isRunning;
        stopBtn.disabled = !this.isRunning;
        
        // 更新按钮文本
        if (this.isRunning) {
            startBtn.textContent = '运行中...';
            stopBtn.textContent = '停止';
        } else {
            startBtn.textContent = '开始自动勾选';
            stopBtn.textContent = '已停止';
        }
    }

    // 显示状态信息
    showStatus(message, type = 'info') {
        const statusEl = document.getElementById('status');
        statusEl.textContent = message;
        statusEl.className = `status ${type}`;
    }
}

// 监听来自内容脚本的消息
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'updateStatus') {
        // 这里可以更新弹出窗口的状态显示
        console.log('收到状态更新:', message.data);
    }
});

// 初始化弹出窗口
document.addEventListener('DOMContentLoaded', () => {
    const popupManager = new PopupManager();
    
    // 页面卸载时清理定时器
    window.addEventListener('beforeunload', () => {
        popupManager.stopStatusUpdates();
    });
}); 