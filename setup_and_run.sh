#!/bin/bash
# 完整的專案設定與啟動腳本
# Complete project setup and run script

echo "========================================"
echo "🏙️ Citizen App - 專案啟動"
echo "========================================"
echo ""

# 顏色定義
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 步驟 1: 檢查 Python
echo "📋 步驟 1/5: 檢查 Python..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo -e "${GREEN}✅ 找到 $PYTHON_VERSION${NC}"
else
    echo -e "${RED}❌ 找不到 Python 3，請先安裝${NC}"
    exit 1
fi

# 步驟 2: 創建虛擬環境
echo ""
echo "📦 步驟 2/5: 設定 Python 虛擬環境..."
if [ ! -d "venv" ]; then
    echo "   創建虛擬環境中..."
    python3 -m venv venv
    echo -e "${GREEN}✅ 虛擬環境已創建${NC}"
else
    echo -e "${GREEN}✅ 虛擬環境已存在${NC}"
fi

# 啟動虛擬環境
echo "   啟動虛擬環境..."
source venv/bin/activate

# 步驟 3: 安裝相依套件
echo ""
echo "📥 步驟 3/5: 安裝 Python 套件..."
if [ ! -f "venv/bin/uvicorn" ]; then
    echo "   安裝中（這可能需要幾分鐘）..."
    pip install --upgrade pip > /dev/null 2>&1
    pip install -r requirements.txt
    echo -e "${GREEN}✅ 所有套件已安裝${NC}"
else
    echo -e "${GREEN}✅ 套件已安裝${NC}"
fi

# 步驟 4: 檢查設定檔
echo ""
echo "⚙️  步驟 4/5: 檢查設定檔..."
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env 不存在，從範例複製...${NC}"
    cp .env.example .env
    echo -e "${GREEN}✅ .env 已創建${NC}"
else
    echo -e "${GREEN}✅ .env 已存在${NC}"
fi

# 載入環境變數
export $(cat .env | grep -v '^#' | xargs)

# 步驟 5: 檢查 MySQL
echo ""
echo "🗄️  步驟 5/5: 檢查資料庫..."
if command -v mysql &> /dev/null; then
    echo -e "${GREEN}✅ MySQL 已安裝${NC}"

    # 測試資料庫連線
    echo "   測試資料庫連線..."
    if mysql -h${DB_HOST} -u${DB_USER} -p${DB_PASSWORD} -e "SELECT 1" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 資料庫連線成功${NC}"

        # 檢查資料庫是否存在
        DB_EXISTS=$(mysql -h${DB_HOST} -u${DB_USER} -p${DB_PASSWORD} -e "SHOW DATABASES LIKE '${DB_NAME}';" | grep ${DB_NAME})

        if [ -z "$DB_EXISTS" ]; then
            echo -e "${YELLOW}⚠️  資料庫 '${DB_NAME}' 不存在，正在創建...${NC}"
            mysql -h${DB_HOST} -u${DB_USER} -p${DB_PASSWORD} -e "CREATE DATABASE ${DB_NAME} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;"
            echo "   匯入資料表結構..."
            mysql -h${DB_HOST} -u${DB_USER} -p${DB_PASSWORD} ${DB_NAME} < src/main/resources/config/schema.sql
            echo -e "${GREEN}✅ 資料庫已初始化${NC}"
        else
            echo -e "${GREEN}✅ 資料庫 '${DB_NAME}' 已存在${NC}"
        fi
    else
        echo -e "${RED}❌ 資料庫連線失敗${NC}"
        echo "   請檢查 .env 中的資料庫設定："
        echo "   DB_HOST=${DB_HOST}"
        echo "   DB_USER=${DB_USER}"
        echo "   DB_NAME=${DB_NAME}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  MySQL 未安裝或未啟動${NC}"
    echo ""
    echo "請先安裝 MySQL："
    echo "  Ubuntu/Debian: sudo apt-get install mysql-server"
    echo "  或使用 Docker: docker run --name mysql -e MYSQL_ROOT_PASSWORD=${DB_PASSWORD} -p 3306:3306 -d mysql:8"
    echo ""
    read -p "按 Enter 繼續（如果你已經有 MySQL 但未偵測到）或 Ctrl+C 取消..."
fi

# 啟動伺服器
echo ""
echo "========================================"
echo "🚀 啟動 API 伺服器"
echo "========================================"
echo ""
echo -e "${GREEN}伺服器位址：${NC}"
echo "  🌐 API 主頁：      http://localhost:8000"
echo "  📖 API 文件：      http://localhost:8000/api/docs"
echo "  📚 ReDoc 文件：    http://localhost:8000/api/redoc"
echo ""
echo -e "${YELLOW}預設管理員帳號：${NC}"
echo "  使用者名稱：admin"
echo "  密碼：      admin123"
echo ""
echo -e "${YELLOW}按 Ctrl+C 停止伺服器${NC}"
echo "========================================"
echo ""

# 啟動 uvicorn
python -m uvicorn src.main.python.core.app:app --reload --host 0.0.0.0 --port 8000
