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
