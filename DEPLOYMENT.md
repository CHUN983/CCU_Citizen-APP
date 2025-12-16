# 🚀 Citizen App 部署指南

## 📋 目錄

1. [本地到伺服器部署](#本地到伺服器部署)
2. [資料庫遷移](#資料庫遷移-ai-自動審核)
3. [伺服器手動更新](#伺服器手動更新)
4. [常見問題](#常見問題)

---

## 本地到伺服器部署

### 前置準備

**在本地電腦：**

```bash
# 1. 修改部署腳本中的伺服器資訊
nano deploy_to_server.sh

# 修改這些變數：
# SERVER_USER="se_city"
# SERVER_HOST="your_server_ip"  # ← 改成實際 IP
```

### 完整部署流程

```bash
# 1. 在本地專案根目錄執行
chmod +x deploy_to_server.sh
./deploy_to_server.sh

# 腳本會自動：
# ✅ 檢查 Git 狀態
# ✅ 提交更改（可選）
# ✅ 推送到 GitHub（可選）
# ✅ 使用 rsync 同步到伺服器
# ✅ 在伺服器上更新依賴
# ✅ 重啟服務
# ✅ 測試 API
```

### 自動化的內容

部署腳本會自動排除以下文件：
- `.git/` - Git 歷史
- `venv/` - Python 虛擬環境
- `__pycache__/` - Python 快取
- `node_modules/` - Node.js 依賴
- `.env` - 環境變數（保持伺服器設定）
- `*.log` - 日誌文件
- `*.backup` - 備份文件

---

## 資料庫遷移（AI 自動審核）

### 問題 1：安裝 AI 自動審核系統

**在伺服器上執行：**

```bash
cd ~/cityAPP

# 給予執行權限
chmod +x scripts/migrate_database.sh

# 執行遷移工具
./scripts/migrate_database.sh

# 選擇選項 2 或 5：
# 2) 只安裝 AI 自動審核系統
# 5) 執行全部遷移（包括 AI 系統）
```

### AI 自動審核系統包含：

1. **自動審核欄位** - 添加到 opinions 表
   - `auto_moderation_status` - AI 審核狀態
   - `auto_moderation_score` - 信心度分數
   - `auto_category_id` - AI 建議分類
   - `moderation_reason` - 審核原因
   - `needs_manual_review` - 是否需要人工審核

2. **moderation_logs 表** - AI 審核日誌
   - 記錄每次 AI 審核決策
   - 包含 API 請求/回應
   - 檢測到的問題

3. **sensitive_words 表** - 敏感詞黑名單
   - 暴力、仇恨、色情等類別
   - 已包含範例敏感詞

4. **category_keywords 表** - 分類關鍵字庫
   - 交通、環保、工務等 9 個分類
   - 每個分類包含相關關鍵字

5. **moderation_config 表** - 審核配置
   - AI 審核開關
   - 自動通過/拒絕閾值
   - OpenAI API 設定

### 手動執行 SQL（如果需要）

```bash
# 在伺服器上
cd ~/cityAPP

# 執行 AI 自動審核遷移
~/anaconda3/bin/mysql -u root -p \
  --socket=/home/se_city/mysqlCity/mysql_run/mysql.sock \
  citizen_app < src/main/resources/config/add_ai_moderation_safe.sql

# 驗證安裝
~/anaconda3/bin/mysql -u root -p \
  --socket=/home/se_city/mysqlCity/mysql_run/mysql.sock \
  -e "USE citizen_app; SHOW TABLES LIKE '%moderation%';"
```

---

## 伺服器手動更新

如果不想從本地部署，可以在伺服器上直接更新：

### 方法 A：Git Pull（推薦）

```bash
# 在伺服器上
cd ~/cityAPP

# 1. Pull 最新代碼
git pull origin main  # 或你的分支名

# 2. 執行更新腳本
chmod +x scripts/server_update.sh
./scripts/server_update.sh
```

### 方法 B：使用更新腳本

```bash
cd ~/cityAPP
./scripts/server_update.sh

# 腳本會自動：
# ✅ 備份 .env
# ✅ 更新 Python 依賴
# ✅ 更新前端依賴
# ✅ 執行資料庫遷移（如果需要）
# ✅ 重啟服務
# ✅ 測試 API
```

---

## 快速參考

### 本地開發流程

```bash
# 1. 在本地修改代碼
git add .
git commit -m "新功能描述"

# 2. 推送到 GitHub
git push origin main

# 3. 部署到伺服器
./deploy_to_server.sh
```

### 伺服器維護

```bash
# 查看服務狀態
systemctl --user status citizenapp

# 查看日誌
journalctl --user -u citizenapp -f

# 重啟服務
systemctl --user restart citizenapp

# 連接資料庫
~/anaconda3/bin/mysql -u root -p --socket=/home/se_city/mysqlCity/mysql_run/mysql.sock citizen_app

# 執行資料庫遷移
./scripts/migrate_database.sh
```

---

## 常見問題

### Q: 為什麼 .env 不會被覆蓋？

A: 部署腳本會自動排除 .env 文件，並在伺服器上自動備份。這確保伺服器的配置（資料庫密碼、JWT 密鑰）不會被覆蓋。

### Q: 如何回滾到之前的版本？

```bash
# 在伺服器上
cd ~/cityAPP
git log --oneline  # 查看歷史
git checkout <commit-hash>  # 回滾到特定版本
./scripts/server_update.sh  # 更新依賴並重啟
```

### Q: 部署後 API 無法訪問？

```bash
# 檢查服務狀態
systemctl --user status citizenapp

# 查看錯誤日誌
journalctl --user -u citizenapp -n 50

# 測試資料庫連接
curl http://localhost:8080/health
```

### Q: 前端修改後需要重新構建嗎？

A:
- **開發環境**：vite dev server 會自動熱重載，不需要
- **生產環境**：需要執行 `npm run build`

---

## 檔案結構

```
citizenApp/
├── deploy_to_server.sh           # 本地部署腳本（在本地執行）
├── scripts/
│   ├── server_update.sh          # 伺服器更新腳本（在伺服器執行）
│   ├── migrate_database.sh       # 資料庫遷移工具（在伺服器執行）
│   ├── start_server.sh           # 啟動後端
│   └── init_database.sh          # 初始化資料庫
├── src/main/resources/config/
│   ├── schema.sql                # 基礎資料庫結構
│   └── add_ai_moderation_safe.sql # AI 自動審核遷移
└── DEPLOYMENT.md                 # 本文檔
```

---

## 最佳實踐

1. **每次部署前先提交到 Git**
2. **使用 Git 分支管理功能開發**
3. **測試環境驗證後再部署到生產環境**
4. **定期備份資料庫**
5. **保持本地和伺服器的 .env 獨立**

---

**🎯 Created with ❤️ by V&V Team**
