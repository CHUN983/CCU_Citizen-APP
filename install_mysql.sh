#!/bin/bash
# MySQL 安裝腳本 for WSL2/Ubuntu

echo "🗄️ 安裝 MySQL 到 WSL2"
echo "===================="
echo ""

# 更新套件列表
echo "📦 更新套件列表..."
sudo apt-get update

# 安裝 MySQL Server
echo "📥 安裝 MySQL Server..."
sudo apt-get install -y mysql-server

# 啟動 MySQL 服務
echo "🚀 啟動 MySQL 服務..."
sudo service mysql start

# 檢查服務狀態
echo ""
echo "✅ 檢查 MySQL 狀態..."
sudo service mysql status

echo ""
echo "===================="
echo "✅ MySQL 安裝完成！"
echo "===================="
echo ""

# 載入 .env 設定
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# 設定 root 密碼並創建資料庫
echo "🔧 設定資料庫..."
sudo mysql -e "ALTER USER 'root'@'localhost' IDENTIFIED WITH mysql_native_password BY '${DB_PASSWORD:-e20040731}';" 2>/dev/null || true
sudo mysql -e "CREATE DATABASE IF NOT EXISTS ${DB_NAME:-citizen_app} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;" 2>/dev/null || true
sudo mysql -e "FLUSH PRIVILEGES;"

# 匯入資料表結構
if [ -f "src/main/resources/config/schema.sql" ]; then
    echo "📋 匯入資料表結構..."
    mysql -u root -p${DB_PASSWORD:-e20040731} ${DB_NAME:-citizen_app} < src/main/resources/config/schema.sql
    echo "✅ 資料表已建立"
fi

echo ""
echo "===================="
echo "🎉 完成！"
echo "===================="
echo ""
echo "資料庫資訊："
echo "  主機: localhost"
echo "  使用者: root"
echo "  密碼: ${DB_PASSWORD:-e20040731}"
echo "  資料庫: ${DB_NAME:-citizen_app}"
echo ""
echo "下一步："
echo "  執行 ./setup_and_run.sh 啟動專案"
echo ""
