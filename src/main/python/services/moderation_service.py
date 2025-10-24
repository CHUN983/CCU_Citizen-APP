"""
Moderation service for admin operations
"""

from typing import Optional
from models.opinion import OpinionStatus
from models.notification import NotificationCreate, NotificationType
from utils.database import get_db_cursor
from services.notification_service import NotificationService


class ModerationService:
    """Service for content moderation"""

    @staticmethod
    def approve_opinion(opinion_id: int, moderator_id: int) -> bool:
        """Approve an opinion"""
        return ModerationService._change_status(
            opinion_id, moderator_id, OpinionStatus.APPROVED,
            "Opinion approved", "Your opinion has been approved and is now public"
        )

    @staticmethod
    def reject_opinion(opinion_id: int, moderator_id: int, reason: str = "") -> bool:
        """Reject an opinion"""
        content = f"Your opinion has been rejected. Reason: {reason}" if reason else "Your opinion has been rejected"
        return ModerationService._change_status(
            opinion_id, moderator_id, OpinionStatus.REJECTED,
            "Opinion rejected", content
        )

    @staticmethod
    def merge_opinions(source_id: int, target_id: int, moderator_id: int) -> bool:
        """Merge source opinion into target opinion"""
        query = """
            UPDATE opinions
            SET merged_to_id = %s, status = 'merged'
            WHERE id = %s
        """

        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (target_id, source_id))

                # Log history
                cursor.execute(
                    """INSERT INTO opinion_history (opinion_id, user_id, action, changes)
                       VALUES (%s, %s, 'merged', JSON_OBJECT('merged_to', %s))""",
                    (source_id, moderator_id, target_id)
                )

                # Notify opinion owner (non-blocking)
                cursor.execute("SELECT user_id FROM opinions WHERE id = %s", (source_id,))
                owner = cursor.fetchone()

                if owner:
                    try:
                        NotificationService.create_notification(
                            NotificationCreate(
                                user_id=owner['user_id'],
                                opinion_id=source_id,
                                type=NotificationType.MERGED,
                                title="Opinion merged",
                                content=f"Your opinion has been merged with opinion #{target_id}"
                            )
                        )
                    except Exception as notif_error:
                        print(f"Error creating notification: {notif_error}")
                        # Continue anyway

                return True
        except Exception as e:
            print(f"Error merging opinions: {e}")
            return False

    @staticmethod
    def delete_comment(comment_id: int, moderator_id: int) -> bool:
        """Soft delete a comment"""
        query = """
            UPDATE comments
            SET is_deleted = TRUE, deleted_by = %s, deleted_at = NOW()
            WHERE id = %s
        """

        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (moderator_id, comment_id))
                return cursor.rowcount > 0
        except Exception as e:
            print(f"Error deleting comment: {e}")
            return False

    @staticmethod
    def update_opinion_category(opinion_id: int, category_id: int, moderator_id: int) -> bool:
        """Update opinion category"""
        query = "UPDATE opinions SET category_id = %s WHERE id = %s"

        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (category_id, opinion_id))

                # Log history
                cursor.execute(
                    """INSERT INTO opinion_history (opinion_id, user_id, action, changes)
                       VALUES (%s, %s, 'updated', JSON_OBJECT('category_id', %s))""",
                    (opinion_id, moderator_id, category_id)
                )

                return True
        except Exception as e:
            print(f"Error updating category: {e}")
            return False

    @staticmethod
    def _change_status(opinion_id: int, moderator_id: int, new_status: OpinionStatus,
                      notification_title: str, notification_content: str) -> bool:
        """Helper to change opinion status and notify owner"""
        query = "UPDATE opinions SET status = %s WHERE id = %s"

        try:
            with get_db_cursor() as cursor:
                # Get old status
                cursor.execute("SELECT status, user_id FROM opinions WHERE id = %s", (opinion_id,))
                opinion = cursor.fetchone()

                if not opinion:
                    return False

                old_status = opinion['status']

                # Update status
                cursor.execute(query, (new_status.value, opinion_id))

                # Log history
                cursor.execute(
                    """INSERT INTO opinion_history (opinion_id, user_id, action, old_status, new_status)
                       VALUES (%s, %s, 'status_changed', %s, %s)""",
                    (opinion_id, moderator_id, old_status, new_status.value)
                )

                # Notify owner (non-blocking, don't fail if notification fails)
                try:
                    NotificationService.create_notification(
                        NotificationCreate(
                            user_id=opinion['user_id'],
                            opinion_id=opinion_id,
                            type=NotificationType.STATUS_CHANGE,
                            title=notification_title,
                            content=notification_content
                        )
                    )
                except Exception as notif_error:
                    print(f"Error creating notification: {notif_error}")
                    # Continue anyway - notification failure should not fail the moderation

                return True
        except Exception as e:
            print(f"Error changing status: {e}")
            return False
