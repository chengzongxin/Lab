import { test, expect } from '@playwright/test';

// test('has title', async ({ page }) => {
//   await page.goto('https://playwright.dev/');

//   // Expect a title "to contain" a substring.
//   await expect(page).toHaveTitle(/Playwright/);
// });

// test('get started link', async ({ page }) => {
//   await page.goto('https://playwright.dev/');

//   // Click the get started link.
//   await page.getByRole('link', { name: 'Get started' }).click();

//   // Expects page to have a heading with the name of Installation.
//   await expect(page.getByRole('heading', { name: 'Installation' })).toBeVisible();
// });

// test('baidu', async ({ page }) => {
//   await page.goto('https://www.baidu.com/');
//   await page.waitForTimeout(10000);
//   await page.getByRole('textbox').click();
//   await page.getByRole('textbox').fill('哈哈哈');
//   await page.getByRole('textbox').press('Enter');
//   await page.waitForTimeout(10000);
// });


test('kuajingmaihuo', async ({ page }) => {
  await page.goto('https://seller.kuajingmaihuo.com/login?redirectUrl=https%3A%2F%2Fseller.kuajingmaihuo.com%2F');
  await page.getByRole('textbox', { name: '手机号码' }).click();
  await page.getByRole('textbox', { name: '手机号码' }).fill('13924668547');
  await page.getByRole('textbox', { name: '密码' }).click();
  await page.getByRole('textbox', { name: '密码' }).fill('Xiaozhou1221.');
  await page.getByTestId('beast-core-icon-check').click();
  await page.getByRole('button', { name: '登录' }).click();
  await page.waitForTimeout(10000)
});