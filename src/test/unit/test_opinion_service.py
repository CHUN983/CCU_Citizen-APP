import importlib
import sys

import mysql.connector.pooling as mysql_pooling
import pytest

from models.vote import VoteCreate, VoteType
from src.test.unit.helpers import FakeCursor, cursor_context

pytestmark = pytest.mark.no_db


def load_opinion_service(monkeypatch):
    class DummyPool:
        def __init__(self, *args, **kwargs):
            pass

        def get_connection(self):
            raise RuntimeError("connection pool not available in unit tests")

    monkeypatch.setattr(mysql_pooling, "MySQLConnectionPool", lambda *a, **k: DummyPool())
    sys.modules.pop("utils.database", None)
    sys.modules.pop("services.opinion_service", None)
    return importlib.import_module("services.opinion_service")


@pytest.fixture
def opinion_service(monkeypatch):
    return load_opinion_service(monkeypatch)


def patch_cursor(monkeypatch, opinion_service, cursor):
    monkeypatch.setattr(opinion_service, "get_db_cursor", lambda *a, **k: cursor_context(cursor))


def test_vote_opinion_inserts_when_no_existing_vote(monkeypatch, opinion_service):
    cursor = FakeCursor(fetchone_results=[None])
    patch_cursor(monkeypatch, opinion_service, cursor)

    result = opinion_service.OpinionService.vote_opinion(
        opinion_id=1,
        user_id=42,
        vote_data=VoteCreate(vote_type=VoteType.LIKE),
    )

    assert result is True
    assert any("INSERT INTO votes" in stmt for stmt, _ in cursor.executed)


def test_vote_opinion_deletes_when_same_vote_clicked(monkeypatch, opinion_service):
    cursor = FakeCursor(fetchone_results=[{"vote_type": VoteType.LIKE.value}])
    patch_cursor(monkeypatch, opinion_service, cursor)

    result = opinion_service.OpinionService.vote_opinion(
        opinion_id=5,
        user_id=7,
        vote_data=VoteCreate(vote_type=VoteType.LIKE),
    )

    assert result is True
    assert any("DELETE FROM votes" in stmt for stmt, _ in cursor.executed)


def test_vote_opinion_updates_when_different_vote_selected(monkeypatch, opinion_service):
    cursor = FakeCursor(fetchone_results=[{"vote_type": VoteType.LIKE.value}])
    patch_cursor(monkeypatch, opinion_service, cursor)

    result = opinion_service.OpinionService.vote_opinion(
        opinion_id=99,
        user_id=3,
        vote_data=VoteCreate(vote_type=VoteType.DISLIKE),
    )

    assert result is True
    assert any("UPDATE votes" in stmt for stmt, _ in cursor.executed)


def test_vote_opinion_returns_false_on_exception(monkeypatch, opinion_service):
    class ExplodingCursor(FakeCursor):
        def execute(self, *args, **kwargs):
            raise RuntimeError("boom")

    cursor = ExplodingCursor()
    patch_cursor(monkeypatch, opinion_service, cursor)

    assert opinion_service.OpinionService.vote_opinion(1, 2, VoteCreate()) is False


def test_get_user_vote_returns_vote_type(monkeypatch, opinion_service):
    cursor = FakeCursor(fetchone_results=[{"vote_type": "like"}])
    patch_cursor(monkeypatch, opinion_service, cursor)

    vote = opinion_service.OpinionService.get_user_vote(1, 2)

    assert vote == "like"


def test_get_user_vote_returns_none_on_error(monkeypatch, opinion_service):
    class ExplodingCursor(FakeCursor):
        def execute(self, *args, **kwargs):
            raise RuntimeError("boom")

    cursor = ExplodingCursor()
    patch_cursor(monkeypatch, opinion_service, cursor)

    assert opinion_service.OpinionService.get_user_vote(1, 2) is None


def test_add_tags_inserts_and_links_tags(monkeypatch, opinion_service):
    cursor = FakeCursor(fetchone_results=[{"id": 10}, {"id": 11}])

    opinion_service.OpinionService._add_tags(cursor, opinion_id=5, tag_names=["a", "b"])

    executed_statements = [stmt for stmt, _ in cursor.executed]
    assert executed_statements.count("INSERT IGNORE INTO tags (name) VALUES (%s)") == 2
    assert executed_statements.count("SELECT id FROM tags WHERE name = %s") == 2
    assert executed_statements.count("INSERT IGNORE INTO opinion_tags (opinion_id, tag_id) VALUES (%s, %s)") == 2


# ==================== Comment Related Tests ====================

def test_get_comment_by_id_returns_comment(monkeypatch, opinion_service):
    """Test getting comment by ID"""
    cursor = FakeCursor(fetchone_results=[{
        'id': 1,
        'opinion_id': 10,
        'user_id': 5,
        'content': 'Test comment',
        'username': 'testuser',
        'created_at': '2025-10-24 10:00:00',
        'updated_at': '2025-10-24 10:00:00',
        'is_deleted': False
    }])
    patch_cursor(monkeypatch, opinion_service, cursor)

    result = opinion_service.OpinionService.get_comment_by_id(1)

    assert result is not None
    assert result.id == 1
    assert result.content == 'Test comment'


def test_get_comment_by_id_returns_none_when_not_found(monkeypatch, opinion_service):
    """Test getting non-existent comment"""
    cursor = FakeCursor(fetchone_results=[None])
    patch_cursor(monkeypatch, opinion_service, cursor)

    result = opinion_service.OpinionService.get_comment_by_id(999)

    assert result is None


def test_get_comments_by_opinion_id_returns_list(monkeypatch, opinion_service):
    """Test getting all comments for an opinion"""
    cursor = FakeCursor(fetchall_results=[[
        {
            'id': 1,
            'opinion_id': 10,
            'user_id': 5,
            'content': 'Comment 1',
            'username': 'user1',
            'created_at': '2025-10-24 10:00:00',
            'updated_at': '2025-10-24 10:00:00',
            'is_deleted': False
        },
        {
            'id': 2,
            'opinion_id': 10,
            'user_id': 6,
            'content': 'Comment 2',
            'username': 'user2',
            'created_at': '2025-10-24 11:00:00',
            'updated_at': '2025-10-24 11:00:00',
            'is_deleted': False
        }
    ]])
    patch_cursor(monkeypatch, opinion_service, cursor)

    results = opinion_service.OpinionService.get_comments_by_opinion_id(10)

    assert len(results) == 2
    assert results[0].content == 'Comment 1'
    assert results[1].content == 'Comment 2'


def test_get_comments_by_opinion_id_respects_limit(monkeypatch, opinion_service):
    """Test comment retrieval respects limit parameter"""
    cursor = FakeCursor(fetchall_results=[[]])
    patch_cursor(monkeypatch, opinion_service, cursor)

    opinion_service.OpinionService.get_comments_by_opinion_id(10, limit=10)

    # Check that LIMIT was used in query
    assert any("LIMIT" in stmt for stmt, _ in cursor.executed)


# ==================== Collection Related Tests ====================

def test_collect_opinion_success(monkeypatch, opinion_service):
    """Test successfully collecting an opinion"""
    cursor = FakeCursor()
    patch_cursor(monkeypatch, opinion_service, cursor)

    result = opinion_service.OpinionService.collect_opinion(opinion_id=1, user_id=5)

    assert result is True
    assert any("INSERT INTO collections" in stmt for stmt, _ in cursor.executed)


def test_collect_opinion_fails_on_exception(monkeypatch, opinion_service):
    """Test collect_opinion returns False on database error"""
    class ExplodingCursor(FakeCursor):
        def execute(self, *args, **kwargs):
            raise RuntimeError("Database error")

    cursor = ExplodingCursor()
    patch_cursor(monkeypatch, opinion_service, cursor)

    result = opinion_service.OpinionService.collect_opinion(opinion_id=1, user_id=5)

    assert result is False


def test_uncollect_opinion_success(monkeypatch, opinion_service):
    """Test successfully uncollecting an opinion"""
    cursor = FakeCursor()
    cursor.rowcount = 1
    patch_cursor(monkeypatch, opinion_service, cursor)

    result = opinion_service.OpinionService.uncollect_opinion(opinion_id=1, user_id=5)

    assert result is True
    assert any("DELETE FROM collections" in stmt for stmt, _ in cursor.executed)


def test_uncollect_opinion_returns_false_when_not_found(monkeypatch, opinion_service):
    """Test uncollecting non-existent collection"""
    cursor = FakeCursor()
    cursor.rowcount = 0
    patch_cursor(monkeypatch, opinion_service, cursor)

    result = opinion_service.OpinionService.uncollect_opinion(opinion_id=1, user_id=5)

    assert result is False


def test_is_collected_returns_true_when_collected(monkeypatch, opinion_service):
    """Test is_collected returns True for collected opinion"""
    cursor = FakeCursor(fetchone_results=[{'count': 1}])
    patch_cursor(monkeypatch, opinion_service, cursor)

    result = opinion_service.OpinionService.is_collected(opinion_id=1, user_id=5)

    assert result is True


def test_is_collected_returns_false_when_not_collected(monkeypatch, opinion_service):
    """Test is_collected returns False for non-collected opinion"""
    cursor = FakeCursor(fetchone_results=[None])
    patch_cursor(monkeypatch, opinion_service, cursor)

    result = opinion_service.OpinionService.is_collected(opinion_id=1, user_id=5)

    assert result is False


# ==================== User Opinions Tests ====================

def test_get_bookmarked_opinions_returns_list(monkeypatch, opinion_service):
    """Test getting user's bookmarked opinions"""
    cursor = FakeCursor(
        fetchone_results=[{'total': 2}],
        fetchall_results=[
            [  # Main query results
                {
                    'id': 1,
                    'user_id': 10,
                    'title': 'Opinion 1',
                    'content': 'Test content for opinion 1',
                    'status': 'approved',
                    'username': 'user1',
                    'user_full_name': 'User One',
                    'category_id': 1,
                    'category_name': '交通',
                    'upvotes': 5,
                    'downvotes': 1,
                    'comment_count': 3,
                    'view_count': 100,
                    'is_public': True,
                    'region': 'taipei',
                    'latitude': None,
                    'longitude': None,
                    'merged_to_id': None,
                    'created_at': '2025-10-24 10:00:00',
                    'updated_at': '2025-10-24 10:00:00'
                }
            ],
            [],  # Tags query result for first opinion
        ]
    )
    patch_cursor(monkeypatch, opinion_service, cursor)

    result = opinion_service.OpinionService.get_bookmarked_opinions(user_id=5, page=1, page_size=10)

    assert result.total == 2
    assert len(result.items) == 1
    assert result.items[0].title == 'Opinion 1'


def test_get_user_opinions_returns_list(monkeypatch, opinion_service):
    """Test getting opinions created by user"""
    cursor = FakeCursor(
        fetchone_results=[{'total': 1}],
        fetchall_results=[
            [  # Main query results
                {
                    'id': 1,
                    'user_id': 5,
                    'title': 'My Opinion',
                    'content': 'This is my opinion content',
                    'status': 'pending',
                    'username': 'me',
                    'user_full_name': 'Me Myself',
                    'category_id': 1,
                    'category_name': '交通',
                    'upvotes': 0,
                    'downvotes': 0,
                    'comment_count': 0,
                    'view_count': 10,
                    'is_public': True,
                    'region': 'taipei',
                    'latitude': None,
                    'longitude': None,
                    'merged_to_id': None,
                    'created_at': '2025-10-24 10:00:00',
                    'updated_at': '2025-10-24 10:00:00'
                }
            ],
            [],  # Tags query result
        ]
    )
    patch_cursor(monkeypatch, opinion_service, cursor)

    result = opinion_service.OpinionService.get_user_opinions(user_id=5, page=1, page_size=10)

    assert result.total == 1
    assert len(result.items) == 1
    assert result.items[0].title == 'My Opinion'


def test_get_user_opinions_with_status_filter(monkeypatch, opinion_service):
    """Test filtering user opinions by status"""
    from models.opinion import OpinionStatus

    cursor = FakeCursor(
        fetchone_results=[{'total': 0}],
        fetchall_results=[[]]
    )
    patch_cursor(monkeypatch, opinion_service, cursor)

    opinion_service.OpinionService.get_user_opinions(
        user_id=5,
        page=1,
        page_size=10,
        status=OpinionStatus.APPROVED
    )

    # Check that status filter was applied
    executed_sql = " ".join([stmt for stmt, _ in cursor.executed])
    assert "status" in executed_sql.lower()


# ==================== Delete Opinion Tests ====================

def test_delete_opinion_success(monkeypatch, opinion_service):
    """Test successfully deleting opinion"""
    cursor = FakeCursor()
    cursor.rowcount = 1
    patch_cursor(monkeypatch, opinion_service, cursor)

    result = opinion_service.OpinionService.delete_opinion(opinion_id=1, user_id=5)

    assert result is True
    assert any("DELETE FROM opinions" in stmt for stmt, _ in cursor.executed)


def test_delete_opinion_returns_false_when_not_found(monkeypatch, opinion_service):
    """Test deleting non-existent opinion"""
    cursor = FakeCursor()
    cursor.rowcount = 0
    patch_cursor(monkeypatch, opinion_service, cursor)

    result = opinion_service.OpinionService.delete_opinion(opinion_id=999, user_id=5)

    assert result is False


def test_delete_opinion_fails_on_exception(monkeypatch, opinion_service):
    """Test delete_opinion returns False on database error"""
    class ExplodingCursor(FakeCursor):
        def execute(self, *args, **kwargs):
            raise RuntimeError("Database error")

    cursor = ExplodingCursor()
    patch_cursor(monkeypatch, opinion_service, cursor)

    result = opinion_service.OpinionService.delete_opinion(opinion_id=1, user_id=5)

    assert result is False


# ==================== Create Opinion Tests ====================

def test_create_opinion_success(monkeypatch, opinion_service):
    """Test successfully creating an opinion without tags or media"""
    from models.opinion import OpinionCreate, OpinionStatus

    cursor = FakeCursor(lastrowid=123)
    patch_cursor(monkeypatch, opinion_service, cursor)

    # Mock get_opinion_by_id to return a created opinion
    def mock_get_opinion_by_id(opinion_id):
        from models.opinion import OpinionWithUser
        return OpinionWithUser(
            id=123,
            user_id=5,
            title='Test Opinion',
            content='This is test content for the opinion',
            status='pending',
            username='testuser',
            user_full_name='Test User',
            category_id=1,
            category_name='交通',
            upvotes=0,
            downvotes=0,
            comment_count=0,
            view_count=0,
            is_public=True,
            region='taipei',
            latitude=None,
            longitude=None,
            merged_to_id=None,
            created_at='2025-10-24 10:00:00',
            updated_at='2025-10-24 10:00:00',
            tags=[],
            media=[]
        )

    monkeypatch.setattr(opinion_service.OpinionService, 'get_opinion_by_id', mock_get_opinion_by_id)

    opinion_data = OpinionCreate(
        title='Test Opinion',
        content='This is test content for the opinion',
        category_id=1,
        status=OpinionStatus.PENDING,
        region='taipei',
        is_public=True
    )

    result = opinion_service.OpinionService.create_opinion(opinion_data=opinion_data, user_id=5)

    assert result is not None
    assert result.id == 123
    assert result.title == 'Test Opinion'
    assert any("INSERT INTO opinions" in stmt for stmt, _ in cursor.executed)
    assert any("INSERT INTO opinion_history" in stmt for stmt, _ in cursor.executed)


def test_create_opinion_with_tags(monkeypatch, opinion_service):
    """Test creating opinion with tags"""
    from models.opinion import OpinionCreate, OpinionStatus

    cursor = FakeCursor(
        lastrowid=124,
        fetchone_results=[{'id': 10}, {'id': 11}]  # Tag IDs
    )
    patch_cursor(monkeypatch, opinion_service, cursor)

    def mock_get_opinion_by_id(opinion_id):
        from models.opinion import OpinionWithUser
        return OpinionWithUser(
            id=124,
            user_id=5,
            title='Tagged Opinion',
            content='Opinion with tags for testing purposes',
            status='pending',
            username='testuser',
            user_full_name='Test User',
            category_id=1,
            category_name='交通',
            upvotes=0,
            downvotes=0,
            comment_count=0,
            view_count=0,
            is_public=True,
            region='taipei',
            latitude=None,
            longitude=None,
            merged_to_id=None,
            created_at='2025-10-24 10:00:00',
            updated_at='2025-10-24 10:00:00',
            tags=['tag1', 'tag2'],
            media=[]
        )

    monkeypatch.setattr(opinion_service.OpinionService, 'get_opinion_by_id', mock_get_opinion_by_id)

    opinion_data = OpinionCreate(
        title='Tagged Opinion',
        content='Opinion with tags for testing purposes',
        category_id=1,
        status=OpinionStatus.PENDING,
        region='taipei',
        is_public=True,
        tags=['tag1', 'tag2']
    )

    result = opinion_service.OpinionService.create_opinion(opinion_data=opinion_data, user_id=5)

    assert result is not None
    assert any("INSERT IGNORE INTO tags" in stmt for stmt, _ in cursor.executed)


def test_create_opinion_returns_none_on_error(monkeypatch, opinion_service):
    """Test create_opinion returns None on database error"""
    from models.opinion import OpinionCreate, OpinionStatus

    class ExplodingCursor(FakeCursor):
        def execute(self, *args, **kwargs):
            raise RuntimeError("Database error")

    cursor = ExplodingCursor()
    patch_cursor(monkeypatch, opinion_service, cursor)

    opinion_data = OpinionCreate(
        title='Test Opinion',
        content='Test content here',
        category_id=1,
        status=OpinionStatus.PENDING
    )

    result = opinion_service.OpinionService.create_opinion(opinion_data=opinion_data, user_id=5)

    assert result is None


# ==================== Get Opinion By ID Tests ====================

def test_get_opinion_by_id_success(monkeypatch, opinion_service):
    """Test successfully getting opinion by ID"""
    cursor = FakeCursor(
        fetchone_results=[
            {  # Main opinion data
                'id': 1,
                'user_id': 5,
                'title': 'Test Opinion',
                'content': 'This is test content for the opinion',
                'status': 'approved',
                'username': 'testuser',
                'user_full_name': 'Test User',
                'category_id': 1,
                'category_name': '交通',
                'upvotes': 10,
                'downvotes': 2,
                'comment_count': 5,
                'view_count': 100,
                'is_public': True,
                'region': 'taipei',
                'latitude': None,
                'longitude': None,
                'merged_to_id': None,
                'created_at': '2025-10-24 10:00:00',
                'updated_at': '2025-10-24 10:00:00'
            }
        ],
        fetchall_results=[
            [{'name': 'tag1'}, {'name': 'tag2'}],  # Tags
            []  # Media (empty)
        ]
    )
    patch_cursor(monkeypatch, opinion_service, cursor)

    result = opinion_service.OpinionService.get_opinion_by_id(opinion_id=1)

    assert result is not None
    assert result.id == 1
    assert result.title == 'Test Opinion'
    assert result.upvotes == 10
    assert result.tags == ['tag1', 'tag2']


def test_get_opinion_by_id_not_found(monkeypatch, opinion_service):
    """Test getting non-existent opinion returns None"""
    cursor = FakeCursor(fetchone_results=[None])
    patch_cursor(monkeypatch, opinion_service, cursor)

    result = opinion_service.OpinionService.get_opinion_by_id(opinion_id=999)

    assert result is None


def test_get_opinion_by_id_increments_view_count(monkeypatch, opinion_service):
    """Test that view count is incremented when requested"""
    cursor = FakeCursor(
        fetchone_results=[
            {
                'id': 1,
                'user_id': 5,
                'title': 'Test Opinion',
                'content': 'Content for view count test',
                'status': 'approved',
                'username': 'testuser',
                'user_full_name': 'Test User',
                'category_id': 1,
                'category_name': '交通',
                'upvotes': 0,
                'downvotes': 0,
                'comment_count': 0,
                'view_count': 10,
                'is_public': True,
                'region': 'taipei',
                'latitude': None,
                'longitude': None,
                'merged_to_id': None,
                'created_at': '2025-10-24 10:00:00',
                'updated_at': '2025-10-24 10:00:00'
            }
        ],
        fetchall_results=[[], []]  # Tags and media
    )
    patch_cursor(monkeypatch, opinion_service, cursor)

    result = opinion_service.OpinionService.get_opinion_by_id(opinion_id=1, increment_view=True)

    assert result is not None
    assert any("UPDATE opinions SET view_count" in stmt for stmt, _ in cursor.executed)


# ==================== Get Opinions (Paginated) Tests ====================

def test_get_opinions_basic(monkeypatch, opinion_service):
    """Test basic paginated opinion retrieval"""
    cursor = FakeCursor(
        fetchone_results=[{'total': 25}],
        fetchall_results=[
            [  # Main opinions data
                {
                    'id': 1,
                    'user_id': 5,
                    'title': 'Opinion 1',
                    'content': 'Content for opinion 1 test',
                    'status': 'approved',
                    'username': 'user1',
                    'user_full_name': 'User One',
                    'category_id': 1,
                    'category_name': '交通',
                    'upvotes': 5,
                    'downvotes': 1,
                    'comment_count': 3,
                    'view_count': 50,
                    'is_public': True,
                    'region': 'taipei',
                    'latitude': None,
                    'longitude': None,
                    'merged_to_id': None,
                    'created_at': '2025-10-24 10:00:00',
                    'updated_at': '2025-10-24 10:00:00'
                },
                {
                    'id': 2,
                    'user_id': 6,
                    'title': 'Opinion 2',
                    'content': 'Content for opinion 2 test',
                    'status': 'approved',
                    'username': 'user2',
                    'user_full_name': 'User Two',
                    'category_id': 2,
                    'category_name': '環境',
                    'upvotes': 3,
                    'downvotes': 0,
                    'comment_count': 1,
                    'view_count': 30,
                    'is_public': True,
                    'region': 'kaohsiung',
                    'latitude': None,
                    'longitude': None,
                    'merged_to_id': None,
                    'created_at': '2025-10-24 11:00:00',
                    'updated_at': '2025-10-24 11:00:00'
                }
            ],
            [],  # Tags for opinion 1
            []   # Tags for opinion 2
        ]
    )
    patch_cursor(monkeypatch, opinion_service, cursor)

    result = opinion_service.OpinionService.get_opinions(page=1, page_size=20)

    assert result.total == 25
    assert result.page == 1
    assert result.page_size == 20
    assert len(result.items) == 2
    assert result.items[0].title == 'Opinion 1'
    assert result.items[1].title == 'Opinion 2'


def test_get_opinions_with_status_filter(monkeypatch, opinion_service):
    """Test filtering opinions by status"""
    from models.opinion import OpinionStatus

    cursor = FakeCursor(
        fetchone_results=[{'total': 5}],
        fetchall_results=[[]]
    )
    patch_cursor(monkeypatch, opinion_service, cursor)

    result = opinion_service.OpinionService.get_opinions(
        page=1,
        page_size=20,
        status=OpinionStatus.APPROVED
    )

    # Check that status filter was applied
    executed_sql = " ".join([stmt for stmt, _ in cursor.executed])
    assert "status" in executed_sql.lower()


def test_get_opinions_with_search(monkeypatch, opinion_service):
    """Test searching opinions by title/content"""
    cursor = FakeCursor(
        fetchone_results=[{'total': 3}],
        fetchall_results=[[]]
    )
    patch_cursor(monkeypatch, opinion_service, cursor)

    result = opinion_service.OpinionService.get_opinions(
        page=1,
        page_size=20,
        search='traffic'
    )

    # Check that search was applied
    executed_sql = " ".join([stmt for stmt, _ in cursor.executed])
    assert "like" in executed_sql.lower()


def test_get_opinions_with_sort(monkeypatch, opinion_service):
    """Test sorting opinions"""
    cursor = FakeCursor(
        fetchone_results=[{'total': 10}],
        fetchall_results=[[]]
    )
    patch_cursor(monkeypatch, opinion_service, cursor)

    result = opinion_service.OpinionService.get_opinions(
        page=1,
        page_size=20,
        sort_by='upvotes'
    )

    # Check that ORDER BY was applied
    executed_sql = " ".join([stmt for stmt, _ in cursor.executed])
    assert "order by" in executed_sql.lower()


# ==================== Add Comment Tests ====================

def test_add_comment_success(monkeypatch, opinion_service):
    """Test successfully adding a comment"""
    from models.comment import CommentCreate

    cursor = FakeCursor(
        lastrowid=1,
        fetchone_results=[
            {'user_id': 10},  # Opinion owner
            {  # Created comment
                'id': 1,
                'opinion_id': 5,
                'user_id': 7,
                'content': 'This is a test comment',
                'username': 'commenter',
                'created_at': '2025-10-24 12:00:00',
                'updated_at': '2025-10-24 12:00:00',
                'is_deleted': False
            }
        ]
    )
    patch_cursor(monkeypatch, opinion_service, cursor)

    # Mock NotificationService
    notification_called = {'called': False}
    def mock_create_notification(notification_data):
        notification_called['called'] = True
        return None

    from services import notification_service
    monkeypatch.setattr(notification_service.NotificationService, 'create_notification', mock_create_notification)

    comment_data = CommentCreate(content='This is a test comment')

    result = opinion_service.OpinionService.add_comment(
        opinion_id=5,
        user_id=7,
        comment_data=comment_data
    )

    assert result is not None
    assert result.id == 1
    assert result.content == 'This is a test comment'
    assert any("INSERT INTO comments" in stmt for stmt, _ in cursor.executed)
    assert notification_called['called'] is True


def test_add_comment_no_notification_for_own_comment(monkeypatch, opinion_service):
    """Test that no notification is sent when commenting on own opinion"""
    from models.comment import CommentCreate

    cursor = FakeCursor(
        lastrowid=2,
        fetchone_results=[
            {'user_id': 7},  # Opinion owner (same as commenter)
            {
                'id': 2,
                'opinion_id': 5,
                'user_id': 7,
                'content': 'Self comment',
                'username': 'self',
                'created_at': '2025-10-24 12:00:00',
                'updated_at': '2025-10-24 12:00:00',
                'is_deleted': False
            }
        ]
    )
    patch_cursor(monkeypatch, opinion_service, cursor)

    notification_called = {'called': False}
    def mock_create_notification(notification_data):
        notification_called['called'] = True
        return None

    from services import notification_service
    monkeypatch.setattr(notification_service.NotificationService, 'create_notification', mock_create_notification)

    comment_data = CommentCreate(content='Self comment')

    result = opinion_service.OpinionService.add_comment(
        opinion_id=5,
        user_id=7,  # Same as opinion owner
        comment_data=comment_data
    )

    assert result is not None
    assert notification_called['called'] is False  # No notification for self-comment


# ==================== Create Opinion with Media Tests ====================

def test_create_opinion_with_media_files(monkeypatch, opinion_service):
    """Test creating opinion with media files"""
    from models.opinion import OpinionCreate, OpinionStatus, MediaType, OpinionMediaCreate

    cursor = FakeCursor(
        lastrowid=125,
        fetchone_results=[{'id': 10}, {'id': 11}]  # Tag IDs
    )
    patch_cursor(monkeypatch, opinion_service, cursor)

    def mock_get_opinion_by_id(opinion_id):
        from models.opinion import OpinionWithUser
        return OpinionWithUser(
            id=125,
            user_id=5,
            title='Opinion with Media',
            content='This opinion has media attachments',
            status='pending',
            username='testuser',
            user_full_name='Test User',
            category_id=1,
            category_name='交通',
            upvotes=0,
            downvotes=0,
            comment_count=0,
            view_count=0,
            is_public=True,
            region='taipei',
            latitude=None,
            longitude=None,
            merged_to_id=None,
            created_at='2025-10-24 10:00:00',
            updated_at='2025-10-24 10:00:00',
            tags=['tag1', 'tag2'],
            media=[]
        )

    monkeypatch.setattr(opinion_service.OpinionService, 'get_opinion_by_id', mock_get_opinion_by_id)

    opinion_data = OpinionCreate(
        title='Opinion with Media',
        content='This opinion has media attachments',
        category_id=1,
        status=OpinionStatus.PENDING,
        region='taipei',
        is_public=True,
        tags=['tag1', 'tag2'],
        media=[
            OpinionMediaCreate(
                file_path='/uploads/images/test1.jpg',
                file_size=1024,
                media_type=MediaType.IMAGE,
                mime_type='image/jpeg'
            ),
            OpinionMediaCreate(
                file_path='/uploads/videos/test2.mp4',
                file_size=2048,
                media_type=MediaType.VIDEO,
                mime_type='video/mp4'
            )
        ]
    )

    result = opinion_service.OpinionService.create_opinion(opinion_data=opinion_data, user_id=5)

    assert result is not None
    # Check that media was inserted
    assert any("INSERT INTO opinion_media" in stmt for stmt, _ in cursor.executed)
    # Verify executemany was called for media (multiple inserts)
    media_inserts = [stmt for stmt, _ in cursor.executed if "INSERT INTO opinion_media" in stmt]
    assert len(media_inserts) > 0


# ==================== Get Opinion with Media Tests ====================

def test_get_opinion_by_id_with_media_files(monkeypatch, opinion_service):
    """Test getting opinion with media files processes URLs correctly"""
    cursor = FakeCursor(
        fetchone_results=[
            {
                'id': 1,
                'user_id': 5,
                'title': 'Opinion with Media',
                'content': 'This has media files',
                'status': 'approved',
                'username': 'testuser',
                'user_full_name': 'Test User',
                'category_id': 1,
                'category_name': '交通',
                'upvotes': 5,
                'downvotes': 1,
                'comment_count': 2,
                'view_count': 50,
                'is_public': True,
                'region': 'taipei',
                'latitude': None,
                'longitude': None,
                'merged_to_id': None,
                'created_at': '2025-10-24 10:00:00',
                'updated_at': '2025-10-24 10:00:00'
            }
        ],
        fetchall_results=[
            [],  # Tags (empty)
            [    # Media files
                {
                    'id': 1,
                    'opinion_id': 1,
                    'file_path': '/uploads/images/test_image.jpg',
                    'file_size': 1024,
                    'media_type': 'image',
                    'mime_type': 'image/jpeg',
                    'created_at': '2025-10-24 10:00:00'
                },
                {
                    'id': 2,
                    'opinion_id': 1,
                    'file_path': '/uploads/videos/test_video.mp4',
                    'file_size': 2048,
                    'media_type': 'video',
                    'mime_type': 'video/mp4',
                    'created_at': '2025-10-24 10:00:00'
                }
            ]
        ]
    )
    patch_cursor(monkeypatch, opinion_service, cursor)

    result = opinion_service.OpinionService.get_opinion_by_id(opinion_id=1)

    assert result is not None
    assert len(result.media) == 2

    # Check that media URLs were processed correctly
    # Media is returned as OpinionMedia objects
    image_media = result.media[0]
    # Verify filename extraction from file_path
    assert image_media.filename == 'test_image.jpg'
    assert image_media.url == '/media/files/image/test_image.jpg'
    assert image_media.thumbnail_url == '/media/thumbnails/test_image.jpg'

    video_media = result.media[1]
    assert video_media.filename == 'test_video.mp4'
    assert video_media.url == '/media/files/video/test_video.mp4'
    assert video_media.thumbnail_url is None  # Videos don't have thumbnails


# ==================== Get Opinions with Category Filter Tests ====================

def test_get_opinions_with_category_filter(monkeypatch, opinion_service):
    """Test filtering opinions by category_id"""
    cursor = FakeCursor(
        fetchone_results=[{'total': 10}],
        fetchall_results=[[]]
    )
    patch_cursor(monkeypatch, opinion_service, cursor)

    result = opinion_service.OpinionService.get_opinions(
        page=1,
        page_size=20,
        category_id=5
    )

    # Check that category filter was applied
    executed_sql = " ".join([stmt for stmt, _ in cursor.executed])
    assert "category_id" in executed_sql.lower()
