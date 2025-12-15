"""
AI Media Moderation Service 單元測試
測試目標: AIMediaModerationService 的所有核心功能
測試策略: Mock 所有外部依賴（OpenAI Vision API、檔案系統操作）
"""

import pytest
from unittest.mock import Mock, patch, mock_open, MagicMock
import base64
import json
from pathlib import Path
from services.ai_media_moderation_service import AIMediaModerationService
from services.ai_content_moderation_service import ModerationDecision


# ==================== Fixtures ====================

@pytest.fixture
def sample_image_path():
    """範例圖片路徑"""
    return "/tmp/test_image.jpg"


@pytest.fixture
def sample_image_base64():
    """範例圖片的 base64 編碼"""
    return "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="


@pytest.fixture
def mock_safe_vision_response():
    """Mock OpenAI Vision API 安全圖片回應"""
    return {
        'choices': [{
            'message': {
                'content': json.dumps({
                    'is_safe': True,
                    'detected_issues': [],
                    'severity_scores': {
                        'violence': 0.01,
                        'hate': 0.01,
                        'sexual': 0.005,
                        'self-harm': 0.001,
                        'harassment': 0.01
                    },
                    'description': '這是一張正常的圖片',
                    'recommendation': 'approve'
                })
            }
        }]
    }


@pytest.fixture
def mock_unsafe_vision_response():
    """Mock OpenAI Vision API 不安全圖片回應"""
    return {
        'choices': [{
            'message': {
                'content': json.dumps({
                    'is_safe': False,
                    'detected_issues': ['violence', 'hate'],
                    'severity_scores': {
                        'violence': 0.95,
                        'hate': 0.85,
                        'sexual': 0.02,
                        'self-harm': 0.01,
                        'harassment': 0.03
                    },
                    'description': '圖片包含暴力和仇恨內容',
                    'recommendation': 'reject'
                })
            }
        }]
    }


@pytest.fixture
def mock_review_vision_response():
    """Mock OpenAI Vision API 需審核圖片回應"""
    return {
        'choices': [{
            'message': {
                'content': json.dumps({
                    'is_safe': False,
                    'detected_issues': ['harassment'],
                    'severity_scores': {
                        'violence': 0.15,
                        'hate': 0.20,
                        'sexual': 0.10,
                        'self-harm': 0.05,
                        'harassment': 0.65
                    },
                    'description': '圖片可能包含騷擾內容',
                    'recommendation': 'review'
                })
            }
        }]
    }


# ==================== 測試類別 1: 圖片處理工具函數 ====================

@pytest.mark.no_db
class TestImageProcessing:
    """圖片處理工具函數測試"""

    def test_encode_image_to_base64_success(self, sample_image_path):
        """TC-MEDIA-001: 成功編碼圖片為 base64"""
        test_data = b"fake image data"

        with patch('builtins.open', mock_open(read_data=test_data)):
            result = AIMediaModerationService._encode_image_to_base64(sample_image_path)

        expected = base64.b64encode(test_data).decode('utf-8')
        assert result == expected

    def test_encode_image_file_not_found(self):
        """TC-MEDIA-002: 圖片檔案不存在"""
        result = AIMediaModerationService._encode_image_to_base64("/non/existent/path.jpg")

        assert result is None

    def test_encode_image_permission_error(self, sample_image_path):
        """TC-MEDIA-003: 圖片檔案權限錯誤"""
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            result = AIMediaModerationService._encode_image_to_base64(sample_image_path)

        assert result is None

    def test_get_image_mime_type_jpg(self):
        """TC-MEDIA-004: 獲取 JPG MIME 類型"""
        result = AIMediaModerationService._get_image_mime_type("/path/to/image.jpg")
        assert result == 'image/jpeg'

    def test_get_image_mime_type_jpeg(self):
        """TC-MEDIA-005: 獲取 JPEG MIME 類型"""
        result = AIMediaModerationService._get_image_mime_type("/path/to/image.jpeg")
        assert result == 'image/jpeg'

    def test_get_image_mime_type_png(self):
        """TC-MEDIA-006: 獲取 PNG MIME 類型"""
        result = AIMediaModerationService._get_image_mime_type("/path/to/image.png")
        assert result == 'image/png'

    def test_get_image_mime_type_gif(self):
        """TC-MEDIA-007: 獲取 GIF MIME 類型"""
        result = AIMediaModerationService._get_image_mime_type("/path/to/image.gif")
        assert result == 'image/gif'

    def test_get_image_mime_type_webp(self):
        """TC-MEDIA-008: 獲取 WebP MIME 類型"""
        result = AIMediaModerationService._get_image_mime_type("/path/to/image.webp")
        assert result == 'image/webp'

    def test_get_image_mime_type_unknown(self):
        """TC-MEDIA-009: 未知副檔名默認為 JPEG"""
        result = AIMediaModerationService._get_image_mime_type("/path/to/file.unknown")
        assert result == 'image/jpeg'

    def test_get_image_mime_type_case_insensitive(self):
        """TC-MEDIA-010: MIME 類型判斷不區分大小寫"""
        result = AIMediaModerationService._get_image_mime_type("/path/to/IMAGE.PNG")
        assert result == 'image/png'


# ==================== 測試類別 2: OpenAI Vision API Mock 測試 ====================

@pytest.mark.no_db
class TestOpenAIVisionAPI:
    """OpenAI Vision API Mock 測試"""

    @patch('services.ai_media_moderation_service.requests.post')
    @patch.object(AIMediaModerationService, '_encode_image_to_base64')
    def test_vision_api_success_with_local_image(
        self, mock_encode, mock_post, sample_image_path,
        sample_image_base64, mock_safe_vision_response
    ):
        """TC-MEDIA-011: Vision API 成功處理本地圖片"""
        mock_encode.return_value = sample_image_base64
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_safe_vision_response
        mock_post.return_value.raise_for_status = Mock()

        result = AIMediaModerationService._call_openai_vision_api(sample_image_path, is_url=False)

        assert result['is_safe'] is True
        assert result['confidence'] > 90
        assert len(result['issues']) == 0

    @patch('services.ai_media_moderation_service.requests.post')
    def test_vision_api_success_with_url(self, mock_post, mock_safe_vision_response):
        """TC-MEDIA-012: Vision API 成功處理 URL 圖片"""
        image_url = "https://example.com/image.jpg"
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_safe_vision_response
        mock_post.return_value.raise_for_status = Mock()

        result = AIMediaModerationService._call_openai_vision_api(image_url, is_url=True)

        assert result['is_safe'] is True
        assert 'confidence' in result

    @patch('services.ai_media_moderation_service.requests.post')
    @patch.object(AIMediaModerationService, '_encode_image_to_base64')
    def test_vision_api_detect_violence(
        self, mock_encode, mock_post, sample_image_path,
        sample_image_base64, mock_unsafe_vision_response
    ):
        """TC-MEDIA-013: 檢測暴力圖片"""
        mock_encode.return_value = sample_image_base64
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_unsafe_vision_response
        mock_post.return_value.raise_for_status = Mock()

        result = AIMediaModerationService._call_openai_vision_api(sample_image_path)

        assert result['is_safe'] is False
        assert 'violence' in result['issues']
        assert result['confidence'] > 80

    @patch('services.ai_media_moderation_service.requests.post')
    @patch.object(AIMediaModerationService, '_encode_image_to_base64')
    def test_vision_api_review_recommendation(
        self, mock_encode, mock_post, sample_image_path,
        sample_image_base64, mock_review_vision_response
    ):
        """TC-MEDIA-014: API 建議人工審核"""
        mock_encode.return_value = sample_image_base64
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_review_vision_response
        mock_post.return_value.raise_for_status = Mock()

        result = AIMediaModerationService._call_openai_vision_api(sample_image_path)

        assert result['is_safe'] is False
        assert result['recommendation'] == 'review'
        assert 'harassment' in result['issues']

    @patch('services.ai_media_moderation_service.requests.post')
    def test_vision_api_timeout_error(self, mock_post, sample_image_path):
        """TC-MEDIA-015: API 超時錯誤處理"""
        mock_post.side_effect = Exception("Timeout")

        result = AIMediaModerationService._call_openai_vision_api(sample_image_path)

        # 應該返回安全的默認值
        assert result['is_safe'] is True
        assert 'error' in result

    @patch('services.ai_media_moderation_service.requests.post')
    def test_vision_api_rate_limit(self, mock_post, sample_image_path):
        """TC-MEDIA-016: API 速率限制處理"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = Exception("Rate limit exceeded")
        mock_post.return_value = mock_response

        result = AIMediaModerationService._call_openai_vision_api(sample_image_path)

        assert 'error' in result or result['is_safe'] is True

    @patch.object(AIMediaModerationService, '_encode_image_to_base64')
    def test_vision_api_image_encode_failure(self, mock_encode, sample_image_path):
        """TC-MEDIA-017: 圖片編碼失敗處理"""
        mock_encode.return_value = None

        result = AIMediaModerationService._call_openai_vision_api(sample_image_path, is_url=False)

        assert result['is_safe'] is True
        assert result['confidence'] == 0.0
        assert 'error' in result

    @patch('services.ai_content_moderation_service.ModerationConfig.openai_api_key', '')
    def test_vision_api_no_api_key(self, sample_image_path):
        """TC-MEDIA-018: 無 API Key 配置"""
        result = AIMediaModerationService._call_openai_vision_api(sample_image_path)

        assert result['is_safe'] is True
        assert 'error' in result
        assert 'API key not configured' in result['error']

    @patch('services.ai_media_moderation_service.requests.post')
    @patch.object(AIMediaModerationService, '_encode_image_to_base64')
    def test_vision_api_invalid_json_response(
        self, mock_encode, mock_post, sample_image_path, sample_image_base64
    ):
        """TC-MEDIA-019: API 返回無效 JSON"""
        mock_encode.return_value = sample_image_base64
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'choices': [{
                'message': {
                    'content': 'invalid json content'
                }
            }]
        }
        mock_post.return_value.raise_for_status = Mock()

        result = AIMediaModerationService._call_openai_vision_api(sample_image_path)

        # 應該有錯誤處理
        assert 'error' in result or result['is_safe'] is True


# ==================== 測試類別 3: 圖片審核流程測試 ====================

@pytest.mark.no_db
class TestModerateImage:
    """圖片審核流程測試"""

    @patch.object(AIMediaModerationService, '_call_openai_vision_api')
    @patch('services.ai_media_moderation_service.get_db_cursor')
    def test_moderate_safe_image(self, mock_cursor, mock_api, sample_image_path):
        """TC-MEDIA-020: 審核安全圖片"""
        mock_api.return_value = {
            'is_safe': True,
            'confidence': 95.0,
            'issues': [],
            'description': '安全圖片',
            'recommendation': 'approve'
        }

        result = AIMediaModerationService.moderate_image(sample_image_path, opinion_id=1)

        assert result['decision'] == 'approve'
        assert result['is_safe'] is True
        assert result['confidence'] >= 90

    @patch.object(AIMediaModerationService, '_call_openai_vision_api')
    @patch('services.ai_media_moderation_service.get_db_cursor')
    def test_moderate_unsafe_image(self, mock_cursor, mock_api, sample_image_path):
        """TC-MEDIA-021: 審核不安全圖片"""
        mock_api.return_value = {
            'is_safe': False,
            'confidence': 95.0,
            'issues': ['violence', 'hate'],
            'description': '包含暴力內容',
            'recommendation': 'reject'
        }

        result = AIMediaModerationService.moderate_image(sample_image_path, opinion_id=1)

        assert result['decision'] == 'reject'
        assert result['is_safe'] is False
        assert 'violence' in result['detected_issues']

    @patch.object(AIMediaModerationService, '_call_openai_vision_api')
    @patch('services.ai_media_moderation_service.get_db_cursor')
    def test_moderate_image_needs_review(self, mock_cursor, mock_api, sample_image_path):
        """TC-MEDIA-022: 圖片需要人工審核"""
        mock_api.return_value = {
            'is_safe': False,
            'confidence': 65.0,
            'issues': ['harassment'],
            'description': '可能包含騷擾內容',
            'recommendation': 'review'
        }

        result = AIMediaModerationService.moderate_image(sample_image_path, opinion_id=1)

        assert result['decision'] == 'review'
        assert result['needs_manual_review'] is True

    @patch.object(AIMediaModerationService, '_call_openai_vision_api')
    @patch('services.ai_media_moderation_service.get_db_cursor')
    def test_moderate_image_confidence_calculation(self, mock_cursor, mock_api, sample_image_path):
        """TC-MEDIA-023: 信心度計算測試"""
        mock_api.return_value = {
            'is_safe': True,
            'confidence': 88.5,
            'issues': [],
            'description': '安全圖片',
            'recommendation': 'approve'
        }

        result = AIMediaModerationService.moderate_image(sample_image_path, opinion_id=1)

        assert 'confidence' in result
        assert result['confidence'] == 88.5

    @patch.object(AIMediaModerationService, '_call_openai_vision_api')
    def test_moderate_image_with_api_error(self, mock_api, sample_image_path):
        """TC-MEDIA-024: API 錯誤時的處理"""
        mock_api.return_value = {
            'is_safe': True,
            'confidence': 50.0,
            'issues': [],
            'description': '',
            'error': 'API Error'
        }

        result = AIMediaModerationService.moderate_image(sample_image_path, opinion_id=1)

        # 應該能處理錯誤而不崩潰
        assert 'decision' in result
        assert 'error' in result


# ==================== 測試類別 4: 批量審核測試 ====================

@pytest.mark.no_db
class TestBatchModeration:
    """批量審核測試"""

    @patch.object(AIMediaModerationService, 'moderate_image')
    def test_moderate_multiple_images(self, mock_moderate):
        """TC-MEDIA-025: 批量審核多張圖片"""
        mock_moderate.return_value = {
            'decision': 'approve',
            'is_safe': True,
            'confidence': 95.0
        }

        media_files = [
            {'path': '/tmp/image1.jpg', 'type': 'image'},
            {'path': '/tmp/image2.jpg', 'type': 'image'},
            {'path': '/tmp/image3.jpg', 'type': 'image'}
        ]

        result = AIMediaModerationService.moderate_media_batch(media_files, opinion_id=1)

        assert result['total_count'] == 3
        assert mock_moderate.call_count == 3

    @patch.object(AIMediaModerationService, 'moderate_image')
    def test_batch_with_mixed_results(self, mock_moderate):
        """TC-MEDIA-026: 批量審核混合結果"""
        # 設定不同的回應
        mock_moderate.side_effect = [
            {'decision': 'approve', 'is_safe': True, 'confidence': 95.0},
            {'decision': 'reject', 'is_safe': False, 'confidence': 92.0},
            {'decision': 'review', 'is_safe': False, 'confidence': 65.0}
        ]

        media_files = [
            {'path': '/tmp/image1.jpg', 'type': 'image'},
            {'path': '/tmp/image2.jpg', 'type': 'image'},
            {'path': '/tmp/image3.jpg', 'type': 'image'}
        ]

        result = AIMediaModerationService.moderate_media_batch(media_files, opinion_id=1)

        assert result['total_count'] == 3
        assert result['approved_count'] == 1
        assert result['rejected_count'] == 1
        assert result['review_count'] == 1

    @patch.object(AIMediaModerationService, 'moderate_image')
    def test_batch_with_some_failures(self, mock_moderate):
        """TC-MEDIA-027: 批量審核部分失敗"""
        mock_moderate.side_effect = [
            {'decision': 'approve', 'is_safe': True, 'confidence': 95.0},
            Exception("Processing failed"),
            {'decision': 'approve', 'is_safe': True, 'confidence': 93.0}
        ]

        media_files = [
            {'path': '/tmp/image1.jpg', 'type': 'image'},
            {'path': '/tmp/image2.jpg', 'type': 'image'},
            {'path': '/tmp/image3.jpg', 'type': 'image'}
        ]

        result = AIMediaModerationService.moderate_media_batch(media_files, opinion_id=1)

        # 應該繼續處理其他檔案
        assert result['total_count'] == 3
        assert result['failed_count'] == 1
        assert result['approved_count'] == 2

    def test_batch_with_empty_list(self):
        """TC-MEDIA-028: 批量審核空列表"""
        result = AIMediaModerationService.moderate_media_batch([], opinion_id=1)

        assert result['total_count'] == 0
        assert result['approved_count'] == 0

    @patch.object(AIMediaModerationService, 'moderate_image')
    @patch.object(AIMediaModerationService, 'moderate_video')
    def test_batch_with_mixed_media_types(self, mock_video, mock_image):
        """TC-MEDIA-029: 批量審核混合媒體類型"""
        mock_image.return_value = {'decision': 'approve', 'is_safe': True}
        mock_video.return_value = {'decision': 'approve', 'is_safe': True}

        media_files = [
            {'path': '/tmp/image.jpg', 'type': 'image'},
            {'path': '/tmp/video.mp4', 'type': 'video'}
        ]

        result = AIMediaModerationService.moderate_media_batch(media_files, opinion_id=1)

        assert result['total_count'] == 2
        assert mock_image.call_count == 1
        assert mock_video.call_count == 1


# ==================== 測試類別 5: 視頻審核測試 ====================

@pytest.mark.no_db
class TestVideoModeration:
    """視頻審核測試"""

    @patch.object(AIMediaModerationService, 'moderate_image')
    @patch('services.ai_media_moderation_service.get_db_cursor')
    def test_moderate_video_basic(self, mock_cursor, mock_image):
        """TC-MEDIA-030: 基本視頻審核（抽幀檢測）"""
        mock_image.return_value = {
            'decision': 'approve',
            'is_safe': True,
            'confidence': 95.0
        }

        result = AIMediaModerationService.moderate_video('/tmp/video.mp4', opinion_id=1)

        # 視頻審核應該基於抽幀結果
        assert 'decision' in result
        assert 'is_safe' in result

    @patch.object(AIMediaModerationService, 'moderate_image')
    @patch('services.ai_media_moderation_service.get_db_cursor')
    def test_moderate_video_unsafe_frame(self, mock_cursor, mock_image):
        """TC-MEDIA-031: 檢測到不安全的視頻幀"""
        mock_image.return_value = {
            'decision': 'reject',
            'is_safe': False,
            'confidence': 92.0,
            'detected_issues': ['violence']
        }

        result = AIMediaModerationService.moderate_video('/tmp/video.mp4', opinion_id=1)

        assert result['decision'] == 'reject'
        assert result['is_safe'] is False


# ==================== 測試類別 6: 整合場景測試 ====================

@pytest.mark.no_db
class TestIntegrationScenarios:
    """整合場景測試"""

    @patch.object(AIMediaModerationService, '_call_openai_vision_api')
    @patch('services.ai_media_moderation_service.get_db_cursor')
    def test_complete_image_moderation_workflow(self, mock_cursor, mock_api, sample_image_path):
        """TC-MEDIA-032: 完整圖片審核工作流"""
        mock_api.return_value = {
            'is_safe': True,
            'confidence': 95.0,
            'issues': [],
            'description': '正常圖片',
            'recommendation': 'approve'
        }

        # 模擬資料庫操作
        mock_cursor_instance = MagicMock()
        mock_cursor.return_value.__enter__.return_value = mock_cursor_instance

        result = AIMediaModerationService.moderate_image(sample_image_path, opinion_id=1)

        # 驗證完整流程
        assert result['decision'] == 'approve'
        assert result['is_safe'] is True
        # 驗證有記錄到資料庫
        assert mock_cursor_instance.execute.called

    @patch.object(AIMediaModerationService, '_call_openai_vision_api')
    @patch('services.ai_media_moderation_service.get_db_cursor')
    def test_high_confidence_threshold_handling(self, mock_cursor, mock_api, sample_image_path):
        """TC-MEDIA-033: 高信心度閾值處理"""
        mock_api.return_value = {
            'is_safe': True,
            'confidence': 99.5,
            'issues': [],
            'description': '非常安全的圖片',
            'recommendation': 'approve'
        }

        result = AIMediaModerationService.moderate_image(sample_image_path, opinion_id=1)

        assert result['decision'] == 'approve'
        assert result['confidence'] >= 95

    @patch.object(AIMediaModerationService, '_call_openai_vision_api')
    @patch('services.ai_media_moderation_service.get_db_cursor')
    def test_low_confidence_threshold_handling(self, mock_cursor, mock_api, sample_image_path):
        """TC-MEDIA-034: 低信心度閾值處理"""
        mock_api.return_value = {
            'is_safe': False,
            'confidence': 55.0,
            'issues': ['uncertain'],
            'description': '不確定的內容',
            'recommendation': 'review'
        }

        result = AIMediaModerationService.moderate_image(sample_image_path, opinion_id=1)

        # 低信心度應該建議人工審核
        assert result['decision'] == 'review'
        assert result['needs_manual_review'] is True
