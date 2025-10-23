"""
審核模組 API 整合測試
測試案例對應: TC-MOD-001 ~ TC-MOD-010
需求對應: REQ-008 (管理審核功能), REQ-009 (權限控制系統)
"""

import pytest
from fastapi.testclient import TestClient


class TestOpinionApproval:
    """意見核准測試類別"""

    def test_approve_opinion_success(
        self,
        test_client: TestClient,
        auth_headers_admin,
        create_test_opinion
    ):
        """
        TC-MOD-001: 管理員成功核准意見
        測試目標: 驗證管理員能夠核准待審意見
        優先級: Critical
        """
        opinion_id = create_test_opinion.id

        # 執行核准請求
        response = test_client.post(
            f"/admin/opinions/{opinion_id}/approve",
            headers=auth_headers_admin
        )

        # 驗證結果
        assert response.status_code == 200
        assert "message" in response.json() or "success" in str(response.json()).lower()

        # 驗證意見狀態已更新
        opinion_response = test_client.get(f"/opinions/{opinion_id}")
        assert opinion_response.status_code == 200
        assert opinion_response.json()["status"] == "approved"

    def test_approve_opinion_without_permission(
        self,
        test_client: TestClient,
        auth_headers_user,
        create_test_opinion
    ):
        """
        TC-MOD-002: 普通用戶無權核准意見
        測試目標: 驗證權限控制正確運作
        優先級: Critical
        """
        opinion_id = create_test_opinion.id

        # 使用普通用戶 Token 嘗試核准
        response = test_client.post(
            f"/admin/opinions/{opinion_id}/approve",
            headers=auth_headers_user
        )

        # 驗證結果
        assert response.status_code == 403
        assert "insufficient" in response.json()["detail"].lower() or \
               "permission" in response.json()["detail"].lower()

    def test_approve_nonexistent_opinion(
        self,
        test_client: TestClient,
        auth_headers_admin
    ):
        """
        測試核准不存在的意見失敗
        測試目標: 驗證不存在的意見無法核准
        優先級: High
        """
        # 使用不存在的意見 ID
        response = test_client.post(
            "/admin/opinions/99999/approve",
            headers=auth_headers_admin
        )

        # 驗證結果
        assert response.status_code in [400, 404]

    def test_approve_without_auth(
        self,
        test_client: TestClient,
        create_test_opinion
    ):
        """
        測試未登入核准失敗
        測試目標: 驗證未認證請求被拒絕
        優先級: Critical
        """
        opinion_id = create_test_opinion.id

        # 不提供認證標頭
        response = test_client.post(f"/admin/opinions/{opinion_id}/approve")

        # 驗證結果
        assert response.status_code == 401


class TestOpinionRejection:
    """意見拒絕測試類別"""

    def test_reject_opinion_success(
        self,
        test_client: TestClient,
        auth_headers_admin,
        create_test_opinion
    ):
        """
        TC-MOD-003: 管理員成功拒絕意見
        測試目標: 驗證管理員能夠拒絕待審意見
        優先級: Critical
        """
        opinion_id = create_test_opinion.id

        reject_data = {
            "reason": "內容不符合社區規範"
        }

        # 執行拒絕請求
        response = test_client.post(
            f"/admin/opinions/{opinion_id}/reject",
            json=reject_data,
            headers=auth_headers_admin
        )

        # 驗證結果
        assert response.status_code == 200
        assert "message" in response.json()

        # 驗證意見狀態已更新
        opinion_response = test_client.get(f"/opinions/{opinion_id}")
        assert opinion_response.status_code == 200
        assert opinion_response.json()["status"] == "rejected"

    def test_reject_opinion_without_reason(
        self,
        test_client: TestClient,
        auth_headers_admin,
        create_test_opinion
    ):
        """
        TC-MOD-004: 不提供原因拒絕意見
        測試目標: 驗證系統處理空原因的邏輯
        優先級: Medium
        """
        opinion_id = create_test_opinion.id

        reject_data = {
            "reason": ""  # 空原因
        }

        # 執行拒絕請求
        response = test_client.post(
            f"/admin/opinions/{opinion_id}/reject",
            json=reject_data,
            headers=auth_headers_admin
        )

        # 驗證結果（根據業務邏輯，可能接受或拒絕）
        # 如果系統允許空原因
        assert response.status_code in [200, 400, 422]

    def test_reject_opinion_without_permission(
        self,
        test_client: TestClient,
        auth_headers_user,
        create_test_opinion
    ):
        """
        測試普通用戶無權拒絕意見
        測試目標: 驗證權限控制
        優先級: Critical
        """
        opinion_id = create_test_opinion.id

        reject_data = {
            "reason": "測試拒絕"
        }

        # 使用普通用戶 Token
        response = test_client.post(
            f"/admin/opinions/{opinion_id}/reject",
            json=reject_data,
            headers=auth_headers_user
        )

        # 驗證結果
        assert response.status_code == 403

    def test_reject_nonexistent_opinion(
        self,
        test_client: TestClient,
        auth_headers_admin
    ):
        """
        測試拒絕不存在的意見失敗
        測試目標: 驗證錯誤處理
        優先級: High
        """
        reject_data = {
            "reason": "測試拒絕"
        }

        response = test_client.post(
            "/admin/opinions/99999/reject",
            json=reject_data,
            headers=auth_headers_admin
        )

        # 驗證結果
        assert response.status_code in [400, 404]


class TestOpinionMerge:
    """意見合併測試類別"""

    def test_merge_opinions_success(
        self,
        test_client: TestClient,
        auth_headers_admin,
        create_multiple_opinions
    ):
        """
        TC-MOD-005: 成功合併意見
        測試目標: 驗證管理員能夠合併重複意見
        優先級: High
        """
        # 使用前兩個意見進行合併測試
        source_id = create_multiple_opinions[0].id
        target_id = create_multiple_opinions[1].id

        merge_data = {
            "target_id": target_id
        }

        # 執行合併請求
        response = test_client.post(
            f"/admin/opinions/{source_id}/merge",
            json=merge_data,
            headers=auth_headers_admin
        )

        # 驗證結果
        assert response.status_code == 200
        assert "message" in response.json()

    def test_merge_with_nonexistent_target(
        self,
        test_client: TestClient,
        auth_headers_admin,
        create_test_opinion
    ):
        """
        TC-MOD-006: 合併到不存在的目標失敗
        測試目標: 驗證目標意見存在性檢查
        優先級: High
        """
        source_id = create_test_opinion.id

        merge_data = {
            "target_id": 99999  # 不存在的目標
        }

        # 執行合併請求
        response = test_client.post(
            f"/admin/opinions/{source_id}/merge",
            json=merge_data,
            headers=auth_headers_admin
        )

        # 驗證結果
        assert response.status_code == 400
        assert "failed" in response.json()["detail"].lower()

    def test_merge_without_permission(
        self,
        test_client: TestClient,
        auth_headers_user,
        create_multiple_opinions
    ):
        """
        測試普通用戶無權合併意見
        測試目標: 驗證權限控制
        優先級: High
        """
        source_id = create_multiple_opinions[0].id
        target_id = create_multiple_opinions[1].id

        merge_data = {
            "target_id": target_id
        }

        # 使用普通用戶 Token
        response = test_client.post(
            f"/admin/opinions/{source_id}/merge",
            json=merge_data,
            headers=auth_headers_user
        )

        # 驗證結果
        assert response.status_code == 403

    def test_merge_opinion_with_itself(
        self,
        test_client: TestClient,
        auth_headers_admin,
        create_test_opinion
    ):
        """
        測試意見與自己合併失敗
        測試目標: 驗證邊界條件處理
        優先級: Medium
        """
        opinion_id = create_test_opinion.id

        merge_data = {
            "target_id": opinion_id  # 目標是自己
        }

        # 執行合併請求
        response = test_client.post(
            f"/admin/opinions/{opinion_id}/merge",
            json=merge_data,
            headers=auth_headers_admin
        )

        # 驗證結果（應該被拒絕）
        assert response.status_code == 400


class TestCommentDeletion:
    """留言刪除測試類別"""

    def test_delete_comment_success(
        self,
        test_client: TestClient,
        auth_headers_admin,
        auth_headers_user,
        create_test_opinion
    ):
        """
        TC-MOD-007: 管理員成功刪除留言
        測試目標: 驗證管理員能夠刪除不當留言
        優先級: Critical
        """
        opinion_id = create_test_opinion.id

        # 先建立一個留言
        comment_data = {"content": "測試留言"}
        comment_response = test_client.post(
            f"/opinions/{opinion_id}/comments",
            json=comment_data,
            headers=auth_headers_user
        )
        assert comment_response.status_code == 201
        comment_id = comment_response.json()["id"]

        # 執行刪除請求
        delete_response = test_client.delete(
            f"/admin/comments/{comment_id}",
            headers=auth_headers_admin
        )

        # 驗證結果
        assert delete_response.status_code == 200
        assert "message" in delete_response.json()

    def test_delete_nonexistent_comment(
        self,
        test_client: TestClient,
        auth_headers_admin
    ):
        """
        TC-MOD-008: 刪除不存在的留言失敗
        測試目標: 驗證錯誤處理
        優先級: Medium
        """
        # 使用不存在的留言 ID
        response = test_client.delete(
            "/admin/comments/99999",
            headers=auth_headers_admin
        )

        # 驗證結果
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_delete_comment_without_permission(
        self,
        test_client: TestClient,
        auth_headers_user,
        create_test_opinion
    ):
        """
        測試普通用戶無權刪除留言
        測試目標: 驗證權限控制
        優先級: Critical
        """
        opinion_id = create_test_opinion.id

        # 建立留言
        comment_data = {"content": "測試留言"}
        comment_response = test_client.post(
            f"/opinions/{opinion_id}/comments",
            json=comment_data,
            headers=auth_headers_user
        )
        assert comment_response.status_code == 201
        comment_id = comment_response.json()["id"]

        # 嘗試刪除（使用普通用戶權限）
        delete_response = test_client.delete(
            f"/admin/comments/{comment_id}",
            headers=auth_headers_user
        )

        # 驗證結果
        assert delete_response.status_code == 403


class TestCategoryUpdate:
    """分類更新測試類別"""

    def test_update_opinion_category_success(
        self,
        test_client: TestClient,
        auth_headers_admin,
        create_test_opinion
    ):
        """
        TC-MOD-009: 管理員成功更新意見分類
        測試目標: 驗證管理員能夠更新意見分類
        優先級: Medium
        """
        opinion_id = create_test_opinion.id

        update_data = {
            "category_id": 3
        }

        # 執行更新請求
        response = test_client.put(
            f"/admin/opinions/{opinion_id}/category",
            json=update_data,
            headers=auth_headers_admin
        )

        # 驗證結果
        assert response.status_code == 200
        assert "message" in response.json()

    def test_update_category_with_invalid_id(
        self,
        test_client: TestClient,
        auth_headers_admin,
        create_test_opinion
    ):
        """
        TC-MOD-010: 使用無效分類 ID 更新失敗
        測試目標: 驗證分類 ID 驗證
        優先級: Medium
        """
        opinion_id = create_test_opinion.id

        update_data = {
            "category_id": 99999  # 不存在的分類
        }

        # 執行更新請求
        response = test_client.put(
            f"/admin/opinions/{opinion_id}/category",
            json=update_data,
            headers=auth_headers_admin
        )

        # 驗證結果
        assert response.status_code == 400
        assert "failed" in response.json()["detail"].lower()

    def test_update_category_without_permission(
        self,
        test_client: TestClient,
        auth_headers_user,
        create_test_opinion
    ):
        """
        測試普通用戶無權更新分類
        測試目標: 驗證權限控制
        優先級: Medium
        """
        opinion_id = create_test_opinion.id

        update_data = {
            "category_id": 2
        }

        # 使用普通用戶 Token
        response = test_client.put(
            f"/admin/opinions/{opinion_id}/category",
            json=update_data,
            headers=auth_headers_user
        )

        # 驗證結果
        assert response.status_code == 403


# ==================== 權限與角色測試 ====================

class TestModeratorPermissions:
    """審核員權限測試類別"""

    def test_moderator_can_approve(
        self,
        test_client: TestClient,
        test_moderator_data,
        test_db_session,
        create_test_opinion
    ):
        """
        測試審核員可以核准意見
        測試目標: 驗證審核員擁有審核權限
        優先級: High
        """
        from models.user import User
        from utils.security import hash_password

        # 建立審核員
        moderator = User(
            username=test_moderator_data["username"],
            email=test_moderator_data["email"],
            password_hash=hash_password(test_moderator_data["password"]),
            role=test_moderator_data["role"]
        )
        test_db_session.add(moderator)
        test_db_session.commit()

        # 登入獲取 Token
        login_response = test_client.post(
            "/auth/login",
            json={
                "username": test_moderator_data["username"],
                "password": test_moderator_data["password"]
            }
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        moderator_headers = {"Authorization": f"Bearer {token}"}

        # 嘗試核准意見
        opinion_id = create_test_opinion.id
        response = test_client.post(
            f"/admin/opinions/{opinion_id}/approve",
            headers=moderator_headers
        )

        # 驗證結果
        assert response.status_code == 200


# ==================== 整合測試 ====================

class TestModerationWorkflow:
    """審核工作流程整合測試"""

    def test_complete_moderation_workflow(
        self,
        test_client: TestClient,
        auth_headers_user,
        auth_headers_admin,
        test_opinion_data
    ):
        """
        完整的審核工作流程測試
        測試目標: 驗證從意見建立到審核的完整流程
        優先級: Critical
        """
        # 1. 用戶建立意見
        create_response = test_client.post(
            "/opinions",
            json=test_opinion_data,
            headers=auth_headers_user
        )
        assert create_response.status_code == 201
        opinion_id = create_response.json()["id"]

        # 2. 驗證意見狀態為待審
        detail_response = test_client.get(f"/opinions/{opinion_id}")
        assert detail_response.json()["status"] in ["draft", "pending"]

        # 3. 管理員核准意見
        approve_response = test_client.post(
            f"/admin/opinions/{opinion_id}/approve",
            headers=auth_headers_admin
        )
        assert approve_response.status_code == 200

        # 4. 驗證意見狀態已更新為已核准
        final_response = test_client.get(f"/opinions/{opinion_id}")
        assert final_response.json()["status"] == "approved"

    def test_rejection_workflow(
        self,
        test_client: TestClient,
        auth_headers_user,
        auth_headers_admin,
        test_opinion_data
    ):
        """
        拒絕工作流程測試
        測試目標: 驗證拒絕意見的完整流程
        優先級: High
        """
        # 1. 建立意見
        create_response = test_client.post(
            "/opinions",
            json=test_opinion_data,
            headers=auth_headers_user
        )
        assert create_response.status_code == 201
        opinion_id = create_response.json()["id"]

        # 2. 管理員拒絕意見
        reject_data = {"reason": "測試拒絕原因"}
        reject_response = test_client.post(
            f"/admin/opinions/{opinion_id}/reject",
            json=reject_data,
            headers=auth_headers_admin
        )
        assert reject_response.status_code == 200

        # 3. 驗證狀態
        final_response = test_client.get(f"/opinions/{opinion_id}")
        assert final_response.json()["status"] == "rejected"


# ==================== 批量操作測試 ====================

@pytest.mark.slow
class TestBatchModeration:
    """批量審核測試類別"""

    def test_approve_multiple_opinions(
        self,
        test_client: TestClient,
        auth_headers_admin,
        create_multiple_opinions
    ):
        """
        測試批量核准意見
        測試目標: 驗證能夠批量處理多個意見
        優先級: Medium
        """
        success_count = 0

        for opinion in create_multiple_opinions[:3]:  # 核准前 3 個
            response = test_client.post(
                f"/admin/opinions/{opinion.id}/approve",
                headers=auth_headers_admin
            )
            if response.status_code == 200:
                success_count += 1

        # 驗證至少成功核准了一些意見
        assert success_count > 0
