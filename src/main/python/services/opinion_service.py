"""
Opinion service for managing citizen submissions
"""

from typing import List, Optional
from models.opinion import (
    Opinion, OpinionCreate, OpinionUpdate, OpinionWithUser,
    OpinionList, OpinionStatus
)
from models.comment import Comment, CommentCreate
from models.vote import Vote, VoteCreate
from models.notification import NotificationCreate, NotificationType
from utils.database import get_db_cursor
from services.notification_service import NotificationService


class OpinionService:
    """Service for opinion management"""

    @staticmethod
    def create_opinion(user_id: int, opinion_data: OpinionCreate) -> Optional[Opinion]:
        """Create a new opinion"""
        query = """
            INSERT INTO opinions (user_id, title, content, category_id, status,
                                 region, latitude, longitude, is_public)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        with get_db_cursor() as cursor:
            cursor.execute(
                query,
                (user_id, opinion_data.title, opinion_data.content,
                 opinion_data.category_id, opinion_data.status.value,
                 opinion_data.region, opinion_data.latitude,
                 opinion_data.longitude, opinion_data.is_public)
            )

            opinion_id = cursor.lastrowid

            # Add tags if provided
            if opinion_data.tags:
                OpinionService._add_tags(cursor, opinion_id, opinion_data.tags)

            # Log history
            cursor.execute(
                """INSERT INTO opinion_history (opinion_id, user_id, action, new_status)
                   VALUES (%s, %s, 'created', %s)""",
                (opinion_id, user_id, opinion_data.status.value)
            )

            return OpinionService.get_opinion_by_id(opinion_id)

    @staticmethod
    def get_opinion_by_id(opinion_id: int, increment_view: bool = False) -> Optional[OpinionWithUser]:
        """Get opinion by ID with user information"""
        if increment_view:
            with get_db_cursor() as cursor:
                cursor.execute(
                    "UPDATE opinions SET view_count = view_count + 1 WHERE id = %s",
                    (opinion_id,)
                )

        query = """
            SELECT o.*, u.username, u.full_name as user_full_name,
                   (SELECT COUNT(*) FROM votes WHERE opinion_id = o.id) as vote_count,
                   (SELECT COUNT(*) FROM comments WHERE opinion_id = o.id AND is_deleted = FALSE) as comment_count
            FROM opinions o
            JOIN users u ON o.user_id = u.id
            WHERE o.id = %s
        """

        with get_db_cursor() as cursor:
            cursor.execute(query, (opinion_id,))
            opinion_row = cursor.fetchone()

            if not opinion_row:
                return None

            # Get tags
            cursor.execute(
                """SELECT t.name FROM tags t
                   JOIN opinion_tags ot ON t.id = ot.tag_id
                   WHERE ot.opinion_id = %s""",
                (opinion_id,)
            )
            tags = [row['name'] for row in cursor.fetchall()]
            opinion_row['tags'] = tags

            return OpinionWithUser(**opinion_row)

    @staticmethod
    def get_opinions(page: int = 1, page_size: int = 20,
                    status: Optional[OpinionStatus] = None,
                    category_id: Optional[int] = None) -> OpinionList:
        """Get paginated list of opinions"""
        offset = (page - 1) * page_size

        # Build query
        where_clauses = ["o.is_public = TRUE"]
        params = []

        if status:
            where_clauses.append("o.status = %s")
            params.append(status.value)

        if category_id:
            where_clauses.append("o.category_id = %s")
            params.append(category_id)

        where_sql = " AND ".join(where_clauses)

        count_query = f"SELECT COUNT(*) as total FROM opinions o WHERE {where_sql}"

        data_query = f"""
            SELECT o.*, u.username, u.full_name as user_full_name,
                   (SELECT COUNT(*) FROM votes WHERE opinion_id = o.id) as vote_count,
                   (SELECT COUNT(*) FROM comments WHERE opinion_id = o.id AND is_deleted = FALSE) as comment_count
            FROM opinions o
            JOIN users u ON o.user_id = u.id
            WHERE {where_sql}
            ORDER BY o.created_at DESC
            LIMIT %s OFFSET %s
        """

        with get_db_cursor() as cursor:
            # Get total count
            cursor.execute(count_query, params)
            total = cursor.fetchone()['total']

            # Get data
            cursor.execute(data_query, params + [page_size, offset])
            opinions = cursor.fetchall()

            # Get tags for each opinion
            for opinion in opinions:
                cursor.execute(
                    """SELECT t.name FROM tags t
                       JOIN opinion_tags ot ON t.id = ot.tag_id
                       WHERE ot.opinion_id = %s""",
                    (opinion['id'],)
                )
                opinion['tags'] = [row['name'] for row in cursor.fetchall()]

            items = [OpinionWithUser(**opinion) for opinion in opinions]

            return OpinionList(
                total=total,
                page=page,
                page_size=page_size,
                items=items
            )

    @staticmethod
    def add_comment(opinion_id: int, user_id: int, comment_data: CommentCreate) -> Optional[Comment]:
        """Add comment to opinion"""
        query = """
            INSERT INTO comments (opinion_id, user_id, content)
            VALUES (%s, %s, %s)
        """

        with get_db_cursor() as cursor:
            cursor.execute(query, (opinion_id, user_id, comment_data.content))
            comment_id = cursor.lastrowid

            # Get opinion owner and notify
            cursor.execute("SELECT user_id FROM opinions WHERE id = %s", (opinion_id,))
            opinion_owner = cursor.fetchone()

            if opinion_owner and opinion_owner['user_id'] != user_id:
                NotificationService.create_notification(
                    NotificationCreate(
                        user_id=opinion_owner['user_id'],
                        opinion_id=opinion_id,
                        type=NotificationType.COMMENT,
                        title="New comment on your opinion",
                        content=f"Someone commented on your opinion"
                    )
                )

            # Fetch created comment
            cursor.execute(
                """SELECT c.*, u.username FROM comments c
                   JOIN users u ON c.user_id = u.id
                   WHERE c.id = %s""",
                (comment_id,)
            )
            return Comment(**cursor.fetchone())

    @staticmethod
    def vote_opinion(opinion_id: int, user_id: int, vote_data: VoteCreate) -> bool:
        """Vote on an opinion"""
        query = """
            INSERT INTO votes (opinion_id, user_id, vote_type)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE vote_type = VALUES(vote_type)
        """

        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (opinion_id, user_id, vote_data.vote_type.value))
                return True
        except Exception as e:
            print(f"Error voting: {e}")
            return False

    @staticmethod
    def collect_opinion(opinion_id: int, user_id: int) -> bool:
        """Add opinion to user's collection"""
        query = """
            INSERT INTO collections (opinion_id, user_id)
            VALUES (%s, %s)
        """

        try:
            with get_db_cursor() as cursor:
                cursor.execute(query, (opinion_id, user_id))
                return True
        except Exception:
            return False

    @staticmethod
    def uncollect_opinion(opinion_id: int, user_id: int) -> bool:
        """Remove opinion from user's collection"""
        query = "DELETE FROM collections WHERE opinion_id = %s AND user_id = %s"

        with get_db_cursor() as cursor:
            cursor.execute(query, (opinion_id, user_id))
            return cursor.rowcount > 0

    @staticmethod
    def _add_tags(cursor, opinion_id: int, tag_names: List[str]):
        """Helper to add tags to opinion"""
        for tag_name in tag_names:
            # Insert tag if not exists
            cursor.execute(
                "INSERT IGNORE INTO tags (name) VALUES (%s)",
                (tag_name,)
            )

            # Get tag ID
            cursor.execute("SELECT id FROM tags WHERE name = %s", (tag_name,))
            tag_id = cursor.fetchone()['id']

            # Link tag to opinion
            cursor.execute(
                "INSERT IGNORE INTO opinion_tags (opinion_id, tag_id) VALUES (%s, %s)",
                (opinion_id, tag_id)
            )
