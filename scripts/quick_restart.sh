#!/bin/bash
# ========================================
# 快速重啟腳本（不需要 sudo）
# 用途：只重啟服務，不更新依賴
# ========================================

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}🔄 快速重啟 Citizen App${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# 檢查是否使用 systemd 用戶服務
if systemctl --user is-active --quiet citizenapp; then
    echo -e "${YELLOW}📍 偵測到 systemd 用戶服務${NC}"
    echo -e "${YELLOW}🔄 重啟服務中...${NC}"
    systemctl --user restart citizenapp

    sleep 2

    if systemctl --user is-active --quiet citizenapp; then
        echo -e "${GREEN}✅ 服務重啟成功！${NC}"
        echo ""
        systemctl --user status citizenapp --no-pager -l | head -15
    else
        echo -e "${RED}❌ 服務啟動失敗${NC}"
        echo -e "${YELLOW}查看日誌：journalctl --user -u citizenapp -n 50${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  未偵測到 systemd 服務${NC}"
    echo -e "${YELLOW}正在查找 Python 進程...${NC}"

    # 查找 uvicorn 進程
    PID=$(ps aux | grep -E "uvicorn.*app:app" | grep -v grep | awk '{print $2}')

    if [ -n "$PID" ]; then
        echo -e "${YELLOW}找到進程 PID: $PID${NC}"
        echo -e "${YELLOW}正在停止進程...${NC}"
        kill $PID
        sleep 2

        echo -e "${YELLOW}正在啟動服務...${NC}"
        cd ~/cityAPP
        source ~/anaconda3/etc/profile.d/conda.sh
        conda activate citizenapp
        nohup python -m uvicorn src.main.python.core.app:app --host 0.0.0.0 --port 8443 --ssl-keyfile ~/cityAPP/ssl/selfsigned.key --ssl-certfile ~/cityAPP/ssl/selfsigned.crt > ~/cityAPP/logs/app.log 2>&1 &

        sleep 2
        echo -e "${GREEN}✅ 服務已重啟${NC}"
    else
        echo -e "${RED}❌ 未找到運行中的服務${NC}"
        echo -e "${YELLOW}請使用 start_server.sh 啟動服務${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}✅ 重啟完成！${NC}"
echo -e "${GREEN}========================================${NC}"
