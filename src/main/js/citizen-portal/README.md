# 🏙️ Citizen Portal - 市民意見前端

市民參與城市規劃系統的跨平台應用 (Web / iOS / Android)

## 📱 行動 APP 支援 (NEW!)

**現在支援 Android 和 iOS APP!**

基於 **Capacitor 7** 技術,一份程式碼部署到三個平台:
- 🌐 **Web** - 瀏覽器版本
- 🤖 **Android** - Android APP
- 🍎 **iOS** - iOS APP

### 📚 快速開始

| 文件 | 說明 |
|------|------|
| [🚀 快速開始](./QUICK_START.md) | 5分鐘上手 APP 開發 |
| [📘 完整開發指南](./MOBILE_APP_GUIDE.md) | 詳細技術文件 |
| [📋 專案總結](../../MOBILE_DEVELOPMENT_SUMMARY.md) | 方案說明與資源 |
| [📐 架構文件](../../docs/MOBILE_ARCHITECTURE.md) | 技術架構詳解 |

### ⚡ 立即體驗

```bash
# Android APP
npm run android

# iOS APP (需要 macOS)
npm run ios

# Web 版本
npm run dev
```

## ✨ 功能特色

### 已實現功能
- ✅ 用戶認證 (註冊/登入)
- ✅ 意見列表瀏覽 (含篩選、搜尋、分頁)
- ✅ 意見詳細頁面
- ✅ 意見提交功能
- ✅ 投票功能 (支持/反對)
- ✅ 留言討論功能
- ✅ 意見收藏功能
- ✅ 個人資料頁面
- ✅ 響應式設計 (支援手機/平板/桌面)
- ✅ **📸 相機拍照與相簿選擇** (NEW!)
- ✅ **📱 跨平台 APP 支援** (NEW!)
- ✅ **🖼️ 圖片壓縮與上傳** (NEW!)

## 🛠️ 技術棧

### 核心框架
- **Vue 3.5.22** - 漸進式JavaScript框架
- **Vite 7.1.7** - 極速構建工具
- **Vue Router 4.6.3** - 官方路由
- **Pinia 3.0.3** - 狀態管理
- **Element Plus 2.11.5** - UI組件庫
- **Axios 1.12.2** - HTTP客戶端

### 跨平台支援
- **Capacitor 7.4.4** - 原生橋接框架
- **@capacitor/camera** - 相機功能
- **@capacitor/filesystem** - 檔案系統
- **@capacitor/splash-screen** - 啟動畫面

## 🚀 快速開始

### 前提條件

- Node.js 16+
- npm 或 yarn
- 後端 API 運行在 http://localhost:8000

### 安裝依賴

```bash
cd /root/project/citizenApp/src/main/js/citizen-portal
npm install
```

### Web 開發

```bash
# 啟動開發服務器
npm run dev

# 應用將運行在: http://localhost:5173
```

### 行動 APP 開發

```bash
# Android APP (需要 Android Studio)
npm run android

# iOS APP (需要 macOS 和 Xcode)
npm run ios

# 同步 Web 變更到原生平台
npm run cap:sync
```

### 構建生產版本

```bash
# Web 版本
npm run build

# 預覽構建
npm run preview
```

## 📁 專案結構

```
citizen-portal/
├── 📱 android/            # Android 原生專案 (Capacitor)
├── 🍎 ios/                # iOS 原生專案 (Capacitor)
├── 🌐 src/                # Vue 3 程式碼
│   ├── api/              # API 請求封裝
│   │   ├── axios.js      # Axios 配置與攔截器
│   │   └── index.js      # API 端點定義
│   ├── components/       # 可重用組件
│   │   ├── Header.vue    # 頂部導航
│   │   ├── Footer.vue    # 底部資訊
│   │   └── CameraUpload.vue  # 📸 相機上傳元件 (NEW!)
│   ├── utils/            # 工具函式
│   │   └── camera.js     # 📷 相機工具 (NEW!)
│   ├── router/           # 路由配置
│   │   └── index.js      # 路由定義
│   ├── store/            # Pinia 狀態管理
│   │   ├── user.js       # 用戶狀態
│   │   └── opinion.js    # 意見狀態
│   ├── views/            # 頁面組件
│   │   ├── Home/         # 首頁
│   │   ├── Auth/         # 登入/註冊
│   │   ├── Opinions/     # 意見相關頁面
│   │   ├── Profile/      # 個人資料
│   │   └── Example/
│   │       └── CameraDemo.vue  # 📸 相機示範 (NEW!)
│   ├── App.vue           # 根組件
│   └── main.js           # 入口文件
├── 📦 dist/               # 建置輸出
├── 📄 public/             # 靜態資源
├── ⚙️ capacitor.config.json  # Capacitor 設定
├── 📘 MOBILE_APP_GUIDE.md    # 行動 APP 開發指南
├── 🚀 QUICK_START.md         # 快速開始指南
├── index.html            # HTML 模板
├── vite.config.js        # Vite 配置
└── package.json          # 依賴配置
```

## 🎯 主要頁面

### 首頁 (`/`)
- 功能介紹
- 最新意見列表
- 快速註冊/登入入口

### 意見列表 (`/opinions`)
- 完整意見列表
- 多維度篩選 (分類、狀態、關鍵字)
- 排序功能 (最新、最多投票、最多留言)
- 分頁瀏覽

### 意見詳情 (`/opinions/:id`)
- 完整意見內容
- 投票功能
- 留言討論
- 收藏功能

### 提交意見 (`/opinions/create`)
- 意見提交表單
- 分類選擇
- 標籤系統
- 位置標記

### 用戶認證
- 登入頁面 (`/login`)
- 註冊頁面 (`/register`)

### 個人資料 (`/profile`)
- 用戶資訊
- 我的意見 (開發中)

## 🔐 認證機制

- 基於 JWT Token 的認證
- Token 儲存在 LocalStorage
- 自動在請求頭添加 Authorization
- Token 過期自動導向登入頁

## 🎨 UI 設計

- 使用 Element Plus 組件庫
- 簡潔現代的設計風格
- 完整的響應式支援
- 友善的交互反饋

## 📡 API 整合

### API Base URL
開發環境: `/api` (代理到 `http://localhost:8000`)

### 主要 API 端點

- `POST /auth/login` - 用戶登入
- `POST /auth/register` - 用戶註冊
- `GET /auth/profile` - 獲取用戶資料
- `GET /opinions` - 獲取意見列表
- `GET /opinions/:id` - 獲取意見詳情
- `POST /opinions` - 提交新意見
- `POST /opinions/:id/vote` - 投票
- `POST /opinions/:id/bookmark` - 收藏
- `GET /opinions/:id/comments` - 獲取留言
- `POST /opinions/:id/comments` - 發表留言
- `GET /categories` - 獲取分類列表

## 🧪 開發注意事項

### 環境變數
Vite 配置中已設定 API 代理，無需額外配置

### 路由守衛
- 部分路由需要登入才能訪問
- 未登入訪問受保護路由會重定向到登入頁
- 登入後自動返回原頁面

### 狀態管理
- 用戶狀態持久化到 LocalStorage
- 頁面刷新不會丟失登入狀態

## 📝 開發計畫

### Phase 1: 基礎功能 ✅
- [x] Capacitor 整合
- [x] 相機與圖片上傳
- [x] Android/iOS 平台支援
- [x] 基礎文件與範例

### Phase 2: 功能擴充
- [ ] 我的意見管理
- [ ] 意見編輯功能
- [ ] GPS 定位功能
- [ ] 推播通知系統
- [ ] 離線資料同步

### Phase 3: 體驗優化
- [ ] 通知中心
- [ ] 多語言支援
- [ ] 暗黑模式
- [ ] 效能優化
- [ ] 自動化測試

## 🐛 常見問題

### 無法連接到後端 API
確保後端服務正在運行:
```bash
cd /root/project/citizenApp
source venv/bin/activate
python -m uvicorn src.main.python.core.app:app --host 0.0.0.0 --port 8000 --reload
```

### 登入後無法訪問功能
檢查瀏覽器控制台是否有錯誤訊息，清除 LocalStorage 後重新登入

### 熱更新不工作
重啟開發服務器: `npm run dev`

## 📄 授權

此專案為開源專案，供學習與研究使用

---

**開發時間**: 2025-10-24
**技術支援**: Vue 3 + Element Plus
**🚀 Built with Claude Code**
