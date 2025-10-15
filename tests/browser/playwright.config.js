// @ts-check
const { defineConfig, devices } = require('@playwright/test');

/**
 * Browser testing configuration for Customer Data Tools
 *
 * Tests connection setup functionality at http://localhost:6001/connections/setup
 */
module.exports = defineConfig({
  testDir: './',
  fullyParallel: false, // Run tests sequentially for reliability
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: 1, // Run one test at a time
  reporter: [
    ['html', { outputFolder: './playwright-report', open: 'never' }],
    ['list']
  ],

  use: {
    baseURL: 'http://localhost:6001',
    trace: 'retain-on-failure',
    screenshot: 'only-on-failure',
    video: 'retain-on-failure',
    actionTimeout: 10000,
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],

  // Note: Server should already be running on port 6001
  // Start with: PYTHONPATH=. PORT=6001 ./venv/bin/python src/app.py
});
