import { defineConfig, devices } from '@playwright/test'

/**
 * Playwright E2E 測試配置
 * @see https://playwright.dev/docs/test-configuration
 */
export default defineConfig({
  testDir: './e2e',

  /* 最大測試失敗數 */
  maxFailures: process.env.CI ? 2 : undefined,

  /* 平行執行的 worker 數量 */
  workers: process.env.CI ? 1 : undefined,

  /* Reporter to use */
  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['list']
  ],

  /* 共享設定 */
  use: {
    /* Base URL */
    baseURL: process.env.VITE_API_URL || 'http://localhost:5173',

    /* 截圖設定 */
    screenshot: 'only-on-failure',

    /* 錄影設定 */
    video: 'retain-on-failure',

    /* 追蹤設定 */
    trace: 'on-first-retry'
  },

  /* 測試專案配置 */
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    },

    // 可選：其他瀏覽器測試
    // {
    //   name: 'firefox',
    //   use: { ...devices['Desktop Firefox'] }
    // },
    // {
    //   name: 'webkit',
    //   use: { ...devices['Desktop Safari'] }
    // },

    /* 移動端測試 */
    // {
    //   name: 'Mobile Chrome',
    //   use: { ...devices['Pixel 5'] }
    // },
    // {
    //   name: 'Mobile Safari',
    //   use: { ...devices['iPhone 12'] }
    // }
  ],

  /* 開發伺服器配置（用於本地測試） */
  webServer: process.env.CI ? undefined : {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000
  }
})
