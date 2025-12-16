#!/bin/bash
# ========================================
# Citizen App 自動部署腳本
# 用途：從本地部署到遠端伺服器
# ========================================

set -e  # 遇到錯誤立即停止

# 配置變數（請修改為你的設定）
SERVER_USER="se_city"
SERVER_HOST="your_server_ip"  # ← 修改為實際 IP
SERVER_PATH="~/cityAPP"
EXCLUDE_FILE=".deployignore"

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🚀 Citizen App 部署到伺服器${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 1. 檢查是否在專案根目錄
if [ ! -f "README.md" ] || [ ! -d "src/main/python" ]; then
    echo -e "${RED}❌ 錯誤：請在專案根目錄執行此腳本${NC}"
    exit 1
fi

# 2. 檢查是否有未提交的更改
echo -e "${YELLOW}📋 檢查 Git 狀態...${NC}"
if [[ -n $(git status -s) ]]; then
    echo -e "${YELLOW}⚠️  發現未提交的更改：${NC}"
    git status -s
    echo ""
    read -p "是否要先提交這些更改？(y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        read -p "請輸入 commit 訊息: " commit_msg
        git add .
        git commit -m "$commit_msg"
        echo -e "${GREEN}✅ 已提交更改${NC}"
    fi
fi

# 3. 獲取當前分支和 commit
CURRENT_BRANCH=$(git branch --show-current)
CURRENT_COMMIT=$(git rev-parse --short HEAD)
echo -e "${GREEN}當前分支: ${CURRENT_BRANCH}${NC}"
echo -e "${GREEN}當前 commit: ${CURRENT_COMMIT}${NC}"
echo ""

# 4. 推送到 GitHub
echo -e "${YELLOW}📤 推送到 GitHub...${NC}"
read -p "是否要推送到 GitHub? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git push origin $CURRENT_BRANCH
    echo -e "${GREEN}✅ 已推送到 GitHub${NC}"
fi

# 5. 使用 rsync 同步到伺服器
echo ""
echo -e "${YELLOW}📦 同步文件到伺服器...${NC}"

# 創建排除清單
cat > $EXCLUDE_FILE << 'EOF'
.git/
.gitignore
venv/
__pycache__/
*.pyc
.pytest_cache/
.coverage
htmlcov/
node_modules/
.DS_Store
*.log
.env
.env.local
*.sql.backup
*.backup
deploy_to_server.sh
.deployignore
EOF

# rsync 同步
rsync -avz --delete \
    --exclude-from="$EXCLUDE_FILE" \
    --progress \
    ./ ${SERVER_USER}@${SERVER_HOST}:${SERVER_PATH}/

rm -f $EXCLUDE_FILE

echo -e "${GREEN}✅ 文件同步完成${NC}"

# 6. 在伺服器上執行部署腳本
echo ""
echo -e "${YELLOW}🔧 在伺服器上執行部署...${NC}"

ssh ${SERVER_USER}@${SERVER_HOST} << 'ENDSSH'
cd ~/cityAPP

echo "========================================="
echo "🔧 伺服器端部署流程"
echo "========================================="

# 1. 備份現有 .env
if [ -f .env ]; then
    cp .env .env.backup
    echo "✅ 已備份 .env"
fi

# 2. 激活 conda 環境並更新依賴
echo ""
echo "📦 更新 Python 依賴..."
source ~/anaconda3/etc/profile.d/conda.sh
conda activate citizenapp
pip install -r requirements.txt --upgrade

# 3. 更新前端依賴（如果需要）
echo ""
echo "📦 更新前端依賴..."
cd src/main/js/citizen-portal
if [ -f package.json ]; then
    npm install
fi

cd ../admin-dashboard
if [ -f package.json ]; then
    npm install
fi

cd ~/cityAPP

# 4. 資料庫遷移（如果有新的 SQL 文件）
echo ""
echo "🗄️  檢查資料庫遷移..."
# 這裡會在後面添加自動遷移邏輯

# 5. 重啟服務
echo ""
echo "🔄 重啟服務..."
systemctl --user restart citizenapp

# 6. 檢查服務狀態
sleep 3
echo ""
echo "✅ 服務狀態:"
systemctl --user status citizenapp --no-pager -l | head -20

# 7. 測試 API
echo ""
echo "🧪 測試 API..."
if curl -s http://localhost:8080/health | grep -q "healthy"; then
    echo "✅ API 正常運行"
else
    echo "❌ API 異常，請檢查日誌"
fi

echo ""
echo "========================================="
echo "✅ 伺服器部署完成！"
echo "========================================="
ENDSSH

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ 部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}📊 部署資訊:${NC}"
echo -e "  分支: ${CURRENT_BRANCH}"
echo -e "  Commit: ${CURRENT_COMMIT}"
echo -e "  伺服器: ${SERVER_USER}@${SERVER_HOST}"
echo ""
echo -e "${YELLOW}🔍 後續操作:${NC}"
echo -e "  查看日誌: ssh ${SERVER_USER}@${SERVER_HOST} 'journalctl --user -u citizenapp -f'"
echo -e "  連接伺服器: ssh ${SERVER_USER}@${SERVER_HOST}"
echo ""
