"""
Notification service
"""

from typing import List, Optional
from models.notification import Notification, NotificationCreate
from utils.database import get_db_cursor


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
        """Mark notification as read (idempotent)"""
        print("mark_as_read: id =", notification_id, "user_id =", user_id)

        query = """
            UPDATE notifications
            SET is_read = TRUE
            WHERE id = %s AND user_id = %s
        """

        with get_db_cursor() as cursor:
            cursor.execute(query, (notification_id, user_id))

            # 如果 rowcount = 0，不代表不存在，可能是 is_read 已經是 TRUE
            # ➜ 改成檢查資料是否存在
            cursor.execute(
                "SELECT 1 FROM notifications WHERE id = %s AND user_id = %s",
                (notification_id, user_id)
            )
            exists = cursor.fetchone() is not None

            print("exists =", exists, "rowcount =", cursor.rowcount)
            return exists



from typing import Optional
import math


def calculate_next_milestone(current_count: int) -> int:
    """
    Calculate next notification milestone using power of 2 progression
    級距: 1, 2, 4, 8, 16, 32, 64...
    """
    if current_count <= 0:
        return 1

    # Find the power of 2 that is greater than current_count
    power = math.ceil(math.log2(current_count))
    next_milestone = 2 ** power

    # If current_count is already a power of 2, get the next one
    if next_milestone == current_count:
        next_milestone = 2 ** (power + 1)

    return next_milestone


class MilestoneNotificationService:
    """Service for managing milestone-based notifications"""

    @staticmethod
    def check_and_notify_milestone(opinion_id: int, milestone_type: str,
                                   current_count: int, opinion_owner_id: int) -> bool:
        """
        Check if current count reaches a milestone and send notification

        Args:
            opinion_id: Opinion ID
            milestone_type: 'like' or 'comment'
            current_count: Current count of likes or comments
            opinion_owner_id: Owner of the opinion to notify

        Returns:
            True if notification was sent, False otherwise
        """
        from utils.database import get_db_cursor

        try:
            with get_db_cursor() as cursor:
                # Get or create milestone record
                cursor.execute(
                    """SELECT last_notified_count, next_milestone
                       FROM notification_milestones
                       WHERE opinion_id = %s AND milestone_type = %s""",
                    (opinion_id, milestone_type)
                )

                milestone_record = cursor.fetchone()

                if not milestone_record:
                    # Create initial milestone record
                    cursor.execute(
                        """INSERT INTO notification_milestones
                           (opinion_id, milestone_type, last_notified_count, next_milestone)
                           VALUES (%s, %s, 0, 1)""",
                        (opinion_id, milestone_type)
                    )
                    last_notified = 0
                    next_milestone = 1
                else:
                    last_notified = milestone_record['last_notified_count']
                    next_milestone = milestone_record['next_milestone']

                # Check if we've reached the milestone
                if current_count >= next_milestone:
                    # Send notification
                    notification_type = NotificationType.LIKE if milestone_type == 'like' else NotificationType.COMMENT

                    if milestone_type == 'like':
                        title = f"你的貼文獲得了 {current_count} 個按讚！"
                        content = f"恭喜！你的貼文已經獲得 {current_count} 個按讚"
                    else:
                        title = f"你的貼文收到了 {current_count} 則留言！"
                        content = f"你的貼文已經收到 {current_count} 則留言"

                    NotificationService.create_notification(
                        NotificationCreate(
                            user_id=opinion_owner_id,
                            opinion_id=opinion_id,
                            type=notification_type,
                            title=title,
                            content=content
                        )
                    )

                    # Update milestone record
                    new_next_milestone = calculate_next_milestone(current_count)
                    cursor.execute(
                        """UPDATE notification_milestones
                           SET last_notified_count = %s, next_milestone = %s
                           WHERE opinion_id = %s AND milestone_type = %s""",
                        (current_count, new_next_milestone, opinion_id, milestone_type)
                    )

                    return True

        except Exception as e:
            print(f"Error checking milestone: {e}")

        return False
