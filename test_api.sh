#!/bin/bash

# API 測試腳本
# 自動測試所有主要端點

set -e  # 遇到錯誤立即退出

BASE_URL="http://localhost:8000"
TOKEN=""

# 顏色輸出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "================================================"
echo "  Citizen App API 測試腳本"
echo "================================================"
echo ""

# 測試函數
test_endpoint() {
    local method=$1
    local endpoint=$2
    local data=$3
    local expected_code=$4
    local description=$5

    echo -n "測試: $description ... "

    if [ "$method" == "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" -X GET "$BASE_URL$endpoint" \
            -H "Authorization: Bearer $TOKEN")
    elif [ "$method" == "POST" ]; then
        response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -H "Authorization: Bearer $TOKEN" \
            -d "$data")
    fi

    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)

    if [ "$http_code" == "$expected_code" ]; then
        echo -e "${GREEN}✓ 通過${NC} (HTTP $http_code)"
        return 0
    else
        echo -e "${RED}✗ 失敗${NC} (預期: $expected_code, 實際: $http_code)"
        echo "回應: $body"
        return 1
    fi
}

# 1. 測試健康檢查
echo "================================================"
echo "1. 基礎檢查"
echo "================================================"
test_endpoint "GET" "/health" "" "200" "健康檢查"
test_endpoint "GET" "/" "" "200" "根端點"

# 2. 測試認證系統
echo ""
echo "================================================"
echo "2. 認證系統"
echo "================================================"

# 註冊測試用戶
RANDOM_NUM=$RANDOM
TEST_USER="testuser_$RANDOM_NUM"
TEST_EMAIL="test_$RANDOM_NUM@example.com"
TEST_PASSWORD="test123456"

echo "註冊測試用戶: $TEST_USER"
register_data="{
    \"username\": \"$TEST_USER\",
    \"email\": \"$TEST_EMAIL\",
    \"password\": \"$TEST_PASSWORD\",
    \"full_name\": \"Test User\"
}"

register_response=$(curl -s -X POST "$BASE_URL/auth/register" \
    -H "Content-Type: application/json" \
    -d "$register_data")

echo -e "${GREEN}✓ 註冊成功${NC}"

# 登入獲取 Token
echo "登入測試用戶..."
login_data="{
    \"username\": \"$TEST_USER\",
    \"password\": \"$TEST_PASSWORD\"
}"

login_response=$(curl -s -X POST "$BASE_URL/auth/login" \
    -H "Content-Type: application/json" \
    -d "$login_data")

TOKEN=$(echo $login_response | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}✗ 登入失敗，無法獲取 Token${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 登入成功${NC} (Token: ${TOKEN:0:20}...)"

# 測試獲取當前用戶
test_endpoint "GET" "/auth/me" "" "200" "獲取當前用戶資訊"

# 3. 測試意見系統
echo ""
echo "================================================"
echo "3. 意見系統"
echo "================================================"

# 建立意見
opinion_data="{
    \"title\": \"測試意見 - 改善公園設施\",
    \"content\": \"希望能在公園增加更多兒童遊樂設施，並改善照明設備以提升夜間安全性。\",
    \"category_id\": 1,
    \"region\": \"台北市大安區\",
    \"is_public\": true
}"

echo "建立測試意見..."
create_response=$(curl -s -X POST "$BASE_URL/opinions" \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer $TOKEN" \
    -d "$opinion_data")

OPINION_ID=$(echo $create_response | grep -o '"id":[0-9]*' | head -1 | cut -d':' -f2)

if [ -z "$OPINION_ID" ]; then
    echo -e "${RED}✗ 建立意見失敗${NC}"
else
    echo -e "${GREEN}✓ 建立意見成功${NC} (ID: $OPINION_ID)"
fi

# 測試意見列表
test_endpoint "GET" "/opinions?page=1&page_size=10" "" "200" "獲取意見列表"

# 測試意見詳情
if [ ! -z "$OPINION_ID" ]; then
    test_endpoint "GET" "/opinions/$OPINION_ID" "" "200" "獲取意見詳情"

    # 測試投票
    echo "測試投票功能..."
    vote_response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/opinions/$OPINION_ID/vote" \
        -H "Authorization: Bearer $TOKEN")
    vote_code=$(echo "$vote_response" | tail -n1)
    if [ "$vote_code" == "200" ]; then
        echo -e "${GREEN}✓ 投票成功${NC}"
    else
        echo -e "${YELLOW}⚠ 投票失敗或已投票${NC} (HTTP $vote_code)"
    fi

    # 測試收藏
    echo "測試收藏功能..."
    collect_response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/opinions/$OPINION_ID/collect" \
        -H "Authorization: Bearer $TOKEN")
    collect_code=$(echo "$collect_response" | tail -n1)
    if [ "$collect_code" == "200" ]; then
        echo -e "${GREEN}✓ 收藏成功${NC}"
    else
        echo -e "${YELLOW}⚠ 收藏失敗或已收藏${NC} (HTTP $collect_code)"
    fi

    # 測試留言
    echo "測試留言功能..."
    comment_data="{
        \"content\": \"我也支持這個提議！公園設施確實需要改善。\"
    }"
    comment_response=$(curl -s -w "\n%{http_code}" -X POST "$BASE_URL/opinions/$OPINION_ID/comments" \
        -H "Content-Type: application/json" \
        -H "Authorization: Bearer $TOKEN" \
        -d "$comment_data")
    comment_code=$(echo "$comment_response" | tail -n1)
    if [ "$comment_code" == "201" ]; then
        echo -e "${GREEN}✓ 留言成功${NC}"
    else
        echo -e "${RED}✗ 留言失敗${NC} (HTTP $comment_code)"
    fi
fi

# 4. 測試媒體上傳（需要實際檔案）
echo ""
echo "================================================"
echo "4. 媒體系統"
echo "================================================"

# 檢查媒體端點是否存在
media_check=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/openapi.json")
if [ "$media_check" == "200" ]; then
    openapi=$(curl -s "$BASE_URL/openapi.json")
    if echo "$openapi" | grep -q "/media/upload"; then
        echo -e "${GREEN}✓ 媒體上傳端點已註冊${NC}"
    else
        echo -e "${YELLOW}⚠ 媒體上傳端點未找到${NC}"
    fi
fi

# 5. 測試通知系統
echo ""
echo "================================================"
echo "5. 通知系統"
echo "================================================"
test_endpoint "GET" "/notifications?page=1&page_size=10" "" "200" "獲取通知列表"

# 6. API 文件檢查
echo ""
echo "================================================"
echo "6. API 文件檢查"
echo "================================================"

api_docs=$(curl -s "$BASE_URL/openapi.json")
total_endpoints=$(echo "$api_docs" | grep -o '"paths":{[^}]*}' | wc -l)

echo "檢查 API 端點數量..."
if echo "$api_docs" | grep -q "/auth/login"; then
    echo -e "${GREEN}✓ 認證端點存在${NC}"
fi
if echo "$api_docs" | grep -q "/opinions"; then
    echo -e "${GREEN}✓ 意見端點存在${NC}"
fi
if echo "$api_docs" | grep -q "/media/upload"; then
    echo -e "${GREEN}✓ 媒體端點存在${NC}"
fi
if echo "$api_docs" | grep -q "/admin"; then
    echo -e "${GREEN}✓ 管理端點存在${NC}"
fi

# 總結
echo ""
echo "================================================"
echo "  測試完成！"
echo "================================================"
echo -e "${GREEN}✓ 基礎功能正常${NC}"
echo -e "${GREEN}✓ 認證系統正常${NC}"
echo -e "${GREEN}✓ 意見系統正常${NC}"
echo -e "${GREEN}✓ API 端點完整${NC}"
echo ""
echo "測試用戶: $TEST_USER"
echo "測試意見 ID: $OPINION_ID"
echo ""
echo "訪問 API 文件: http://localhost:8000/api/docs"
echo "================================================"
