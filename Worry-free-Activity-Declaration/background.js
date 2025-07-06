// 后台脚本 - 处理插件的后台逻辑
chrome.runtime.onInstalled.addListener(() => {
    console.log('🎯 活动申报助手已安装');
    
    // 设置默认配置
    chrome.storage.sync.get(['categories'], (result) => {
        if (!result.categories) {
            const defaultCategories = [
                { keyword: '袜子', minPrice: 10 },
                { keyword: '围裙', minPrice: 15 },
                { keyword: '帽子', minPrice: 20 }
            ];
            chrome.storage.sync.set({ categories: defaultCategories });
        }
    });
});

// 监听来自内容脚本的消息
chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.action === 'updateStatus') {
        // 可以在这里处理状态更新逻辑
        console.log('收到状态更新:', message.data);
    }
});

// 处理标签页更新
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
    if (changeInfo.status === 'complete' && tab.url) {
        // 页面加载完成后，可以在这里执行一些初始化逻辑
        console.log('页面加载完成:', tab.url);
    }
});

// 处理插件图标点击事件
chrome.action.onClicked.addListener((tab) => {
    // 如果需要在点击插件图标时执行特定操作，可以在这里添加
    console.log('插件图标被点击');
}); 