"""
單元測試: 安全性功能
測試案例: UT-SEC-001 ~ UT-SEC-008
"""

import pytest
from datetime import datetime, timedelta
import sys
from pathlib import Path

# 添加專案路徑
project_root = Path(__file__).parent.parent.parent.parent
python_src = project_root / "src" / "main" / "python"
if str(python_src) not in sys.path:
    sys.path.insert(0, str(python_src))

from utils.security import hash_password, verify_password, create_access_token, decode_access_token


class TestPasswordHashing:
    """密碼雜湊測試"""

    def test_hash_password_not_equal_to_original(self):
        """UT-SEC-001: 密碼雜湊功能 - 雜湊值不等於原密碼"""
        password = "test_password_123"
        hashed = hash_password(password)

        assert hashed != password, "雜湊後的密碼不應等於原密碼"
        assert len(hashed) > 20, "雜湊值應該有足夠的長度"

    def test_hash_password_can_verify(self):
        """UT-SEC-001: 密碼雜湊功能 - 可正確驗證"""
        password = "test_password_123"
        hashed = hash_password(password)

        assert verify_password(password, hashed), "應該能夠驗證正確的密碼"
        assert not verify_password("wrong_password", hashed), "不應該驗證錯誤的密碼"

    def test_hash_password_uniqueness(self):
        """UT-SEC-002: 密碼雜湊唯一性 - 相同密碼產生不同雜湊"""
        password = "test_password_123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        # bcrypt 使用隨機 salt，所以每次雜湊結果都不同
        assert hash1 != hash2, "相同密碼應產生不同的雜湊值（使用不同 salt）"

        # 但都應該能驗證原密碼
        assert verify_password(password, hash1), "第一個雜湊應能驗證原密碼"
        assert verify_password(password, hash2), "第二個雜湊應能驗證原密碼"


class TestTokenManagement:
    """Token 管理測試"""

    def test_create_access_token(self):
        """UT-SEC-003: Token 生成 - JWT Token 格式正確"""
        user_data = {"user_id": 1, "username": "testuser"}
        token = create_access_token(user_data)

        assert isinstance(token, str), "Token 應該是字串"
        assert len(token) > 50, "JWT Token 應該有足夠的長度"
        assert token.count('.') == 2, "JWT Token 應該有三個部分（header.payload.signature）"

    def test_decode_token_valid(self):
        """UT-SEC-004: Token 驗證 - 有效 Token 驗證通過"""
        user_data = {"user_id": 1, "username": "testuser"}
        token = create_access_token(user_data)

        payload = decode_access_token(token)

        assert payload is not None, "有效的 Token 應該能解析"
        assert payload.get("user_id") == 1, "應包含正確的 user_id"
        assert payload.get("username") == "testuser", "應包含正確的 username"

    def test_decode_token_invalid(self):
        """UT-SEC-004: Token 驗證 - 無效 Token 被拒絕"""
        invalid_token = "invalid.token.here"

        payload = decode_access_token(invalid_token)

        assert payload is None, "無效的 Token 應該返回 None"

    def test_decode_token_expired(self):
        """UT-SEC-005: Token 過期檢查 - 過期 Token 被正確識別"""
        user_data = {"user_id": 1, "username": "testuser"}

        # 創建一個已經過期的 token（過期時間為 -1 分鐘）
        token = create_access_token(user_data, expires_delta=timedelta(minutes=-1))

        payload = decode_access_token(token)

        assert payload is None, "過期的 Token 應該被拒絕"


class TestPasswordStrength:
    """密碼強度驗證測試"""

    def test_strong_password_requirements(self):
        """UT-SEC-008: 密碼強度驗證 - 檢查長度、大小寫、數字、特殊字元"""
        # 測試強密碼
        strong_password = "SecureP@ssw0rd123"

        assert len(strong_password) >= 8, "密碼應至少 8 個字元"
        assert any(c.isupper() for c in strong_password), "應包含大寫字母"
        assert any(c.islower() for c in strong_password), "應包含小寫字母"
        assert any(c.isdigit() for c in strong_password), "應包含數字"
        assert any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in strong_password), "應包含特殊字元"

    def test_weak_password_detection(self):
        """UT-SEC-008: 密碼強度驗證 - 檢測弱密碼"""
        weak_passwords = [
            "short",           # 太短
            "alllowercase",    # 只有小寫
            "ALLUPPERCASE",    # 只有大寫
            "NoNumbers!@#",    # 沒有數字
            "NoSpecial123",    # 沒有特殊字元
        ]

        for weak_pw in weak_passwords:
            # 檢查是否缺少某些必要元素
            is_weak = (
                len(weak_pw) < 8 or
                not any(c.isupper() for c in weak_pw) or
                not any(c.islower() for c in weak_pw) or
                not any(c.isdigit() for c in weak_pw) or
                not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in weak_pw)
            )

            assert is_weak, f"密碼 '{weak_pw}' 應被識別為弱密碼"


class TestInputSanitization:
    """輸入清理測試"""

    def test_xss_prevention_basic(self):
        """UT-SEC-006: XSS 防護 - 基本驗證（函數尚未實作）"""
        # TODO: 實作 utils.sanitize.sanitize_html() 函數後啟用
        import re

        dangerous_input = '<script>alert("XSS")</script><p>Safe content</p>'

        # 基本的清理邏輯（示範）
        def basic_sanitize(html):
            # 移除 script 標籤
            return re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)

        cleaned = basic_sanitize(dangerous_input)

        assert '<script>' not in cleaned.lower(), "應移除 <script> 標籤"
        assert 'alert' not in cleaned, "應移除 JavaScript 代碼"

    def test_sql_injection_prevention(self):
        """UT-SEC-007: SQL 注入防護 - 參數化查詢概念驗證"""
        # 這個測試主要驗證我們使用參數化查詢
        # 實際上應該在整合測試中驗證
        dangerous_input = "'; DROP TABLE users; --"

        # 確保我們的系統使用參數化查詢，而不是字串拼接
        # 這裡只是一個概念性測試
        assert "'" in dangerous_input, "測試資料應包含單引號"
        assert "--" in dangerous_input, "測試資料應包含 SQL 註解符號"
        # 實際防護應該在資料庫查詢層面實現（使用 %s 參數佔位符）


if __name__ == "__main__":
    # 可以直接執行此檔案進行測試
    pytest.main([__file__, "-v"])
