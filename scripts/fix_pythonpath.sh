#!/bin/bash
# ========================================
# 修復 PYTHONPATH 配置
# ========================================

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🔧 修復 PYTHONPATH 配置${NC}"
echo -e "${GREEN}========================================${NC}"

# 1. 停止服務
echo -e "${YELLOW}停止服務...${NC}"
systemctl --user stop citizenapp

# 2. 更新服務配置
echo -e "${YELLOW}更新服務配置...${NC}"
cat > ~/.config/systemd/user/citizenapp.service << 'EOF'
[Unit]
Description=Citizen Urban Planning Participation System
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/se_city/cityAPP
Environment="PATH=/home/se_city/anaconda3/envs/citizenapp/bin:/usr/local/bin:/usr/bin:/bin"
Environment="PYTHONPATH=/home/se_city/cityAPP/src/main/python"
EnvironmentFile=/home/se_city/cityAPP/.env
ExecStart=/home/se_city/anaconda3/envs/citizenapp/bin/python -m uvicorn src.main.python.core.app:app --host 0.0.0.0 --port 8080
Restart=always
RestartSec=10

StandardOutput=journal
StandardError=journal

[Install]
WantedBy=default.target
EOF

# 3. 重新載入並啟動
echo -e "${YELLOW}重新載入服務...${NC}"
systemctl --user daemon-reload

echo -e "${YELLOW}啟動服務...${NC}"
systemctl --user start citizenapp

# 4. 等待啟動
sleep 3

# 5. 檢查狀態
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ 服務狀態${NC}"
echo -e "${GREEN}========================================${NC}"
systemctl --user status citizenapp --no-pager -l | head -20

# 6. 測試 API
echo ""
echo -e "${YELLOW}測試 API...${NC}"
if curl -s http://localhost:8080/health | grep -q "healthy"; then
    echo -e "${GREEN}✅ API 正常運行${NC}"
else
    echo -e "${YELLOW}⚠️  API 測試失敗，請查看日誌${NC}"
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ 修復完成！${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}📋 後續操作：${NC}"
echo "  查看日誌: journalctl --user -u citizenapp -f"
echo "  重啟服務: systemctl --user restart citizenapp"
echo ""
