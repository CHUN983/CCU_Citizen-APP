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
