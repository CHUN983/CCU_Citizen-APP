"""
E2E 測試: 認證流程
測試範圍: 註冊、登入、登出、token 驗證等完整流程
測試案例對應: TC-E2E-AUTH-001 ~ TC-E2E-AUTH-010
"""

import pytest
import requests


@pytest.mark.system
@pytest.mark.e2e
class TestAuthenticationE2E:
    """認證流程端到端測試"""

    def test_user_registration_and_login_flow(self, api_client):
        """
        TC-E2E-AUTH-001: 完整的用戶註冊和登入流程
        測試目標: 驗證用戶可以註冊、登入並獲取 token
        優先級: Critical
        """
        # Step 1: 註冊新用戶
        unique_username = f"e2e_user_{int(pytest.timestamp() * 1000)}"
        registration_data = {
            "username": unique_username,
            "email": f"{unique_username}@test.com",
            "password": "SecurePassword123!",
            "full_name": "E2E Test User"
        }

        register_response = api_client.post("/auth/register", json=registration_data)

        # 驗證註冊成功 (或用戶已存在)
        assert register_response.status_code in [200, 201, 400], \
            f"註冊失敗: {register_response.status_code}"

        # Step 2: 使用新註冊的憑證登入
        login_response = api_client.login(unique_username, "SecurePassword123!")

        # 驗證登入成功
        assert login_response.status_code == 200, \
            f"登入失敗: {login_response.status_code}"

        # Step 3: 驗證返回的 token
        login_data = login_response.json()
        assert "access_token" in login_data, "登入回應應包含 access_token"
        assert login_data["token_type"] == "bearer", "Token 類型應為 bearer"

        # Step 4: 使用 token 訪問受保護的端點
        profile_response = api_client.get("/auth/me")
        assert profile_response.status_code == 200, \
            f"獲取個人資料失敗: {profile_response.status_code}"

        profile_data = profile_response.json()
        assert profile_data["username"] == unique_username, "用戶名應匹配"

    def test_invalid_login_credentials(self, api_client):
        """
        TC-E2E-AUTH-002: 無效憑證登入失敗
        測試目標: 驗證系統拒絕無效的登入憑證
        優先級: High
        """
        # 嘗試使用錯誤的密碼登入
        response = api_client.login("nonexistent_user", "WrongPassword123!")

        # 驗證登入失敗
        assert response.status_code == 401, "應返回 401 Unauthorized"

    def test_access_protected_endpoint_without_token(self, api_client):
        """
        TC-E2E-AUTH-003: 未認證訪問受保護端點
        測試目標: 驗證未認證用戶無法訪問受保護的端點
        優先級: Critical
        """
        # 清除 token
        api_client.token = None

        # 嘗試訪問受保護的端點
        response = api_client.get("/auth/me")

        # 驗證訪問被拒絕
        assert response.status_code == 401, "應返回 401 Unauthorized"

    def test_token_expiration_handling(self, api_client):
        """
        TC-E2E-AUTH-004: Token 過期處理
        測試目標: 驗證系統正確處理過期的 token
        優先級: Medium
        """
        # 使用無效的 token
        api_client.token = "invalid_expired_token"

        # 嘗試訪問受保護的端點
        response = api_client.get("/auth/me")

        # 驗證訪問被拒絕
        assert response.status_code in [401, 403], \
            "過期的 token 應返回 401 或 403"


@pytest.mark.system
@pytest.mark.e2e
@pytest.mark.skip(reason="需要實際的註冊端點實現")
class TestUserRegistrationE2E:
    """用戶註冊端到端測試"""

    def test_duplicate_username_registration(self, api_client):
        """
        TC-E2E-AUTH-005: 重複用戶名註冊失敗
        測試目標: 驗證系統拒絕重複的用戶名
        優先級: High
        """
        username = "duplicate_user"
        user_data = {
            "username": username,
            "email": "duplicate@test.com",
            "password": "Password123!",
            "full_name": "Duplicate User"
        }

        # 第一次註冊
        first_response = api_client.post("/auth/register", json=user_data)

        # 第二次使用相同用戶名註冊
        second_response = api_client.post("/auth/register", json=user_data)

        # 驗證第二次註冊失敗
        assert second_response.status_code == 400, \
            "重複用戶名應返回 400 Bad Request"

    def test_weak_password_registration(self, api_client):
        """
        TC-E2E-AUTH-006: 弱密碼註冊失敗
        測試目標: 驗證系統拒絕弱密碼
        優先級: Medium
        """
        weak_passwords = ["123456", "password", "abc"]

        for weak_password in weak_passwords:
            user_data = {
                "username": f"user_{weak_password}",
                "email": f"user_{weak_password}@test.com",
                "password": weak_password,
                "full_name": "Weak Password User"
            }

            response = api_client.post("/auth/register", json=user_data)

            # 驗證註冊失敗
            assert response.status_code in [400, 422], \
                f"弱密碼 '{weak_password}' 應被拒絕"
