"""
Async Moderation Tasks
異步審核任務處理器
"""

import asyncio
from typing import Optional, List
from ..services.ai_content_moderation_service import AIContentModerationService, ModerationDecision
from ..services.ai_media_moderation_service import AIMediaModerationService
from ..services.moderation_service import ModerationService


async def process_opinion_moderation(
    opinion_id: int,
    title: str,
    content: str,
    media_files: Optional[List[dict]] = None,
    current_category_id: Optional[int] = None
):
    """
    異步處理意見審核
    1. 審核文本內容
    2. 審核多媒體內容
    3. 更新意見狀態
    """
    try:
        print(f"[AI Moderation] Starting moderation for opinion {opinion_id}")

        # 1. 審核文本內容
        text_result = AIContentModerationService.moderate_text_content(
            title=title,
            content=content,
            current_category_id=current_category_id
        )

        print(f"[AI Moderation] Text moderation result: {text_result['decision']}, confidence: {text_result['confidence']}")

        # 記錄文本審核日誌
        AIContentModerationService.log_moderation_decision(
            opinion_id=opinion_id,
            moderation_type='text',
            decision=text_result['decision'],
            confidence_score=text_result['confidence'],
            suggested_category_id=text_result['suggested_category_id'],
            category_confidence=text_result['category_confidence'],
            is_safe=text_result['is_safe'],
            detected_issues=text_result['detected_issues'],
            blocked_keywords=text_result.get('blocked_keywords'),
            matched_keywords=text_result.get('matched_keywords'),
            processing_time_ms=text_result.get('processing_time_ms')
        )

        # 如果文本審核就被拒絕，直接更新狀態並返回
        if text_result['decision'] == ModerationDecision.REJECT:
            ModerationService.reject_opinion(opinion_id, reason=text_result['reason'], moderator_id=0)
            AIContentModerationService.update_opinion_moderation_status(
                opinion_id=opinion_id,
                auto_moderation_status='rejected',
                auto_moderation_score=text_result['confidence'],
                auto_category_id=text_result['suggested_category_id'],
                category_confidence=text_result['category_confidence'],
                moderation_reason=text_result['reason'],
                needs_manual_review=False
            )
            print(f"[AI Moderation] Opinion {opinion_id} rejected due to text content")
            return

        # 2. 審核多媒體內容(如果有)
        media_result = None
        if media_files and len(media_files) > 0:
            print(f"[AI Moderation] Checking {len(media_files)} media files for opinion {opinion_id}")
            media_result = AIMediaModerationService.moderate_media_batch(
                media_files=media_files,
                opinion_id=opinion_id
            )

            print(f"[AI Moderation] Media moderation result: {media_result['overall_decision']}")

            # 如果多媒體審核被拒絕
            if media_result['overall_decision'] == ModerationDecision.REJECT:
                ModerationService.reject_opinion(opinion_id, reason=media_result['reason'], moderator_id=0)
                AIContentModerationService.update_opinion_moderation_status(
                    opinion_id=opinion_id,
                    auto_moderation_status='rejected',
                    auto_moderation_score=media_result['overall_confidence'],
                    auto_category_id=text_result['suggested_category_id'],
                    category_confidence=text_result['category_confidence'],
                    moderation_reason=f"多媒體內容不當: {media_result['reason']}",
                    needs_manual_review=False
                )
                print(f"[AI Moderation] Opinion {opinion_id} rejected due to media content")
                return

        # 3. 綜合決策
        final_decision = text_result['decision']
        needs_manual_review = text_result['needs_manual_review']
        final_reason = text_result['reason']

        # 如果多媒體審核需要人工審核，則整體需要人工審核
        if media_result and media_result['needs_manual_review']:
            needs_manual_review = True
            if media_result['overall_decision'] == ModerationDecision.REVIEW:
                final_decision = ModerationDecision.REVIEW
                final_reason = f"{text_result['reason']}; 多媒體內容需要人工審核"

        # 映射決策到auto_moderation_status
        status_mapping = {
            ModerationDecision.APPROVE: 'approved',
            ModerationDecision.REJECT: 'rejected',
            ModerationDecision.FLAG: 'flagged',
            ModerationDecision.REVIEW: 'pending'
        }

        auto_moderation_status = status_mapping.get(final_decision, 'pending')
        if not needs_manual_review:
            ModerationService.approve_opinion(opinion_id, moderator_id=0)
        # 4. 更新意見的審核狀態
        AIContentModerationService.update_opinion_moderation_status(
            opinion_id=opinion_id,
            auto_moderation_status=auto_moderation_status,
            auto_moderation_score=text_result['confidence'],
            auto_category_id=text_result['suggested_category_id'],
            category_confidence=text_result['category_confidence'],
            moderation_reason=final_reason,
            needs_manual_review=needs_manual_review
        )

        print(f"[AI Moderation] Opinion {opinion_id} moderation completed: {auto_moderation_status}, needs_review: {needs_manual_review}")

    except Exception as e:
        print(f"[AI Moderation] Error processing opinion {opinion_id}: {e}")
        # 發生錯誤時，標記需要人工審核
        try:
            AIContentModerationService.update_opinion_moderation_status(
                opinion_id=opinion_id,
                auto_moderation_status='pending',
                auto_moderation_score=0.0,
                auto_category_id=current_category_id,
                category_confidence=0.0,
                moderation_reason=f"自動審核錯誤: {str(e)}",
                needs_manual_review=True
            )
        except Exception as inner_e:
            print(f"[AI Moderation] Failed to update error status: {inner_e}")


def sync_process_opinion_moderation(*args, **kwargs):
    """
    同步包裝器，用於在非async環境中調用
    """
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(process_opinion_moderation(*args, **kwargs))
    finally:
        loop.close()
