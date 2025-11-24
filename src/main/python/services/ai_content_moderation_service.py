"""
AI Content Moderation Service
使用OpenAI API進行內容安全檢測與自動分類
"""

import os
import json
import time
from typing import Dict, List, Optional, Tuple
from decimal import Decimal
from ..utils.database import get_db_cursor
from ..services.moderation_service import ModerationService
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class ModerationConfig:
    """審核配置常量"""
    SENSITIVE_WORDS_TABLE = "sensitive_words"
    MODERATION_LOGS_TABLE = "moderation_logs"
    CATEGORIES_TABLE = "categories"
    CATEGORY_KEYWORDS_TABLE = "category_keywords"
    openai_api_key = os.getenv("OPENAI_API_KEY", "")


class ModerationDecision:
    """審核決策結果"""
    APPROVE = "approve"
    REJECT = "reject"
    FLAG = "flag"
    REVIEW = "review"


class AIContentModerationService:
    """AI內容審核服務"""

    # 配置常量
    DEFAULT_AUTO_APPROVE_THRESHOLD = 80  # 自動通過閾值
    DEFAULT_AUTO_REJECT_THRESHOLD = 90   # 自動拒絕閾值(惡意內容)
    DEFAULT_MANUAL_REVIEW_THRESHOLD = 60  # 人工審核閾值

    @staticmethod
    def _get_config(key: str, default: str = "") -> str:
        """從資料庫獲取配置"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    "SELECT config_value FROM moderation_config WHERE config_key = %s",
                    (key,)
                )
                result = cursor.fetchone()
                return result['config_value'] if result else default
        except Exception as e:
            print(f"Error getting config {key}: {e}")
            return default

    @staticmethod
    def _get_sensitive_words() -> Dict[str, List[Dict]]:
        """獲取敏感詞黑名單"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT word, category, severity, action
                    FROM sensitive_words
                    WHERE is_active = TRUE
                """)
                words = cursor.fetchall()

                # 組織成字典，按action分類
                result = {
                    'reject': [],
                    'flag': [],
                    'review': []
                }

                for word_info in words:
                    action = word_info['action']
                    result[action].append({
                        'word': word_info['word'],
                        'category': word_info['category'],
                        'severity': word_info['severity']
                    })

                return result
        except Exception as e:
            print(f"Error getting sensitive words: {e}")
            return {'reject': [], 'flag': [], 'review': []}

    @staticmethod
    def _check_sensitive_words(text: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        檢查文本是否包含敏感詞
        Returns: (is_blocked, action, matched_words)
        """
        sensitive_words = AIContentModerationService._get_sensitive_words()

        # 檢查reject級別(直接拒絕)
        for word_info in sensitive_words['reject']:
            if word_info['word'] in text:
                return True, 'reject', word_info['word']

        # 檢查flag級別(標記)
        flagged_words = []
        for word_info in sensitive_words['flag']:
            if word_info['word'] in text:
                flagged_words.append(word_info['word'])

        if flagged_words:
            return False, 'flag', ', '.join(flagged_words)

        # 檢查review級別(需審核)
        review_words = []
        for word_info in sensitive_words['review']:
            if word_info['word'] in text:
                review_words.append(word_info['word'])

        if review_words:
            return False, 'review', ', '.join(review_words)

        return False, None, None

    @staticmethod
    def _get_category_keywords() -> Dict[int, List[Dict]]:
        """獲取分類關鍵字"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    SELECT ck.category_id, ck.keyword, ck.weight, c.name as category_name
                    FROM category_keywords ck
                    JOIN categories c ON ck.category_id = c.id
                    WHERE ck.is_active = TRUE
                    ORDER BY ck.category_id, ck.weight DESC
                """)
                keywords = cursor.fetchall()

                # 組織成字典，按category_id分類
                result = {}
                for kw in keywords:
                    cat_id = kw['category_id']
                    if cat_id not in result:
                        result[cat_id] = []
                    result[cat_id].append({
                        'keyword': kw['keyword'],
                        'weight': float(kw['weight']),
                        'category_name': kw['category_name']
                    })

                return result
        except Exception as e:
            print(f"Error getting category keywords: {e}")
            return {}

    @staticmethod
    def _classify_by_keywords(text: str) -> Tuple[Optional[int], float, str]:
        """
        使用關鍵字進行分類
        Returns: (category_id, confidence, matched_keywords)
        """
        category_keywords = AIContentModerationService._get_category_keywords()

        if not category_keywords:
            return None, 0.0, ""

        # 計算每個分類的匹配分數
        scores = {}
        matched_kws = {}

        for cat_id, keywords in category_keywords.items():
            score = 0.0
            matches = []

            for kw_info in keywords:
                keyword = kw_info['keyword']
                weight = kw_info['weight']

                # 計算關鍵字在文本中出現的次數
                count = text.count(keyword)
                if count > 0:
                    score += weight * count
                    matches.append(keyword)

            if score > 0:
                scores[cat_id] = score
                matched_kws[cat_id] = ', '.join(matches)

        if not scores:
            return None, 0.0, ""

        # 找出最高分的分類
        best_cat_id = max(scores, key=scores.get)
        max_score = scores[best_cat_id]

        # 計算信心度 (normalized to 0-100)
        # 簡單的啟發式: score > 5 -> 高信心, score > 3 -> 中信心
        if max_score >= 5:
            confidence = min(85.0, 60.0 + max_score * 5)
        elif max_score >= 3:
            confidence = min(75.0, 50.0 + max_score * 8)
        else:
            confidence = min(60.0, 30.0 + max_score * 10)

        return best_cat_id, confidence, matched_kws.get(best_cat_id, "")

    @staticmethod
    def _call_openai_moderation(text: str) -> Dict:
        """
        調用OpenAI Moderation API檢測內容安全性
        """
        api_key = ModerationConfig.openai_api_key

        if not api_key:
            print("Warning: OpenAI API key not configured")
            return {
                'is_safe': True,
                'confidence': 50.0,
                'issues': {},
                'error': 'API key not configured'
            }

        try:
            import requests

            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }

            data = {
                'model': 'omni-moderation-latest',
                'input': text
            }

            response = requests.post(
                'https://api.openai.com/v1/moderations',
                headers=headers,
                json=data,
                timeout=100
            )

            response.raise_for_status()
            result = response.json()

            # 解析結果
            if result.get('results'):
                moderation_result = result['results'][0]
                flagged = moderation_result.get('flagged', False)
                categories = moderation_result.get('categories', {})
                category_scores = moderation_result.get('category_scores', {})

                # 找出最高分的問題類別
                max_score = 0.0
                issues = {}

                for category, score in category_scores.items():
                    if score > 0.1:  # 只記錄分數 > 0.1 的
                        issues[category] = round(score, 3)
                        max_score = max(max_score, score)

                # 計算安全信心度
                confidence = (1 - max_score) * 100

                return {
                    'is_safe': not flagged,
                    'confidence': round(confidence, 2),
                    'issues': issues,
                    'raw_response': result
                }

        except Exception as e:
            print(f"Error calling OpenAI Moderation API: {e}")
            return {
                'is_safe': True,
                'confidence': 50.0,
                'issues': {},
                'error': str(e)
            }

    @staticmethod
    def _call_openai_classification(title: str, content: str) -> Tuple[Optional[int], float, str]:
        """
        調用OpenAI API進行智能分類
        """
        api_key = ModerationConfig.openai_api_key
        model = AIContentModerationService._get_config('openai_model', 'gpt-4o-mini')

        if not api_key:
            print("Warning: OpenAI API key not configured")
            return None, 0.0, "API key not configured"

        try:
            import requests

            # 獲取可用的分類列表
            with get_db_cursor() as cursor:
                cursor.execute("SELECT id, name, description FROM categories WHERE parent_id IS NULL")
                categories = cursor.fetchall()

            if not categories:
                return None, 0.0, "No categories available"

            # 構建分類選項字符串
            category_options = "\n".join([
                f"{cat['id']}. {cat['name']}: {cat['description'] or ''}"
                for cat in categories
            ])

            # 構建prompt
            prompt = f"""你是一個政府市民意見分類助手，負責判斷「市民意見」與「政府各局處」之間的關聯程度。
            你的任務是：
            1. 判斷內容是否與任何一個局處明顯相關
            2. 若有相關，選出最符合的分類
            3. 若沒有明顯相關，分類為「其他」並給予非常低的信心分數（0～20）

            === 市民意見 ===
            標題：{title}
            內容：{content}

            === 可用局處分類 ===
            {category_options}

            === 分類標準（請嚴格遵守） ===
            你必須依照以下準則進行分類與評分：

            【A. 高相關（80–100 分）】
            - 市民意見中明確提到該局處負責的具體事項 
            - 例如：道路、交通號誌 → 交通局；醫療院所 → 衛生局；土地使用 → 都發局

            【B. 中度相關（40–79 分）】
            - 與某局處略有關聯，但資訊不足以非常確定

            【C. 低相關（0–39 分）】
            - 內容模糊、無具體事件、無法判斷負責單位
            - 投訴只是一般抱怨（例如「政府效率低」、「官僚太多」）
            - 表面看似跟社會議題有關，但沒有明確對象（如「台灣治安很差」→ 論述太抽象）

            【D. 完全無關（0–10 分）】
            - 與政府業務無明顯關係的內容
            - 單純抱怨、不屬於任何局處管轄範圍

            === 回應格式（只能回傳 JSON）===
            {
                "category_id": <最適合的分類ID或 其他類別ID>,
                "confidence": <0-100>,
                "reason": "<簡短的分類理由，若不相關需說明為何給低分>"
            }

            請務必只回傳 JSON，不要額外文字。
            """

            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }

            data = {
                'model': model,
                'messages': [
                    {
                        'role': 'system',
                        'content': '你是一個專業的市民意見分類助手，能準確理解市民的訴求並分類到正確的政府部門。'
                    },
                    {
                        'role': 'user',
                        'content': prompt
                    }
                ],
                'temperature': 0.3,
                'response_format': {'type': 'json_object'}
            }

            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=75
            )

            response.raise_for_status()
            result = response.json()

            # 解析結果
            if result.get('choices'):
                content_text = result['choices'][0]['message']['content']
                classification = json.loads(content_text)

                category_id = classification.get('category_id')
                confidence = float(classification.get('confidence', 0))
                reason = classification.get('reason', '')

                return category_id, confidence, reason

        except Exception as e:
            print(f"Error calling OpenAI Classification API: {e}")
            return None, 0.0, f"Error: {str(e)}"

    @staticmethod
    def moderate_text_content(
        title: str,
        content: str,
        current_category_id: Optional[int] = None
    ) -> Dict:
        """
        審核文本內容(標題+內容)
        Returns: {
            'decision': 'approve'|'reject'|'flag'|'review',
            'confidence': float,
            'suggested_category_id': int or None,
            'category_confidence': float,
            'is_safe': bool,
            'detected_issues': dict,
            'blocked_keywords': str or None,
            'matched_keywords': str or None,
            'reason': str,
            'needs_manual_review': bool
        }
        """
        start_time = time.time()

        # 完整文本
        full_text = f"{title} {content}"

        # 1. 檢查敏感詞黑名單
        is_blocked, action, blocked_words = AIContentModerationService._check_sensitive_words(full_text)

        if is_blocked and action == 'reject':
            return {
                'decision': ModerationDecision.REJECT,
                'confidence': 100.0,
                'suggested_category_id': current_category_id,
                'category_confidence': 0.0,
                'is_safe': False,
                'detected_issues': {'sensitive_words': 1.0},
                'blocked_keywords': blocked_words,
                'matched_keywords': None,
                'reason': f'包含敏感詞: {blocked_words}',
                'needs_manual_review': False,
                'processing_time_ms': int((time.time() - start_time) * 1000)
            }

        # 2. 調用OpenAI Moderation API檢測安全性
        safety_result = AIContentModerationService._call_openai_moderation(full_text)

        # 如果檢測到不安全內容且信心度高,直接拒絕
        auto_reject_threshold = float(
            AIContentModerationService._get_config(
                'auto_reject_threshold',
                str(AIContentModerationService.DEFAULT_AUTO_REJECT_THRESHOLD)
            )
        )

        if not safety_result['is_safe'] and safety_result['confidence'] < (100 - auto_reject_threshold):
            return {
                'decision': ModerationDecision.REJECT,
                'confidence': 100 - safety_result['confidence'],
                'suggested_category_id': current_category_id,
                'category_confidence': 0.0,
                'is_safe': False,
                'detected_issues': safety_result['issues'],
                'blocked_keywords': None,
                'matched_keywords': None,
                'reason': f"檢測到不安全內容: {', '.join(safety_result['issues'].keys())}",
                'needs_manual_review': False,
                'processing_time_ms': int((time.time() - start_time) * 1000)
            }

        # 3. 自動分類
        suggested_category_id = current_category_id
        category_confidence = 0.0
        matched_keywords = None
        ai_reason = " "

        # 3a. 先嘗試使用關鍵字分類
        enable_category_keywords = AIContentModerationService._get_config(
            'enable_category_keywords', 'true'
        ) == 'true'

        if enable_category_keywords:
            kw_cat_id, kw_confidence, kw_matches = AIContentModerationService._classify_by_keywords(full_text)
            if kw_cat_id:
                suggested_category_id = kw_cat_id
                category_confidence = kw_confidence
                matched_keywords = kw_matches

        # 3b. 如果關鍵字分類信心度不高,使用OpenAI分類
        if category_confidence < 70:
            ai_cat_id, ai_confidence, ai_reason = AIContentModerationService._call_openai_classification(
                title, content
            )
            if ai_cat_id and ai_confidence > category_confidence:
                suggested_category_id = ai_cat_id
                category_confidence = ai_confidence

        # 4. 決策邏輯
        auto_approve_threshold = float(
            AIContentModerationService._get_config(
                'auto_approve_threshold',
                str(AIContentModerationService.DEFAULT_AUTO_APPROVE_THRESHOLD)
            )
        )

        manual_review_threshold = float(
            AIContentModerationService._get_config(
                'manual_review_threshold',
                str(AIContentModerationService.DEFAULT_MANUAL_REVIEW_THRESHOLD)
            )
        )

        # 綜合信心度 = 安全信心度和分類信心度的平均
        overall_confidence = (safety_result['confidence'] + category_confidence) / 2

        # 決策
        if action == 'flag' or (not safety_result['is_safe'] and safety_result['confidence'] >= 50):
            # 被標記或安全性存疑
            decision = ModerationDecision.FLAG
            needs_manual_review = True
            reason = f"內容被標記需要審核: {blocked_words or ', '.join(safety_result['issues'].keys())}"
        elif overall_confidence >= auto_approve_threshold and safety_result['is_safe']:
            # 高信心度且安全 -> 自動通過
            decision = ModerationDecision.APPROVE
            needs_manual_review = False
            reason = "自動審核通過"     
        elif overall_confidence < manual_review_threshold:
            # 低信心度 -> 自動拒絕
            decision = ModerationDecision.REJECT
            needs_manual_review = False
            reason = f"相關度較低 ({overall_confidence:.1f}%), 自動拒絕無效意見: {ai_reason}"
  
        else:
            # 中等信心度 -> 需要審核
            decision = ModerationDecision.REVIEW
            needs_manual_review = True
            reason = f"相關度中等 ({overall_confidence:.1f}%), 需要人工審核: {ai_reason}"

        return {
            'decision': decision,
            'confidence': round(overall_confidence, 2),
            'suggested_category_id': suggested_category_id,
            'category_confidence': round(category_confidence, 2),
            'is_safe': safety_result['is_safe'],
            'detected_issues': safety_result['issues'],
            'blocked_keywords': blocked_words if action else None,
            'matched_keywords': matched_keywords,
            'reason': reason,
            'needs_manual_review': needs_manual_review,
            'processing_time_ms': int((time.time() - start_time) * 1000)
        }

    @staticmethod
    def log_moderation_decision(
        opinion_id: int,
        moderation_type: str,
        decision: str,
        confidence_score: float,
        suggested_category_id: Optional[int],
        category_confidence: Optional[float],
        is_safe: bool,
        detected_issues: Dict,
        blocked_keywords: Optional[str],
        matched_keywords: Optional[str],
        api_request: Optional[Dict] = None,
        api_response: Optional[Dict] = None,
        processing_time_ms: Optional[int] = None
    ) -> bool:
        """記錄審核決策到資料庫"""
        try:
            with get_db_cursor() as cursor:
                cursor.execute("""
                    INSERT INTO moderation_logs (
                        opinion_id, moderation_type, service_provider,
                        decision, confidence_score,
                        suggested_category_id, category_confidence,
                        is_safe, detected_issues,
                        api_request, api_response, processing_time_ms,
                        blocked_by_keywords, matched_category_keywords
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                """, (
                    opinion_id, moderation_type, 'openai',
                    decision, confidence_score,
                    suggested_category_id, category_confidence,
                    is_safe, json.dumps(detected_issues, ensure_ascii=False),
                    json.dumps(api_request, ensure_ascii=False) if api_request else None,
                    json.dumps(api_response, ensure_ascii=False) if api_response else None,
                    processing_time_ms,
                    blocked_keywords, matched_keywords
                ))
                return True
        except Exception as e:
            print(f"Error logging moderation decision: {e}")
            return False

    @staticmethod
    def update_opinion_moderation_status(
        opinion_id: int,
        auto_moderation_status: str,
        auto_moderation_score: float,
        auto_category_id: Optional[int],
        moderation_reason: str,
        needs_manual_review: bool
    ) -> bool:
        """更新意見的審核狀態（包含真正的 status）"""
        try:
            # 根據 AI 審核結果決定主狀態
            if needs_manual_review:
                final_status = "pending"
            elif auto_moderation_status == "approved":
                final_status = "approved"
                ModerationService.approve_opinion(opinion_id, moderator_id=0)
            elif auto_moderation_status == "rejected":
                final_status = "rejected"
                ModerationService.reject_opinion(opinion_id, reason=moderation_reason, moderator_id=0)
            else:
                final_status = "pending"

            with get_db_cursor() as cursor:
                cursor.execute("""
                    UPDATE opinions
                    SET 
                        status = %s,
                        auto_moderation_status = %s,
                        auto_moderation_score = %s,
                        auto_category_id = %s,
                        moderation_reason = %s,
                        needs_manual_review = %s,
                        category_id = COALESCE(category_id, %s)
                    WHERE id = %s
                """, (
                    final_status,
                    auto_moderation_status,
                    auto_moderation_score,
                    auto_category_id,
                    moderation_reason,
                    needs_manual_review,
                    auto_category_id,
                    opinion_id
                ))

                return True

        except Exception as e:
            print(f"Error updating opinion moderation status: {e}")
            return False

