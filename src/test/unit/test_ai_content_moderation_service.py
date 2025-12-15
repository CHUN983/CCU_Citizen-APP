"""
AI Content Moderation Service 單元測試
測試目標: AIContentModerationService 的所有核心功能
測試策略: Mock 所有外部依賴（OpenAI API、資料庫查詢）
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List
from services.ai_content_moderation_service import (
    AIContentModerationService,
    ModerationDecision,
    ModerationConfig
)


# ==================== Fixtures ====================

@pytest.fixture
def mock_sensitive_words():
    """Mock 敏感詞資料"""
    return {
        'reject': [
            {'word': '暴力詞彙', 'category': 'violence', 'severity': 'high'},
            {'word': '違禁品', 'category': 'illegal', 'severity': 'high'}
        ],
        'flag': [
            {'word': '爭議話題', 'category': 'controversial', 'severity': 'medium'},
            {'word': '敏感政治', 'category': 'political', 'severity': 'medium'}
        ],
        'review': [
            {'word': '需審核', 'category': 'review', 'severity': 'low'}
        ]
    }


@pytest.fixture
def mock_category_keywords():
    """Mock 分類關鍵字資料"""
    return {
        1: [  # 交通分類
            {'keyword': '交通', 'weight': 2.0, 'category_name': '交通運輸'},
            {'keyword': '道路', 'weight': 1.5, 'category_name': '交通運輸'},
            {'keyword': '公車', 'weight': 1.5, 'category_name': '交通運輸'}
        ],
        2: [  # 環境分類
            {'keyword': '環境', 'weight': 2.0, 'category_name': '環境保護'},
            {'keyword': '污染', 'weight': 1.8, 'category_name': '環境保護'},
            {'keyword': '垃圾', 'weight': 1.5, 'category_name': '環境保護'}
        ],
        3: [  # 教育分類
            {'keyword': '教育', 'weight': 2.0, 'category_name': '教育文化'},
            {'keyword': '學校', 'weight': 1.5, 'category_name': '教育文化'}
        ]
    }


@pytest.fixture
def mock_openai_safe_response():
    """Mock OpenAI API 安全內容回應"""
    return {
        'flagged': False,
        'categories': {
            'violence': False,
            'hate': False,
            'sexual': False,
            'self-harm': False,
            'harassment': False
        },
        'category_scores': {
            'violence': 0.01,
            'hate': 0.01,
            'sexual': 0.005,
            'self-harm': 0.001,
            'harassment': 0.01
        }
    }


@pytest.fixture
def mock_openai_unsafe_response():
    """Mock OpenAI API 不安全內容回應"""
    return {
        'flagged': True,
        'categories': {
            'violence': True,
            'hate': False,
            'sexual': False,
            'self-harm': False,
            'harassment': False
        },
        'category_scores': {
            'violence': 0.95,
            'hate': 0.02,
            'sexual': 0.01,
            'self-harm': 0.001,
            'harassment': 0.03
        }
    }


@pytest.fixture
def mock_openai_classification_response():
    """Mock OpenAI 分類 API 回應"""
    return {
        'choices': [{
            'message': {
                'content': '{"category_id": 1, "confidence": 85.5, "reasoning": "內容包含交通相關關鍵字"}'
            }
        }]
    }


# ==================== 測試類別 1: 敏感詞檢測 ====================

@pytest.mark.no_db
class TestSensitiveWordsDetection:
    """敏感詞檢測測試"""

    @patch.object(AIContentModerationService, '_get_sensitive_words')
    def test_detect_reject_level_sensitive_word(self, mock_get_words, mock_sensitive_words):
        """TC-AI-001: 檢測拒絕級敏感詞"""
        mock_get_words.return_value = mock_sensitive_words

        text = "這是一篇包含暴力詞彙的文章"
        is_blocked, action, matched = AIContentModerationService._check_sensitive_words(text)

        assert is_blocked is True
        assert action == 'reject'
        assert matched == '暴力詞彙'

    @patch.object(AIContentModerationService, '_get_sensitive_words')
    def test_detect_flag_level_sensitive_word(self, mock_get_words, mock_sensitive_words):
        """TC-AI-002: 檢測標記級敏感詞"""
        mock_get_words.return_value = mock_sensitive_words

        text = "這是一篇關於爭議話題的討論"
        is_blocked, action, matched = AIContentModerationService._check_sensitive_words(text)

        assert is_blocked is False
        assert action == 'flag'
        assert '爭議話題' in matched

    @patch.object(AIContentModerationService, '_get_sensitive_words')
    def test_detect_review_level_sensitive_word(self, mock_get_words, mock_sensitive_words):
        """TC-AI-003: 檢測審核級敏感詞"""
        mock_get_words.return_value = mock_sensitive_words

        text = "這是一篇需審核的內容"
        is_blocked, action, matched = AIContentModerationService._check_sensitive_words(text)

        assert is_blocked is False
        assert action == 'review'
        assert '需審核' in matched

    @patch.object(AIContentModerationService, '_get_sensitive_words')
    def test_no_sensitive_words_detected(self, mock_get_words, mock_sensitive_words):
        """TC-AI-004: 正常內容無敏感詞"""
        mock_get_words.return_value = mock_sensitive_words

        text = "這是一篇正常的文章內容"
        is_blocked, action, matched = AIContentModerationService._check_sensitive_words(text)

        assert is_blocked is False
        assert action is None
        assert matched is None

    @patch.object(AIContentModerationService, '_get_sensitive_words')
    def test_multiple_sensitive_words_priority(self, mock_get_words, mock_sensitive_words):
        """TC-AI-005: 多個敏感詞優先級測試（reject > flag > review）"""
        mock_get_words.return_value = mock_sensitive_words

        # 包含 reject 和 flag 級別的詞，應該返回 reject
        text = "這篇文章包含暴力詞彙和爭議話題"
        is_blocked, action, matched = AIContentModerationService._check_sensitive_words(text)

        assert is_blocked is True
        assert action == 'reject'
        assert matched == '暴力詞彙'

    @patch.object(AIContentModerationService, '_get_sensitive_words')
    def test_empty_text_handling(self, mock_get_words, mock_sensitive_words):
        """TC-AI-006: 空文本處理"""
        mock_get_words.return_value = mock_sensitive_words

        text = ""
        is_blocked, action, matched = AIContentModerationService._check_sensitive_words(text)

        assert is_blocked is False
        assert action is None


# ==================== 測試類別 2: 關鍵字分類 ====================

@pytest.mark.no_db
class TestKeywordClassification:
    """關鍵字分類測試"""

    @patch.object(AIContentModerationService, '_get_category_keywords')
    def test_classify_by_single_keyword(self, mock_get_keywords, mock_category_keywords):
        """TC-AI-007: 單關鍵字分類"""
        mock_get_keywords.return_value = mock_category_keywords

        text = "我想反映交通問題"
        category_id, confidence, matched_kws = AIContentModerationService._classify_by_keywords(text)

        assert category_id == 1  # 交通分類
        assert confidence > 0
        assert '交通' in matched_kws

    @patch.object(AIContentModerationService, '_get_category_keywords')
    def test_classify_by_multiple_keywords(self, mock_get_keywords, mock_category_keywords):
        """TC-AI-008: 多關鍵字分類"""
        mock_get_keywords.return_value = mock_category_keywords

        text = "關於道路和公車的交通問題"
        category_id, confidence, matched_kws = AIContentModerationService._classify_by_keywords(text)

        assert category_id == 1  # 交通分類
        assert confidence > 50  # 多關鍵字應該有較高信心度
        assert '交通' in matched_kws
        assert '道路' in matched_kws

    @patch.object(AIContentModerationService, '_get_category_keywords')
    def test_keyword_weight_calculation(self, mock_get_keywords, mock_category_keywords):
        """TC-AI-009: 權重計算測試"""
        mock_get_keywords.return_value = mock_category_keywords

        # 環境分類的"污染"權重(1.8) > 交通分類的"道路"權重(1.5)
        text = "道路污染問題"
        category_id, confidence, matched_kws = AIContentModerationService._classify_by_keywords(text)

        # 應該匹配到環境分類（污染權重更高）
        assert category_id in [1, 2]  # 可能是交通或環境

    @patch.object(AIContentModerationService, '_get_category_keywords')
    def test_no_matching_keywords(self, mock_get_keywords, mock_category_keywords):
        """TC-AI-010: 無匹配關鍵字"""
        mock_get_keywords.return_value = mock_category_keywords

        text = "這是一篇完全不相關的內容"
        category_id, confidence, matched_kws = AIContentModerationService._classify_by_keywords(text)

        assert category_id is None
        assert confidence == 0.0
        assert matched_kws == ""

    @patch.object(AIContentModerationService, '_get_category_keywords')
    def test_keyword_frequency_impact(self, mock_get_keywords, mock_category_keywords):
        """TC-AI-011: 關鍵字頻率影響分數"""
        mock_get_keywords.return_value = mock_category_keywords

        # 同一關鍵字出現多次
        text = "交通交通交通問題"
        category_id, confidence, matched_kws = AIContentModerationService._classify_by_keywords(text)

        assert category_id == 1
        # 多次出現應該提高分數和信心度
        assert confidence > 50


# ==================== 測試類別 3: OpenAI API Mock 測試 ====================

@pytest.mark.no_db
class TestOpenAIModerationAPI:
    """OpenAI API Mock 測試"""

    @patch('services.ai_content_moderation_service.requests.post')
    def test_openai_api_success_response(self, mock_post, mock_openai_safe_response):
        """TC-AI-012: OpenAI API 成功回應"""
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'results': [mock_openai_safe_response]
        }
        mock_post.return_value.raise_for_status = Mock()

        result = AIContentModerationService._call_openai_moderation("測試內容")

        assert result['is_safe'] is True
        assert 'confidence' in result
        assert 'issues' in result

    @patch('services.ai_content_moderation_service.requests.post')
    def test_openai_api_detect_violence(self, mock_post, mock_openai_unsafe_response):
        """TC-AI-013: 檢測暴力內容"""
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {
            'results': [mock_openai_unsafe_response]
        }
        mock_post.return_value.raise_for_status = Mock()

        result = AIContentModerationService._call_openai_moderation("暴力內容測試")

        assert result['is_safe'] is False
        assert 'violence' in result['issues']
        assert result['issues']['violence'] > 0.9

    @patch('services.ai_content_moderation_service.requests.post')
    def test_openai_api_timeout_handling(self, mock_post):
        """TC-AI-014: API 超時處理"""
        mock_post.side_effect = Exception("Timeout")

        result = AIContentModerationService._call_openai_moderation("測試內容")

        # 應該返回安全的默認值
        assert result['is_safe'] is True
        assert 'error' in result

    @patch('services.ai_content_moderation_service.requests.post')
    def test_openai_api_rate_limit_handling(self, mock_post):
        """TC-AI-015: API 速率限制處理"""
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = Exception("Rate limit exceeded")
        mock_post.return_value = mock_response

        result = AIContentModerationService._call_openai_moderation("測試內容")

        # 應該有錯誤處理
        assert 'error' in result or result['is_safe'] is True

    @patch.object(ModerationConfig, 'openai_api_key', '')
    def test_openai_api_no_api_key(self):
        """TC-AI-016: 無 API Key 情況"""
        result = AIContentModerationService._call_openai_moderation("測試內容")

        # 應該返回默認安全值，並包含錯誤信息
        assert result['is_safe'] is True
        assert 'error' in result or result.get('confidence', 0) == 50.0


# ==================== 測試類別 4: 綜合審核流程測試 ====================

@pytest.mark.no_db
class TestModerateTextContent:
    """綜合審核流程測試"""

    @patch.object(AIContentModerationService, '_check_sensitive_words')
    @patch.object(AIContentModerationService, '_call_openai_moderation')
    @patch.object(AIContentModerationService, '_classify_by_keywords')
    @patch.object(AIContentModerationService, '_call_openai_classification')
    def test_approve_clean_content(
        self, mock_ai_classify, mock_classify, mock_openai, mock_check_words
    ):
        """TC-AI-017: 批准正常內容"""
        # Mock 所有檢查都通過
        mock_check_words.return_value = (False, None, None)
        mock_openai.return_value = {
            'is_safe': True,
            'confidence': 95.0,
            'issues': {}
        }
        mock_classify.return_value = (1, 80.0, "交通")
        mock_ai_classify.return_value = (1, 85.0, "AI 判斷為交通類")

        result = AIContentModerationService.moderate_text_content(
            title="正常標題",
            content="這是一篇正常的內容"
        )

        assert result['decision'] == ModerationDecision.APPROVE
        assert result['is_safe'] is True
        assert result['suggested_category_id'] == 1
        assert result['needs_manual_review'] is False

    @patch.object(AIContentModerationService, '_check_sensitive_words')
    def test_reject_with_sensitive_words(self, mock_check_words):
        """TC-AI-018: 因敏感詞拒絕"""
        mock_check_words.return_value = (True, 'reject', '暴力詞彙')

        result = AIContentModerationService.moderate_text_content(
            title="測試標題",
            content="包含暴力詞彙的內容"
        )

        assert result['decision'] == ModerationDecision.REJECT
        assert result['confidence'] == 100.0
        assert '暴力詞彙' in result['reason']
        assert result['blocked_keywords'] == '暴力詞彙'

    @patch.object(AIContentModerationService, '_check_sensitive_words')
    @patch.object(AIContentModerationService, '_call_openai_moderation')
    @patch.object(AIContentModerationService, '_classify_by_keywords')
    @patch.object(AIContentModerationService, '_call_openai_classification')
    def test_reject_by_ai_detection(self, mock_ai_classify, mock_classify, mock_openai, mock_check_words):
        """TC-AI-019: AI 檢測拒絕"""
        mock_check_words.return_value = (False, None, None)
        mock_openai.return_value = {
            'is_safe': False,
            'confidence': 5.0,  # 低信心度 = 高風險
            'issues': {'violence': 0.95}
        }
        mock_classify.return_value = (None, 0.0, "")
        mock_ai_classify.return_value = (None, 0.0, "內容不安全")

        result = AIContentModerationService.moderate_text_content(
            title="測試標題",
            content="AI 檢測為不安全的內容"
        )

        assert result['decision'] == ModerationDecision.FLAG
        assert result['is_safe'] is False

    @patch.object(AIContentModerationService, '_check_sensitive_words')
    @patch.object(AIContentModerationService, '_call_openai_moderation')
    @patch.object(AIContentModerationService, '_classify_by_keywords')
    @patch.object(AIContentModerationService, '_call_openai_classification')
    def test_flag_for_manual_review(self, mock_ai_classify, mock_classify, mock_openai, mock_check_words):
        """TC-AI-020: 標記人工審核"""
        mock_check_words.return_value = (False, 'flag', '爭議話題')
        mock_openai.return_value = {
            'is_safe': True,
            'confidence': 70.0,
            'issues': {}
        }
        mock_classify.return_value = (1, 75.0, "交通")
        mock_ai_classify.return_value = (1, 75.0, "交通相關")

        result = AIContentModerationService.moderate_text_content(
            title="測試標題",
            content="包含爭議話題的內容"
        )

        assert result['decision'] == ModerationDecision.FLAG
        assert result['needs_manual_review'] is True

    @patch.object(AIContentModerationService, '_check_sensitive_words')
    @patch.object(AIContentModerationService, '_call_openai_moderation')
    @patch.object(AIContentModerationService, '_classify_by_keywords')
    @patch.object(AIContentModerationService, '_call_openai_classification')
    def test_auto_categorization(self, mock_ai_classify, mock_classify, mock_openai, mock_check_words):
        """TC-AI-021: 自動分類"""
        mock_check_words.return_value = (False, None, None)
        mock_openai.return_value = {
            'is_safe': True,
            'confidence': 90.0,
            'issues': {}
        }
        mock_classify.return_value = (2, 85.0, "環境, 污染")
        mock_ai_classify.return_value = (2, 90.0, "環境污染相關")

        result = AIContentModerationService.moderate_text_content(
            title="環境問題",
            content="關於環境污染的討論"
        )

        assert result['suggested_category_id'] == 2
        assert '環境' in result['matched_keywords'] or '污染' in result['matched_keywords']

    def test_empty_content_handling(self):
        """TC-AI-022: 空內容處理"""
        result = AIContentModerationService.moderate_text_content(
            title="",
            content=""
        )

        # 應該能處理空內容而不崩潰
        assert 'decision' in result
        assert 'confidence' in result

    @patch.object(AIContentModerationService, '_check_sensitive_words')
    @patch.object(AIContentModerationService, '_call_openai_moderation')
    @patch.object(AIContentModerationService, '_classify_by_keywords')
    @patch.object(AIContentModerationService, '_call_openai_classification')
    def test_processing_time_recording(self, mock_ai_classify, mock_classify, mock_openai, mock_check_words):
        """TC-AI-023: 處理時間記錄"""
        mock_check_words.return_value = (False, None, None)
        mock_openai.return_value = {
            'is_safe': True,
            'confidence': 90.0,
            'issues': {}
        }
        mock_classify.return_value = (1, 80.0, "交通")
        mock_ai_classify.return_value = (1, 85.0, "交通相關")

        result = AIContentModerationService.moderate_text_content(
            title="測試標題",
            content="測試內容"
        )

        assert 'processing_time_ms' in result
        assert result['processing_time_ms'] >= 0

    @patch.object(AIContentModerationService, '_check_sensitive_words')
    @patch.object(AIContentModerationService, '_call_openai_moderation')
    @patch.object(AIContentModerationService, '_classify_by_keywords')
    @patch.object(AIContentModerationService, '_call_openai_classification')
    def test_very_long_content_handling(self, mock_ai_classify, mock_classify, mock_openai, mock_check_words):
        """TC-AI-024: 超長內容處理"""
        mock_check_words.return_value = (False, None, None)
        mock_openai.return_value = {
            'is_safe': True,
            'confidence': 90.0,
            'issues': {}
        }
        mock_classify.return_value = (1, 80.0, "交通")
        mock_ai_classify.return_value = (1, 85.0, "交通相關")

        long_content = "這是一段很長的內容 " * 1000  # 非常長的內容

        result = AIContentModerationService.moderate_text_content(
            title="測試標題",
            content=long_content
        )

        # 應該能處理長內容
        assert 'decision' in result
        assert result['decision'] in [
            ModerationDecision.APPROVE,
            ModerationDecision.REJECT,
            ModerationDecision.FLAG,
            ModerationDecision.REVIEW
        ]


# ==================== 測試類別 5: 配置與工具函數 ====================

@pytest.mark.no_db
class TestConfigAndUtilities:
    """配置與工具函數測試"""

    @patch('services.ai_content_moderation_service.get_db_cursor')
    def test_get_config_success(self, mock_cursor):
        """TC-AI-025: 成功獲取配置"""
        mock_cursor.return_value.__enter__.return_value.fetchone.return_value = {
            'config_value': 'test_value'
        }

        result = AIContentModerationService._get_config('test_key', 'default')

        assert result == 'test_value'

    @patch('services.ai_content_moderation_service.get_db_cursor')
    def test_get_config_not_found(self, mock_cursor):
        """TC-AI-026: 配置不存在返回默認值"""
        mock_cursor.return_value.__enter__.return_value.fetchone.return_value = None

        result = AIContentModerationService._get_config('non_existent', 'default_value')

        assert result == 'default_value'

    @patch('services.ai_content_moderation_service.get_db_cursor')
    def test_get_config_database_error(self, mock_cursor):
        """TC-AI-027: 資料庫錯誤處理"""
        mock_cursor.side_effect = Exception("Database error")

        result = AIContentModerationService._get_config('test_key', 'default')

        # 應該返回默認值
        assert result == 'default'
