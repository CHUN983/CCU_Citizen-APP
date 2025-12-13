#!/bin/bash
# ========================================
# 伺服器端更新腳本
# 用途：在伺服器上手動執行更新
# ========================================

set -e

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🔄 Citizen App 伺服器更新${NC}"
echo -e "${GREEN}========================================${NC}"

cd ~/cityAPP

# 1. 備份 .env
if [ -f .env ]; then
    cp .env .env.backup.$(date +%Y%m%d_%H%M%S)
    echo -e "${GREEN}✅ 已備份 .env${NC}"
fi

# 2. 更新 Python 依賴
echo -e "${YELLOW}📦 更新 Python 依賴...${NC}"
source ~/anaconda3/etc/profile.d/conda.sh
conda activate citizenapp
pip install -r requirements.txt --upgrade --quiet

# 3. 更新前端依賴
echo -e "${YELLOW}📦 更新前端依賴...${NC}"

if [ -d "src/main/js/citizen-portal" ]; then
    cd src/main/js/citizen-portal
    npm install --silent
    cd ~/cityAPP
fi

if [ -d "src/main/js/admin-dashboard" ]; then
    cd src/main/js/admin-dashboard
    npm install --silent
    cd ~/cityAPP
fi

# 4. 執行資料庫遷移（如果需要）
if [ -f "scripts/migrate_database.sh" ]; then
    echo -e "${YELLOW}🗄️  執行資料庫遷移...${NC}"
    bash scripts/migrate_database.sh
fi

# 5. 重啟服務
echo -e "${YELLOW}🔄 重啟服務...${NC}"
systemctl --user restart citizenapp

sleep 3

# 6. 檢查狀態
echo -e "${YELLOW}✅ 檢查服務狀態...${NC}"
systemctl --user status citizenapp --no-pager -l | head -20

echo ""
if curl -s http://localhost:8080/health | grep -q "healthy"; then
    echo -e "${GREEN}✅ API 正常運行${NC}"
else
    echo -e "${YELLOW}⚠️  API 可能異常，請檢查日誌${NC}"
    echo -e "${YELLOW}   journalctl --user -u citizenapp -n 50${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ 更新完成！${NC}"
echo -e "${GREEN}========================================${NC}"
