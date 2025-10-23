"""
Pytest 配置文件 - 共用 fixtures 和測試工具
專案: citizenApp
用途: 提供測試所需的共用資源和設定
"""

import pytest
import asyncio
from typing import Generator, AsyncGenerator
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

# 導入應用程式和資料庫模型
import sys
from pathlib import Path

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root / "src" / "main" / "python"))


# ==================== 資料庫 Fixtures ====================

@pytest.fixture(scope="session")
def test_db_engine():
    """
    建立測試資料庫引擎 (使用 SQLite in-memory)
    作用域: session - 整個測試會話只建立一次
    """
    from utils.database import Base

    # 使用記憶體資料庫進行測試
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # 建立所有資料表
    Base.metadata.create_all(bind=engine)

    yield engine

    # 清理: 刪除所有資料表
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def test_db_session(test_db_engine) -> Generator[Session, None, None]:
    """
    建立測試資料庫 session
    作用域: function - 每個測試函數都有獨立的 session
    """
    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_db_engine
    )

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.rollback()
        session.close()


# ==================== FastAPI 應用 Fixtures ====================

@pytest.fixture(scope="module")
def test_app():
    """
    建立測試用的 FastAPI 應用實例
    作用域: module - 每個測試模組共用一個實例
    """
    from core.app import app
    return app


@pytest.fixture(scope="function")
def test_client(test_app) -> Generator[TestClient, None, None]:
    """
    建立測試客戶端
    作用域: function - 每個測試函數都有獨立的客戶端
    """
    with TestClient(test_app) as client:
        yield client


# ==================== 認證 Fixtures ====================

@pytest.fixture(scope="function")
def test_user_data():
    """提供測試用戶資料"""
    return {
        "username": "test_user",
        "email": "test@example.com",
        "password": "TestPassword123!",
        "role": "citizen"
    }


@pytest.fixture(scope="function")
def test_admin_data():
    """提供測試管理員資料"""
    return {
        "username": "test_admin",
        "email": "admin@example.com",
        "password": "AdminPassword123!",
        "role": "admin"
    }


@pytest.fixture(scope="function")
def test_moderator_data():
    """提供測試審核員資料"""
    return {
        "username": "test_moderator",
        "email": "moderator@example.com",
        "password": "ModPassword123!",
        "role": "moderator"
    }


@pytest.fixture(scope="function")
def create_test_user(test_db_session, test_user_data):
    """
    建立測試用戶並返回用戶物件
    """
    from models.user import User
    from utils.security import hash_password

    user = User(
        username=test_user_data["username"],
        email=test_user_data["email"],
        password_hash=hash_password(test_user_data["password"]),
        role=test_user_data["role"]
    )

    test_db_session.add(user)
    test_db_session.commit()
    test_db_session.refresh(user)

    return user


@pytest.fixture(scope="function")
def create_test_admin(test_db_session, test_admin_data):
    """
    建立測試管理員並返回用戶物件
    """
    from models.user import User
    from utils.security import hash_password

    admin = User(
        username=test_admin_data["username"],
        email=test_admin_data["email"],
        password_hash=hash_password(test_admin_data["password"]),
        role=test_admin_data["role"]
    )

    test_db_session.add(admin)
    test_db_session.commit()
    test_db_session.refresh(admin)

    return admin


@pytest.fixture(scope="function")
def auth_headers_user(test_client, test_user_data, create_test_user):
    """
    獲取普通用戶的認證標頭
    """
    response = test_client.post(
        "/auth/login",
        json={
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
    )

    assert response.status_code == 200
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(scope="function")
def auth_headers_admin(test_client, test_admin_data, create_test_admin):
    """
    獲取管理員的認證標頭
    """
    response = test_client.post(
        "/auth/login",
        json={
            "username": test_admin_data["username"],
            "password": test_admin_data["password"]
        }
    )

    assert response.status_code == 200
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}


# ==================== 意見系統 Fixtures ====================

@pytest.fixture(scope="function")
def test_opinion_data():
    """提供測試意見資料"""
    return {
        "title": "測試意見標題",
        "content": "這是一個測試意見的內容，用於驗證意見系統功能。",
        "category_id": 1,
        "region": "台北市"
    }


@pytest.fixture(scope="function")
def create_test_opinion(test_db_session, create_test_user, test_opinion_data):
    """
    建立測試意見並返回意見物件
    """
    from models.opinion import Opinion

    opinion = Opinion(
        title=test_opinion_data["title"],
        content=test_opinion_data["content"],
        user_id=create_test_user.id,
        category_id=test_opinion_data["category_id"],
        region=test_opinion_data["region"],
        status="pending"
    )

    test_db_session.add(opinion)
    test_db_session.commit()
    test_db_session.refresh(opinion)

    return opinion


@pytest.fixture(scope="function")
def create_multiple_opinions(test_db_session, create_test_user, test_opinion_data):
    """
    建立多個測試意見
    """
    from models.opinion import Opinion

    opinions = []
    statuses = ["draft", "pending", "approved", "rejected"]

    for i, status in enumerate(statuses):
        opinion = Opinion(
            title=f"{test_opinion_data['title']} {i+1}",
            content=f"{test_opinion_data['content']} {i+1}",
            user_id=create_test_user.id,
            category_id=test_opinion_data["category_id"],
            region=test_opinion_data["region"],
            status=status
        )
        test_db_session.add(opinion)
        opinions.append(opinion)

    test_db_session.commit()

    for opinion in opinions:
        test_db_session.refresh(opinion)

    return opinions


# ==================== 工具 Fixtures ====================

@pytest.fixture(scope="function")
def cleanup_db(test_db_session):
    """
    測試後清理資料庫
    """
    yield

    # 清理所有資料表
    from utils.database import Base

    for table in reversed(Base.metadata.sorted_tables):
        test_db_session.execute(table.delete())

    test_db_session.commit()


# ==================== 異步測試支援 ====================

@pytest.fixture(scope="session")
def event_loop():
    """
    建立事件迴圈供異步測試使用
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# ==================== Pytest Hooks ====================

def pytest_configure(config):
    """
    Pytest 配置 hook
    """
    config.addinivalue_line(
        "markers", "slow: 標記為執行時間較長的測試"
    )
    config.addinivalue_line(
        "markers", "smoke: 標記為冒煙測試"
    )


def pytest_collection_modifyitems(config, items):
    """
    修改測試收集的 hook - 自動添加標記
    """
    for item in items:
        # 根據測試路徑自動添加標記
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)

        # 根據測試名稱添加標記
        if "auth" in item.nodeid.lower():
            item.add_marker(pytest.mark.auth)
        elif "opinion" in item.nodeid.lower():
            item.add_marker(pytest.mark.opinion)
        elif "moderation" in item.nodeid.lower() or "admin" in item.nodeid.lower():
            item.add_marker(pytest.mark.moderation)
