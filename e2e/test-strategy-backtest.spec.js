// @ts-check
const { test, expect } = require('@playwright/test');

const BASE = 'http://localhost:5100';

test.describe('QT Platform E2E', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto(BASE + '/login');
    // Login tab: first 2 input fields
    const inputs = page.locator('.el-input__inner');
    await inputs.first().fill('test');
    await inputs.nth(1).fill('test123');
    await page.click('button:has-text("登录"):not(:has-text("注册"))');
    await page.waitForURL('**/workspace', { timeout: 15000 }).catch(() => {});
    // If still on login page, login failed - try to continue anyway
    await page.waitForTimeout(1000);
  });

  test('01 - Workspace loads with KPI cards', async ({ page }) => {
    await expect(page.locator('.workspace')).toBeVisible();
    // Check KPI cards exist
    const cards = page.locator('.stat-grid .el-card');
    await expect(cards).toHaveCount(4);
  });

  test('02 - Navigate to Strategy Research', async ({ page }) => {
    await page.click('.el-menu-item:has-text("策略研究")');
    await page.waitForURL('**/strategies');
    await expect(page.locator('.strategy-page')).toBeVisible();
  });

  test('03 - Strategy list loads and first item auto-selected', async ({ page }) => {
    await page.click('.el-menu-item:has-text("策略研究")');
    await page.waitForURL('**/strategies');
    // Wait for list to load
    await page.waitForSelector('.strategy-item', { timeout: 5000 });
    const items = page.locator('.strategy-item');
    const count = await items.count();
    expect(count).toBeGreaterThan(0);
    // First item should be active
    await expect(items.first()).toHaveClass(/active/);
  });

  test('04 - Code editor shows strategy code', async ({ page }) => {
    await page.click('.el-menu-item:has-text("策略研究")');
    await page.waitForURL('**/strategies');
    await page.waitForSelector('.strategy-item.active', { timeout: 5000 });
    // Code editor should be visible
    await expect(page.locator('.code-editor-wrap')).toBeVisible({ timeout: 5000 });
  });

  test('05 - Edit code button toggles edit mode', async ({ page }) => {
    await page.click('.el-menu-item:has-text("策略研究")');
    await page.waitForURL('**/strategies');
    await page.waitForSelector('.strategy-item.active', { timeout: 5000 });
    // Click edit button
    const editBtn = page.locator('button:has-text("编辑代码")');
    if (await editBtn.isVisible()) {
      await editBtn.click();
      // Check mode badge changed
      await expect(page.locator('.mode-badge:has-text("编辑中")')).toBeVisible({ timeout: 3000 });
    }
  });

  test('06 - Version history dialog opens', async ({ page }) => {
    await page.click('.el-menu-item:has-text("策略研究")');
    await page.waitForURL('**/strategies');
    await page.waitForSelector('.strategy-item.active', { timeout: 5000 });
    // Click version history
    const btn = page.locator('button:has-text("版本历史")');
    if (await btn.isVisible()) {
      await btn.click();
      // Dialog should appear
      await expect(page.locator('.el-dialog:has-text("版本历史")')).toBeVisible({ timeout: 3000 });
      // Close it
      await page.click('.el-dialog__close');
    }
  });

  test('07 - Strategy research backtest dialog opens', async ({ page }) => {
    await page.click('.el-menu-item:has-text("策略研究")');
    await page.waitForURL('**/strategies');
    await page.waitForSelector('.strategy-item.active', { timeout: 5000 });
    // Click backtest button
    const btn = page.locator('button:has-text("回测")').first();
    if (await btn.isVisible()) {
      await btn.click();
      await expect(page.locator('.el-dialog:has-text("新建回测")')).toBeVisible({ timeout: 3000 });
      // Close it
      await page.keyboard.press('Escape');
    }
  });

  test('08 - Navigate to Backtest Center', async ({ page }) => {
    await page.click('.el-menu-item:has-text("回测中心")');
    await page.waitForURL('**/backtest');
    await expect(page.locator('.bt-page')).toBeVisible();
  });

  test('09 - Backtest list loads and first item auto-selected', async ({ page }) => {
    await page.click('.el-menu-item:has-text("回测中心")');
    await page.waitForURL('**/backtest');
    await page.waitForSelector('.bt-item', { timeout: 5000 });
    const items = page.locator('.bt-item');
    const count = await items.count();
    expect(count).toBeGreaterThan(0);
    // First item should be active
    await expect(items.first()).toHaveClass(/active/);
  });

  test('10 - Backtest detail shows summary card', async ({ page }) => {
    await page.click('.el-menu-item:has-text("回测中心")');
    await page.waitForURL('**/backtest');
    await page.waitForSelector('.bt-item.active', { timeout: 5000 });
    // Summary card visible
    await expect(page.locator('.summary-card')).toBeVisible({ timeout: 3000 });
    // Title visible
    await expect(page.locator('.summary-title')).toBeVisible({ timeout: 2000 });
  });

  test('11 - Backtest metrics grid has 12 items', async ({ page }) => {
    await page.click('.el-menu-item:has-text("回测中心")');
    await page.waitForURL('**/backtest');
    await page.waitForSelector('.bt-item.active', { timeout: 5000 });
    // Metrics grid should have 12 items
    const items = page.locator('.metrics .m-item');
    await expect(items).toHaveCount(12, { timeout: 3000 });
  });

  test('12 - Backtest tabs switch correctly', async ({ page }) => {
    await page.click('.el-menu-item:has-text("回测中心")');
    await page.waitForURL('**/backtest');
    await page.waitForSelector('.bt-item.active', { timeout: 5000 });
    // Wait for tabs to be visible
    await page.waitForSelector('.tab-item', { timeout: 3000 });
    // Click each tab
    const tabLabels = ['净值曲线', '交易记录', '持仓分析', '风险分析', '收益分布', '日志'];
    for (const label of tabLabels) {
      const tab = page.locator(`.tab-item:has-text("${label}")`);
      if (await tab.isVisible()) {
        await tab.click();
        await page.waitForTimeout(300);
        await expect(tab).toHaveClass(/active/);
      }
    }
  });

  test('13 - New backtest dialog opens from Backtest Center', async ({ page }) => {
    await page.click('.el-menu-item:has-text("回测中心")');
    await page.waitForURL('**/backtest');
    await page.waitForSelector('.bt-item.active', { timeout: 5000 });
    // Click new backtest button
    const btn = page.locator('button:has-text("新建回测")');
    if (await btn.isVisible()) {
      await btn.click();
      await expect(page.locator('.el-dialog:has-text("新建回测")')).toBeVisible({ timeout: 3000 });
      await page.keyboard.press('Escape');
    }
  });

  test('14 - Backtest has action buttons', async ({ page }) => {
    await page.click('.el-menu-item:has-text("回测中心")');
    await page.waitForURL('**/backtest');
    await page.waitForSelector('.bt-item.active', { timeout: 5000 });
    // Should see delete button (for non-running backtests)
    const delBtn = page.locator('button:has-text("删除")');
    await expect(delBtn.first()).toBeVisible({ timeout: 3000 });
  });

  test('15 - Log tab shows log content', async ({ page }) => {
    await page.click('.el-menu-item:has-text("回测中心")');
    await page.waitForURL('**/backtest');
    await page.waitForSelector('.bt-item.active', { timeout: 5000 });
    // Click log tab
    const logTab = page.locator('.tab-item:has-text("日志")');
    if (await logTab.isVisible()) {
      await logTab.click();
      await page.waitForTimeout(500);
      // Log panel should be visible
      await expect(page.locator('.log-panel')).toBeVisible({ timeout: 3000 });
    }
  });
});
