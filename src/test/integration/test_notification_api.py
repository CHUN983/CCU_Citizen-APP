"""
通知系統 API 整合測試
測試案例對應: TC-NOT-001 ~ TC-NOT-008
需求對應: REQ-007 (通知系統)
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock


class TestNotificationRetrieval:
    """通知獲取測試類別"""

    def test_get_all_notifications(self, test_client: TestClient, auth_headers_user):
        """
        TC-NOT-001: 獲取所有通知
        測試目標: 驗證用戶能夠獲取自己的所有通知
        優先級: Critical
        """
        # Mock NotificationService 來模擬通知資料
        mock_notifications = [
            {
                "id": 1,
                "user_id": 1,
                "type": "approved",
                "title": "您的意見已被核准",
                "is_read": False,
                "created_at": "2025-10-24T10:00:00"
            },
            {
                "id": 2,
                "user_id": 1,
                "type": "comment",
                "title": "您的意見收到新留言",
                "is_read": True,
                "created_at": "2025-10-23T15:30:00"
            }
        ]

        with patch('api.notifications.NotificationService.get_user_notifications') as mock_get:
            mock_get.return_value = mock_notifications

            # 執行請求
            response = test_client.get("/notifications", headers=auth_headers_user)

            # 驗證結果
            assert response.status_code == 200, f"期望狀態碼 200，實際 {response.status_code}"

            data = response.json()
            assert isinstance(data, list), "回應應為通知陣列"
            assert len(data) == 2, "應該返回 2 個通知"
            assert data[0]["type"] == "opinion_approved"
            assert data[1]["type"] == "new_comment"

    def test_get_unread_notifications_only(self, test_client: TestClient, auth_headers_user):
        """
        TC-NOT-002: 僅獲取未讀通知
        測試目標: 驗證能夠篩選未讀通知
        優先級: High
        """
        mock_unread_notifications = [
            {
                "id": 1,
                "user_id": 1,
                "type": "approved",
                "title": "您的意見已被核准",
                "is_read": False,
                "created_at": "2025-10-24T10:00:00"
            }
        ]

        with patch('api.notifications.NotificationService.get_user_notifications') as mock_get:
            mock_get.return_value = mock_unread_notifications

            # 執行請求（僅未讀）
            response = test_client.get("/notifications?unread_only=true", headers=auth_headers_user)

            # 驗證結果
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1, "應該只返回 1 個未讀通知"
            assert data[0]["is_read"] is False, "通知應為未讀狀態"

    def test_get_notifications_without_auth(self, test_client: TestClient):
        """
        TC-NOT-003: 未認證用戶無法獲取通知
        測試目標: 驗證未登入用戶無法訪問通知
        優先級: Critical
        """
        # 不提供認證標頭
        response = test_client.get("/notifications")

        # 驗證結果
        assert response.status_code == 401, "應返回 401 Unauthorized"
        assert "not authenticated" in response.json()["detail"].lower()

    def test_get_empty_notifications(self, test_client: TestClient, auth_headers_user):
        """
        TC-NOT-004: 獲取空通知列表
        測試目標: 驗證新用戶或無通知時返回空陣列
        優先級: Medium
        """
        with patch('api.notifications.NotificationService.get_user_notifications') as mock_get:
            mock_get.return_value = []

            response = test_client.get("/notifications", headers=auth_headers_user)

            assert response.status_code == 200
            assert response.json() == [], "應返回空陣列"


class TestNotificationMarkAsRead:
    """通知已讀標記測試類別"""

    def test_mark_notification_as_read(self, test_client: TestClient, auth_headers_user):
        """
        TC-NOT-005: 標記通知為已讀
        測試目標: 驗證用戶能夠標記通知為已讀
        優先級: Critical
        """
        notification_id = 1

        with patch('api.notifications.NotificationService.mark_as_read') as mock_mark:
            mock_mark.return_value = True  # 成功標記

            # 執行標記請求
            response = test_client.post(
                f"/notifications/{notification_id}/read",
                headers=auth_headers_user
            )

            # 驗證結果
            assert response.status_code == 200, f"期望狀態碼 200，實際 {response.status_code}"
            assert "marked as read" in response.json()["message"].lower()

            # 驗證 service 被正確呼叫
            mock_mark.assert_called_once_with(notification_id, auth_headers_user["user_id"])

    def test_mark_nonexistent_notification(self, test_client: TestClient, auth_headers_user):
        """
        TC-NOT-006: 標記不存在的通知
        測試目標: 驗證標記不存在的通知返回 404
        優先級: High
        """
        notification_id = 99999  # 不存在的通知 ID

        with patch('api.notifications.NotificationService.mark_as_read') as mock_mark:
            mock_mark.return_value = False  # 標記失敗（通知不存在）

            response = test_client.post(
                f"/notifications/{notification_id}/read",
                headers=auth_headers_user
            )

            # 驗證結果
            assert response.status_code == 404, "應返回 404 Not Found"
            assert "not found" in response.json()["detail"].lower()

    def test_mark_other_user_notification(self, test_client: TestClient, auth_headers_user):
        """
        TC-NOT-007: 無法標記其他用戶的通知
        測試目標: 驗證用戶無法標記其他用戶的通知
        優先級: High
        """
        other_user_notification_id = 100

        with patch('api.notifications.NotificationService.mark_as_read') as mock_mark:
            # Service 應該檢查 user_id 並返回 False（權限不足）
            mock_mark.return_value = False

            response = test_client.post(
                f"/notifications/{other_user_notification_id}/read",
                headers=auth_headers_user
            )

            # 驗證結果
            assert response.status_code == 404, "應返回 404（隱藏權限錯誤）"


class TestNotificationTypes:
    """通知類型測試類別"""

    def test_opinion_approved_notification(self, test_client: TestClient, auth_headers_user):
        """
        TC-NOT-008: 意見核准通知
        測試目標: 驗證意見核准時會產生通知
        優先級: High
        """
        mock_notifications = [
            {
                "id": 1,
                "user_id": 1,
                "type": "approved",
                "title": "您的意見「改善公園設施」已被核准",
                "related_id": 123,  # 意見 ID
                "is_read": False,
                "created_at": "2025-10-24T10:00:00"
            }
        ]

        with patch('api.notifications.NotificationService.get_user_notifications') as mock_get:
            mock_get.return_value = mock_notifications

            response = test_client.get("/notifications", headers=auth_headers_user)

            assert response.status_code == 200
            data = response.json()
            assert data[0]["type"] == "opinion_approved", "通知類型應為 opinion_approved"
            assert "related_id" in data[0], "應包含關聯的意見 ID"

    def test_new_comment_notification(self, test_client: TestClient, auth_headers_user):
        """
        TC-NOT-009: 新留言通知
        測試目標: 驗證收到新留言時會產生通知
        優先級: High
        """
        mock_notifications = [
            {
                "id": 2,
                "user_id": 1,
                "type": "comment",
                "title": "user123 在您的意見下留言",
                "related_id": 456,  # 留言 ID
                "is_read": False,
                "created_at": "2025-10-24T11:00:00"
            }
        ]

        with patch('api.notifications.NotificationService.get_user_notifications') as mock_get:
            mock_get.return_value = mock_notifications

            response = test_client.get("/notifications", headers=auth_headers_user)

            assert response.status_code == 200
            data = response.json()
            assert data[0]["type"] == "new_comment", "通知類型應為 new_comment"

    def test_vote_notification(self, test_client: TestClient, auth_headers_user):
        """
        TC-NOT-010: 投票通知
        測試目標: 驗證意見獲得投票時會產生通知（達到里程碑時）
        優先級: Medium
        """
        mock_notifications = [
            {
                "id": 3,
                "user_id": 1,
                "type": "status_change",
                "title": "您的意見已獲得 100 票支持！",
                "related_id": 789,  # 意見 ID
                "is_read": False,
                "created_at": "2025-10-24T12:00:00"
            }
        ]

        with patch('api.notifications.NotificationService.get_user_notifications') as mock_get:
            mock_get.return_value = mock_notifications

            response = test_client.get("/notifications", headers=auth_headers_user)

            assert response.status_code == 200
            data = response.json()
            assert data[0]["type"] == "vote_milestone", "通知類型應為 vote_milestone"

    def test_opinion_rejected_notification(self, test_client: TestClient, auth_headers_user):
        """
        TC-NOT-011: 意見被拒絕通知
        測試目標: 驗證意見被拒絕時會產生通知
        優先級: High
        """
        mock_notifications = [
            {
                "id": 4,
                "user_id": 1,
                "type": "rejected",
                "title": "您的意見已被拒絕：內容違反社群規範",
                "related_id": 321,
                "is_read": False,
                "created_at": "2025-10-24T13:00:00"
            }
        ]

        with patch('api.notifications.NotificationService.get_user_notifications') as mock_get:
            mock_get.return_value = mock_notifications

            response = test_client.get("/notifications", headers=auth_headers_user)

            assert response.status_code == 200
            data = response.json()
            assert data[0]["type"] == "opinion_rejected", "通知類型應為 opinion_rejected"


class TestNotificationPagination:
    """通知分頁測試類別（未來擴展）"""

    @pytest.mark.skip(reason="分頁功能尚未實作")
    def test_get_notifications_with_pagination(self, test_client: TestClient, auth_headers_user):
        """
        TC-NOT-012: 分頁獲取通知
        測試目標: 驗證通知列表支援分頁
        優先級: Low
        """
        # 當 API 支援分頁時，測試分頁功能
        response = test_client.get("/notifications?page=1&limit=10", headers=auth_headers_user)

        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data


class TestNotificationIntegration:
    """通知整合測試類別"""

    def test_notification_workflow(self, test_client: TestClient, auth_headers_user, auth_headers_admin):
        """
        TC-NOT-013: 完整通知流程
        測試目標: 驗證從意見核准到通知接收的完整流程
        優先級: High
        """
        # 模擬完整流程:
        # 1. 用戶發表意見
        # 2. 管理員核准意見
        # 3. 用戶收到核准通知
        # 4. 用戶標記通知為已讀

        # 步驟 1: 建立意見（假設已完成）
        # 步驟 2: 核准意見（假設已完成）

        # 步驟 3: 檢查通知
        mock_notifications = [
            {
                "id": 1,
                "user_id": 1,
                "type": "approved",
                "title": "您的意見已被核准",
                "is_read": False,
                "created_at": "2025-10-24T10:00:00"
            }
        ]

        with patch('api.notifications.NotificationService.get_user_notifications') as mock_get:
            mock_get.return_value = mock_notifications

            # 獲取通知
            get_response = test_client.get("/notifications", headers=auth_headers_user)
            assert get_response.status_code == 200
            notifications = get_response.json()
            assert len(notifications) == 1
            assert notifications[0]["is_read"] is False

        # 步驟 4: 標記為已讀
        with patch('api.notifications.NotificationService.mark_as_read') as mock_mark:
            mock_mark.return_value = True

            mark_response = test_client.post(
                "/notifications/1/read",
                headers=auth_headers_user
            )
            assert mark_response.status_code == 200

    def test_multiple_users_notifications_isolation(
        self,
        test_client: TestClient,
        auth_headers_user,
        create_test_admin,
        test_admin_data
    ):
        """
        TC-NOT-014: 多用戶通知隔離
        測試目標: 驗證不同用戶的通知互不干擾
        優先級: Critical
        """
        # 用戶 1 的通知
        user1_notifications = [
            {"id": 1, "user_id": 1, "title": "User 1 notification", "is_read": False}
        ]

        # 用戶 2（管理員）的通知
        user2_notifications = [
            {"id": 2, "user_id": 2, "title": "Admin notification", "is_read": False}
        ]

        # 測試用戶 1
        with patch('api.notifications.NotificationService.get_user_notifications') as mock_get:
            mock_get.return_value = user1_notifications

            response1 = test_client.get("/notifications", headers=auth_headers_user)
            assert response1.status_code == 200
            assert len(response1.json()) == 1
            assert response1.json()[0]["message"] == "User 1 notification"

        # 登入管理員並獲取 token
        admin_login = test_client.post("/auth/login", json={
            "username": test_admin_data["username"],
            "password": test_admin_data["password"]
        })
        admin_token = admin_login.json()["access_token"]
        auth_headers_admin_real = {"Authorization": f"Bearer {admin_token}"}

        # 測試管理員
        with patch('api.notifications.NotificationService.get_user_notifications') as mock_get:
            mock_get.return_value = user2_notifications

            response2 = test_client.get("/notifications", headers=auth_headers_admin_real)
            assert response2.status_code == 200
            assert len(response2.json()) == 1
            assert response2.json()[0]["message"] == "Admin notification"


# ==================== 性能測試 ====================

@pytest.mark.slow
class TestNotificationPerformance:
    """通知系統性能測試"""

    def test_concurrent_notification_reads(self, test_client: TestClient, auth_headers_user):
        """
        測試並發讀取通知
        測試目標: 驗證系統能處理多個同時讀取通知請求
        優先級: Medium
        """
        import concurrent.futures

        mock_notifications = [
            {"id": i, "user_id": 1, "title": f"Notification {i}", "is_read": False}
            for i in range(10)
        ]

        with patch('api.notifications.NotificationService.get_user_notifications') as mock_get:
            mock_get.return_value = mock_notifications

            def get_notifications():
                return test_client.get("/notifications", headers=auth_headers_user)

            # 執行 10 個並發請求
            with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(get_notifications) for _ in range(10)]
                results = [future.result() for future in futures]

            # 驗證所有請求都成功
            assert all(r.status_code == 200 for r in results), "所有請求應該成功"

    def test_large_notification_list(self, test_client: TestClient, auth_headers_user):
        """
        測試大量通知列表
        測試目標: 驗證系統能處理大量通知
        優先級: Low
        """
        # 模擬 1000 個通知
        large_notification_list = [
            {
                "id": i,
                "user_id": 1,
                "type": "comment",
                "title": f"Notification {i}",
                "is_read": i % 2 == 0,
                "created_at": f"2025-10-{(i % 30) + 1:02d}T10:00:00"
            }
            for i in range(1000)
        ]

        with patch('api.notifications.NotificationService.get_user_notifications') as mock_get:
            mock_get.return_value = large_notification_list

            response = test_client.get("/notifications", headers=auth_headers_user)

            assert response.status_code == 200
            assert len(response.json()) == 1000, "應該返回 1000 個通知"
