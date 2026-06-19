const { defineConfig } = require('@playwright/test');

module.exports = defineConfig({
  testDir: '.',
  timeout: 30000,
  retries: 0,
  use: {
    baseURL: 'http://localhost:5100',
    headless: true,
    viewport: { width: 1280, height: 800 },
    actionTimeout: 10000,
  },
});
