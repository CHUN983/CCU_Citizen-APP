import { test, expect } from '@playwright/test'

/**
 * E2E 測試：我的意見管理功能
 * 測試案例：TC-OPIN-016 到 TC-OPIN-018
 */

test.describe('My Opinions Management', () => {
  test.beforeEach(async ({ page }) => {
    // 登入
    await page.goto('/login')
    await page.fill('input[type="text"]', 'testuser')
    await page.fill('input[type="password"]', 'testpass123')
    await page.click('button[type="submit"]')

    // 等待導航到意見列表頁
    await page.waitForURL('/opinions')

    // 導航到個人資料頁
    await page.goto('/profile')
  })

  test('TC-OPIN-018: 個人資料頁面應顯示「我的意見」區塊', async ({ page }) => {
    // 1. 驗證「我的意見」卡片存在
    await expect(page.locator('.el-card:has-text("我的意見")')).toBeVisible()

    // 2. 驗證有「提交新意見」按鈕
    await expect(page.locator('button:has-text("提交新意見")')).toBeVisible()

    // 3. 驗證有分頁標籤
    await expect(page.locator('.el-tabs__item:has-text("已通過")')).toBeVisible()
    await expect(page.locator('.el-tabs__item:has-text("審核中")')).toBeVisible()
  })

  test('TC-OPIN-016: 應能獲取並顯示用戶自己的意見列表', async ({ page }) => {
    // 1. 等待資料載入
    await page.waitForTimeout(1000)

    // 2. 檢查是否有意見卡片或空狀態提示
    const opinionCards = page.locator('.opinion-item')
    const emptyState = page.locator('.el-empty')

    const hasOpinions = await opinionCards.count() > 0
    const isEmpty = await emptyState.isVisible()

    // 應該至少有一個狀態存在
    expect(hasOpinions || isEmpty).toBeTruthy()

    if (hasOpinions) {
      // 3. 驗證意見卡片包含必要資訊
      const firstOpinion = opinionCards.first()

      // 驗證有標題
      await expect(firstOpinion.locator('.opinion-title')).toBeVisible()

      // 驗證有狀態標籤
      await expect(firstOpinion.locator('.el-tag')).toBeVisible()

      // 驗證有統計資訊（瀏覽數、投票數等）
      await expect(firstOpinion.locator('.opinion-stats')).toBeVisible()
    }
  })

  test('TC-OPIN-017: 應能依狀態篩選意見（已通過/審核中）', async ({ page }) => {
    await page.waitForTimeout(1000)

    // 1. 默認顯示「已通過」標籤
    const approvedTab = page.locator('.el-tabs__item:has-text("已通過")')
    await expect(approvedTab).toHaveClass(/is-active/)

    // 記錄已通過意見的數量
    const approvedOpinions = page.locator('.opinion-item')
    const approvedCount = await approvedOpinions.count()

    // 2. 切換到「審核中」標籤
    const pendingTab = page.locator('.el-tabs__item:has-text("審核中")')
    await pendingTab.click()

    // 等待資料載入
    await page.waitForTimeout(1000)

    // 3. 驗證標籤狀態改變
    await expect(pendingTab).toHaveClass(/is-active/)

    // 4. 記錄審核中意見的數量
    const pendingOpinions = page.locator('.opinion-item')
    const pendingCount = await pendingOpinions.count()

    // 5. 驗證兩個狀態的意見列表可能不同
    // （如果用戶同時有已通過和審核中的意見，數量應該不同）
    console.log(`Approved: ${approvedCount}, Pending: ${pendingCount}`)

    // 6. 切換回「已通過」標籤
    await approvedTab.click()
    await page.waitForTimeout(500)

    // 7. 驗證切換成功
    await expect(approvedTab).toHaveClass(/is-active/)
  })

  test('應能點擊「提交新意見」按鈕導航到意見提交頁', async ({ page }) => {
    // 點擊「提交新意見」按鈕
    await page.click('button:has-text("提交新意見")')

    // 驗證導航到意見建立頁面
    await page.waitForURL('/opinions/create')

    // 驗證頁面包含表單元素
    await expect(page.locator('form')).toBeVisible()
  })

  test('應能點擊意見卡片查看詳情', async ({ page }) => {
    await page.waitForTimeout(1000)

    const opinionCards = page.locator('.opinion-item')

    if (await opinionCards.count() > 0) {
      // 點擊第一張意見卡片
      await opinionCards.first().click()

      // 驗證導航到詳情頁
      await page.waitForURL(/\/opinions\/\d+/)

      // 驗證詳情頁包含意見內容
      await expect(page.locator('.opinion-detail-container')).toBeVisible()
    } else {
      test.skip()
    }
  })

  test('應顯示正確的分頁功能（如果意見數量超過每頁限制）', async ({ page }) => {
    await page.waitForTimeout(1000)

    // 檢查是否有分頁器
    const pagination = page.locator('.el-pagination')

    if (await pagination.isVisible()) {
      // 驗證分頁功能存在
      await expect(pagination).toBeVisible()

      // 驗證有頁碼按鈕
      const pageNumbers = pagination.locator('.el-pager .number')
      expect(await pageNumbers.count()).toBeGreaterThan(0)

      // 如果有多頁，測試翻頁
      if (await pageNumbers.count() > 1) {
        const secondPage = pageNumbers.nth(1)
        await secondPage.click()

        // 等待資料載入
        await page.waitForTimeout(1000)

        // 驗證第二頁被激活
        await expect(secondPage).toHaveClass(/is-active/)
      }
    }
  })
})
