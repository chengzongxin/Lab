import { Page } from '@playwright/test';

export class BaiduPage {
  // 页面对象
  private page: Page;

  // 页面元素选择器
  private selectors = {
    searchInput: '#kw',
    searchButton: '#su',
    searchResults: '.result'
  };

  // 构造函数
  constructor(page: Page) {
    this.page = page;
  }

  // 导航到百度首页
  async navigate() {
    await this.page.goto('https://www.baidu.com');
  }

  // 执行搜索
  async search(keyword: string) {
    await this.page.waitForSelector(this.selectors.searchInput);
    await this.page.fill(this.selectors.searchInput, keyword);
    await this.page.click(this.selectors.searchButton);
    await this.page.waitForSelector(this.selectors.searchResults);
  }

  // 获取页面标题
  async getTitle() {
    return await this.page.title();
  }

  // 截图
  async takeScreenshot(path: string) {
    await this.page.screenshot({ path });
  }
} 