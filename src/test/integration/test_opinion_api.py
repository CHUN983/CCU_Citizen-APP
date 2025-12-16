"""
意見管理 API 整合測試
測試案例對應: TC-OPIN-001 ~ TC-OPIN-015
需求對應: REQ-002 (意見發表功能), REQ-003 (留言功能), REQ-004 (投票功能), REQ-005 (收藏功能)
"""

import pytest
from fastapi.testclient import TestClient


class TestOpinionCreation:
    """意見建立測試類別"""

    def test_create_opinion_success(
        self,
        test_client: TestClient,
        auth_headers_user,
        test_opinion_data
    ):
        """
        TC-OPIN-001: 成功建立意見
        測試目標: 驗證已登入用戶能夠建立新意見
        優先級: Critical
        """
        # 執行建立意見請求
        response = test_client.post(
            "/opinions",
            json=test_opinion_data,
            headers=auth_headers_user
        )

        # 驗證結果
        assert response.status_code == 201, f"期望狀態碼 201，實際 {response.status_code}"

        data = response.json()
        assert "id" in data
        assert data["title"] == test_opinion_data["title"]
        assert data["content"] == test_opinion_data["content"]
        assert data["status"] in ["draft", "pending"]
        assert "created_at" in data

    def test_create_opinion_without_auth(
        self,
        test_client: TestClient,
        test_opinion_data
    ):
        """
        TC-OPIN-002: 未登入建立意見失敗
        測試目標: 驗證未登入用戶無法建立意見
        優先級: Critical
        """
        # 不提供認證標頭
        response = test_client.post("/opinions", json=test_opinion_data)

        # 驗證結果
        assert response.status_code == 401
        assert "not authenticated" in response.json()["detail"].lower()

    def test_create_opinion_missing_required_fields(
        self,
        test_client: TestClient,
        auth_headers_user
    ):
        """
        TC-OPIN-003: 缺少必填欄位建立失敗
        測試目標: 驗證必填欄位檢查
        優先級: High
        """
        # 缺少 title 和 content
        incomplete_data = {
            "category_id": 1
        }

        response = test_client.post(
            "/opinions",
            json=incomplete_data,
            headers=auth_headers_user
        )

        # 驗證結果
        assert response.status_code == 422, "應返回驗證錯誤"

    def test_create_opinion_empty_content(
        self,
        test_client: TestClient,
        auth_headers_user
    ):
        """
        測試空內容建立失敗
        測試目標: 驗證不接受空內容
        優先級: Medium
        """
        empty_data = {
            "title": "測試標題",
            "content": "",  # 空內容
            "category_id": 1
        }

        response = test_client.post(
            "/opinions",
            json=empty_data,
            headers=auth_headers_user
        )

        # 驗證結果（根據實作可能是 400 或 422）
        assert response.status_code in [400, 422]


class TestOpinionRetrieval:
    """意見查詢測試類別"""

    def test_get_opinions_list_success(
        self,
        test_client: TestClient,
        create_multiple_opinions
    ):
        """
        TC-OPIN-004: 成功獲取意見列表
        測試目標: 驗證能夠獲取分頁的意見列表
        優先級: Critical
        """
        # 執行查詢請求
        response = test_client.get("/opinions")

        # 驗證結果
        assert response.status_code == 200

        data = response.json()
        assert "items" in data or isinstance(data, list)
        assert "total" in data or len(data) > 0

        # 如果是分頁格式
        if "items" in data:
            assert isinstance(data["items"], list)
            assert len(data["items"]) > 0

    def test_get_opinions_with_pagination(
        self,
        test_client: TestClient,
        create_multiple_opinions
    ):
        """
        TC-OPIN-006: 測試分頁功能
        測試目標: 驗證分頁參數正確運作
        優先級: High
        """
        # 第一頁，每頁 2 筆
        response_page1 = test_client.get("/opinions?page=1&page_size=2")
        assert response_page1.status_code == 200

        data_page1 = response_page1.json()

        # 驗證分頁資料
        if "items" in data_page1:
            assert len(data_page1["items"]) <= 2
            assert "total" in data_page1

            # 第二頁
            response_page2 = test_client.get("/opinions?page=2&page_size=2")
            assert response_page2.status_code == 200

            data_page2 = response_page2.json()
            # 驗證兩頁資料不同
            if len(data_page2["items"]) > 0:
                assert data_page1["items"][0]["id"] != data_page2["items"][0]["id"]

    def test_get_opinions_with_status_filter(
        self,
        test_client: TestClient,
        create_multiple_opinions
    ):
        """
        TC-OPIN-005: 依狀態篩選意見
        測試目標: 驗證狀態篩選功能
        優先級: High
        """
        # 篩選已核准的意見
        response = test_client.get("/opinions?status=approved")

        assert response.status_code == 200

        data = response.json()
        items = data.get("items", data)

        # 驗證所有意見狀態為 approved
        for opinion in items:
            assert opinion["status"] == "approved"

    def test_get_opinion_detail_success(
        self,
        test_client: TestClient,
        create_test_opinion
    ):
        """
        TC-OPIN-007: 成功獲取意見詳情
        測試目標: 驗證能夠獲取特定意見的完整資訊
        優先級: Critical
        """
        opinion_id = create_test_opinion.id

        # 執行查詢請求
        response = test_client.get(f"/opinions/{opinion_id}")

        # 驗證結果
        assert response.status_code == 200

        data = response.json()
        assert data["id"] == opinion_id
        assert data["title"] == create_test_opinion.title
        assert data["content"] == create_test_opinion.content
        assert "upvotes" in data, "應包含讚成票數"
        assert "downvotes" in data, "應包含反對票數"
        assert "comment_count" in data, "應包含留言數"

    def test_get_opinion_detail_not_found(self, test_client: TestClient):
        """
        TC-OPIN-008: 獲取不存在的意見失敗
        測試目標: 驗證查詢不存在的意見返回 404
        優先級: High
        """
        # 使用不存在的 ID
        response = test_client.get("/opinions/99999")

        # 驗證結果
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()


class TestOpinionComments:
    """意見留言測試類別"""

    def test_add_comment_success(
        self,
        test_client: TestClient,
        auth_headers_user,
        create_test_opinion
    ):
        """
        TC-OPIN-009: 成功新增留言
        測試目標: 驗證已登入用戶能夠對意見留言
        優先級: Critical
        """
        opinion_id = create_test_opinion.id

        comment_data = {
            "content": "這是一個測試留言"
        }

        # 執行新增留言請求
        response = test_client.post(
            f"/opinions/{opinion_id}/comments",
            json=comment_data,
            headers=auth_headers_user
        )

        # 驗證結果
        assert response.status_code == 201

        data = response.json()
        assert "id" in data
        assert data["content"] == comment_data["content"]
        assert "user_id" in data
        assert "created_at" in data

    def test_add_comment_to_nonexistent_opinion(
        self,
        test_client: TestClient,
        auth_headers_user
    ):
        """
        TC-OPIN-010: 對不存在的意見留言失敗
        測試目標: 驗證無法對不存在的意見留言
        優先級: High
        """
        comment_data = {
            "content": "測試留言"
        }

        # 使用不存在的意見 ID
        response = test_client.post(
            "/opinions/99999/comments",
            json=comment_data,
            headers=auth_headers_user
        )

        # 驗證結果
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_add_comment_without_auth(
        self,
        test_client: TestClient,
        create_test_opinion
    ):
        """
        測試未登入留言失敗
        測試目標: 驗證未登入用戶無法留言
        優先級: Critical
        """
        opinion_id = create_test_opinion.id

        comment_data = {
            "content": "測試留言"
        }

        # 不提供認證標頭
        response = test_client.post(
            f"/opinions/{opinion_id}/comments",
            json=comment_data
        )

        # 驗證結果
        assert response.status_code == 401

    def test_add_empty_comment(
        self,
        test_client: TestClient,
        auth_headers_user,
        create_test_opinion
    ):
        """
        測試空留言被拒絕
        測試目標: 驗證不接受空留言
        優先級: Medium
        """
        opinion_id = create_test_opinion.id

        empty_comment = {
            "content": ""
        }

        response = test_client.post(
            f"/opinions/{opinion_id}/comments",
            json=empty_comment,
            headers=auth_headers_user
        )

        # 驗證結果
        assert response.status_code in [400, 422]


class TestOpinionVoting:
    """意見投票測試類別"""

    def test_vote_opinion_success(
        self,
        test_client: TestClient,
        auth_headers_user,
        create_test_opinion
    ):
        """
        TC-OPIN-011: 成功為意見投票
        測試目標: 驗證已登入用戶能夠投票
        優先級: Critical
        """
        opinion_id = create_test_opinion.id

        vote_data = {
            "vote_type": "support"  # 或 "oppose"
        }

        # 執行投票請求
        response = test_client.post(
            f"/opinions/{opinion_id}/vote",
            json=vote_data,
            headers=auth_headers_user
        )

        # 驗證結果
        assert response.status_code == 200
        assert "message" in response.json() or "success" in str(response.json()).lower()

    def test_vote_nonexistent_opinion(
        self,
        test_client: TestClient,
        auth_headers_user
    ):
        """
        測試對不存在的意見投票失敗
        測試目標: 驗證無法對不存在的意見投票
        優先級: High
        """
        vote_data = {
            "vote_type": "support"
        }

        response = test_client.post(
            "/opinions/99999/vote",
            json=vote_data,
            headers=auth_headers_user
        )

        # 驗證結果
        assert response.status_code == 404

    def test_vote_without_auth(
        self,
        test_client: TestClient,
        create_test_opinion
    ):
        """
        測試未登入投票失敗
        測試目標: 驗證未登入用戶無法投票
        優先級: Critical
        """
        opinion_id = create_test_opinion.id

        vote_data = {
            "vote_type": "support"
        }

        # 不提供認證標頭
        response = test_client.post(
            f"/opinions/{opinion_id}/vote",
            json=vote_data
        )

        # 驗證結果
        assert response.status_code == 401

    def test_duplicate_vote(
        self,
        test_client: TestClient,
        auth_headers_user,
        create_test_opinion
    ):
        """
        TC-OPIN-012: 測試重複投票處理
        測試目標: 驗證重複投票的處理邏輯
        優先級: High
        """
        opinion_id = create_test_opinion.id

        vote_data = {
            "vote_type": "support"
        }

        # 第一次投票
        response1 = test_client.post(
            f"/opinions/{opinion_id}/vote",
            json=vote_data,
            headers=auth_headers_user
        )
        assert response1.status_code == 200

        # 第二次投票（重複）
        response2 = test_client.post(
            f"/opinions/{opinion_id}/vote",
            json=vote_data,
            headers=auth_headers_user
        )

        # 驗證結果（根據業務邏輯，可能允許更新投票或返回錯誤）
        assert response2.status_code in [200, 400]


class TestOpinionCollection:
    """意見收藏測試類別"""

    def test_collect_opinion_success(
        self,
        test_client: TestClient,
        auth_headers_user,
        create_test_opinion
    ):
        """
        TC-OPIN-013: 成功收藏意見
        測試目標: 驗證用戶能夠收藏意見
        優先級: Medium
        """
        opinion_id = create_test_opinion.id

        # 執行收藏請求
        response = test_client.post(
            f"/opinions/{opinion_id}/collect",
            headers=auth_headers_user
        )

        # 驗證結果
        assert response.status_code == 200
        assert "message" in response.json() or "success" in str(response.json()).lower()

    def test_uncollect_opinion_success(
        self,
        test_client: TestClient,
        auth_headers_user,
        create_test_opinion
    ):
        """
        TC-OPIN-014: 成功取消收藏
        測試目標: 驗證用戶能夠取消收藏
        優先級: Medium
        """
        opinion_id = create_test_opinion.id

        # 先收藏
        collect_response = test_client.post(
            f"/opinions/{opinion_id}/collect",
            headers=auth_headers_user
        )
        assert collect_response.status_code == 200

        # 再取消收藏
        uncollect_response = test_client.delete(
            f"/opinions/{opinion_id}/collect",
            headers=auth_headers_user
        )

        # 驗證結果
        assert uncollect_response.status_code == 200

    def test_uncollect_non_collected_opinion(
        self,
        test_client: TestClient,
        auth_headers_user,
        create_test_opinion
    ):
        """
        TC-OPIN-015: 取消不存在的收藏失敗
        測試目標: 驗證取消未收藏的意見返回錯誤
        優先級: Low
        """
        opinion_id = create_test_opinion.id

        # 直接取消收藏（未先收藏）
        response = test_client.delete(
            f"/opinions/{opinion_id}/collect",
            headers=auth_headers_user
        )

        # 驗證結果
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_collect_without_auth(
        self,
        test_client: TestClient,
        create_test_opinion
    ):
        """
        測試未登入收藏失敗
        測試目標: 驗證未登入用戶無法收藏
        優先級: Medium
        """
        opinion_id = create_test_opinion.id

        # 不提供認證標頭
        response = test_client.post(f"/opinions/{opinion_id}/collect")

        # 驗證結果
        assert response.status_code == 401

    def test_collect_nonexistent_opinion(
        self,
        test_client: TestClient,
        auth_headers_user
    ):
        """
        測試收藏不存在的意見失敗
        測試目標: 驗證無法收藏不存在的意見
        優先級: Medium
        """
        # 使用不存在的意見 ID
        response = test_client.post(
            "/opinions/99999/collect",
            headers=auth_headers_user
        )

        # 驗證結果
        assert response.status_code == 404


# ==================== 整合與邊界測試 ====================

class TestOpinionIntegration:
    """意見系統整合測試"""

    def test_complete_opinion_workflow(
        self,
        test_client: TestClient,
        auth_headers_user,
        test_opinion_data
    ):
        """
        完整的意見工作流程測試
        測試目標: 驗證從建立到互動的完整流程
        優先級: Critical
        """
        # 1. 建立意見
        create_response = test_client.post(
            "/opinions",
            json=test_opinion_data,
            headers=auth_headers_user
        )
        assert create_response.status_code == 201
        opinion_id = create_response.json()["id"]

        # 2. 查看意見詳情
        detail_response = test_client.get(f"/opinions/{opinion_id}")
        assert detail_response.status_code == 200

        # 3. 投票
        vote_response = test_client.post(
            f"/opinions/{opinion_id}/vote",
            json={"vote_type": "support"},
            headers=auth_headers_user
        )
        assert vote_response.status_code == 200

        # 4. 留言
        comment_response = test_client.post(
            f"/opinions/{opinion_id}/comments",
            json={"content": "測試留言"},
            headers=auth_headers_user
        )
        assert comment_response.status_code == 201

        # 5. 收藏
        collect_response = test_client.post(
            f"/opinions/{opinion_id}/collect",
            headers=auth_headers_user
        )
        assert collect_response.status_code == 200

    @pytest.mark.slow
    def test_large_opinion_list_performance(
        self,
        test_client: TestClient,
        create_multiple_opinions
    ):
        """
        大量意見列表性能測試
        測試目標: 驗證大量資料的查詢性能
        優先級: Medium
        """
        import time

        start_time = time.time()
        response = test_client.get("/opinions?page=1&page_size=100")
        end_time = time.time()

        assert response.status_code == 200
        # 期望查詢時間小於 2 秒
        assert (end_time - start_time) < 2.0, "查詢時間過長"


class TestOpinionUserQueries:
    """用戶意見查詢測試類別"""

    def test_get_bookmarked_opinions(
        self,
        test_client: TestClient,
        auth_headers_user,
        create_test_opinion
    ):
        """
        TC-OPIN-016: 獲取用戶收藏的意見列表
        測試目標: 驗證用戶可以獲取自己收藏的意見
        優先級: High
        """
        opinion_id = create_test_opinion.id

        # 先收藏意見
        collect_response = test_client.post(
            f"/opinions/{opinion_id}/collect",
            headers=auth_headers_user
        )
        assert collect_response.status_code == 200

        # 獲取收藏列表
        response = test_client.get(
            "/opinions/collect",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1
        # 驗證收藏的意見在列表中
        opinion_ids = [item["id"] for item in data["items"]]
        assert opinion_id in opinion_ids

    def test_get_my_opinions(
        self,
        test_client: TestClient,
        auth_headers_user,
        create_test_opinion
    ):
        """
        TC-OPIN-017: 獲取用戶自己創建的意見列表
        測試目標: 驗證用戶可以獲取自己創建的所有意見
        優先級: High
        """
        opinion_id = create_test_opinion.id

        # 獲取我的意見列表
        response = test_client.get(
            "/opinions/my-opinions",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert data["total"] >= 1
        # 驗證創建的意見在列表中
        opinion_ids = [item["id"] for item in data["items"]]
        assert opinion_id in opinion_ids

    def test_get_my_opinions_with_status_filter(
        self,
        test_client: TestClient,
        auth_headers_user,
        create_test_opinion
    ):
        """
        TC-OPIN-018: 按狀態過濾用戶的意見
        測試目標: 驗證可以按狀態過濾用戶自己的意見
        優先級: Medium
        """
        # 獲取待審核的意見
        response = test_client.get(
            "/opinions/my-opinions?status=pending",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        data = response.json()
        assert "items" in data


class TestOpinionCommentRetrieval:
    """意見留言查詢測試類別"""

    def test_get_opinion_comments(
        self,
        test_client: TestClient,
        auth_headers_user,
        create_test_opinion
    ):
        """
        TC-OPIN-019: 獲取意見的留言列表
        測試目標: 驗證可以獲取指定意見的所有留言
        優先級: High
        """
        opinion_id = create_test_opinion.id

        # 先添加一個留言
        comment_response = test_client.post(
            f"/opinions/{opinion_id}/comments",
            json={"content": "這是一個測試留言"},
            headers=auth_headers_user
        )
        assert comment_response.status_code == 201

        # 獲取留言列表
        response = test_client.get(
            f"/opinions/{opinion_id}/comments",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        # 驗證留言內容
        assert any(comment["content"] == "這是一個測試留言" for comment in data)

    def test_get_comments_with_limit(
        self,
        test_client: TestClient,
        auth_headers_user,
        create_test_opinion
    ):
        """
        TC-OPIN-020: 限制返回的留言數量
        測試目標: 驗證可以限制返回的留言數量
        優先級: Medium
        """
        opinion_id = create_test_opinion.id

        # 添加多個留言
        for i in range(5):
            test_client.post(
                f"/opinions/{opinion_id}/comments",
                json={"content": f"測試留言 {i}"},
                headers=auth_headers_user
            )

        # 獲取有限數量的留言
        response = test_client.get(
            f"/opinions/{opinion_id}/comments?limit=3",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 3

    def test_get_comments_for_nonexistent_opinion(
        self,
        test_client: TestClient,
        auth_headers_user
    ):
        """
        TC-OPIN-021: 獲取不存在意見的留言
        測試目標: 驗證查詢不存在的意見留言時返回 404
        優先級: Medium
        """
        non_existent_id = 999999

        response = test_client.get(
            f"/opinions/{non_existent_id}/comments",
            headers=auth_headers_user
        )

        assert response.status_code == 404


class TestOpinionStatusQueries:
    """意見狀態查詢測試類別"""

    def test_get_vote_status(
        self,
        test_client: TestClient,
        auth_headers_user,
        create_test_opinion
    ):
        """
        TC-OPIN-022: 獲取用戶對意見的投票狀態
        測試目標: 驗證可以查詢用戶對特定意見的投票狀態
        優先級: High
        """
        opinion_id = create_test_opinion.id

        # 先投票
        vote_response = test_client.post(
            f"/opinions/{opinion_id}/vote",
            json={"vote_type": "support"},
            headers=auth_headers_user
        )
        assert vote_response.status_code == 200

        # 獲取投票狀態
        response = test_client.get(
            f"/opinions/{opinion_id}/vote",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        data = response.json()
        assert "vote_type" in data
        assert data["vote_type"] in ["support", "oppose", None]

    def test_get_vote_status_for_nonexistent_opinion(
        self,
        test_client: TestClient,
        auth_headers_user
    ):
        """
        TC-OPIN-023: 獲取不存在意見的投票狀態
        測試目標: 驗證查詢不存在意見的投票狀態時返回 404
        優先級: Medium
        """
        non_existent_id = 999999

        response = test_client.get(
            f"/opinions/{non_existent_id}/vote",
            headers=auth_headers_user
        )

        assert response.status_code == 404

    def test_get_collect_status(
        self,
        test_client: TestClient,
        auth_headers_user,
        create_test_opinion
    ):
        """
        TC-OPIN-024: 獲取意見的收藏狀態
        測試目標: 驗證可以查詢用戶是否收藏了特定意見
        優先級: High
        """
        opinion_id = create_test_opinion.id

        # 先收藏
        collect_response = test_client.post(
            f"/opinions/{opinion_id}/collect",
            headers=auth_headers_user
        )
        assert collect_response.status_code == 200

        # 獲取收藏狀態
        response = test_client.get(
            f"/opinions/{opinion_id}/collect",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        data = response.json()
        assert "is_collected" in data
        assert data["is_collected"] is True

    def test_get_collect_status_not_collected(
        self,
        test_client: TestClient,
        auth_headers_user,
        create_test_opinion
    ):
        """
        TC-OPIN-025: 獲取未收藏意見的狀態
        測試目標: 驗證未收藏的意見返回 false
        優先級: Medium
        """
        opinion_id = create_test_opinion.id

        # 直接獲取收藏狀態 (未收藏)
        response = test_client.get(
            f"/opinions/{opinion_id}/collect",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        data = response.json()
        assert "is_collected" in data
        assert data["is_collected"] is False

    def test_get_collect_status_for_nonexistent_opinion(
        self,
        test_client: TestClient,
        auth_headers_user
    ):
        """
        TC-OPIN-026: 獲取不存在意見的收藏狀態
        測試目標: 驗證查詢不存在意見的收藏狀態時返回 404
        優先級: Medium
        """
        non_existent_id = 999999

        response = test_client.get(
            f"/opinions/{non_existent_id}/collect",
            headers=auth_headers_user
        )

        assert response.status_code == 404


class TestOpinionDeletion:
    """意見刪除測試類別"""

    def test_delete_own_opinion(
        self,
        test_client: TestClient,
        auth_headers_user,
        create_test_opinion
    ):
        """
        TC-OPIN-027: 刪除自己的意見
        測試目標: 驗證用戶可以刪除自己創建的意見
        優先級: High
        """
        opinion_id = create_test_opinion.id

        # 執行刪除
        response = test_client.delete(
            f"/opinions/{opinion_id}",
            headers=auth_headers_user
        )

        assert response.status_code == 200
        data = response.json()
        assert "message" in data

        # 驗證意見已被刪除
        get_response = test_client.get(f"/opinions/{opinion_id}")
        assert get_response.status_code == 404

    def test_delete_nonexistent_opinion(
        self,
        test_client: TestClient,
        auth_headers_user
    ):
        """
        TC-OPIN-028: 刪除不存在的意見
        測試目標: 驗證刪除不存在的意見時返回 404
        優先級: Medium
        """
        non_existent_id = 999999

        response = test_client.delete(
            f"/opinions/{non_existent_id}",
            headers=auth_headers_user
        )

        assert response.status_code == 404

    def test_delete_others_opinion(
        self,
        test_client: TestClient,
        auth_headers_user,
        create_test_opinion
    ):
        """
        TC-OPIN-029: 嘗試刪除他人的意見
        測試目標: 驗證用戶無法刪除他人創建的意見
        優先級: Critical
        """
        opinion_id = create_test_opinion.id

        # 創建另一個用戶
        register_response = test_client.post(
            "/auth/register",
            json={
                "username": "other_user",
                "email": "other@example.com",
                "password": "OtherPassword123!",
                "role": "citizen"
            }
        )

        if register_response.status_code == 201:
            # 登入另一個用戶
            login_response = test_client.post(
                "/auth/login",
                json={
                    "username": "other_user",
                    "password": "OtherPassword123!"
                }
            )
            other_token = login_response.json()["access_token"]
            other_headers = {"Authorization": f"Bearer {other_token}"}

            # 嘗試刪除他人的意見
            response = test_client.delete(
                f"/opinions/{opinion_id}",
                headers=other_headers
            )

            # 應該失敗 (404 或 403)
            assert response.status_code in [403, 404]
