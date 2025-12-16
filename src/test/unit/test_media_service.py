"""
媒體服務單元測試
測試範圍: 媒體類型判斷、檔案驗證、圖片處理等核心功能
測試案例對應: TC-MEDIA-SERVICE-001 ~ TC-MEDIA-SERVICE-020
"""

import pytest
import io
import tempfile
from pathlib import Path
from PIL import Image
from fastapi import HTTPException

# Import functions to test
from api.media import (
    get_media_type,
    validate_file_size,
    compress_image,
    create_thumbnail,
    ALLOWED_IMAGE_EXTENSIONS,
    ALLOWED_VIDEO_EXTENSIONS,
    ALLOWED_AUDIO_EXTENSIONS,
    MAX_FILE_SIZE,
    MAX_IMAGE_SIZE
)
from models.opinion import MediaType


@pytest.mark.unit
@pytest.mark.no_db
class TestMediaTypeDetection:
    """媒體類型檢測測試"""

    def test_detect_image_jpg(self):
        """TC-MEDIA-SERVICE-001: 檢測 JPG 圖片格式"""
        result = get_media_type("test.jpg")
        assert result == MediaType.IMAGE

    def test_detect_image_jpeg(self):
        """TC-MEDIA-SERVICE-002: 檢測 JPEG 圖片格式"""
        result = get_media_type("photo.jpeg")
        assert result == MediaType.IMAGE

    def test_detect_image_png(self):
        """TC-MEDIA-SERVICE-003: 檢測 PNG 圖片格式"""
        result = get_media_type("image.png")
        assert result == MediaType.IMAGE

    def test_detect_image_gif(self):
        """TC-MEDIA-SERVICE-004: 檢測 GIF 圖片格式"""
        result = get_media_type("animation.gif")
        assert result == MediaType.IMAGE

    def test_detect_image_webp(self):
        """TC-MEDIA-SERVICE-005: 檢測 WebP 圖片格式"""
        result = get_media_type("modern.webp")
        assert result == MediaType.IMAGE

    def test_detect_video_mp4(self):
        """TC-MEDIA-SERVICE-006: 檢測 MP4 影片格式"""
        result = get_media_type("video.mp4")
        assert result == MediaType.VIDEO

    def test_detect_video_avi(self):
        """TC-MEDIA-SERVICE-007: 檢測 AVI 影片格式"""
        result = get_media_type("movie.avi")
        assert result == MediaType.VIDEO

    def test_detect_video_mov(self):
        """TC-MEDIA-SERVICE-008: 檢測 MOV 影片格式"""
        result = get_media_type("clip.mov")
        assert result == MediaType.VIDEO

    def test_detect_audio_mp3(self):
        """TC-MEDIA-SERVICE-009: 檢測 MP3 音頻格式"""
        result = get_media_type("music.mp3")
        assert result == MediaType.AUDIO

    def test_detect_audio_wav(self):
        """TC-MEDIA-SERVICE-010: 檢測 WAV 音頻格式"""
        result = get_media_type("sound.wav")
        assert result == MediaType.AUDIO

    def test_detect_audio_ogg(self):
        """TC-MEDIA-SERVICE-011: 檢測 OGG 音頻格式"""
        result = get_media_type("audio.ogg")
        assert result == MediaType.AUDIO

    def test_unsupported_file_type(self):
        """TC-MEDIA-SERVICE-012: 不支援的檔案格式應拋出異常"""
        with pytest.raises(HTTPException) as exc_info:
            get_media_type("document.pdf")

        assert exc_info.value.status_code == 400
        assert "Unsupported file type" in str(exc_info.value.detail)

    def test_case_insensitive_extension(self):
        """TC-MEDIA-SERVICE-013: 副檔名大小寫不敏感"""
        assert get_media_type("IMAGE.JPG") == MediaType.IMAGE
        assert get_media_type("Video.MP4") == MediaType.VIDEO
        assert get_media_type("Audio.MP3") == MediaType.AUDIO


@pytest.mark.unit
@pytest.mark.no_db
class TestFileSizeValidation:
    """檔案大小驗證測試"""

    def test_validate_normal_image_size(self):
        """TC-MEDIA-SERVICE-014: 正常圖片大小通過驗證"""
        file_size = 5 * 1024 * 1024  # 5MB
        # Should not raise exception
        validate_file_size(file_size, MediaType.IMAGE)

    def test_validate_oversized_image(self):
        """TC-MEDIA-SERVICE-015: 超大圖片被拒絕"""
        file_size = 15 * 1024 * 1024  # 15MB (超過 10MB 限制)

        with pytest.raises(HTTPException) as exc_info:
            validate_file_size(file_size, MediaType.IMAGE)

        assert exc_info.value.status_code == 400
        assert "too large" in str(exc_info.value.detail).lower()

    def test_validate_normal_video_size(self):
        """TC-MEDIA-SERVICE-016: 正常影片大小通過驗證"""
        file_size = 30 * 1024 * 1024  # 30MB
        # Should not raise exception
        validate_file_size(file_size, MediaType.VIDEO)

    def test_validate_oversized_video(self):
        """TC-MEDIA-SERVICE-017: 超大影片被拒絕"""
        file_size = 60 * 1024 * 1024  # 60MB (超過 50MB 限制)

        with pytest.raises(HTTPException) as exc_info:
            validate_file_size(file_size, MediaType.VIDEO)

        assert exc_info.value.status_code == 400
        assert "too large" in str(exc_info.value.detail).lower()

    def test_validate_normal_audio_size(self):
        """TC-MEDIA-SERVICE-018: 正常音頻大小通過驗證"""
        file_size = 20 * 1024 * 1024  # 20MB
        # Should not raise exception
        validate_file_size(file_size, MediaType.AUDIO)


@pytest.mark.unit
@pytest.mark.no_db
class TestImageProcessing:
    """圖片處理測試"""

    def test_compress_image_reduces_size(self):
        """TC-MEDIA-SERVICE-019: 壓縮圖片功能"""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp:
            # 創建大圖片
            large_image = Image.new('RGB', (3000, 2000), color='blue')
            large_image.save(tmp.name, 'JPEG', quality=100)
            tmp_path = Path(tmp.name)

            original_size = tmp_path.stat().st_size

            # 壓縮圖片
            compress_image(tmp_path, max_size=(1920, 1080), quality=85)

            compressed_size = tmp_path.stat().st_size

            # 驗證圖片被壓縮
            assert compressed_size < original_size

            # 驗證圖片仍然有效
            with Image.open(tmp_path) as img:
                assert img.size[0] <= 1920
                assert img.size[1] <= 1080

            # 清理
            tmp_path.unlink()

    def test_compress_image_handles_rgba(self):
        """TC-MEDIA-SERVICE-020: 壓縮 RGBA 圖片轉換為 RGB"""
        with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp:
            # 創建 RGBA 圖片
            rgba_image = Image.new('RGBA', (800, 600), color=(255, 0, 0, 128))
            rgba_image.save(tmp.name, 'PNG')
            tmp_path = Path(tmp.name)

            # 壓縮圖片
            compress_image(tmp_path)

            # 驗證圖片轉換為 RGB
            with Image.open(tmp_path) as img:
                assert img.mode == 'RGB'

            # 清理
            tmp_path.unlink()

    def test_create_thumbnail_success(self):
        """TC-MEDIA-SERVICE-021: 成功創建縮圖"""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_src:
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_thumb:
                # 創建原始圖片
                original_image = Image.new('RGB', (1000, 800), color='green')
                original_image.save(tmp_src.name, 'JPEG')

                src_path = Path(tmp_src.name)
                thumb_path = Path(tmp_thumb.name)

                # 創建縮圖
                create_thumbnail(src_path, thumb_path, size=(300, 300))

                # 驗證縮圖存在且大小正確
                assert thumb_path.exists()

                with Image.open(thumb_path) as thumb:
                    assert thumb.size[0] <= 300
                    assert thumb.size[1] <= 300

                # 清理
                src_path.unlink()
                thumb_path.unlink()

    def test_create_thumbnail_preserves_aspect_ratio(self):
        """TC-MEDIA-SERVICE-022: 縮圖保持長寬比"""
        with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_src:
            with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as tmp_thumb:
                # 創建長方形圖片
                original_image = Image.new('RGB', (1600, 900), color='purple')
                original_image.save(tmp_src.name, 'JPEG')

                src_path = Path(tmp_src.name)
                thumb_path = Path(tmp_thumb.name)

                # 創建縮圖
                create_thumbnail(src_path, thumb_path, size=(300, 300))

                # 驗證縮圖保持長寬比
                with Image.open(thumb_path) as thumb:
                    # 16:9 比例應該保持
                    aspect_ratio = thumb.size[0] / thumb.size[1]
                    expected_ratio = 1600 / 900
                    assert abs(aspect_ratio - expected_ratio) < 0.01

                # 清理
                src_path.unlink()
                thumb_path.unlink()
