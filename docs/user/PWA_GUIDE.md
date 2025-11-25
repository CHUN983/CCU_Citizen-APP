# 📱 PWA (Progressive Web App) 使用指南

## 📖 什麼是 PWA？

PWA (漸進式網頁應用程式) 是一種可以像原生 APP 一樣使用的網頁應用：
- ✅ 可安裝到手機桌面
- ✅ 支援離線瀏覽
- ✅ 可接收推送通知
- ✅ 快速載入
- ✅ 無需透過應用商店下載

---

## 🚀 如何安裝市民平台 APP

### 📱 Android 手機 (Chrome/Edge)

1. 使用 Chrome 或 Edge 瀏覽器開啟網站：`http://localhost:5174`
2. 等待 3 秒，底部會出現「安裝市民平台 APP」提示橫幅
3. 點擊「安裝」按鈕
4. APP 圖示會自動出現在桌面

**手動安裝方式：**
1. 點擊瀏覽器右上角的「...」選單
2. 選擇「安裝應用程式」或「加入主畫面」
3. 確認安裝

### 🍎 iPhone/iPad (Safari)

1. 使用 Safari 瀏覽器開啟網站：`http://localhost:5174`
2. 點擊底部的「分享」按鈕 (方框加向上箭頭圖示)
3. 向下滾動，選擇「加入主畫面」
4. 編輯 APP 名稱（可選）
5. 點擊「加入」
6. APP 圖示會出現在主畫面

**注意：** iOS 的 PWA 功能較受限，但仍可正常使用

### 💻 桌面電腦 (Chrome/Edge)

1. 使用 Chrome 或 Edge 瀏覽器開啟網站
2. 地址欄右側會出現「安裝」圖示 ⊕
3. 點擊圖示，確認安裝
4. APP 會像桌面應用一樣開啟

---

## ✨ PWA 功能特色

### 1️⃣ 離線瀏覽

- **已瀏覽過的意見** - 自動快取，離線也能查看
- **API 快取** - 網路中斷時使用快取數據
- **自動同步** - 網路恢復後自動更新

### 2️⃣ 快速載入

- **Service Worker** - 智能快取策略
- **預快取** - 重要資源預先載入
- **漸進增強** - 逐步載入內容

### 3️⃣ 推送通知 (即將推出)

- 意見審核通知
- 回覆提醒
- 投票結果更新

### 4️⃣ 原生體驗

- 全螢幕顯示（無瀏覽器地址欄）
- 桌面圖示
- 啟動畫面
- 與其他 APP 一樣的切換體驗

---

## 🔧 開發者指南

### 檔案結構

```
src/main/js/citizen-portal/
├── public/
│   ├── manifest.json          # PWA 配置清單
│   ├── sw.js                  # Service Worker
│   └── icons/                 # APP 圖示
│       └── README.md          # 圖示生成說明
├── src/
│   ├── main.js               # Service Worker 註冊
│   ├── App.vue               # PWA Install Prompt 整合
│   └── components/
│       └── PWAInstallPrompt.vue  # 安裝提示組件
└── index.html                # PWA Meta Tags
```

### Service Worker 快取策略

#### 網路優先 (Network First)
- **用途：** API 請求
- **行為：** 優先從網路載入，失敗時使用快取
- **適用：** `/api/*` 路徑

#### 快取優先 (Cache First)
- **用途：** 靜態資源 (JS, CSS, 圖片)
- **行為：** 優先使用快取，沒有時才從網路載入
- **適用：** 所有靜態檔案

### 測試 PWA 功能

#### 1. Lighthouse 測試

```bash
# Chrome DevTools
1. 按 F12 開啟開發者工具
2. 切換到「Lighthouse」分頁
3. 勾選「Progressive Web App」
4. 點擊「Analyze page load」
5. 查看 PWA 評分和建議
```

#### 2. Service Worker 檢查

```bash
# Chrome DevTools
1. 按 F12 開啟開發者工具
2. 切換到「Application」分頁
3. 左側選單點擊「Service Workers」
4. 查看 Service Worker 狀態
```

#### 3. Manifest 檢查

```bash
# Chrome DevTools
1. 按 F12 開啟開發者工具
2. 切換到「Application」分頁
3. 左側選單點擊「Manifest」
4. 查看 manifest.json 配置
```

#### 4. 離線測試

```bash
# Chrome DevTools
1. 按 F12 開啟開發者工具
2. 切換到「Network」分頁
3. 勾選「Offline」模擬離線狀態
4. 重新整理頁面，測試離線功能
```

---

## 🎨 自訂 APP 圖示

### 準備圖示

1. 設計一個 512x512 像素的 PNG 圖示
2. 使用線上工具生成各種尺寸：
   - [PWA Builder](https://www.pwabuilder.com/imageGenerator)
   - [Maskable.app](https://maskable.app/editor)

### 替換圖示

```bash
# 將生成的圖示複製到以下目錄：
src/main/js/citizen-portal/public/icons/

# 需要的尺寸：
icon-72x72.png
icon-96x96.png
icon-128x128.png
icon-144x144.png
icon-152x152.png
icon-192x192.png
icon-384x384.png
icon-512x512.png
```

---

## 🐛 常見問題

### Q1: 安裝提示沒有出現？

**原因：**
- 瀏覽器不支援 PWA
- 已經安裝過
- 已經點擊過「稍後再說」（7天內不再顯示）

**解決方法：**
```javascript
// 清除 localStorage 重置提示
localStorage.removeItem('pwa-install-dismissed');
localStorage.removeItem('pwa-installed');
```

### Q2: Service Worker 沒有註冊？

**檢查：**
1. 確認在 HTTPS 或 localhost 環境（Service Worker 要求）
2. 查看瀏覽器控制台是否有錯誤訊息
3. 確認 `sw.js` 檔案存在於 `public/` 目錄

### Q3: 離線功能不起作用？

**排查步驟：**
1. 確認 Service Worker 已成功註冊
2. 檢查快取策略是否正確
3. 先在線上瀏覽一次（建立快取）
4. 再測試離線功能

### Q4: iOS 安裝後沒有推送通知？

**說明：**
- iOS 的 PWA 目前不支援推送通知
- 這是 Apple 的限制，不是程式問題
- 可使用網頁版接收通知

---

## 📊 PWA 評分標準

使用 Lighthouse 測試時，會評估以下項目：

### ✅ 必須通過
- [ ] 註冊 Service Worker
- [ ] 離線時可回應 200 狀態
- [ ] 提供 manifest.json
- [ ] 設定 viewport meta tag
- [ ] 使用 HTTPS (生產環境)

### 🎯 建議達成
- [ ] 快取策略合理
- [ ] 圖示完整（各種尺寸）
- [ ] Theme color 設定
- [ ] 提供離線頁面
- [ ] 載入時間 < 3 秒

---

## 🔄 更新 PWA

### 自動更新

Service Worker 會每 60 秒檢查一次更新：

```javascript
// main.js 中已設定
setInterval(() => {
  registration.update()
}, 60000)
```

### 手動強制更新

```bash
# Chrome DevTools
1. Application > Service Workers
2. 點擊「Update」按鈕
3. 勾選「Update on reload」
4. 重新整理頁面
```

---

## 🚀 生產環境部署

### 1. Build 前端

```bash
cd src/main/js/citizen-portal
npm run build
```

### 2. 確認檔案

Build 後的 `dist/` 目錄應包含：
- `manifest.json`
- `sw.js`
- `icons/` 目錄
- HTML/JS/CSS 檔案

### 3. 部署到伺服器

- 使用 HTTPS（PWA 要求）
- 設定正確的 MIME types
- 啟用 Gzip/Brotli 壓縮

### 4. 測試

- 使用 Lighthouse 測試 PWA 評分
- 在多種裝置測試安裝功能
- 驗證離線功能正常

---

## 📚 相關資源

### 官方文檔
- [PWA 介紹](https://web.dev/progressive-web-apps/)
- [Service Worker API](https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API)
- [Web App Manifest](https://web.dev/add-manifest/)

### 工具
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)
- [PWA Builder](https://www.pwabuilder.com/)
- [Workbox](https://developers.google.com/web/tools/workbox)

### 範例
- [Google PWA Examples](https://developers.google.com/web/showcase)

---

**✅ PWA 功能已完成！您現在可以測試安裝和離線功能了。**

**📱 下一步：添加自訂圖示，讓 APP 更有辨識度！**
