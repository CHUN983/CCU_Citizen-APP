# 前端測試與 CI/CD Pipeline 指南
# Frontend Testing & CI/CD Pipeline Guide

> **專案名稱**: citizenApp - 市民意見平台 (Citizen Portal)
> **文件版本**: 1.0
> **建立日期**: 2025-12-12
> **文件狀態**: 正式版
> **適用對象**: 前端開發者、測試工程師、DevOps 工程師

---

## 📋 文件修訂歷史

| 版本 | 日期 | 修訂者 | 修訂說明 |
|------|------|--------|----------|
| 1.0 | 2025-12-12 | Dev Team | 初版發布 - 前端測試框架與 CI/CD Pipeline |

---

# 目錄

- [壹、簡介](#壹簡介)
- [貳、CI/CD Pipeline 架構](#貳cicd-pipeline-架構)
- [參、測試框架配置](#參測試框架配置)
- [肆、單元測試 (Vitest)](#肆單元測試-vitest)
- [伍、E2E 測試 (Playwright)](#伍e2e-測試-playwright)
- [陸、程式碼品質 (ESLint)](#陸程式碼品質-eslint)
- [柒、實用指南](#柒實用指南)
- [捌、故障排查](#捌故障排查)

---

# 壹、簡介

## 1.1 文件目的

本文件旨在提供 citizenApp Citizen Portal 前端測試框架的完整指南，包括：
- **CI/CD Pipeline** 的架構與配置
- **單元測試**框架（Vitest）的使用方法
- **E2E 測試**框架（Playwright）的使用方法
- **程式碼品質**工具（ESLint）的配置
- 測試編寫最佳實踐與故障排查

## 1.2 技術堆疊

### 前端框架
- **Vue 3** (Composition API)
- **Vite** 7.x (構建工具)
- **Pinia** 3.x (狀態管理)
- **Element Plus** 2.x (UI 組件庫)

### 測試框架
- **Vitest** 2.1.8 (單元測試)
- **@vue/test-utils** 2.4.6 (Vue 組件測試)
- **Playwright** 1.48.0 (E2E 測試)
- **jsdom** 25.0.1 (DOM 模擬環境)

### 程式碼品質
- **ESLint** 8.57.0 (Linter)
- **eslint-plugin-vue** 9.27.0 (Vue 規則)

### CI/CD
- **GitHub Actions** (自動化 CI/CD)
- **Python 3.10** (後端)
- **Node.js 18** (前端)

---

# 貳、CI/CD Pipeline 架構

## 2.1 Pipeline 概覽

### 2.1.1 觸發條件

```yaml
觸發分支: main, develop, claude
觸發事件: push, pull_request
```

CI/CD Pipeline 會在以下情況自動執行：
- Push 到 `main`、`develop` 或 `claude` 分支
- 向 `main` 或 `develop` 分支發起 Pull Request

### 2.1.2 Pipeline 架構圖

```
┌─────────────────────────────────────────────────────┐
│ Trigger: Push/PR to main/develop/claude            │
└─────────────────────────────────────────────────────┘
                         ↓
┌──────────────────────────────────────────────────────┐
│ Job 1: Code Quality (Python Lint + Black)           │
│ - flake8 語法檢查                                     │
│ - Black 格式檢查                                      │
└──────────────────────────────────────────────────────┘
                    ↙    ↓    ↘
         ┌──────────┬─────────┬──────────┐
         │ Job 2:   │ Job 3:  │ Job 5:   │
         │ Admin    │ Citizen │ Backend  │
         │ Dashboard│ Portal  │ Unit     │
         │ Tests    │ Tests   │ Tests    │
         │          │ ✨ NEW  │          │
         └──────────┴─────────┴──────────┘
                         ↓
         ┌────────────────────────────────┐
         │ Job 6: API Health Check        │
         │ - 基本健康檢查                   │
         │ - 新增端點檢查 ✨                │
         │   • /opinions/my-opinions       │
         │   • /opinions/{id}/vote         │
         │   • /opinions/{id}/collect      │
         └────────────────────────────────┘
                         ↓
         ┌────────────────────────────────┐
         │ Job 7: E2E Tests (Playwright)  │
         │ ✨ NEW                         │
         │ - 投票切換測試                   │
         │ - 審核限制測試                   │
         │ - 我的意見測試                   │
         └────────────────────────────────┘
                    ↙         ↘
         ┌──────────┐    ┌──────────┐
         │ Job 8:   │    │ Job 9:   │
         │ Security │    │ Docker   │
         │ Scan     │    │ Build    │
         └──────────┘    └──────────┘
                         ↓
         ┌────────────────────────────────┐
         │ Job 10: Deploy Staging         │
         └────────────────────────────────┘
                         ↓
         ┌────────────────────────────────┐
         │ Job 11: Notification           │
         │ ✨ 包含所有測試狀態               │
         └────────────────────────────────┘
```

## 2.2 Job 詳細說明

### Job 3: Citizen Portal Tests ✨ 新增

**目的**: 測試 Citizen Portal 前端應用

**執行步驟**:
1. Checkout 程式碼
2. 設置 Node.js 18 環境
3. 安裝依賴 (`npm ci`)
4. **Lint 檢查** (`npm run lint`)
5. **構建專案** (`npm run build`)
6. **運行單元測試** (`npm run test -- --run`)
7. **生成覆蓋率報告** (`npm run test:coverage`)
8. 上傳覆蓋率報告到 artifacts

**成功條件**:
- ✅ Lint 無錯誤（警告可接受）
- ✅ 構建成功
- ✅ 所有單元測試通過

### Job 7: E2E Tests (Playwright) ✨ 新增

**目的**: 端對端測試關鍵用戶流程

**執行步驟**:
1. 啟動 MySQL 測試資料庫
2. 設置 Python 和 Node.js 環境
3. 初始化測試資料庫
4. 啟動 FastAPI 後端服務
5. 安裝 Playwright 瀏覽器
6. **運行 E2E 測試** (`npm run test:e2e`)
7. 上傳測試報告到 artifacts

**測試涵蓋**:
- ✅ 投票切換功能 (3 個測試)
- ✅ 審核中意見限制 (4 個測試)
- ✅ 我的意見管理 (6 個測試)

**觸發條件**: 僅在 `push` 事件觸發（PR 不運行 E2E）

## 2.3 測試報告與 Artifacts

### 可下載的測試報告

Pipeline 執行後，可在 GitHub Actions 頁面下載以下報告：

| Artifact 名稱 | 內容 | 保留天數 |
|--------------|------|----------|
| `frontend-coverage` | Admin Dashboard 覆蓋率報告 | 7 天 |
| `citizen-portal-coverage` | Citizen Portal 覆蓋率報告 | 7 天 |
| `playwright-report` | E2E 測試報告（HTML） | 7 天 |

### 查看測試報告步驟

1. 進入 GitHub Repository
2. 點擊 **Actions** 標籤
3. 選擇最近的 workflow run
4. 滾動到頁面底部找到 **Artifacts**
5. 下載並解壓報告
6. 開啟 `index.html`（覆蓋率報告）或 Playwright 報告

---

# 參、測試框架配置

## 3.1 專案結構

```
src/main/js/citizen-portal/
├── src/
│   ├── api/              # API 呼叫
│   ├── components/       # Vue 組件
│   ├── store/           # Pinia stores
│   ├── views/           # 頁面組件
│   ├── router/          # Vue Router
│   └── test/            # 測試工具 ✨
│       ├── setup.js     # Vitest 測試環境設置
│       └── store/       # Store 單元測試
│           └── opinion.spec.js
├── e2e/                 # E2E 測試 ✨
│   ├── opinion-voting.spec.js
│   ├── pending-opinion-restrictions.spec.js
│   └── my-opinions.spec.js
├── .eslintrc.cjs        # ESLint 配置 ✨
├── .eslintignore        # ESLint 忽略檔案 ✨
├── vitest.config.js     # Vitest 配置 ✨
├── playwright.config.js # Playwright 配置 ✨
├── vite.config.js       # Vite 配置
└── package.json         # 依賴與腳本
```

## 3.2 NPM 腳本

### 可用命令

```json
{
  "scripts": {
    // 開發相關
    "dev": "vite",                    // 啟動開發伺服器
    "build": "vite build",            // 構建生產版本
    "preview": "vite preview",        // 預覽生產版本

    // 程式碼品質
    "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs --ignore-path .gitignore",
    "lint:fix": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs --fix --ignore-path .gitignore",

    // 單元測試
    "test": "vitest",                 // 運行測試（watch 模式）
    "test:ui": "vitest --ui",         // 測試 UI 界面
    "test:coverage": "vitest run --coverage",  // 生成覆蓋率報告

    // E2E 測試
    "test:e2e": "playwright test",    // 運行 E2E 測試
    "test:e2e:ui": "playwright test --ui",  // Playwright UI 模式

    // Capacitor (移動端)
    "cap:sync": "npm run build && npx cap sync",
    "cap:android": "npm run cap:sync && npx cap open android",
    "cap:ios": "npm run cap:sync && npx cap open ios"
  }
}
```

## 3.3 依賴版本

### 生產依賴

```json
{
  "@capacitor/android": "^7.4.4",
  "@capacitor/camera": "^7.0.2",
  "@capacitor/cli": "^7.4.4",
  "@capacitor/core": "^7.4.4",
  "@capacitor/filesystem": "^7.1.5",
  "@capacitor/ios": "^7.4.4",
  "@capacitor/splash-screen": "^7.0.3",
  "@element-plus/icons-vue": "^2.3.2",
  "axios": "^1.12.2",
  "element-plus": "^2.11.5",
  "pinia": "^3.0.3",
  "vue": "^3.5.22",
  "vue-router": "^4.6.3"
}
```

### 開發依賴

```json
{
  "@playwright/test": "^1.48.0",        // E2E 測試
  "@vitejs/plugin-vue": "^6.0.1",       // Vite Vue 插件
  "@vitest/ui": "^2.1.8",               // Vitest UI
  "@vue/test-utils": "^2.4.6",          // Vue 測試工具
  "@vitest/coverage-v8": "^2.1.8",      // 覆蓋率報告
  "eslint": "^8.57.0",                  // Linter
  "eslint-plugin-vue": "^9.27.0",       // Vue ESLint 規則
  "jsdom": "^25.0.1",                   // DOM 模擬
  "vite": "^7.1.7",                     // 構建工具
  "vitest": "^2.1.8"                    // 測試框架
}
```

---

# 肆、單元測試 (Vitest)

## 4.1 Vitest 簡介

**Vitest** 是一個基於 Vite 的快速單元測試框架，專為現代前端應用設計。

### 主要特點
- ⚡ **極快的執行速度** - 基於 Vite 的熱模塊替換
- 🔄 **Watch 模式** - 自動重新運行變更的測試
- 📊 **內建覆蓋率** - 使用 v8 引擎
- 🎯 **Vue 友好** - 完美支援 Vue 3 組件測試
- 🖥️ **UI 界面** - 視覺化測試運行器

## 4.2 配置文件

### vitest.config.js

```javascript
import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { fileURLToPath } from 'node:url'

export default defineConfig({
  plugins: [vue()],
  test: {
    globals: true,              // 全局測試 API (describe, it, expect)
    environment: 'jsdom',       // 使用 jsdom 模擬瀏覽器環境
    setupFiles: ['./src/test/setup.js'],  // 測試環境設置
    coverage: {
      provider: 'v8',           // 使用 V8 覆蓋率
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/',
        'src/test/',
        '**/*.config.js',
        '**/mockData.js',
        'android/',
        'ios/',
        '.capacitor/'
      ]
    }
  },
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  }
})
```

### src/test/setup.js

測試環境初始化文件：

```javascript
import { vi } from 'vitest'

// Mock localStorage
global.localStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}

// Mock sessionStorage
global.sessionStorage = {
  getItem: vi.fn(),
  setItem: vi.fn(),
  removeItem: vi.fn(),
  clear: vi.fn()
}

// Mock window.matchMedia (響應式測試)
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: vi.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: vi.fn(),
    removeListener: vi.fn(),
    addEventListener: vi.fn(),
    removeEventListener: vi.fn(),
    dispatchEvent: vi.fn()
  }))
})
```

## 4.3 編寫單元測試

### 4.3.1 測試 Pinia Store

**範例**: `src/test/store/opinion.spec.js`

```javascript
import { describe, it, expect, beforeEach, vi } from 'vitest'
import { setActivePinia, createPinia } from 'pinia'
import { useOpinionStore } from '../../store/opinion'

// Mock API
vi.mock('../../api', () => ({
  opinionAPI: {
    getList: vi.fn(() => Promise.resolve({ items: [], total: 0 })),
    getById: vi.fn(() => Promise.resolve({ id: 1, title: 'Test' })),
    getMyOpinions: vi.fn(() => Promise.resolve({ items: [], total: 0 }))
  }
}))

describe('Opinion Store', () => {
  let store

  beforeEach(() => {
    setActivePinia(createPinia())
    store = useOpinionStore()
  })

  describe('State Initialization', () => {
    it('should initialize with default state', () => {
      expect(store.opinions).toEqual([])
      expect(store.currentOpinion).toBeNull()
      expect(store.total).toBe(0)
    })
  })

  describe('fetchMyOpinions', () => {
    it('should fetch user opinions with status filter', async () => {
      const { opinionAPI } = await import('../../api')
      const mockData = {
        items: [{ id: 1, title: 'My Opinion', status: 'approved' }],
        total: 1
      }
      opinionAPI.getMyOpinions.mockResolvedValueOnce(mockData)

      await store.fetchMyOpinions(1, 10, 'approved')

      expect(store.myOpinions).toEqual(mockData.items)
      expect(store.myOpinionsTotal).toBe(1)
      expect(opinionAPI.getMyOpinions).toHaveBeenCalledWith({
        page: 1,
        page_size: 10,
        status: 'approved'
      })
    })
  })
})
```

### 4.3.2 測試 Vue 組件（範例）

```javascript
import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import MyComponent from '@/components/MyComponent.vue'

describe('MyComponent', () => {
  it('renders properly', () => {
    const wrapper = mount(MyComponent, {
      props: { msg: 'Hello Vitest' }
    })
    expect(wrapper.text()).toContain('Hello Vitest')
  })

  it('emits event when button clicked', async () => {
    const wrapper = mount(MyComponent)
    await wrapper.find('button').trigger('click')
    expect(wrapper.emitted()).toHaveProperty('submit')
  })
})
```

## 4.4 運行測試

### 開發模式（Watch）

```bash
cd src/main/js/citizen-portal
npm run test

# Vitest 會監聽文件變化並自動重新運行測試
```

### CI 模式（單次運行）

```bash
npm run test -- --run
```

### 測試 UI 界面

```bash
npm run test:ui

# 開啟瀏覽器訪問 http://localhost:51204/__vitest__/
```

### 生成覆蓋率報告

```bash
npm run test:coverage

# 報告生成在 ./coverage/ 目錄
# 開啟 ./coverage/index.html 查看
```

## 4.5 測試覆蓋範圍

### 當前單元測試統計

| 模組 | 測試檔案 | 測試案例數 | 覆蓋率目標 | 狀態 |
|------|---------|-----------|-----------|------|
| Opinion Store | `store/opinion.spec.js` | 8 | 90%+ | ✅ 完成 |
| User Store | - | - | 90%+ | ⏳ 待開發 |
| API Utils | - | - | 80%+ | ⏳ 待開發 |

### 測試案例清單

**Opinion Store** (8 個測試):
1. ✅ State initialization
2. ✅ fetchOpinions - loading state
3. ✅ fetchOpinions - success
4. ✅ fetchMyOpinions - with status filter
5. ✅ bookmarkOpinion - update state
6. ✅ unbookmarkOpinion - remove state
7. ✅ fetchOpinionById - with vote status
8. ✅ fetchOpinionById - with bookmark status

---

# 伍、E2E 測試 (Playwright)

## 5.1 Playwright 簡介

**Playwright** 是由 Microsoft 開發的現代端對端測試框架。

### 主要特點
- 🌐 **跨瀏覽器** - Chromium, Firefox, WebKit
- 📱 **跨平台** - Windows, Linux, macOS
- 🎯 **自動等待** - 智能等待元素可見/可操作
- 📸 **截圖與錄影** - 失敗時自動捕捉
- 🔍 **強大選擇器** - CSS, XPath, Text, Role 等
- 🐛 **調試工具** - UI 模式、trace viewer

## 5.2 配置文件

### playwright.config.js

```javascript
import { defineConfig, devices } from '@playwright/test'

export default defineConfig({
  testDir: './e2e',                   // E2E 測試目錄
  maxFailures: process.env.CI ? 2 : undefined,
  workers: process.env.CI ? 1 : undefined,

  reporter: [
    ['html', { outputFolder: 'playwright-report' }],
    ['list']
  ],

  use: {
    baseURL: process.env.VITE_API_URL || 'http://localhost:5173',
    screenshot: 'only-on-failure',    // 失敗時截圖
    video: 'retain-on-failure',       // 失敗時保留錄影
    trace: 'on-first-retry'           // 重試時啟用追蹤
  },

  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] }
    }
  ],

  // 本地測試時自動啟動 dev server
  webServer: process.env.CI ? undefined : {
    command: 'npm run dev',
    url: 'http://localhost:5173',
    reuseExistingServer: !process.env.CI,
    timeout: 120 * 1000
  }
})
```

## 5.3 E2E 測試案例

### 5.3.1 投票切換測試

**文件**: `e2e/opinion-voting.spec.js`

**測試案例**:
- **TC-VOTE-001**: 用戶可以成功投票支持意見
- **TC-VOTE-002**: 用戶可以取消已投的支持票（切換）
- **TC-VOTE-003**: 用戶可以從支持切換到反對

**範例測試**:

```javascript
import { test, expect } from '@playwright/test'

test.describe('Opinion Voting Toggle', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/')
  })

  test('TC-VOTE-001: 用戶可以成功投票支持意見', async ({ page }) => {
    // 1. 登入
    await page.goto('/login')
    await page.fill('input[type="text"]', 'testuser')
    await page.fill('input[type="password"]', 'testpass123')
    await page.click('button[type="submit"]')

    // 2. 進入意見詳情頁
    await page.waitForURL('/opinions')
    await page.click('.opinion-card:first-child')

    // 3. 點擊支持按鈕
    const supportButton = page.locator('button:has-text("支持")')
    await supportButton.click()

    // 4. 驗證按鈕狀態變更
    await expect(supportButton).toContainText('已支持')
  })

  test('TC-VOTE-002: 用戶可以取消已投的支持票（切換）', async ({ page }) => {
    // ... 類似的測試邏輯
  })
})
```

### 5.3.2 審核限制測試

**文件**: `e2e/pending-opinion-restrictions.spec.js`

**測試案例**:
- **TC-RESTRICT-001**: 審核中意見應禁用投票按鈕
- **TC-RESTRICT-002**: 審核中意見應禁用留言功能
- **TC-RESTRICT-003**: 審核中意見可以正常查看內容
- **TC-RESTRICT-004**: 已通過意見應正常顯示所有互動功能

**關鍵測試邏輯**:

```javascript
test('TC-RESTRICT-001: 審核中意見應禁用投票按鈕', async ({ page }) => {
  // 登入並找到審核中的意見
  const pendingOpinion = page.locator('.opinion-card:has(.el-tag:has-text("待審核"))')

  if (await pendingOpinion.count() > 0) {
    await pendingOpinion.first().click()

    // 驗證警告訊息顯示
    await expect(page.locator('.el-alert:has-text("審核中")')).toBeVisible()

    // 驗證投票按鈕不存在
    const supportButton = page.locator('button:has-text("支持")')
    await expect(supportButton).toHaveCount(0)
  }
})
```

### 5.3.3 我的意見測試

**文件**: `e2e/my-opinions.spec.js`

**測試案例**:
- **TC-OPIN-018**: 個人資料頁面應顯示「我的意見」區塊
- **TC-OPIN-016**: 應能獲取並顯示用戶自己的意見列表
- **TC-OPIN-017**: 應能依狀態篩選意見（已通過/審核中）
- 提交新意見導航測試
- 查看意見詳情測試
- 分頁功能測試

**範例測試**:

```javascript
test('TC-OPIN-017: 應能依狀態篩選意見（已通過/審核中）', async ({ page }) => {
  await page.goto('/profile')
  await page.waitForTimeout(1000)

  // 默認顯示「已通過」標籤
  const approvedTab = page.locator('.el-tabs__item:has-text("已通過")')
  await expect(approvedTab).toHaveClass(/is-active/)

  // 切換到「審核中」標籤
  const pendingTab = page.locator('.el-tabs__item:has-text("審核中")')
  await pendingTab.click()
  await page.waitForTimeout(1000)

  // 驗證標籤狀態改變
  await expect(pendingTab).toHaveClass(/is-active/)
})
```

## 5.4 運行 E2E 測試

### 前置需求

1. **安裝 Playwright 瀏覽器**（首次運行）:
```bash
cd src/main/js/citizen-portal
npx playwright install
```

2. **啟動後端 API**（另一個終端）:
```bash
# 從專案根目錄
cd /root/project/citizenApp
python -m uvicorn src.main.python.core.app:app --reload
```

### 運行測試

**Headless 模式**（CI 使用）:
```bash
npm run test:e2e
```

**UI 模式**（開發推薦）:
```bash
npm run test:e2e:ui

# 開啟互動式 UI，可以：
# - 查看測試步驟
# - 時間旅行調試
# - 查看 DOM 快照
# - 檢查網絡請求
```

**Debug 模式**:
```bash
npx playwright test --debug

# 逐步執行測試，可以：
# - 暫停執行
# - 查看元素選擇器
# - 檢查頁面狀態
```

**運行特定測試**:
```bash
# 運行單一測試檔案
npx playwright test e2e/opinion-voting.spec.js

# 運行符合模式的測試
npx playwright test --grep "TC-VOTE"

# 運行特定瀏覽器
npx playwright test --project=chromium
```

### 查看測試報告

測試完成後，Playwright 會生成 HTML 報告：

```bash
# 自動開啟報告（測試失敗時）
npx playwright show-report

# 手動開啟報告
npx playwright show-report playwright-report
```

報告包含：
- ✅ 測試結果摘要
- 📸 失敗時的截圖
- 🎬 失敗時的錄影
- 🔍 Trace 檔案（可用於調試）

## 5.5 E2E 測試覆蓋範圍

### 測試統計

| 測試套件 | 測試檔案 | 測試案例數 | 狀態 |
|---------|---------|-----------|------|
| 投票切換 | `opinion-voting.spec.js` | 3 | ✅ 完成 |
| 審核限制 | `pending-opinion-restrictions.spec.js` | 4 | ✅ 完成 |
| 我的意見 | `my-opinions.spec.js` | 6 | ✅ 完成 |
| **總計** | **3 個檔案** | **13 個案例** | ✅ **完成** |

### 測試案例對照表

| 測試 ID | 測試案例名稱 | 優先級 | 狀態 |
|---------|-------------|--------|------|
| TC-VOTE-001 | 首次投票支持 | P0 | ✅ |
| TC-VOTE-002 | 取消支持投票（切換） | P1 | ✅ |
| TC-VOTE-003 | 從支持切換到反對 | P1 | ✅ |
| TC-RESTRICT-001 | 審核中意見禁用投票 | P0 | ✅ |
| TC-RESTRICT-002 | 審核中意見禁用留言 | P0 | ✅ |
| TC-RESTRICT-003 | 審核中意見可查看 | P1 | ✅ |
| TC-RESTRICT-004 | 已通過意見正常互動 | P1 | ✅ |
| TC-OPIN-016 | 獲取用戶意見列表 | P1 | ✅ |
| TC-OPIN-017 | 依狀態篩選意見 | P1 | ✅ |
| TC-OPIN-018 | 個人資料頁面顯示 | P1 | ✅ |
| - | 提交新意見導航 | P2 | ✅ |
| - | 查看意見詳情 | P2 | ✅ |
| - | 分頁功能測試 | P2 | ✅ |

---

# 陸、程式碼品質 (ESLint)

## 6.1 ESLint 配置

### .eslintrc.cjs

```javascript
module.exports = {
  root: true,
  env: {
    browser: true,
    es2021: true,
    node: true
  },
  extends: [
    'eslint:recommended',           // ESLint 推薦規則
    'plugin:vue/vue3-recommended'   // Vue 3 推薦規則
  ],
  parserOptions: {
    ecmaVersion: 'latest',
    sourceType: 'module'
  },
  plugins: ['vue'],
  rules: {
    // Vue 相關規則
    'vue/multi-word-component-names': 'off',
    'vue/no-v-html': 'warn',
    'vue/require-default-prop': 'off',
    'vue/require-explicit-emits': 'warn',

    // JavaScript 規則
    'no-console': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-debugger': process.env.NODE_ENV === 'production' ? 'warn' : 'off',
    'no-unused-vars': ['warn', {
      argsIgnorePattern: '^_',
      varsIgnorePattern: '^_'
    }],

    // 程式碼風格
    'indent': ['error', 2, { SwitchCase: 1 }],
    'quotes': ['error', 'single', { avoidEscape: true }],
    'semi': ['error', 'never'],
    'comma-dangle': ['error', 'never'],
    'object-curly-spacing': ['error', 'always'],
    'space-before-function-paren': ['error', 'never']
  }
}
```

## 6.2 運行 ESLint

### 檢查程式碼

```bash
npm run lint

# 輸出範例：
# /src/views/Profile/index.vue
#   42:7  warning  'fetchData' is defined but never used  no-unused-vars
#
# ✖ 1 problem (0 errors, 1 warning)
```

### 自動修復

```bash
npm run lint:fix

# 自動修復可修復的問題（格式、引號等）
```

### IDE 整合

**VS Code** 推薦安裝：
- ESLint 擴展套件
- Volar (Vue 3 支援)

設置 `.vscode/settings.json`:
```json
{
  "editor.codeActionsOnSave": {
    "source.fixAll.eslint": true
  },
  "eslint.validate": [
    "javascript",
    "javascriptreact",
    "vue"
  ]
}
```

---

# 柒、實用指南

## 7.1 本地開發流程

### 完整開發流程

```bash
# 1. 安裝依賴（首次或依賴更新時）
cd src/main/js/citizen-portal
npm install

# 2. 啟動開發伺服器
npm run dev
# 訪問 http://localhost:5173

# 3. 程式碼檢查（開發過程中）
npm run lint

# 4. 運行單元測試（watch 模式）
npm run test

# 5. 提交前檢查
npm run lint:fix          # 修復程式碼問題
npm run test -- --run     # 運行所有測試
npm run build             # 確保可以構建成功
```

## 7.2 測試編寫最佳實踐

### 單元測試

**✅ 好的實踐**:
```javascript
// 測試命名清晰
it('should fetch opinions and update state when called', async () => {
  // Arrange (準備)
  const mockData = { items: [{ id: 1 }], total: 1 }
  opinionAPI.getList.mockResolvedValueOnce(mockData)

  // Act (執行)
  await store.fetchOpinions()

  // Assert (驗證)
  expect(store.opinions).toEqual(mockData.items)
})
```

**❌ 避免**:
```javascript
// 測試過於簡單，沒有實際意義
it('works', () => {
  expect(true).toBe(true)
})

// 測試過於複雜，測試多個功能
it('test everything', () => {
  // 100 行測試程式碼...
})
```

### E2E 測試

**✅ 好的實踐**:
```javascript
// 使用 Page Object Pattern
const loginPage = {
  goto: (page) => page.goto('/login'),
  login: async (page, username, password) => {
    await page.fill('input[type="text"]', username)
    await page.fill('input[type="password"]', password)
    await page.click('button[type="submit"]')
  }
}

test('user can login', async ({ page }) => {
  await loginPage.goto(page)
  await loginPage.login(page, 'testuser', 'testpass')
  await expect(page).toHaveURL('/opinions')
})
```

**❌ 避免**:
```javascript
// 硬編碼延遲
await page.waitForTimeout(5000)  // ❌ 不可靠

// 應該使用智能等待
await page.waitForSelector('.opinion-card')  // ✅ 正確
```

## 7.3 CI/CD 整合

### 觸發測試

當你推送程式碼到 `main`、`develop` 或 `claude` 分支時，CI/CD 會自動運行：

```bash
git add .
git commit -m "feat: add new feature"
git push origin claude

# GitHub Actions 自動執行：
# 1. Lint 檢查
# 2. 單元測試
# 3. 構建
# 4. E2E 測試（僅 push）
```

### 查看 CI 狀態

1. 進入 GitHub Repository
2. 點擊 **Actions** 標籤
3. 查看最新的 workflow run
4. 點擊任何 job 查看詳細日誌

### CI 失敗處理

如果 CI 失敗：

1. **查看失敗的 Job**
   - 點擊紅色的 ❌ 標記
   - 展開失敗的步驟

2. **本地重現問題**
   ```bash
   # 運行相同的命令
   npm run lint
   npm run test -- --run
   npm run build
   ```

3. **修復並重新推送**
   ```bash
   npm run lint:fix      # 修復 lint 問題
   # 修復測試或程式碼
   git add .
   git commit -m "fix: resolve CI issues"
   git push
   ```

## 7.4 測試資料準備

### 單元測試 Mock 資料

**建議**: 在 `src/test/fixtures/` 目錄建立 mock 資料

```javascript
// src/test/fixtures/opinions.js
export const mockOpinions = [
  {
    id: 1,
    title: '測試意見 1',
    content: '這是測試內容',
    status: 'approved',
    upvotes: 10,
    downvotes: 2
  },
  {
    id: 2,
    title: '測試意見 2',
    content: '這是測試內容 2',
    status: 'pending',
    upvotes: 0,
    downvotes: 0
  }
]
```

在測試中使用：
```javascript
import { mockOpinions } from '../fixtures/opinions'

it('should display opinions', () => {
  opinionAPI.getList.mockResolvedValueOnce({
    items: mockOpinions,
    total: 2
  })
  // ...
})
```

### E2E 測試資料

**建議**: 使用測試帳號和測試資料庫

```javascript
// e2e/fixtures/test-users.js
export const testUsers = {
  admin: {
    username: 'admin_test',
    password: 'admin_pass_123'
  },
  citizen: {
    username: 'citizen_test',
    password: 'citizen_pass_123'
  }
}
```

---

# 捌、故障排查

## 8.1 常見問題

### 問題 1: Vitest 無法找到模組

**症狀**:
```
Error: Cannot find module '@/store/opinion'
```

**解決方案**:
檢查 `vitest.config.js` 的 alias 配置：
```javascript
resolve: {
  alias: {
    '@': fileURLToPath(new URL('./src', import.meta.url))
  }
}
```

### 問題 2: Playwright 瀏覽器未安裝

**症狀**:
```
browserType.launch: Executable doesn't exist
```

**解決方案**:
```bash
npx playwright install
# 或安裝特定瀏覽器
npx playwright install chromium
```

### 問題 3: E2E 測試超時

**症狀**:
```
Test timeout of 30000ms exceeded
```

**解決方案**:
1. 增加測試超時時間：
```javascript
test('slow test', async ({ page }) => {
  test.setTimeout(60000)  // 60 秒
  // ...
})
```

2. 檢查後端 API 是否運行
3. 使用 `page.waitForSelector()` 替代 `waitForTimeout()`

### 問題 4: ESLint 報告大量錯誤

**解決方案**:
```bash
# 自動修復所有可修復的問題
npm run lint:fix

# 如果仍有問題，逐一檢查並修復
npm run lint
```

### 問題 5: CI 本地通過但遠端失敗

**可能原因**:
1. **環境變數不同**: 檢查 `.env` 檔案
2. **依賴版本不同**: 使用 `npm ci` 而非 `npm install`
3. **檔案權限問題**: 確保在 Linux/Mac 環境測試

**調試方法**:
```bash
# 模擬 CI 環境
CI=true npm run test -- --run
CI=true npm run build
```

## 8.2 調試技巧

### Vitest 調試

**使用 Vitest UI**:
```bash
npm run test:ui
```
- 查看測試執行時間線
- 檢查變數狀態
- 重新運行失敗的測試

**使用 console.log**:
```javascript
it('debug test', () => {
  console.log('Store state:', store.$state)
  // ...
})
```

### Playwright 調試

**使用 UI 模式** (推薦):
```bash
npm run test:e2e:ui
```
- 查看每個步驟的 DOM 快照
- 檢查網絡請求
- 時間旅行調試

**使用 Debug 模式**:
```bash
npx playwright test --debug
```
- 逐步執行測試
- 在瀏覽器中即時操作
- 查看選擇器匹配的元素

**使用 Trace Viewer**:
```bash
# 啟用 trace
npx playwright test --trace on

# 查看 trace
npx playwright show-trace trace.zip
```

### ESLint 調試

**查看詳細規則資訊**:
```bash
npx eslint src/views/Profile/index.vue --debug
```

**查看特定規則**:
```bash
npx eslint --print-config src/views/Profile/index.vue
```

## 8.3 效能優化

### Vitest 效能優化

```javascript
// vitest.config.js
export default defineConfig({
  test: {
    // 使用多執行緒
    threads: true,
    // 使用執行緒池
    poolOptions: {
      threads: {
        singleThread: false
      }
    },
    // 僅測試變更的檔案
    changed: true
  }
})
```

### Playwright 效能優化

```javascript
// playwright.config.js
export default defineConfig({
  // 平行執行測試
  workers: process.env.CI ? 1 : 4,

  // 重用瀏覽器 context
  use: {
    // 禁用不必要的功能
    video: process.env.CI ? 'off' : 'retain-on-failure',
    screenshot: 'only-on-failure'
  }
})
```

---

# 附錄

## A. 測試腳本速查表

| 命令 | 用途 | 何時使用 |
|------|------|---------|
| `npm run lint` | ESLint 檢查 | 提交前 |
| `npm run lint:fix` | 自動修復 lint 問題 | 批量修復格式問題 |
| `npm run test` | 運行單元測試 (watch) | 開發過程中 |
| `npm run test -- --run` | 運行單元測試 (單次) | CI/提交前 |
| `npm run test:ui` | Vitest UI 界面 | 調試測試 |
| `npm run test:coverage` | 生成覆蓋率報告 | 檢查測試覆蓋率 |
| `npm run test:e2e` | 運行 E2E 測試 | 提交前/發布前 |
| `npm run test:e2e:ui` | Playwright UI 模式 | 調試 E2E 測試 |
| `npm run build` | 構建生產版本 | 提交前確認 |

## B. 資源連結

### 官方文檔
- [Vitest 官方文檔](https://vitest.dev/)
- [Playwright 官方文檔](https://playwright.dev/)
- [Vue Test Utils](https://test-utils.vuejs.org/)
- [ESLint 官方文檔](https://eslint.org/)
- [GitHub Actions 文檔](https://docs.github.com/en/actions)

### 教學資源
- [Vitest 快速入門](https://vitest.dev/guide/)
- [Playwright 教學](https://playwright.dev/docs/intro)
- [Vue 3 測試指南](https://vuejs.org/guide/scaling-up/testing.html)

## C. 測試覆蓋率目標

| 模組類型 | 目標覆蓋率 | 當前狀態 |
|---------|-----------|---------|
| Store (Pinia) | 90%+ | 🟢 已達成 |
| API Utils | 80%+ | 🟡 進行中 |
| Components | 70%+ | 🔴 待開發 |
| Views | 60%+ | 🔴 待開發 |
| **整體目標** | **80%+** | 🟡 **進行中** |

---

<div align="center">

**📝 文件結束**

**citizenApp - Citizen Portal Testing & CI/CD Guide**
Version 1.0 | 2025-12-12

[🏠 返回測試文檔中心](README.md)

</div>
