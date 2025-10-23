# 🗄️ MySQL 安裝指南 (WSL2/Ubuntu)

## 快速安裝 MySQL

### 方法一：一鍵安裝（推薦）

```bash
./install_mysql.sh
```

這個腳本會自動：
1. 安裝 MySQL Server
2. 啟動 MySQL 服務
3. 設定 root 密碼（使用 .env 中的密碼）
4. 創建 citizen_app 資料庫
5. 匯入所有資料表

---

### 方法二：手動安裝

#### 1. 安裝 MySQL

```bash
# 更新套件
sudo apt-get update

# 安裝 MySQL
sudo apt-get install -y mysql-server

# 啟動 MySQL
sudo service mysql start

# 檢查狀態
sudo service mysql status
```

#### 2. 設定 root 密碼

```bash
# 進入 MySQL（預設無密碼）
sudo mysql

# 在 MySQL 命令列中執行：
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'e20040731';
FLUSH PRIVILEGES;
exit;
```

#### 3. 創建資料庫

```bash
# 使用新密碼登入
mysql -u root -p
# 輸入密碼: e20040731

# 創建資料庫
CREATE DATABASE citizen_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
exit;
```

#### 4. 匯入資料表

```bash
mysql -u root -pe20040731 citizen_app < src/main/resources/config/schema.sql
```

---

## 驗證安裝

### 測試連線

```bash
mysql -u root -pe20040731 -e "SELECT VERSION();"
```

應該看到 MySQL 版本資訊。

### 檢查資料庫

```bash
mysql -u root -pe20040731 -e "SHOW DATABASES;"
```

應該看到 `citizen_app` 資料庫。

### 檢查資料表

```bash
mysql -u root -pe20040731 citizen_app -e "SHOW TABLES;"
```

應該看到 13 個資料表：
- users
- categories
- opinions
- opinion_media
- comments
- votes
- collections
- tags
- opinion_tags
- notifications
- opinion_history
- subscriptions

---

## WSL2 特別注意事項

### MySQL 服務管理

在 WSL2 中，每次重啟電腦後需要手動啟動 MySQL：

```bash
# 啟動 MySQL
sudo service mysql start

# 檢查狀態
sudo service mysql status

# 停止 MySQL
sudo service mysql stop

# 重啟 MySQL
sudo service mysql restart
```

### 自動啟動（可選）

創建一個啟動腳本：

```bash
# 編輯 ~/.bashrc
echo 'sudo service mysql start 2>/dev/null' >> ~/.bashrc
```

這樣每次開啟終端機時會自動嘗試啟動 MySQL。

---

## 常見問題

### ❌ 無法連線到 MySQL

```bash
# 確認 MySQL 正在運行
sudo service mysql status

# 如果沒有運行，啟動它
sudo service mysql start
```

### ❌ 密碼錯誤

重設密碼：

```bash
sudo mysql
ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY 'e20040731';
FLUSH PRIVILEGES;
exit;
```

### ❌ 資料庫不存在

```bash
mysql -u root -pe20040731 -e "CREATE DATABASE citizen_app CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
```

### ❌ Port 3306 被佔用

```bash
# 查看誰在使用
sudo netstat -tlnp | grep 3306

# 停止 MySQL
sudo service mysql stop

# 重新啟動
sudo service mysql start
```

---

## 完整安裝流程

```bash
# 1. 安裝 MySQL
./install_mysql.sh

# 2. 啟動專案
./setup_and_run.sh
```

就這麼簡單！

---

## 使用 Docker Desktop（替代方案）

如果你有 Docker Desktop for Windows：

### 1. 啟用 WSL2 整合

1. 打開 Docker Desktop
2. Settings → Resources → WSL Integration
3. 勾選你的 WSL2 發行版
4. Apply & Restart

### 2. 使用 Docker 運行 MySQL

```bash
docker run --name citizen-mysql \
  -e MYSQL_ROOT_PASSWORD=e20040731 \
  -e MYSQL_DATABASE=citizen_app \
  -p 3306:3306 \
  -d mysql:8

# 等待 30 秒讓 MySQL 啟動
sleep 30

# 匯入資料表
docker exec -i citizen-mysql mysql -uroot -pe20040731 citizen_app < src/main/resources/config/schema.sql
```

---

## 下一步

安裝完成後：

```bash
# 啟動專案
./setup_and_run.sh
```

打開瀏覽器訪問：
- http://localhost:8000/api/docs

**祝你使用順利！** 🎉
