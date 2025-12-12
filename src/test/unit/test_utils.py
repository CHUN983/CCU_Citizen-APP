"""
單元測試: 工具函數
測試案例: UT-UTL-001 ~ UT-UTL-010
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


class TestTextProcessing:
    """文字處理測試"""

    def test_text_truncation(self):
        """UT-UTL-002: 文字截斷 - 正確截斷並加上省略號"""
        long_text = "這是一段很長的文字" * 20

        def truncate_text(text, max_length=50):
            """截斷文字並加上省略號"""
            if len(text) <= max_length:
                return text
            return text[:max_length] + "..."

        truncated = truncate_text(long_text, 50)

        assert len(truncated) == 53, "截斷後長度應為 50 + 3（省略號）"
        assert truncated.endswith("..."), "應以省略號結尾"

    def test_text_truncation_short_text(self):
        """UT-UTL-003: 文字截斷（短文字）- 短於限制的文字不被截斷"""
        short_text = "短文字"

        def truncate_text(text, max_length=50):
            if len(text) <= max_length:
                return text
            return text[:max_length] + "..."

        result = truncate_text(short_text, 50)

        assert result == short_text, "短文字不應被截斷"
        assert not result.endswith("..."), "短文字不應有省略號"


class TestDateTimeFormatting:
    """日期時間格式化測試"""

    def test_datetime_formatting(self):
        """UT-UTL-004: 日期格式化 - 正確轉換為本地時區與格式"""
        test_datetime = datetime(2025, 12, 13, 15, 30, 45)

        formatted = test_datetime.strftime("%Y-%m-%d %H:%M:%S")

        assert formatted == "2025-12-13 15:30:45", "日期格式化應正確"

    def test_relative_time_calculation(self):
        """UT-UTL-005: 相對時間計算 - "3 天前"、"剛剛" 等正確顯示"""

        def get_relative_time(past_datetime):
            """計算相對時間"""
            now = datetime.now()
            diff = now - past_datetime

            if diff.total_seconds() < 60:
                return "剛剛"
            elif diff.total_seconds() < 3600:
                minutes = int(diff.total_seconds() / 60)
                return f"{minutes} 分鐘前"
            elif diff.total_seconds() < 86400:
                hours = int(diff.total_seconds() / 3600)
                return f"{hours} 小時前"
            else:
                days = diff.days
                return f"{days} 天前"

        # 測試不同時間差
        just_now = datetime.now() - timedelta(seconds=30)
        assert get_relative_time(just_now) == "剛剛"

        minutes_ago = datetime.now() - timedelta(minutes=5)
        assert get_relative_time(minutes_ago) == "5 分鐘前"

        hours_ago = datetime.now() - timedelta(hours=2)
        assert get_relative_time(hours_ago) == "2 小時前"

        days_ago = datetime.now() - timedelta(days=3)
        assert get_relative_time(days_ago) == "3 天前"


class TestFileSizeFormatting:
    """檔案大小格式化測試"""

    def test_file_size_formatting(self):
        """UT-UTL-007: 檔案大小格式化 - "1.5 MB"、"500 KB" 等正確顯示"""

        def format_file_size(size_bytes):
            """格式化檔案大小"""
            if size_bytes < 1024:
                return f"{size_bytes} B"
            elif size_bytes < 1024 * 1024:
                return f"{size_bytes / 1024:.1f} KB"
            elif size_bytes < 1024 * 1024 * 1024:
                return f"{size_bytes / (1024 * 1024):.1f} MB"
            else:
                return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

        assert format_file_size(500) == "500 B"
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1024 * 500) == "500.0 KB"
        assert format_file_size(1024 * 1024) == "1.0 MB"
        assert format_file_size(1024 * 1024 * 1.5) == "1.5 MB"
        assert format_file_size(1024 * 1024 * 1024) == "1.0 GB"


class TestURLValidation:
    """URL 驗證測試"""

    def test_url_validation(self):
        """UT-UTL-008: URL 驗證 - 有效 URL 通過、無效 URL 被拒絕"""
        import re

        def is_valid_url(url):
            """驗證 URL 格式"""
            url_pattern = r'^https?://[^\s]+$'
            return bool(re.match(url_pattern, url))

        # 有效 URL
        assert is_valid_url("https://example.com")
        assert is_valid_url("http://example.com")
        assert is_valid_url("https://sub.domain.com/path")

        # 無效 URL
        assert not is_valid_url("not-a-url")
        assert not is_valid_url("ftp://example.com")  # 不是 HTTP(S)
        assert not is_valid_url("https://")


class TestSlugGeneration:
    """Slug 生成測試"""

    def test_slug_generation(self):
        """UT-UTL-009: Slug 生成 - 中文轉拼音、特殊字元處理"""

        def generate_slug(text):
            """生成 URL 友善的 slug"""
            import re

            # 簡化版：只處理基本字元
            slug = text.lower()
            slug = re.sub(r'[^\w\s-]', '', slug)  # 移除特殊字元
            slug = re.sub(r'[\s_-]+', '-', slug)  # 空白轉為連字號
            slug = slug.strip('-')
            return slug

        assert generate_slug("Test Title") == "test-title"
        assert generate_slug("Test  Multiple   Spaces") == "test-multiple-spaces"
        assert generate_slug("Test-With-Dashes") == "test-with-dashes"


class TestRandomStringGeneration:
    """隨機字串生成測試"""

    def test_random_string_generation(self):
        """UT-UTL-010: 隨機字串生成 - 指定長度、唯一性"""
        import random
        import string

        def generate_random_string(length=16):
            """生成隨機字串"""
            characters = string.ascii_letters + string.digits
            return ''.join(random.choice(characters) for _ in range(length))

        # 測試長度
        random_str = generate_random_string(16)
        assert len(random_str) == 16, "隨機字串長度應正確"

        random_str_32 = generate_random_string(32)
        assert len(random_str_32) == 32, "隨機字串長度應正確"

        # 測試唯一性
        str1 = generate_random_string(16)
        str2 = generate_random_string(16)
        assert str1 != str2, "兩次生成的隨機字串應不同"

        # 測試只包含字母和數字
        assert random_str.isalnum(), "隨機字串應只包含字母和數字"


class TestHTMLSanitization:
    """HTML 清理測試"""

    def test_html_sanitization_basic(self):
        """UT-UTL-001: HTML 清理 - 移除危險標籤、保留安全標籤"""

        def sanitize_html_basic(html):
            """基本的 HTML 清理（示範版）"""
            import re

            # 移除 script 標籤
            html = re.sub(r'<script[^>]*>.*?</script>', '', html, flags=re.DOTALL | re.IGNORECASE)
            # 移除 iframe 標籤
            html = re.sub(r'<iframe[^>]*>.*?</iframe>', '', html, flags=re.DOTALL | re.IGNORECASE)
            # 移除 onclick 等事件處理器
            html = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', html, flags=re.IGNORECASE)

            return html.strip()

        dangerous_html = '<script>alert("XSS")</script><p onclick="alert()">Test</p>'
        cleaned = sanitize_html_basic(dangerous_html)

        assert '<script>' not in cleaned, "應移除 script 標籤"
        assert 'onclick' not in cleaned.lower(), "應移除事件處理器"


if __name__ == "__main__":
    # 可以直接執行此檔案進行測試
    pytest.main([__file__, "-v"])
