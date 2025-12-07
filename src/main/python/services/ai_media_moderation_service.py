"""
AI Media Moderation Service
使用OpenAI Vision API進行圖片/視頻內容檢測
"""

import os
import json
import time
import base64
from typing import Dict, Optional
from pathlib import Path
from services.ai_content_moderation_service import ModerationDecision, AIContentModerationService, ModerationConfig


class AIMediaModerationService:
    """AI多媒體內容審核服務"""

    @staticmethod
    def _encode_image_to_base64(image_path: str) -> Optional[str]:
        """將圖片編碼為base64"""
        try:
            with open(image_path, 'rb') as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            print(f"Error encoding image: {e}")
            return None

    @staticmethod
    def _get_image_mime_type(file_path: str) -> str:
        """獲取圖片MIME類型"""
        ext = Path(file_path).suffix.lower()
        mime_types = {
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.png': 'image/png',
            '.gif': 'image/gif',
            '.webp': 'image/webp'
        }
        return mime_types.get(ext, 'image/jpeg')

    @staticmethod
    def _call_openai_vision_api(image_path: str, is_url: bool = False) -> Dict:
        """
        調用OpenAI Vision API檢測圖片內容
        """
        api_key = ModerationConfig.openai_api_key
        model = AIContentModerationService._get_config('openai_model', 'gpt-4o-mini')

        if not api_key:
            print("Warning: OpenAI API key not configured")
            return {
                'is_safe': True,
                'confidence': 50.0,
                'issues': [],
                'description': '',
                'error': 'API key not configured'
            }

        try:
            import requests

            headers = {
                'Authorization': f'Bearer {api_key}',
                'Content-Type': 'application/json'
            }

            # 構建prompt
            prompt = """請仔細分析這張圖片,判斷是否包含以下不當內容:

1. 暴力內容 (violence): 血腥、暴力場景、武器攻擊等
2. 仇恨內容 (hate): 種族歧視、性別歧視、仇恨符號等
3. 不雅內容 (sexual): 裸露、色情、性暗示等
4. 自殘內容 (self-harm): 自殺、自殘行為等
5. 騷擾內容 (harassment): 恐嚇、威脅等

請以JSON格式回應,包含:
{
    "is_safe": true/false,
    "detected_issues": ["issue1", "issue2"],
    "severity_scores": {
        "violence": 0-1的分數,
        "hate": 0-1的分數,
        "sexual": 0-1的分數,
        "self-harm": 0-1的分數,
        "harassment": 0-1的分數
    },
    "description": "簡短描述圖片內容",
    "recommendation": "approve/reject/review"
}

只需回傳JSON,不要其他說明文字。"""

            # 構建圖片內容
            if is_url:
                image_content = {
                    "type": "image_url",
                    "image_url": {
                        "url": image_path
                    }
                }
            else:
                # 本地文件,需要編碼為base64
                base64_image = AIMediaModerationService._encode_image_to_base64(image_path)
                if not base64_image:
                    return {
                        'is_safe': True,
                        'confidence': 0.0,
                        'issues': [],
                        'description': '',
                        'error': 'Failed to encode image'
                    }

                mime_type = AIMediaModerationService._get_image_mime_type(image_path)
                image_content = {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{base64_image}"
                    }
                }

            data = {
                'model': model,
                'messages': [
                    {
                        'role': 'system',
                        'content': '你是一個專業的圖片內容審核助手,能準確識別不當內容。'
                    },
                    {
                        'role': 'user',
                        'content': [
                            {
                                "type": "text",
                                "text": prompt
                            },
                            image_content
                        ]
                    }
                ],
                'temperature': 0.2,
                'max_tokens': 500,
                'response_format': {'type': 'json_object'}
            }

            response = requests.post(
                'https://api.openai.com/v1/chat/completions',
                headers=headers,
                json=data,
                timeout=30
            )

            response.raise_for_status()
            result = response.json()

            # 解析結果
            if result.get('choices'):
                content_text = result['choices'][0]['message']['content']
                analysis = json.loads(content_text)

                is_safe = analysis.get('is_safe', True)
                detected_issues = analysis.get('detected_issues', [])
                severity_scores = analysis.get('severity_scores', {})
                description = analysis.get('description', '')
                recommendation = analysis.get('recommendation', 'approve')

                # 計算最高嚴重度分數
                max_severity = max(severity_scores.values()) if severity_scores else 0.0

                # 計算信心度
                if is_safe:
                    confidence = (1 - max_severity) * 100
                else:
                    confidence = max_severity * 100

                return {
                    'is_safe': is_safe,
                    'confidence': round(confidence, 2),
                    'issues': detected_issues,
                    'severity_scores': severity_scores,
                    'description': description,
                    'recommendation': recommendation,
                    'raw_response': result
                }

        except Exception as e:
            print(f"Error calling OpenAI Vision API: {e}")
            return {
                'is_safe': True,
                'confidence': 50.0,
                'issues': [],
                'description': '',
                'error': str(e)
            }

    @staticmethod
    def moderate_image(image_path: str, opinion_id: int) -> Dict:
        """
        審核圖片內容
        Returns: {
            'decision': 'approve'|'reject'|'review',
            'confidence': float,
            'is_safe': bool,
            'detected_issues': list,
            'description': str,
            'reason': str,
            'needs_manual_review': bool
        }
        """
        start_time = time.time()

        # 調用OpenAI Vision API
        vision_result = AIMediaModerationService._call_openai_vision_api(image_path)

        # 獲取配置閾值
        auto_reject_threshold = float(
            AIContentModerationService._get_config(
                'auto_reject_threshold',
                str(AIContentModerationService.DEFAULT_AUTO_REJECT_THRESHOLD)
            )
        )

        manual_review_threshold = float(
            AIContentModerationService._get_config(
                'manual_review_threshold',
                str(AIContentModerationService.DEFAULT_MANUAL_REVIEW_THRESHOLD)
            )
        )

        confidence = vision_result['confidence']
        is_safe = vision_result['is_safe']
        detected_issues = vision_result.get('issues', [])

        # 決策邏輯
        if not is_safe and confidence >= auto_reject_threshold:
            # 高信心度檢測到不安全內容 -> 自動拒絕
            decision = ModerationDecision.REJECT
            needs_manual_review = False
            reason = f"檢測到不當圖片內容: {', '.join(detected_issues)}"
        elif not is_safe and confidence >= manual_review_threshold:
            # 中等信心度檢測到不安全內容 -> 需要人工審核
            decision = ModerationDecision.REVIEW
            needs_manual_review = True
            reason = f"圖片內容可能不當,需要人工審核: {', '.join(detected_issues)}"
        elif not is_safe:
            # 低信心度不安全 -> 標記
            decision = ModerationDecision.FLAG
            needs_manual_review = True
            reason = "圖片內容存疑,已標記需審核"
        else:
            # 安全內容 -> 通過
            decision = ModerationDecision.APPROVE
            needs_manual_review = False
            reason = "圖片內容審核通過"

        result = {
            'decision': decision,
            'confidence': confidence,
            'is_safe': is_safe,
            'detected_issues': detected_issues,
            'description': vision_result.get('description', ''),
            'reason': reason,
            'needs_manual_review': needs_manual_review,
            'processing_time_ms': int((time.time() - start_time) * 1000)
        }

        # 記錄審核日誌
        AIContentModerationService.log_moderation_decision(
            opinion_id=opinion_id,
            moderation_type='image',
            decision=decision,
            confidence_score=confidence,
            suggested_category_id=None,
            category_confidence=None,
            is_safe=is_safe,
            detected_issues={'issues': detected_issues, 'scores': vision_result.get('severity_scores', {})},
            blocked_keywords=None,
            matched_keywords=None,
            api_response=vision_result.get('raw_response'),
            processing_time_ms=result['processing_time_ms']
        )

        return result

    @staticmethod
    def moderate_video(video_path: str, opinion_id: int) -> Dict:
        """
        審核視頻內容
        目前簡化實現: 提取關鍵幀並使用圖片審核
        未來可以使用專門的視頻分析服務
        """
        # TODO: 實現視頻幀提取和分析
        # 目前返回通過,標記需要人工審核
        return {
            'decision': ModerationDecision.REVIEW,
            'confidence': 50.0,
            'is_safe': True,
            'detected_issues': [],
            'description': '視頻內容需要人工審核',
            'reason': '視頻自動審核功能尚未完全實現,需要人工審核',
            'needs_manual_review': True,
            'processing_time_ms': 0
        }

    @staticmethod
    def moderate_media_batch(media_files: list, opinion_id: int) -> Dict:
        """
        批量審核多個多媒體文件
        Returns: {
            'overall_decision': 'approve'|'reject'|'review',
            'overall_confidence': float,
            'results': [individual results],
            'needs_manual_review': bool
        }
        """
        results = []
        all_safe = True
        min_confidence = 100.0
        any_needs_review = False

        for media_file in media_files:
            media_type = media_file.get('media_type')
            file_path = media_file.get('file_path')

            if media_type == 'image':
                result = AIMediaModerationService.moderate_image(file_path, opinion_id)
            elif media_type == 'video':
                result = AIMediaModerationService.moderate_video(file_path, opinion_id)
            else:
                # audio 或其他類型,暫時通過
                result = {
                    'decision': ModerationDecision.APPROVE,
                    'confidence': 100.0,
                    'is_safe': True,
                    'reason': f'{media_type}類型暫不審核',
                    'needs_manual_review': False
                }

            results.append({
                'file_path': file_path,
                'media_type': media_type,
                **result
            })

            if not result['is_safe']:
                all_safe = False

            if result['decision'] == ModerationDecision.REJECT:
                # 任何一個被拒絕,整體就拒絕
                return {
                    'overall_decision': ModerationDecision.REJECT,
                    'overall_confidence': result['confidence'],
                    'results': results,
                    'needs_manual_review': False,
                    'reason': f"多媒體文件 {file_path} 被拒絕: {result['reason']}"
                }

            min_confidence = min(min_confidence, result['confidence'])
            any_needs_review = any_needs_review or result['needs_manual_review']

        # 整體決策
        if any_needs_review or not all_safe:
            overall_decision = ModerationDecision.REVIEW
        else:
            overall_decision = ModerationDecision.APPROVE

        return {
            'overall_decision': overall_decision,
            'overall_confidence': min_confidence,
            'results': results,
            'needs_manual_review': any_needs_review,
            'reason': '所有多媒體文件審核完成'
        }
