import { test, expect } from '@playwright/test';
import { BaiduPage } from './pages/BaiduPage';
import { searchKeywords, expectedResults } from './data/searchData';
import { Logger } from './utils/logger';

test.describe('百度搜索测试套件', () => {
  test('搜索 Playwright', async ({ page }) => {
    const baiduPage = new BaiduPage(page);
    Logger.info('开始测试百度搜索 Playwright');

    try {
      await baiduPage.navigate();
      await baiduPage.search(searchKeywords.playwright);
      
      const title = await baiduPage.getTitle();
      expect(title).toContain(expectedResults.playwright.titleContains);
      
      await baiduPage.takeScreenshot(expectedResults.playwright.screenshotPath);
      Logger.info('测试完成');
    } catch (error) {
      Logger.error('测试失败', error);
      throw error;
    }
  });

  test('搜索 Selenium', async ({ page }) => {
    const baiduPage = new BaiduPage(page);
    Logger.info('开始测试百度搜索 Selenium');

    try {
      await baiduPage.navigate();
      await baiduPage.search(searchKeywords.selenium);
      
      const title = await baiduPage.getTitle();
      expect(title).toContain(expectedResults.selenium.titleContains);
      
      await baiduPage.takeScreenshot(expectedResults.selenium.screenshotPath);
      Logger.info('测试完成');
    } catch (error) {
      Logger.error('测试失败', error);
      throw error;
    }
  });
}); 