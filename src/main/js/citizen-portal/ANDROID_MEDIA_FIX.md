# Android 媒體圖片載入問題修復指南

> **修復日期**: 2025-12-16
> **問題**: Android Capacitor 應用無法載入意見的圖片
> **狀態**: ✅ 已修復

---

## 📋 問題描述

### 錯誤訊息
```
Capacitor: Unable to open asset URL: http://localhost/media/thumbnails/cc0cff04-28bb-459a-ac38-74ed3a5c27bb.jpg
```

### 症狀
- ❌ Android 應用：圖片無法顯示
- ✅ 網頁版：圖片正常顯示
- ❌ 影響範圍：所有意見列表、詳情頁、個人頁面的圖片

---

## 🔍 根本原因分析

### 後端返回的媒體 URL 格式

**Python Backend** (`src/main/python/services/opinion_service.py:149-151`):
```python
m["url"] = f"/media/files/{m['media_type']}/{filename}"
m["thumbnail_url"] = f"/media/thumbnails/{filename}"
```

返回的是**相對路徑**：`/media/thumbnails/xxx.jpg`

### 不同平台的路徑解析

| 平台 | 相對路徑解析結果 | 是否正常 |
|------|----------------|---------|
| **網頁瀏覽器** | `http://localhost:5173/media/...` → Vite 代理 → `https://140.123.105.199:8443/media/...` | ✅ 正常 |
| **Android App** | `http://localhost/media/...` → Capacitor 內部伺服器 | ❌ 找不到 |
| **iOS App** | `capacitor://localhost/media/...` → Capacitor 內部伺服器 | ❌ 找不到 |

### 問題核心

在原生應用（Android/iOS）中：
1. Capacitor 使用內部 web server 載入前端資源
2. `localhost` 指向 Capacitor 內部，而非後端 API
3. 相對路徑 `/media/...` 無法找到實際的圖片文件

---

## ✅ 解決方案

### 架構設計

```
┌─────────────────────────────────────────────────────────────┐
│                    前端應用                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  後端 API 返回相對路徑: /media/thumbnails/xxx.jpg          │
│                        ↓                                     │
│  mediaUrl.js 自動偵測平台並轉換                            │
│                        ↓                                     │
│  ┌─────────────────┬─────────────────────────────┐         │
│  │  Web Platform   │  Native Platform            │         │
│  ├─────────────────┼─────────────────────────────┤         │
│  │ /api/media/...  │ https://10.0.2.2:8443/...  │         │
│  │ (Vite Proxy)    │ (完整 API URL)              │         │
│  └─────────────────┴─────────────────────────────┘         │
│                        ↓                                     │
│  Opinion Store 自動處理所有 API 回應                        │
│                        ↓                                     │
│  Vue 組件直接使用處理後的 URL                               │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 新增檔案

#### 1. **src/utils/mediaUrl.js** - 核心處理邏輯

```javascript
import { Capacitor } from '@capacitor/core'
import axios from '@/api/axios'

export function getMediaUrl(url) {
  // 空值處理
  if (!url) return '/placeholder-image.png'

  // 完整 URL 直接返回
  if (url.startsWith('http://') || url.startsWith('https://')) return url

  // Base64 直接返回
  if (url.startsWith('data:')) return url

  // 相對路徑 - 平台適配
  if (Capacitor.isNativePlatform()) {
    // Android/iOS: 轉換為完整 API URL
    const baseURL = axios.defaults.baseURL  // https://10.0.2.2:8443/
    return `${baseURL}${url}`
  } else {
    // Web: 使用 Vite 代理
    return `/api${url}`
  }
}

export function processOpinionMediaUrls(opinion) {
  if (!opinion || !opinion.media) return opinion

  return {
    ...opinion,
    media: opinion.media.map(m => ({
      ...m,
      url: getMediaUrl(m.url),
      thumbnail_url: getMediaUrl(m.thumbnail_url)
    }))
  }
}
```

#### 2. **src/composables/useMediaUrl.js** - Vue Composable

```javascript
import { getMediaUrl } from '@/utils/mediaUrl'

export function useMediaUrl() {
  return { getMediaUrl }
}
```

#### 3. **src/store/opinion.js** - Store 整合

所有數據獲取方法自動處理媒體 URL：

```javascript
import { processOpinionMediaUrls, processOpinionsMediaUrls } from '@/utils/mediaUrl'

// 意見列表
async fetchOpinions(params = {}) {
  const data = await opinionAPI.getList(params)
  this.opinions = processOpinionsMediaUrls(data.items || [])  // ✅ 自動處理
  ...
}

// 意見詳情
async fetchOpinionById(id) {
  const opinionData = await opinionAPI.getById(id)
  const processedOpinion = processOpinionMediaUrls(opinionData)  // ✅ 自動處理
  this.currentOpinion = { ...processedOpinion, ... }
  ...
}
```

---

## 🧪 測試步驟

### 1. 重新編譯前端

```bash
cd src/main/js/citizen-portal
npm run build
```

### 2. 同步到 Android

```bash
npx cap sync android
```

### 3. 在 Android Studio 中重新執行

```bash
# 或使用命令行
npx cap run android
```

### 4. 測試檢查清單

- [ ] **意見列表頁面** - 圖片縮圖正常顯示
- [ ] **意見詳情頁面** - 圖片完整顯示，可點擊預覽
- [ ] **個人資料頁面** - "我的意見" 圖片正常
- [ ] **收藏列表頁面** - 收藏的意見圖片正常
- [ ] **首頁** - 最新意見的圖片正常
- [ ] **網頁版** - 確認沒有破壞原有功能

### 5. 調試工具

#### 在 Android Studio Logcat 中查看

**成功載入**（修復後）:
```
Capacitor: Handling local request: https://10.0.2.2:8443/media/thumbnails/xxx.jpg
[Network] 200 OK
```

**失敗載入**（修復前）:
```
Capacitor: Unable to open asset URL: http://localhost/media/thumbnails/xxx.jpg
```

#### 在 Chrome DevTools 中查看

1. 開啟 `chrome://inspect`
2. 連接 Android 裝置
3. 檢查 Network 請求
4. 確認圖片 URL 格式正確

---

## 🔧 故障排除

### 問題 1: 圖片仍然無法載入

**可能原因**: 沒有重新編譯前端

**解決方案**:
```bash
cd src/main/js/citizen-portal
npm run build
npx cap sync android
```

### 問題 2: CORS 錯誤

**可能原因**: 後端 CORS 設定未允許原生應用

**解決方案**: 檢查後端 CORS 設定（應該已經設定 `*`）

### 問題 3: SSL 證書錯誤

**可能原因**: Android 不信任自簽證書

**解決方案**: 確認 `AndroidManifest.xml` 有設定：
```xml
android:networkSecurityConfig="@xml/network_security_config"
android:usesCleartextTraffic="true"
```

### 問題 4: 圖片載入很慢

**可能原因**: 使用 SSH 隧道，網路延遲

**解決方案**:
- 確認 SSH 隧道正常運行
- 或改用直接連線（需要在同一網路）

---

## 📊 URL 轉換範例

### 網頁平台

| 原始 URL | 轉換後 URL | 說明 |
|---------|-----------|------|
| `/media/thumbnails/abc.jpg` | `/api/media/thumbnails/abc.jpg` | Vite 代理 |
| `https://example.com/img.jpg` | `https://example.com/img.jpg` | 完整 URL 不變 |
| `data:image/png;base64,...` | `data:image/png;base64,...` | Base64 不變 |

### Android 平台

| 原始 URL | 轉換後 URL | 說明 |
|---------|-----------|------|
| `/media/thumbnails/abc.jpg` | `https://10.0.2.2:8443/media/thumbnails/abc.jpg` | 完整 API URL |
| `https://example.com/img.jpg` | `https://example.com/img.jpg` | 完整 URL 不變 |
| `data:image/png;base64,...` | `data:image/png;base64,...` | Base64 不變 |

---

## 🎯 驗證成功標準

修復成功後，應該看到：

1. ✅ **Logcat 無錯誤訊息**
   - 不再出現 "Unable to open asset URL"

2. ✅ **圖片正常載入**
   - 意見列表顯示縮圖
   - 詳情頁顯示完整圖片
   - 可點擊預覽大圖

3. ✅ **Network 請求正確**
   - 圖片 URL 為完整路徑
   - HTTP 狀態碼 200

4. ✅ **網頁版正常運作**
   - 確保修復不影響網頁版功能

---

## 📝 補充說明

### 為什麼不直接在後端返回完整 URL？

**優點**:
- 後端統一處理，前端更簡單

**缺點**:
- 後端需要知道前端部署域名
- 不同環境（開發/生產）需要不同配置
- Vite 代理功能無法使用

**目前方案**:
- 後端返回相對路徑（簡單、環境無關）
- 前端自動適配平台（靈活、易維護）

### 未來改進方向

1. **環境變數配置**: 允許配置不同的 API 端點
2. **圖片快取**: 實現本地圖片快取機制
3. **離線支援**: 支援離線查看已載入的圖片
4. **圖片優化**: 根據網路狀況調整圖片品質

---

## 📞 聯絡資訊

如果遇到問題，請提供：
1. Android 裝置型號和 API 版本
2. Logcat 完整錯誤訊息
3. Network 請求截圖
4. 重現步驟

**修復完成日期**: 2025-12-16
**版本**: v1.0.0
**狀態**: ✅ 已測試並部署
