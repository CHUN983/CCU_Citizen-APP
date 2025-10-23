"""
認證 API 整合測試
測試案例對應: TC-AUTH-001 ~ TC-AUTH-010
需求對應: REQ-001 (用戶認證系統)
"""

import pytest
from fastapi.testclient import TestClient


class TestUserRegistration:
    """用戶註冊測試類別"""

    def test_register_success(self, test_client: TestClient):
        """
        TC-AUTH-001: 用戶成功註冊
        測試目標: 驗證用戶能夠使用有效資料成功註冊
        優先級: Critical
        """
        # 準備測試資料
        user_data = {
            "username": "newuser001",
            "email": "newuser001@example.com",
            "password": "SecurePass123!",
            "role": "citizen"
        }

        # 執行註冊請求
        response = test_client.post("/auth/register", json=user_data)

        # 驗證結果
        assert response.status_code == 201, f"期望狀態碼 201，實際 {response.status_code}"

        data = response.json()
        assert "id" in data, "回應應包含用戶 ID"
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert "password" not in data, "回應不應包含密碼"
        assert "password_hash" not in data, "回應不應包含密碼雜湊"

    def test_register_duplicate_username(self, test_client: TestClient, create_test_user):
        """
        TC-AUTH-002: 註冊重複用戶名失敗
        測試目標: 驗證系統拒絕重複的用戶名
        優先級: High
        """
        # 使用已存在用戶的用戶名
        duplicate_data = {
            "username": create_test_user.username,  # 重複的用戶名
            "email": "different@example.com",
            "password": "SecurePass123!",
            "role": "citizen"
        }

        # 執行註冊請求
        response = test_client.post("/auth/register", json=duplicate_data)

        # 驗證結果
        assert response.status_code == 400, f"期望狀態碼 400，實際 {response.status_code}"

        data = response.json()
        assert "detail" in data
        assert "already exists" in data["detail"].lower()

    def test_register_duplicate_email(self, test_client: TestClient, create_test_user):
        """
        TC-AUTH-003: 註冊重複郵箱失敗
        測試目標: 驗證系統拒絕重複的郵箱
        優先級: High
        """
        # 使用已存在用戶的郵箱
        duplicate_data = {
            "username": "differentuser",
            "email": create_test_user.email,  # 重複的郵箱
            "password": "SecurePass123!",
            "role": "citizen"
        }

        # 執行註冊請求
        response = test_client.post("/auth/register", json=duplicate_data)

        # 驗證結果
        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_register_invalid_email_format(self, test_client: TestClient):
        """
        TC-AUTH-003: 無效郵箱格式註冊失敗
        測試目標: 驗證系統檢查郵箱格式
        優先級: High
        """
        # 無效的郵箱格式
        invalid_data = {
            "username": "testuser002",
            "email": "invalid-email-format",  # 無效格式
            "password": "SecurePass123!",
            "role": "citizen"
        }

        # 執行註冊請求
        response = test_client.post("/auth/register", json=invalid_data)

        # 驗證結果
        assert response.status_code == 422, "應返回驗證錯誤"

    def test_register_weak_password(self, test_client: TestClient):
        """
        測試弱密碼註冊失敗
        測試目標: 驗證密碼強度要求
        優先級: High
        """
        # 過短的密碼
        weak_data = {
            "username": "testuser003",
            "email": "test003@example.com",
            "password": "123",  # 過短
            "role": "citizen"
        }

        # 執行註冊請求
        response = test_client.post("/auth/register", json=weak_data)

        # 驗證結果 (根據實際實作可能是 400 或 422)
        assert response.status_code in [400, 422]

    def test_register_missing_required_fields(self, test_client: TestClient):
        """
        測試缺少必填欄位註冊失敗
        測試目標: 驗證必填欄位檢查
        優先級: High
        """
        # 缺少密碼
        incomplete_data = {
            "username": "testuser004",
            "email": "test004@example.com"
            # 缺少 password
        }

        # 執行註冊請求
        response = test_client.post("/auth/register", json=incomplete_data)

        # 驗證結果
        assert response.status_code == 422, "應返回驗證錯誤"


class TestUserLogin:
    """用戶登入測試類別"""

    def test_login_success(self, test_client: TestClient, test_user_data, create_test_user):
        """
        TC-AUTH-004: 用戶成功登入
        測試目標: 驗證用戶能夠使用正確憑證登入並獲取 Token
        優先級: Critical
        """
        # 準備登入資料
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }

        # 執行登入請求
        response = test_client.post("/auth/login", json=login_data)

        # 驗證結果
        assert response.status_code == 200, f"期望狀態碼 200，實際 {response.status_code}"

        data = response.json()
        assert "access_token" in data, "回應應包含 access_token"
        assert "token_type" in data, "回應應包含 token_type"
        assert data["token_type"] == "bearer", "Token 類型應為 bearer"
        assert len(data["access_token"]) > 0, "Token 不應為空"

    def test_login_wrong_password(self, test_client: TestClient, test_user_data, create_test_user):
        """
        TC-AUTH-005: 錯誤密碼登入失敗
        測試目標: 驗證系統拒絕錯誤密碼
        優先級: Critical
        """
        # 使用錯誤密碼
        wrong_data = {
            "username": test_user_data["username"],
            "password": "WrongPassword123!"  # 錯誤的密碼
        }

        # 執行登入請求
        response = test_client.post("/auth/login", json=wrong_data)

        # 驗證結果
        assert response.status_code == 401, f"期望狀態碼 401，實際 {response.status_code}"

        data = response.json()
        assert "detail" in data
        assert "incorrect" in data["detail"].lower()

    def test_login_nonexistent_user(self, test_client: TestClient):
        """
        TC-AUTH-006: 不存在的用戶登入失敗
        測試目標: 驗證系統拒絕不存在的用戶
        優先級: High
        """
        # 不存在的用戶
        nonexistent_data = {
            "username": "nonexistentuser999",
            "password": "AnyPassword123!"
        }

        # 執行登入請求
        response = test_client.post("/auth/login", json=nonexistent_data)

        # 驗證結果
        assert response.status_code == 401
        # 不應透露用戶是否存在（安全考量）
        assert "incorrect" in response.json()["detail"].lower()

    def test_login_empty_credentials(self, test_client: TestClient):
        """
        測試空憑證登入失敗
        測試目標: 驗證空憑證被拒絕
        優先級: Medium
        """
        # 空憑證
        empty_data = {
            "username": "",
            "password": ""
        }

        # 執行登入請求
        response = test_client.post("/auth/login", json=empty_data)

        # 驗證結果
        assert response.status_code in [401, 422]


class TestUserAuthentication:
    """用戶認證與 Token 測試類別"""

    def test_get_current_user_with_valid_token(
        self,
        test_client: TestClient,
        auth_headers_user,
        test_user_data
    ):
        """
        TC-AUTH-007: 使用有效 Token 獲取當前用戶資訊
        測試目標: 驗證有效 Token 能夠獲取用戶資訊
        優先級: Critical
        """
        # 使用有效 Token 請求用戶資訊
        response = test_client.get("/auth/me", headers=auth_headers_user)

        # 驗證結果
        assert response.status_code == 200, f"期望狀態碼 200，實際 {response.status_code}"

        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert "password" not in data
        assert "password_hash" not in data

    def test_get_current_user_with_invalid_token(self, test_client: TestClient):
        """
        TC-AUTH-008: 使用無效 Token 被拒絕
        測試目標: 驗證無效 Token 被拒絕
        優先級: Critical
        """
        # 使用無效 Token
        invalid_headers = {"Authorization": "Bearer invalid_token_string"}

        # 執行請求
        response = test_client.get("/auth/me", headers=invalid_headers)

        # 驗證結果
        assert response.status_code == 401
        assert "invalid" in response.json()["detail"].lower() or \
               "expired" in response.json()["detail"].lower()

    def test_get_current_user_without_token(self, test_client: TestClient):
        """
        TC-AUTH-009: 不提供 Token 被拒絕
        測試目標: 驗證缺少 Token 的請求被拒絕
        優先級: High
        """
        # 不提供 Authorization Header
        response = test_client.get("/auth/me")

        # 驗證結果
        assert response.status_code == 401
        assert "not authenticated" in response.json()["detail"].lower()

    def test_get_current_user_with_malformed_header(self, test_client: TestClient):
        """
        測試格式錯誤的 Authorization Header
        測試目標: 驗證格式錯誤的 Header 被拒絕
        優先級: Medium
        """
        # 格式錯誤的 Header (缺少 "Bearer" 前綴)
        malformed_headers = {"Authorization": "some_token_without_bearer"}

        # 執行請求
        response = test_client.get("/auth/me", headers=malformed_headers)

        # 驗證結果
        assert response.status_code == 401


class TestTokenValidation:
    """Token 驗證測試類別"""

    def test_token_contains_user_info(self, test_client: TestClient, auth_headers_user):
        """
        TC-AUTH-010: Token 包含正確的用戶資訊
        測試目標: 驗證 Token 解析後包含正確資訊
        優先級: High
        """
        # 使用 Token 獲取用戶資訊
        response = test_client.get("/auth/me", headers=auth_headers_user)

        assert response.status_code == 200
        data = response.json()

        # 驗證包含必要欄位
        assert "id" in data or "user_id" in data
        assert "username" in data
        assert "email" in data
        assert "role" in data

    def test_token_expires_correctly(self, test_client: TestClient):
        """
        測試 Token 過期處理
        測試目標: 驗證過期 Token 被正確拒絕
        優先級: High
        注意: 這個測試需要等待 Token 過期，或使用手動生成的過期 Token
        """
        # 這裡應該使用手動生成的過期 Token 進行測試
        # 實作細節取決於專案的 JWT 配置
        pytest.skip("需要實作過期 Token 生成邏輯")


class TestRoleBasedAccess:
    """角色權限測試類別"""

    def test_admin_role_authentication(
        self,
        test_client: TestClient,
        test_admin_data,
        create_test_admin
    ):
        """
        測試管理員角色認證
        測試目標: 驗證管理員能夠登入並獲取正確角色
        優先級: Critical
        """
        # 管理員登入
        login_data = {
            "username": test_admin_data["username"],
            "password": test_admin_data["password"]
        }

        response = test_client.post("/auth/login", json=login_data)
        assert response.status_code == 200

        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 獲取用戶資訊驗證角色
        user_response = test_client.get("/auth/me", headers=headers)
        assert user_response.status_code == 200

        user_data = user_response.json()
        assert user_data["role"] == "admin"

    def test_moderator_role_authentication(
        self,
        test_client: TestClient,
        test_moderator_data,
        test_db_session
    ):
        """
        測試審核員角色認證
        測試目標: 驗證審核員能夠登入並獲取正確角色
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

        # 審核員登入
        login_data = {
            "username": test_moderator_data["username"],
            "password": test_moderator_data["password"]
        }

        response = test_client.post("/auth/login", json=login_data)
        assert response.status_code == 200

        token = response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}

        # 驗證角色
        user_response = test_client.get("/auth/me", headers=headers)
        assert user_response.status_code == 200
        assert user_response.json()["role"] == "moderator"


# ==================== 性能與安全測試 ====================

@pytest.mark.slow
class TestAuthenticationPerformance:
    """認證性能測試"""

    def test_concurrent_logins(self, test_client: TestClient, create_test_user, test_user_data):
        """
        測試並發登入
        測試目標: 驗證系統能處理多個同時登入請求
        優先級: Medium
        """
        import concurrent.futures

        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }

        def perform_login():
            return test_client.post("/auth/login", json=login_data)

        # 執行 10 個並發登入
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(perform_login) for _ in range(10)]
            results = [future.result() for future in futures]

        # 驗證所有請求都成功
        for response in results:
            assert response.status_code == 200
            assert "access_token" in response.json()
