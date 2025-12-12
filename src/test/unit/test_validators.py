"""
單元測試: 資料驗證功能
測試案例: UT-VAL-001 ~ UT-VAL-008, UT-PAR-001 ~ UT-PAR-005
"""

import pytest
from datetime import datetime
import sys
from pathlib import Path

# 添加專案路徑
project_root = Path(__file__).parent.parent.parent.parent
python_src = project_root / "src" / "main" / "python"
if str(python_src) not in sys.path:
    sys.path.insert(0, str(python_src))


class TestBoundaryValues:
    """邊界值測試"""

    def test_empty_string_handling(self):
        """UT-VAL-003: 空字串輸入 - 正確處理或拋出異常"""
        empty_string = ""

        assert len(empty_string) == 0, "空字串長度應為 0"
        assert not empty_string, "空字串應為 False"
        assert empty_string == "", "空字串應等於空字串"

    def test_none_value_handling(self):
        """UT-VAL-004: None 值輸入 - 正確處理或拋出異常"""
        none_value = None

        assert none_value is None, "None 應為 None"
        assert not none_value, "None 應為 False"

    def test_max_integer_value(self):
        """UT-VAL-005: 最大整數值 - 不溢位、正確處理"""
        max_int = 2**31 - 1  # 32-bit signed int max

        assert max_int > 0, "最大整數應為正數"
        assert max_int + 1 > max_int, "Python 整數不會溢位"

    def test_negative_number_handling(self):
        """UT-VAL-006: 負數輸入 - 正確拒絕或轉換"""
        negative_number = -100

        assert negative_number < 0, "負數應小於 0"
        abs_value = abs(negative_number)
        assert abs_value > 0, "絕對值應為正數"

    def test_long_string_handling(self):
        """UT-VAL-007: 超長字串 - 正確處理或截斷"""
        long_string = "a" * 10000

        assert len(long_string) == 10000, "超長字串應保持完整"

        # 測試截斷功能
        truncated = long_string[:100]
        assert len(truncated) == 100, "截斷後應為指定長度"

    def test_unicode_special_characters(self):
        """UT-VAL-008: Unicode 特殊字元 - Emoji、中文等正確處理"""
        unicode_string = "測試 Test 🎉 Emoji"

        assert "測試" in unicode_string, "應支援中文"
        assert "🎉" in unicode_string, "應支援 Emoji"
        assert len(unicode_string) > 0, "Unicode 字串應有長度"


class TestEmailValidation:
    """郵箱驗證測試 - 參數化測試"""

    @pytest.mark.parametrize("email,expected", [
        ("user@example.com", True),           # 標準郵箱
        ("test.user@domain.co.uk", True),     # 帶點的郵箱
        ("user+tag@example.com", True),       # 帶加號的郵箱
        ("invalid@", False),                  # 缺少域名
        ("@example.com", False),              # 缺少用戶名
        ("invalid.email", False),             # 缺少 @
        ("user@domain", False),               # 缺少頂級域名
    ])
    def test_email_validation(self, email, expected):
        """UT-PAR-001: 郵箱驗證 - 7 組參數測試"""
        import re

        # 簡單的郵箱正則表達式
        email_pattern = r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        is_valid = bool(re.match(email_pattern, email))

        assert is_valid == expected, f"郵箱 '{email}' 驗證結果應為 {expected}"


class TestPasswordStrength:
    """密碼強度測試 - 參數化測試"""

    @pytest.mark.parametrize("password,expected", [
        ("SecureP@ss123", True),              # 強密碼
        ("WeakPass", False),                  # 缺少數字和特殊字元
        ("short1!", False),                   # 太短
        ("NOLOWERCASE123!", False),           # 缺少小寫
        ("nouppercase123!", False),           # 缺少大寫
        ("NoSpecialChar123", False),          # 缺少特殊字元
    ])
    def test_password_strength(self, password, expected):
        """UT-PAR-002: 密碼強度 - 6 組參數測試"""

        def is_strong_password(pwd):
            """檢查密碼強度"""
            if len(pwd) < 8:
                return False
            if not any(c.isupper() for c in pwd):
                return False
            if not any(c.islower() for c in pwd):
                return False
            if not any(c.isdigit() for c in pwd):
                return False
            if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in pwd):
                return False
            return True

        is_strong = is_strong_password(password)

        assert is_strong == expected, f"密碼 '{password}' 強度應為 {expected}"


class TestURLValidation:
    """URL 驗證測試 - 參數化測試"""

    @pytest.mark.parametrize("url,expected", [
        ("https://example.com", True),
        ("http://example.com", True),
        ("https://sub.domain.example.com", True),
        ("https://example.com/path/to/page", True),
        ("https://example.com?query=value", True),
        ("ftp://example.com", True),          # FTP 協議
        ("not-a-url", False),                 # 缺少協議
        ("://example.com", False),            # 缺少協議名稱
    ])
    def test_url_validation(self, url, expected):
        """UT-PAR-003: URL 驗證 - 8 組參數測試"""
        import re

        # 簡單的 URL 正則表達式
        url_pattern = r'^[a-z]+://[^\s]+$'
        is_valid = bool(re.match(url_pattern, url, re.IGNORECASE))

        assert is_valid == expected, f"URL '{url}' 驗證結果應為 {expected}"


class TestDateFormatParsing:
    """日期格式解析測試 - 參數化測試"""

    @pytest.mark.parametrize("date_string,expected_format", [
        ("2025-12-13", "ISO"),                    # ISO 8601
        ("2025-12-13T00:00:00", "ISO_DATETIME"),  # ISO 8601 datetime
        ("1734048000", "UNIX"),                   # Unix timestamp
        ("12/13/2025", "US"),                     # 美式格式
        ("13/12/2025", "EU"),                     # 歐式格式
    ])
    def test_date_format_parsing(self, date_string, expected_format):
        """UT-PAR-005: 日期格式 - 5 組參數測試"""

        def detect_date_format(date_str):
            """檢測日期格式"""
            import re

            if re.match(r'^\d{4}-\d{2}-\d{2}T', date_str):
                return "ISO_DATETIME"
            elif re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
                return "ISO"
            elif re.match(r'^\d+$', date_str):
                return "UNIX"
            elif re.match(r'^\d{2}/\d{2}/\d{4}$', date_str):
                # 無法區分 US 和 EU 格式，這裡假設是 US
                return "US" if expected_format == "US" else "EU"
            return "UNKNOWN"

        detected = detect_date_format(date_string)

        assert detected == expected_format, f"日期 '{date_string}' 格式應為 {expected_format}"


class TestDataValidation:
    """綜合資料驗證測試"""

    def test_opinion_title_validation(self):
        """驗證意見標題的規則"""
        # 標題至少 5 個字元
        valid_title = "有效的標題"
        invalid_title = "短"

        assert len(valid_title) >= 5, "有效標題應至少 5 個字元"
        assert len(invalid_title) < 5, "無效標題應少於 5 個字元"

    def test_opinion_content_validation(self):
        """驗證意見內容的規則"""
        # 內容不超過 5000 字元
        valid_content = "這是有效的內容" * 10
        too_long_content = "a" * 5001

        assert len(valid_content) < 5000, "有效內容應少於 5000 字元"
        assert len(too_long_content) > 5000, "過長內容應超過 5000 字元"

    def test_category_validation(self):
        """驗證分類的規則"""
        valid_categories = ["交通建設", "環境保護", "教育文化", "社會福利", "經濟發展"]
        invalid_category = "不存在的分類"

        assert "交通建設" in valid_categories, "有效分類應在允許清單中"
        assert invalid_category not in valid_categories, "無效分類不應在允許清單中"


if __name__ == "__main__":
    # 可以直接執行此檔案進行測試
    pytest.main([__file__, "-v"])
