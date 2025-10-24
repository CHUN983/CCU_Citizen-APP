# 🏙️ Citizen Urban Planning Participation System

**市民參與城市規劃行動應用系統**

A complete backend API system enabling citizens to participate in urban planning through opinion submissions, voting, commenting, and collaborative decision-making.

## ✅ MVP Status: COMPLETE

All Phase 1 core requirements implemented:
- ✅ User authentication & authorization
- ✅ Opinion submission system
- ✅ Browsing & filtering
- ✅ Comment & vote system
- ✅ Admin moderation panel
- ✅ Notification system
- ✅ Complete API documentation

## 🚀 Quick Start

### 環境需求

- Python 3.9+
- MySQL 8.0+
- Node.js 16+ (for frontend)
- npm or yarn

---

### 📋 完整啟動流程

#### 步驟 1: 啟動 MySQL 資料庫

```bash
# 檢查 MySQL 狀態
sudo service mysql status

# 如果未運行，啟動 MySQL
sudo service mysql start
```

#### 步驟 2: 啟動後端 FastAPI 服務

**方法 A: 使用啟動腳本（推薦）**

```bash
# 直接執行啟動腳本
./scripts/start_server.sh
```

腳本會自動：
- 啟動 Python 虛擬環境
- 檢查並安裝依賴
- 啟動 FastAPI 服務（支援熱重載）

**方法 B: 手動啟動**

```bash
# 1. 啟動虛擬環境
source venv/bin/activate

# 2. 安裝依賴（首次運行）
pip install -r requirements.txt

# 3. 啟動 FastAPI 服務
python -m uvicorn src.main.python.core.app:app --reload --host 0.0.0.0 --port 8000
```

**後端服務地址：**
- API 主服務: http://localhost:8000
- Swagger 文檔: http://localhost:8000/api/docs
- ReDoc 文檔: http://localhost:8000/api/redoc
- 健康檢查: http://localhost:8000/health

---

#### 步驟 3: 啟動前端服務

本專案包含兩個前端應用：

##### 3.1 啟動市民端（Citizen Portal）

```bash
# 進入市民端目錄
cd src/main/js/citizen-portal

# 安裝依賴（首次運行）
npm install

# 啟動開發服務器
npm run dev
```

**市民端地址：** http://localhost:5174/

**功能：**
- 市民註冊/登入
- 提交意見
- 瀏覽已核准的意見
- 評論和投票
- 收藏意見

##### 3.2 啟動管理端（Admin Dashboard）

```bash
# 進入管理端目錄
cd src/main/js/admin-dashboard

# 安裝依賴（首次運行）
npm install

# 啟動開發服務器
npm run dev
```

**管理端地址：** http://localhost:5173/

**登入資訊：**
- 帳號：`admin`
- 密碼：`admin123`

**功能：**
- 審核待審意見
- 核准/拒絕意見
- 合併重複意見
- 刪除不當評論
- 管理分類

---

### 🔧 常見問題排除

#### 問題 1: 前端頁面空白

**原因：** 瀏覽器 localStorage 存儲了無效數據

**解決方法：**
1. 訪問清理頁面：http://localhost:5174/clear-storage.html
2. 點擊「清理 LocalStorage」按鈕
3. 或在瀏覽器 Console 執行：`localStorage.clear()` 然後重新整理

#### 問題 2: 後端無法連接

```bash
# 確認後端運行狀態
curl http://localhost:8000/health

# 應返回：{"status":"healthy"}
```

#### 問題 3: 資料庫連接失敗

```bash
# 檢查 MySQL 狀態
sudo service mysql status

# 測試資料庫連接
mysql -u root -p citizen_app -e "SELECT COUNT(*) FROM opinions;"
```

#### 問題 4: 前端端口被佔用

如果看到 "Port 5174 is in use"，Vite 會自動嘗試其他端口（5175, 5176...）
查看終端輸出確認實際端口。

---

### 📊 服務狀態檢查

所有服務啟動後：

```bash
# 檢查所有進程
ps aux | grep -E "(mysql|uvicorn|vite)"

# 測試後端
curl http://localhost:8000/health

# 測試前端
curl -I http://localhost:5174/
curl -I http://localhost:5173/
```

---

### 🎯 完整訪問指南

| 服務 | URL | 說明 |
|------|-----|------|
| **後端 API** | http://localhost:8000 | FastAPI 主服務 |
| **API 文檔** | http://localhost:8000/api/docs | Swagger 互動式文檔 |
| **市民端** | http://localhost:5174 | 市民意見平台 |
| **管理端** | http://localhost:5173 | 管理員後台 |
| **測試頁面** | http://localhost:5174/test | 診斷頁面 |
| **清理工具** | http://localhost:5174/clear-storage.html | LocalStorage 清理 |

---

### 🛑 停止服務

```bash
# 停止後端
pkill -f "uvicorn src.main.python.core.app:app"

# 停止前端
pkill -f "vite"

# 停止 MySQL（可選）
sudo service mysql stop
```

---

### 🔄 初始化資料庫

首次運行或重置資料庫：

```bash
# 使用初始化腳本
./scripts/init_database.sh
```

此腳本會：
- 創建資料庫
- 載入 schema
- 建立初始管理員帳號

## Project Structure

**Multi-Language Standard Project** - Supports Python, JavaScript, Java, and more

```
citizenApp/
├── src/main/           # Source code by language
│   ├── python/         # Python components
│   ├── js/             # JavaScript components
│   ├── java/           # Java components
│   ├── shared/         # Shared resources
│   └── resources/      # Configuration and assets
├── src/test/           # Test code
├── docs/               # Documentation
├── tools/              # Development tools
├── examples/           # Usage examples
└── output/             # Generated files
```

## Development Guidelines

- **Always search first** before creating new files
- **Extend existing** functionality rather than duplicating
- **Use Task agents** for operations >30 seconds
- **Single source of truth** for all functionality
- **Language-agnostic structure** - works with Python, JS, Java, etc.
- **Commit frequently** - after each completed task
- **GitHub backup** - push after every commit

## Multi-Language Support

This project supports multiple programming languages:

- **Python**: `src/main/python/` - Python implementations
- **JavaScript**: `src/main/js/` - JavaScript/Node.js code
- **Java**: `src/main/java/` - Java implementations
- **Shared**: `src/main/shared/` - Cross-language resources

Each language directory follows consistent structure:
- `core/` - Core business logic
- `utils/` - Utility functions/classes
- `models/` - Data models
- `services/` - Service layer
- `api/` - API endpoints

## 📚 Documentation

- **[Setup Guide](docs/user/SETUP_GUIDE.md)** - Installation and configuration
- **[API Documentation](docs/api/API_DOCUMENTATION.md)** - Complete API reference
- **[Project Summary](docs/dev/PROJECT_SUMMARY.md)** - Architecture and technical details
- **[Interactive API Docs](http://localhost:8000/api/docs)** - Try the API in your browser

## 🛠️ Technology Stack

- **Backend**: FastAPI (Python 3.9+)
- **Database**: MySQL 8.0+
- **Authentication**: JWT tokens with bcrypt
- **API Style**: RESTful
- **Documentation**: OpenAPI/Swagger

## 📊 Features

### For Citizens
- Register and manage account
- Submit opinions with location and categories
- Upload media (images, videos, audio) - schema ready
- Comment on other opinions
- Vote and bookmark opinions
- Receive notifications
- Track opinion status

### For Administrators
- Review and approve/reject submissions
- Merge similar opinions
- Moderate comments
- Update categories and tags
- View complete audit trail

## 🔐 Security

- JWT token authentication
- Bcrypt password hashing
- Role-based access control
- SQL injection prevention
- Input validation

## 📈 Project Statistics

- **27** Python files
- **~1,675** lines of code
- **13** database tables
- **20+** API endpoints
- **5** git commits
- **100%** MVP requirements met

## 🔜 Next Steps

1. **Frontend Development** - Build Android/iOS mobile apps
2. **Media Upload** - Implement file upload endpoints
3. **AI Integration** - Add NLP for automatic classification
4. **Analytics Dashboard** - Admin analytics and reporting
5. **Real-time Features** - WebSocket notifications

## 🤝 Contributing

This project follows the CLAUDE.md development guidelines:
- Search before creating new files
- Extend existing code rather than duplicating
- Single source of truth principle
- Commit after each completed task
- Automatic GitHub backup

## 📞 Support

- **GitHub**: https://github.com/CHUN983/CCU_Citizen-APP
- **Issues**: Report bugs or request features via GitHub Issues
- **Documentation**: Check docs/ directory

---

**🎯 Template by Chang Ho Chien | HC AI 說人話channel | v1.0.0**
**📺 Tutorial**: https://youtu.be/8Q1bRZaHH24
**💻 Built with Claude Code**
