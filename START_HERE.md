# 🚀 專案啟動指南 (Quick Start Guide)

## 第一步：安裝必要軟體

### 1. 確認 Python 版本
```bash
python3 --version
# 需要 Python 3.9 或更高版本
```

### 2. 確認 MySQL 已安裝並運行
```bash
mysql --version
# 確認 MySQL 8.0 或更高版本
```

如果沒有安裝 MySQL，請先安裝：
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install mysql-server

# 啟動 MySQL
sudo service mysql start
```

---

## 第二步：設定環境

### 1. 創建 .env 設定檔

你的 `.env.example` 已經有設定了，只需複製：

```bash
cp .env.example .env
```

你的資料庫密碼已經設定為 `e20040731`，JWT 金鑰也已經設定好了。

### 2. 創建 Python 虛擬環境

```bash
# 創建虛擬環境
python3 -m venv venv

# 啟動虛擬環境
source venv/bin/activate
```

### 3. 安裝 Python 套件

```bash
pip install -r requirements.txt
```

---

## 第三步：初始化資料庫

### 方法一：使用自動化腳本（推薦）

```bash
./scripts/init_database.sh
```

### 方法二：手動執行

```bash
# 1. 登入 MySQL（使用你的密碼 e20040731）
mysql -u root -p

# 2. 在 MySQL 中執行
CREATE DATABASE IF NOT EXISTS citizen_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit;

# 3. 匯入資料表結構
mysql -u root -p citizen_app < src/main/resources/config/schema.sql
```

---

## 第四步：啟動 API 伺服器

### 方法一：使用自動化腳本（推薦）

```bash
./scripts/start_server.sh
```

### 方法二：手動啟動

```bash
# 確保虛擬環境已啟動
source venv/bin/activate

# 啟動伺服器
python -m uvicorn src.main.python.core.app:app --reload --host 0.0.0.0 --port 8000
```

---

## 第五步：測試 API

### 1. 打開瀏覽器訪問

- **API 首頁**: http://localhost:8000
- **互動式 API 文件**: http://localhost:8000/api/docs
- **ReDoc 文件**: http://localhost:8000/api/redoc

### 2. 測試健康檢查

```bash
curl http://localhost:8000/health
```

應該回傳：
```json
{"status": "healthy"}
```

### 3. 使用預設管理員帳號登入

在 API 文件頁面 (http://localhost:8000/api/docs) 中：

1. 找到 `/auth/login` 端點
2. 點擊 "Try it out"
3. 輸入：
   ```json
   {
     "username": "admin",
     "password": "admin123"
   }
   ```
4. 點擊 "Execute"
5. 複製回傳的 `access_token`

### 4. 使用 Token 測試其他 API

1. 點擊頁面右上角的 "Authorize" 按鈕
2. 輸入：`Bearer <你的token>`
3. 現在可以測試需要認證的 API 了

---

## 常見問題排除

### ❌ MySQL 連線失敗

```bash
# 檢查 MySQL 是否運行
sudo service mysql status

# 啟動 MySQL
sudo service mysql start

# 測試連線
mysql -u root -p
```

### ❌ Port 8000 已被使用

更改端口：
```bash
python -m uvicorn src.main.python.core.app:app --reload --port 8001
```

### ❌ 模組找不到

確認虛擬環境已啟動並安裝套件：
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### ❌ 資料庫連線錯誤

檢查 `.env` 檔案中的資料庫設定：
```bash
cat .env
```

確認：
- DB_HOST=localhost
- DB_USER=root
- DB_PASSWORD=e20040731
- DB_NAME=citizen_app

---

## 下一步

### 📚 閱讀文件

- [API 文件](docs/api/API_DOCUMENTATION.md) - 完整 API 說明
- [設定指南](docs/user/SETUP_GUIDE.md) - 詳細設定說明
- [專案總覽](docs/dev/PROJECT_SUMMARY.md) - 技術架構

### 🧪 測試功能

1. **註冊新用戶** - `/auth/register`
2. **建立意見** - `/opinions` (POST)
3. **瀏覽意見** - `/opinions` (GET)
4. **留言** - `/opinions/{id}/comments`
5. **投票** - `/opinions/{id}/vote`

### 🎯 開發建議

1. 使用互動式文件測試所有 API
2. 查看資料庫結構：`src/main/resources/config/schema.sql`
3. 修改程式碼後會自動重新載入（--reload 模式）
4. 查看即時 log 了解運作狀況

---

## 快速指令參考

```bash
# 啟動虛擬環境
source venv/bin/activate

# 停用虛擬環境
deactivate

# 啟動伺服器
./scripts/start_server.sh

# 初始化資料庫
./scripts/init_database.sh

# 查看 API 文件
# 瀏覽器開啟：http://localhost:8000/api/docs
```

---

**需要幫助？**
- 查看文件：`docs/` 目錄
- GitHub Issues: https://github.com/CHUN983/CCU_Citizen-APP/issues
- 閱讀 API 互動文件獲得範例

**祝你開發順利！** 🎉
