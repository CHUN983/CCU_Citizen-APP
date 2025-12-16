from datetime import datetime
from types import SimpleNamespace
import importlib
import sys

import mysql.connector.pooling as mysql_pooling
import pytest

from models.user import UserCreate, UserLogin, UserRole
from src.test.unit.helpers import FakeCursor, cursor_context

pytestmark = pytest.mark.no_db


def make_user_row(**overrides):
    now = datetime.utcnow()
    base = {
        "id": 1,
        "username": "tester",
        "email": "tester@example.com",
        "full_name": "Test User",
        "role": UserRole.CITIZEN,
        "is_active": True,
        "created_at": now,
        "updated_at": now,
        "password_hash": "stored-hash",
    }
    base.update(overrides)
    return base


def load_auth_service(monkeypatch):
    class DummyPool:
        def __init__(self, *args, **kwargs):
            pass

        def get_connection(self):
            raise RuntimeError("connection pool not available in unit tests")

    monkeypatch.setattr(mysql_pooling, "MySQLConnectionPool", lambda *a, **k: DummyPool())
    sys.modules.pop("utils.database", None)
    sys.modules.pop("services.auth_service", None)
    return importlib.import_module("services.auth_service")


@pytest.fixture
def auth_service(monkeypatch):
    return load_auth_service(monkeypatch)


def test_create_user_success(monkeypatch, auth_service):
    user_data = UserCreate(
        username="tester",
        email="tester@example.com",
        password="secret123",
        full_name="Test User",
        role=UserRole.CITIZEN,
    )
    created_row = make_user_row()
    cursor = FakeCursor(fetchone_results=[created_row])
    cursor.lastrowid = created_row["id"]

    monkeypatch.setattr(auth_service, "get_db_cursor", lambda *a, **k: cursor_context(cursor))
    monkeypatch.setattr(auth_service, "hash_password", lambda pwd: "HASHED-" + pwd)

    user = auth_service.AuthService.create_user(user_data)

    assert user is not None
    assert user.username == "tester"
    assert any("INSERT INTO users" in stmt for stmt, _ in cursor.executed)
    insert_params = cursor.executed[0][1]
    assert insert_params[2] == "HASHED-secret123"


def test_create_user_returns_none_on_error(monkeypatch, auth_service):
    class ExplodingCtx:
        def __enter__(self, *args, **kwargs):
            raise RuntimeError("db unavailable")

        def __exit__(self, exc_type, exc, tb):
            return False

    monkeypatch.setattr(auth_service, "get_db_cursor", lambda *a, **k: ExplodingCtx())
    user_data = UserCreate(
        username="tester",
        email="tester@example.com",
        password="secret123",
        full_name="Test User",
        role=UserRole.CITIZEN,
    )

    assert auth_service.AuthService.create_user(user_data) is None


def test_authenticate_user_returns_user_when_password_matches(monkeypatch, auth_service):
    login_data = UserLogin(username="tester", password="secret123")
    row = make_user_row()
    cursor = FakeCursor(fetchone_results=[row])

    monkeypatch.setattr(auth_service, "get_db_cursor", lambda *a, **k: cursor_context(cursor))

    def fake_verify(password, hash_value):
        assert password == login_data.password
        assert hash_value == row["password_hash"]
        return True

    monkeypatch.setattr(auth_service, "verify_password", fake_verify)

    user = auth_service.AuthService.authenticate_user(login_data)

    assert user is not None
    assert user.username == login_data.username


def test_authenticate_user_returns_none_for_bad_password(monkeypatch, auth_service):
    login_data = UserLogin(username="tester", password="badpass")
    row = make_user_row()
    cursor = FakeCursor(fetchone_results=[row])

    monkeypatch.setattr(auth_service, "get_db_cursor", lambda *a, **k: cursor_context(cursor))
    monkeypatch.setattr(auth_service, "verify_password", lambda *args, **kwargs: False)

    assert auth_service.AuthService.authenticate_user(login_data) is None


def test_login_returns_token(monkeypatch, auth_service):
    fake_user = SimpleNamespace(id=1, username="tester", role=UserRole.CITIZEN)
    monkeypatch.setattr(auth_service.AuthService, "authenticate_user", lambda *_: fake_user)
    monkeypatch.setattr(auth_service, "create_access_token", lambda data: f"token-{data['username']}")

    token = auth_service.AuthService.login(UserLogin(username="tester", password="secret123"))

    assert token is not None
    assert token.access_token == "token-tester"
    assert token.token_type == "bearer"


def test_login_returns_none_when_authentication_fails(monkeypatch, auth_service):
    monkeypatch.setattr(auth_service.AuthService, "authenticate_user", lambda *_: None)

    assert auth_service.AuthService.login(UserLogin(username="nope", password="x")) is None


def test_get_user_by_username_returns_user(monkeypatch, auth_service):
    row = make_user_row(username="alice")
    cursor = FakeCursor(fetchone_results=[row])
    monkeypatch.setattr(auth_service, "get_db_cursor", lambda *a, **k: cursor_context(cursor))

    user = auth_service.AuthService.get_user_by_username("alice")

    assert user is not None
    assert user.username == "alice"


def test_get_user_by_id_returns_none_when_missing(monkeypatch, auth_service):
    cursor = FakeCursor(fetchone_results=[None])
    monkeypatch.setattr(auth_service, "get_db_cursor", lambda *a, **k: cursor_context(cursor))

    assert auth_service.AuthService.get_user_by_id(999) is None
