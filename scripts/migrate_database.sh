#!/bin/bash
# ========================================
# 資料庫遷移腳本
# 用途：執行資料庫結構更新和 AI 自動審核初始化
# ========================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 資料庫配置（從 .env 讀取）
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-3307}"
DB_USER="${DB_USER:-root}"
DB_NAME="${DB_NAME:-citizen_app}"

# MySQL 命令（使用 socket）
if [ -f "$HOME/mysqlCity/mysql_run/mysql.sock" ]; then
    MYSQL_CMD="$HOME/anaconda3/bin/mysql -u $DB_USER -p --socket=$HOME/mysqlCity/mysql_run/mysql.sock"
else
    MYSQL_CMD="$HOME/anaconda3/bin/mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p"
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🗄️  資料庫遷移工具${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}資料庫: ${DB_NAME}${NC}"
echo -e "${YELLOW}主機: ${DB_HOST}:${DB_PORT}${NC}"
echo ""

# 檢查 SQL 文件是否存在
SQL_DIR="src/main/resources/config"
if [ ! -d "$SQL_DIR" ]; then
    echo -e "${RED}❌ 錯誤：找不到 SQL 目錄 $SQL_DIR${NC}"
    exit 1
fi

# 顯示可用的遷移文件
echo -e "${YELLOW}📋 可用的遷移文件:${NC}"
ls -1 $SQL_DIR/*.sql | nl
echo ""

# 互動式選擇
echo -e "${YELLOW}選擇要執行的遷移:${NC}"
echo "1) 完整初始化 (schema.sql)"
echo "2) AI 自動審核系統 (add_ai_moderation_safe.sql)"
echo "3) 檢查遷移狀態 (check_migration_status.sql)"
echo "4) 添加缺失欄位 (add_missing_columns.sql)"
echo "5) 全部執行 (推薦用於新環境)"
echo "0) 取消"
echo ""

read -p "請選擇 [0-5]: " choice

case $choice in
    1)
        echo -e "${YELLOW}🔧 執行完整初始化...${NC}"
        $MYSQL_CMD $DB_NAME < $SQL_DIR/schema.sql
        echo -e "${GREEN}✅ 完整初始化完成${NC}"
        ;;
    2)
        echo -e "${YELLOW}🤖 安裝 AI 自動審核系統...${NC}"
        echo ""
        echo -e "${YELLOW}此遷移將:${NC}"
        echo "  - 添加自動審核欄位到 opinions 表"
        echo "  - 創建 moderation_logs 表（AI 審核日誌）"
        echo "  - 創建 sensitive_words 表（敏感詞黑名單）"
        echo "  - 創建 category_keywords 表（分類關鍵字）"
        echo "  - 創建 moderation_config 表（審核配置）"
        echo "  - 插入預設配置和範例數據"
        echo ""
        read -p "確認執行? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            $MYSQL_CMD $DB_NAME < $SQL_DIR/add_ai_moderation_safe.sql
            echo -e "${GREEN}✅ AI 自動審核系統安裝完成${NC}"

            # 顯示新創建的表
            echo ""
            echo -e "${YELLOW}📊 新增的資料表:${NC}"
            $MYSQL_CMD $DB_NAME -e "SELECT table_name FROM information_schema.tables WHERE table_schema = '$DB_NAME' AND (table_name LIKE '%moderation%' OR table_name LIKE '%sensitive%' OR table_name LIKE '%category_keywords%');"
        fi
        ;;
    3)
        echo -e "${YELLOW}🔍 檢查遷移狀態...${NC}"
        if [ -f "$SQL_DIR/check_migration_status.sql" ]; then
            $MYSQL_CMD $DB_NAME < $SQL_DIR/check_migration_status.sql
        else
            # 手動檢查
            echo ""
            echo -e "${YELLOW}資料表清單:${NC}"
            $MYSQL_CMD $DB_NAME -e "SHOW TABLES;"
            echo ""
            echo -e "${YELLOW}opinions 表結構:${NC}"
            $MYSQL_CMD $DB_NAME -e "DESCRIBE opinions;" | grep -E "auto_|moderation|reviewed"
        fi
        ;;
    4)
        echo -e "${YELLOW}🔧 添加缺失欄位...${NC}"
        if [ -f "$SQL_DIR/add_missing_columns.sql" ]; then
            $MYSQL_CMD $DB_NAME < $SQL_DIR/add_missing_columns.sql
            echo -e "${GREEN}✅ 欄位更新完成${NC}"
        else
            echo -e "${YELLOW}⚠️  找不到 add_missing_columns.sql${NC}"
        fi
        ;;
    5)
        echo -e "${YELLOW}🚀 執行全部遷移...${NC}"
        echo ""
        echo -e "${RED}⚠️  警告：這將執行所有遷移，可能會修改現有資料${NC}"
        read -p "確認執行全部遷移? (y/n) " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            # 1. 檢查 schema 是否已存在
            TABLE_COUNT=$($MYSQL_CMD $DB_NAME -e "SHOW TABLES;" | wc -l)

            if [ $TABLE_COUNT -lt 5 ]; then
                echo -e "${YELLOW}📋 執行基礎 schema...${NC}"
                $MYSQL_CMD $DB_NAME < $SQL_DIR/schema.sql
            else
                echo -e "${GREEN}✅ 基礎 schema 已存在${NC}"
            fi

            # 2. 執行 AI 自動審核遷移
            echo -e "${YELLOW}🤖 安裝 AI 自動審核系統...${NC}"
            $MYSQL_CMD $DB_NAME < $SQL_DIR/add_ai_moderation_safe.sql

            echo ""
            echo -e "${GREEN}========================================${NC}"
            echo -e "${GREEN}✅ 全部遷移完成！${NC}"
            echo -e "${GREEN}========================================${NC}"

            # 顯示最終狀態
            echo ""
            echo -e "${YELLOW}📊 資料表總數:${NC}"
            $MYSQL_CMD $DB_NAME -e "SELECT COUNT(*) AS table_count FROM information_schema.tables WHERE table_schema = '$DB_NAME';"

            echo ""
            echo -e "${YELLOW}📋 所有資料表:${NC}"
            $MYSQL_CMD $DB_NAME -e "SHOW TABLES;"
        fi
        ;;
    0)
        echo -e "${YELLOW}取消遷移${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}❌ 無效的選擇${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ 資料庫遷移完成！${NC}"
echo -e "${GREEN}========================================${NC}"
