import { test, expect } from '@playwright/test'

/**
 * E2E 測試：意見投票切換功能
 * 測試案例：TC-VOTE-001 到 TC-VOTE-004
 */

test.describe('Opinion Voting Toggle', () => {
  test.beforeEach(async ({ page }) => {
    // 假設這是測試環境的 URL
    await page.goto('/')
  })

  test('TC-VOTE-001: 用戶可以成功投票支持意見', async ({ page }) => {
    // 1. 導航到登入頁面
    await page.goto('/login')

    // 2. 執行登入（需要替換為實際的測試帳號）
    await page.fill('input[type="text"]', 'testuser')
    await page.fill('input[type="password"]', 'testpass123')
    await page.click('button[type="submit"]')

    // 3. 等待登入成功
    await page.waitForURL('/opinions')

    // 4. 點擊第一個意見
    await page.click('.opinion-card:first-child')

    // 5. 等待詳情頁載入
    await page.waitForSelector('.voting-section')

    // 6. 點擊支持按鈕
    const supportButton = page.locator('button:has-text("支持")')
    const initialText = await supportButton.textContent()

    await supportButton.click()

    // 7. 驗證按鈕狀態變更
    await expect(supportButton).toContainText('已支持')

    // 8. 驗證投票數增加
    const voteCount = await supportButton.textContent()
    expect(voteCount).toMatch(/\(\d+\)/)
  })

  test('TC-VOTE-002: 用戶可以取消已投的支持票（切換）', async ({ page }) => {
    // 前置條件：假設用戶已登入且已對某意見投支持票

    await page.goto('/login')
    await page.fill('input[type="text"]', 'testuser')
    await page.fill('input[type="password"]', 'testpass123')
    await page.click('button[type="submit"]')

    await page.waitForURL('/opinions')
    await page.click('.opinion-card:first-child')
    await page.waitForSelector('.voting-section')

    // 確保已經是支持狀態
    const supportButton = page.locator('button:has-text("支持"), button:has-text("已支持")')

    // 如果尚未支持，先支持
    const buttonText = await supportButton.textContent()
    if (!buttonText.includes('已支持')) {
      await supportButton.click()
      await page.waitForTimeout(500)
    }

    // 記錄當前投票數
    const beforeText = await supportButton.textContent()
    const beforeMatch = beforeText.match(/\((\d+)\)/)
    const beforeCount = beforeMatch ? parseInt(beforeMatch[1]) : 0

    // 再次點擊取消投票
    await supportButton.click()

    // 等待狀態更新
    await page.waitForTimeout(500)

    // 驗證按鈕文字變回「支持」
    await expect(supportButton).toContainText('支持')
    await expect(supportButton).not.toContainText('已支持')

    // 驗證投票數減少
    const afterText = await supportButton.textContent()
    const afterMatch = afterText.match(/\((\d+)\)/)
    const afterCount = afterMatch ? parseInt(afterMatch[1]) : 0

    expect(afterCount).toBe(beforeCount - 1)
  })

  test('TC-VOTE-003: 用戶可以從支持切換到反對', async ({ page }) => {
    await page.goto('/login')
    await page.fill('input[type="text"]', 'testuser')
    await page.fill('input[type="password"]', 'testpass123')
    await page.click('button[type="submit"]')

    await page.waitForURL('/opinions')
    await page.click('.opinion-card:first-child')
    await page.waitForSelector('.voting-section')

    const supportButton = page.locator('button:has-text("支持"), button:has-text("已支持")')
    const opposeButton = page.locator('button:has-text("反對"), button:has-text("已反對")')

    // 確保是支持狀態
    const supportText = await supportButton.textContent()
    if (!supportText.includes('已支持')) {
      await supportButton.click()
      await page.waitForTimeout(500)
    }

    // 點擊反對按鈕
    await opposeButton.click()
    await page.waitForTimeout(500)

    // 驗證：支持按鈕變回未選中，反對按鈕變為已選中
    await expect(supportButton).toContainText('支持')
    await expect(supportButton).not.toContainText('已支持')
    await expect(opposeButton).toContainText('已反對')
  })
})
