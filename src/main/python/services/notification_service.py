"""
Notification service
"""

from typing import List
from ..models.notification import Notification, NotificationCreate
from ..utils.database import get_db_cursor


class NotificationService:
    """Service for notification management"""

    @staticmethod
    def create_notification(notification_data: NotificationCreate) -> Optional[Notification]:
        """Create a new notification"""
        query = """
            INSERT INTO notifications (user_id, opinion_id, type, title, content)
            VALUES (%s, %s, %s, %s, %s)
        """

        try:
            with get_db_cursor() as cursor:
                cursor.execute(
                    query,
                    (notification_data.user_id, notification_data.opinion_id,
                     notification_data.type.value, notification_data.title,
                     notification_data.content)
                )

                notification_id = cursor.lastrowid

                cursor.execute(
                    "SELECT * FROM notifications WHERE id = %s",
                    (notification_id,)
                )

                return Notification(**cursor.fetchone())
        except Exception as e:
            print(f"Error creating notification: {e}")
            return None

    @staticmethod
    def get_user_notifications(user_id: int, unread_only: bool = False) -> List[Notification]:
        """Get user's notifications"""
        query = "SELECT * FROM notifications WHERE user_id = %s"

        if unread_only:
            query += " AND is_read = FALSE"

        query += " ORDER BY created_at DESC LIMIT 50"

        with get_db_cursor() as cursor:
            cursor.execute(query, (user_id,))
            return [Notification(**row) for row in cursor.fetchall()]

    @staticmethod
    def mark_as_read(notification_id: int, user_id: int) -> bool:
        """Mark notification as read"""
        query = """
            UPDATE notifications
            SET is_read = TRUE
            WHERE id = %s AND user_id = %s
        """

        with get_db_cursor() as cursor:
            cursor.execute(query, (notification_id, user_id))
            return cursor.rowcount > 0


from typing import Optional
