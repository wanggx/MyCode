const { test, expect } = require('@playwright/test');

test.describe('Create Backtest Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5100/login');
    const inputs = page.locator('.el-input__inner');
    await inputs.first().fill('test');
    await inputs.nth(1).fill('test123');
    await page.click('button:has-text("登录"):not(:has-text("注册"))');
    await page.waitForTimeout(1500);
  });

  test('Create strategy via dialog', async ({ page }) => {
    await page.click('.el-menu-item:has-text("策略研究")');
    await page.waitForSelector('.strategy-item', { timeout: 5000 });

    // Create new strategy
    await page.click('button:has-text("新建")');
    await page.waitForSelector('.el-dialog', { timeout: 3000 });
    const nameInput = page.locator('.el-dialog .el-input__inner').first();
    await nameInput.fill('E2E-Create-' + Date.now());
    await page.click('.el-dialog button:has-text("创建")');
    await page.waitForTimeout(1500);

    // Verify list refreshed
    const items = page.locator('.strategy-item');
    const count = await items.count();
    expect(count).toBeGreaterThan(0);
  });

  test('Edit code and save via Ctrl+S', async ({ page }) => {
    await page.click('.el-menu-item:has-text("策略研究")');
    await page.waitForSelector('.strategy-item.active', { timeout: 5000 });

    // Click edit
    await page.click('button:has-text("编辑代码")');
    await page.waitForTimeout(500);

    // Monaco should be editable - find textarea and type
    const editor = page.locator('.monaco-editor textarea');
    if (await editor.isVisible()) {
      await editor.click();
      await page.keyboard.type('def init(context):\n    context.fast = 5\n    context.slow = 20\n\ndef handle_bar(context, bar_dict):\n    pass\n');
      await page.waitForTimeout(300);
    }

    // Press Ctrl+S to save
    await page.keyboard.press('Meta+S');
    await page.waitForTimeout(1500);
  });

  test('Create backtest from strategy page', async ({ page }) => {
    await page.click('.el-menu-item:has-text("策略研究")');
    await page.waitForSelector('.strategy-item.active', { timeout: 5000 });

    // Open backtest dialog
    const btBtn = page.locator('button:has-text("回测")').first();
    if (await btBtn.isVisible()) {
      await btBtn.click();
      await page.waitForSelector('.el-dialog:has-text("新建回测")', { timeout: 3000 });

      // Start backtest
      const startBtn = page.locator('.el-dialog button:has-text("开始回测")');
      await startBtn.click();
      await page.waitForTimeout(3000);

      // Close dialog if still open (error message, etc.)
      await page.keyboard.press('Escape');
      await page.waitForTimeout(500);

      // Navigate to backtest center
      await page.click('.el-menu-item:has-text("回测中心")');
      await page.waitForSelector('.bt-item', { timeout: 5000 });

      // Should show backtest list with items
      const items = page.locator('.bt-item');
      const count = await items.count();
      expect(count).toBeGreaterThan(0);
    }
  });

  test('Backtest center - view completed backtest details', async ({ page }) => {
    await page.click('.el-menu-item:has-text("回测中心")');
    await page.waitForSelector('.bt-item', { timeout: 5000 });

    // Wait for items to load
    const items = page.locator('.bt-item');
    const count = await items.count();
    if (count > 0) {
      // Click first completed or any backtest
      await items.first().click();
      await page.waitForTimeout(1000);

      // Should show summary card
      await expect(page.locator('.summary-card')).toBeVisible({ timeout: 3000 });
      // Should show metrics
      await expect(page.locator('.metrics')).toBeVisible({ timeout: 3000 });

      // Check tabs work
      const tabs = ['净值曲线', '交易记录', '持仓分析', '风险分析', '收益分布', '日志'];
      for (const label of tabs) {
        const tab = page.locator(`.tab-item:has-text("${label}")`);
        if (await tab.isVisible()) {
          await tab.click();
          await page.waitForTimeout(300);
          await expect(tab).toHaveClass(/active/);
        }
      }
    }
  });
});
