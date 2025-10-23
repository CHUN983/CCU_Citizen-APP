#!/bin/bash

###############################################################################
# 測試執行腳本
# 專案: citizenApp
# 用途: 提供各種測試執行選項
###############################################################################

# 顏色定義
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 顯示標題
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  citizenApp 測試執行腳本${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 檢查虛擬環境
if [ ! -d "venv" ]; then
    echo -e "${RED}錯誤: 找不到虛擬環境 (venv)${NC}"
    echo -e "${YELLOW}請先執行: python3 -m venv venv${NC}"
    exit 1
fi

# 啟動虛擬環境
source venv/bin/activate

# 檢查 pytest 是否安裝
if ! command -v pytest &> /dev/null; then
    echo -e "${RED}錯誤: pytest 未安裝${NC}"
    echo -e "${YELLOW}請執行: venv/bin/pip install pytest pytest-asyncio pytest-cov${NC}"
    exit 1
fi

# 顯示選單
echo -e "${GREEN}請選擇測試選項:${NC}"
echo "1. 執行所有測試"
echo "2. 執行單元測試 (unit tests)"
echo "3. 執行整合測試 (integration tests)"
echo "4. 執行認證模組測試"
echo "5. 執行意見管理模組測試"
echo "6. 執行審核模組測試"
echo "7. 執行測試並生成 HTML 報告"
echo "8. 執行測試並生成覆蓋率報告"
echo "9. 執行快速測試 (排除 slow 標記)"
echo "10. 執行冒煙測試 (smoke tests)"
echo "0. 退出"
echo ""

read -p "請輸入選項 [0-10]: " choice

case $choice in
    1)
        echo -e "${BLUE}執行所有測試...${NC}"
        venv/bin/pytest src/test/ -v
        ;;
    2)
        echo -e "${BLUE}執行單元測試...${NC}"
        venv/bin/pytest src/test/unit/ -v -m unit
        ;;
    3)
        echo -e "${BLUE}執行整合測試...${NC}"
        venv/bin/pytest src/test/integration/ -v -m integration
        ;;
    4)
        echo -e "${BLUE}執行認證模組測試...${NC}"
        venv/bin/pytest src/test/integration/test_auth_api.py -v
        ;;
    5)
        echo -e "${BLUE}執行意見管理模組測試...${NC}"
        venv/bin/pytest src/test/integration/test_opinion_api.py -v
        ;;
    6)
        echo -e "${BLUE}執行審核模組測試...${NC}"
        venv/bin/pytest src/test/integration/test_moderation_api.py -v
        ;;
    7)
        echo -e "${BLUE}執行測試並生成 HTML 報告...${NC}"
        venv/bin/pytest src/test/ -v --html=test_report.html --self-contained-html
        echo -e "${GREEN}報告已生成: test_report.html${NC}"
        ;;
    8)
        echo -e "${BLUE}執行測試並生成覆蓋率報告...${NC}"
        venv/bin/pytest src/test/ -v --cov=src/main/python --cov-report=html:htmlcov --cov-report=term-missing
        echo -e "${GREEN}覆蓋率報告已生成: htmlcov/index.html${NC}"
        ;;
    9)
        echo -e "${BLUE}執行快速測試 (排除 slow 標記)...${NC}"
        venv/bin/pytest src/test/ -v -m "not slow"
        ;;
    10)
        echo -e "${BLUE}執行冒煙測試...${NC}"
        venv/bin/pytest src/test/ -v -m smoke
        ;;
    0)
        echo -e "${YELLOW}退出測試腳本${NC}"
        exit 0
        ;;
    *)
        echo -e "${RED}無效的選項${NC}"
        exit 1
        ;;
esac

# 顯示測試結果
TEST_RESULT=$?
echo ""
echo -e "${BLUE}========================================${NC}"
if [ $TEST_RESULT -eq 0 ]; then
    echo -e "${GREEN}✅ 測試執行完成${NC}"
else
    echo -e "${RED}❌ 測試執行失敗${NC}"
fi
echo -e "${BLUE}========================================${NC}"

exit $TEST_RESULT
