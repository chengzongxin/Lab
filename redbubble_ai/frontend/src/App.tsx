import React, { useState } from "react";
import TemuCategoryCrawler from "./components/TemuCategoryCrawler";
import TemuAIWorkflow from "./components/TemuAIWorkflow";
import TemuSellerCrawler from "./components/TemuSellerCrawler";
import AIDebugger from "./components/AIDebugger";
import RedbubblePage from "./components/RedbubblePage";
import "./App.css";

const App: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'redbubble' | 'temu' | 'ai-workflow' | 'seller' | 'ai-debugger'>('ai-workflow');

  const handleTabChange = (tab: 'redbubble' | 'temu' | 'ai-workflow' | 'seller' | 'ai-debugger') => {
    setActiveTab(tab);
  };

  const handleCrawlComplete = () => {
    // 当爬取完成时可以在这里添加全局的处理逻辑
  };

  return (
    <div className="app">
      <div className="header">
        {/* 标题放在左边 */}
        <div className="header-title">
          <h2>商品爬取与分析平台</h2>
        </div>

        {/* 标签页切换放在中间 */}
        <div className="tabs">
          <button
            className={activeTab === 'ai-workflow' ? 'active' : ''}
            onClick={() => handleTabChange('ai-workflow')}
          >
            🤖 AI工作流
          </button>
          <button
            className={activeTab === 'temu' ? 'active' : ''}
            onClick={() => handleTabChange('temu')}
          >
            📦 TEMU类目
          </button>
          <button
            className={activeTab === 'seller' ? 'active' : ''}
            onClick={() => handleTabChange('seller')}
          >
            🏪 TEMU卖家
          </button>
          <button
            className={activeTab === 'redbubble' ? 'active' : ''}
            onClick={() => handleTabChange('redbubble')}
          >
            🎨 Redbubble
          </button>
        </div>

        {/* AI调试器放在右边 */}
        <div className="header-right">
          <button
            className={`ai-debugger-tab ${activeTab === 'ai-debugger' ? 'active' : ''}`}
            onClick={() => handleTabChange('ai-debugger')}
          >
            🔧 AI调试器
          </button>
        </div>
      </div>

      {/* AI工作流标签页内容 */}
      {activeTab === 'ai-workflow' && (
        <div className="ai-workflow-container">
          <TemuAIWorkflow />
        </div>
      )}

      {/* AI调试器标签页内容 */}
      {activeTab === 'ai-debugger' && (
        <div className="ai-debugger-container">
          <AIDebugger />
        </div>
      )}

      {/* TEMU类目爬取标签页内容 */}
      {activeTab === 'temu' && (
        <div className="temu-crawler-container">
          <TemuCategoryCrawler onCrawlComplete={handleCrawlComplete} />
        </div>
      )}

      {/* TEMU卖家店铺标签页内容 */}
      {activeTab === 'seller' && (
        <div className="seller-crawler-container">
          <TemuSellerCrawler />
        </div>
      )}

      {/* Redbubble 标签页内容 */}
      {activeTab === 'redbubble' && (
        <div className="redbubble-container">
          <RedbubblePage onCrawlComplete={handleCrawlComplete} />
        </div>
      )}
    </div>
  );
};

export default App;
