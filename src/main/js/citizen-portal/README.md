# 🏙️ Citizen Portal - 市民意見前端

市民參與城市規劃系統的前端應用

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

## 🛠️ 技術棧

- **Vue 3** - 漸進式JavaScript框架
- **Vite** - 極速構建工具
- **Vue Router** - 官方路由
- **Pinia** - 狀態管理
- **Element Plus** - UI組件庫
- **Axios** - HTTP客戶端

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

### 啟動開發服務器

```bash
npm run dev
```

應用將運行在: http://localhost:5174

### 構建生產版本

```bash
npm run build
```

### 預覽生產構建

```bash
npm run preview
```

## 📁 專案結構

```
citizen-portal/
├── src/
│   ├── api/              # API 請求封裝
│   │   ├── axios.js      # Axios 配置與攔截器
│   │   └── index.js      # API 端點定義
│   ├── components/       # 可重用組件
│   │   ├── Header.vue    # 頂部導航
│   │   └── Footer.vue    # 底部資訊
│   ├── router/           # 路由配置
│   │   └── index.js      # 路由定義
│   ├── store/            # Pinia 狀態管理
│   │   ├── user.js       # 用戶狀態
│   │   └── opinion.js    # 意見狀態
│   ├── views/            # 頁面組件
│   │   ├── Home/         # 首頁
│   │   ├── Auth/         # 登入/註冊
│   │   ├── Opinions/     # 意見相關頁面
│   │   └── Profile/      # 個人資料
│   ├── App.vue           # 根組件
│   └── main.js           # 入口文件
├── public/               # 靜態資源
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

### 即將推出
- [ ] 我的意見管理
- [ ] 意見編輯功能
- [ ] 通知中心
- [ ] 多語言支援
- [ ] 暗黑模式

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
