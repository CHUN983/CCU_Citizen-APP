import { test, expect } from '@playwright/test'

/**
 * E2E 測試：審核中意見的互動限制
 * 測試案例：TC-RESTRICT-001 到 TC-RESTRICT-004
 */

test.describe('Pending Opinion Restrictions', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('TC-RESTRICT-001: 審核中意見應禁用投票按鈕', async ({ page }) => {
    // 1. 登入
    await page.goto('/login')
    await page.fill('input[type="text"]', 'testuser')
    await page.fill('input[type="password"]', 'testpass123')
    await page.click('button[type="submit"]')

    await page.waitForURL('/opinions')

    // 2. 假設存在審核中的意見，找到並點擊
    // （實際測試中需要確保有審核中的意見）
    const pendingOpinion = page.locator('.opinion-card:has(.el-tag:has-text("待審核"))')

    if (await pendingOpinion.count() > 0) {
      await pendingOpinion.first().click()

      // 3. 驗證顯示警告訊息
      await expect(page.locator('.el-alert:has-text("審核中")')).toBeVisible()

      // 4. 驗證投票按鈕被隱藏或禁用
      const supportButton = page.locator('button:has-text("支持")')
      const opposeButton = page.locator('button:has-text("反對")')

      // 按鈕應該不存在於 DOM 中（因為被 v-if 控制）
      await expect(supportButton).toHaveCount(0)
      await expect(opposeButton).toHaveCount(0)
    } else {
      // 如果沒有審核中的意見，跳過測試
      test.skip()
    }
  })

  test('TC-RESTRICT-002: 審核中意見應禁用留言功能', async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[type="text"]', 'testuser')
    await page.fill('input[type="password"]', 'testpass123')
    await page.click('button[type="submit"]')

    await page.waitForURL('/opinions')

    const pendingOpinion = page.locator('.opinion-card:has(.el-tag:has-text("待審核"))')

    if (await pendingOpinion.count() > 0) {
      await pendingOpinion.first().click()

      // 滾動到留言區
      await page.locator('.comments-card').scrollIntoViewIfNeeded()

      // 驗證顯示「無法發表留言」的警告
      await expect(page.locator('.el-alert:has-text("暫時無法發表留言")')).toBeVisible()

      // 驗證留言輸入框不存在
      const commentInput = page.locator('textarea[placeholder*="發表您的看法"]')
      await expect(commentInput).toHaveCount(0)
    } else {
      test.skip()
    }
  })

  test('TC-RESTRICT-003: 審核中意見可以正常查看內容', async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[type="text"]', 'testuser')
    await page.fill('input[type="password"]', 'testpass123')
    await page.click('button[type="submit"]')

    await page.waitForURL('/opinions')

    const pendingOpinion = page.locator('.opinion-card:has(.el-tag:has-text("待審核"))')

    if (await pendingOpinion.count() > 0) {
      await pendingOpinion.first().click()

      // 驗證可以看到標題
      await expect(page.locator('.opinion-header h1')).toBeVisible()

      // 驗證可以看到內容
      await expect(page.locator('.opinion-content')).toBeVisible()

      // 驗證可以看到狀態標籤
      await expect(page.locator('.el-tag:has-text("待審核")')).toBeVisible()
    } else {
      test.skip()
    }
  })

  test('TC-RESTRICT-004: 已通過意見應正常顯示所有互動功能', async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[type="text"]', 'testuser')
    await page.fill('input[type="password"]', 'testpass123')
    await page.click('button[type="submit"]')

    await page.waitForURL('/opinions')

    // 查找已通過的意見
    const approvedOpinion = page.locator('.opinion-card:has(.el-tag:has-text("已通過"))')

    if (await approvedOpinion.count() > 0) {
      await approvedOpinion.first().click()

      // 驗證投票按鈕可見
      await expect(page.locator('button:has-text("支持")')).toBeVisible()
      await expect(page.locator('button:has-text("反對")')).toBeVisible()

      // 驗證收藏按鈕可見
      await expect(page.locator('button:has-text("收藏")')).toBeVisible()

      // 滾動到留言區
      await page.locator('.comments-card').scrollIntoViewIfNeeded()

      // 驗證留言輸入框存在
      await expect(page.locator('textarea[placeholder*="發表您的看法"]')).toBeVisible()

      // 驗證發表按鈕存在
      await expect(page.locator('button:has-text("發表留言")')).toBeVisible()
    } else {
      test.skip()
    }
  })
})
