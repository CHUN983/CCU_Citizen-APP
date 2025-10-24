"""
Pytest 配置文件 - 共用 fixtures 和測試工具
專案: citizenApp
用途: 提供測試所需的共用資源和設定
"""

import pytest
import asyncio
from typing import Generator
from fastapi.testclient import TestClient
import mysql.connector
from mysql.connector import pooling
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from types import SimpleNamespace

# 添加專案根目錄到 Python 路徑
project_root = Path(__file__).parent.parent.parent
python_src = project_root / "src" / "main" / "python"

# 載入 .env 檔案
load_dotenv(project_root / ".env")

# 將 Python 源碼目錄加入路徑
if str(python_src) not in sys.path:
    sys.path.insert(0, str(python_src))

# 設置 PYTHONPATH 環境變數以支持相對導入
os.environ['PYTHONPATH'] = str(python_src) + os.pathsep + os.environ.get('PYTHONPATH', '')


# ==================== 資料庫 Fixtures ====================

# 測試資料庫配置 (使用 production 的密碼，但使用不同的資料庫名稱)
TEST_DB_CONFIG = {
    "host": os.getenv("TEST_DB_HOST", os.getenv("DB_HOST", "localhost")),
    "port": int(os.getenv("TEST_DB_PORT", os.getenv("DB_PORT", "3306"))),
    "user": os.getenv("TEST_DB_USER", os.getenv("DB_USER", "root")),
    "password": os.getenv("TEST_DB_PASSWORD", os.getenv("DB_PASSWORD", "")),
    "database": os.getenv("TEST_DB_NAME", "citizen_app_test"),
    "charset": "utf8mb4",
    "collation": "utf8mb4_unicode_ci"
}


@pytest.fixture(scope="session")
def test_db_connection_pool():
    """
    建立測試資料庫連接池
    作用域: session - 整個測試會話只建立一次
    """
    from utils.database import set_test_connection_pool

    # 首先連接到 MySQL server (不指定資料庫) 以建立測試資料庫
    try:
        conn = mysql.connector.connect(
            host=TEST_DB_CONFIG["host"],
            port=TEST_DB_CONFIG["port"],
            user=TEST_DB_CONFIG["user"],
            password=TEST_DB_CONFIG["password"]
        )
        cursor = conn.cursor()

        # 建立測試資料庫
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {TEST_DB_CONFIG['database']} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
        conn.commit()
        cursor.close()
        conn.close()

        # 重新連接到測試資料庫
        conn = mysql.connector.connect(
            host=TEST_DB_CONFIG["host"],
            port=TEST_DB_CONFIG["port"],
            user=TEST_DB_CONFIG["user"],
            password=TEST_DB_CONFIG["password"],
            database=TEST_DB_CONFIG["database"]  # 直接連接到測試資料庫
        )
        cursor = conn.cursor()

        # 讀取並執行 schema
        schema_file = project_root / "src/main/resources/config/schema.sql"
        with open(schema_file, 'r', encoding='utf-8') as f:
            schema_sql = f.read()

        # 分割並執行每個 SQL 語句
        statements = [s.strip() for s in schema_sql.split(';') if s.strip()]
        for statement in statements:
            if statement and not statement.startswith('--'):
                try:
                    cursor.execute(statement)
                except mysql.connector.Error as e:
                    # 忽略 "already exists" 和 "Duplicate entry" 錯誤
                    if "already exists" not in str(e) and "Duplicate entry" not in str(e):
                        print(f"Warning executing statement: {e}")

        conn.commit()
        cursor.close()
        conn.close()

    except mysql.connector.Error as e:
        print(f"Error setting up test database: {e}")
        raise

    # 建立連接池
    pool = pooling.MySQLConnectionPool(
        pool_name="test_pool",
        pool_size=5,
        pool_reset_session=True,
        **TEST_DB_CONFIG
    )

    # 設置為測試連接池 (這樣應用程式代碼會使用測試資料庫)
    set_test_connection_pool(pool)

    yield pool

    # 恢復為 production 連接池
    set_test_connection_pool(None)

    # 清理: 刪除測試資料庫
    try:
        conn = mysql.connector.connect(
            host=TEST_DB_CONFIG["host"],
            port=TEST_DB_CONFIG["port"],
            user=TEST_DB_CONFIG["user"],
            password=TEST_DB_CONFIG["password"]
        )
        cursor = conn.cursor()
        cursor.execute(f"DROP DATABASE IF EXISTS {TEST_DB_CONFIG['database']}")
        conn.commit()
        cursor.close()
        conn.close()
    except mysql.connector.Error as e:
        print(f"Error cleaning up test database: {e}")


@pytest.fixture(scope="function", autouse=True)
def cleanup_test_data(test_db_connection_pool):
    """
    自動清理測試資料 (在每個測試前後執行)
    """
    def clean_tables():
        connection = test_db_connection_pool.get_connection()
        cursor = connection.cursor()

        try:
            cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
            # 只清理資料，不刪除預設的 categories 和 admin 用戶
            tables_to_clean = [
                'opinion_history',
                'subscriptions',
                'notifications',
                'opinion_tags',
                'tags',
                'collections',
                'votes',
                'comments',
                'opinion_media',
                'opinions'
            ]
            for table in tables_to_clean:
                # 檢查表是否存在
                cursor.execute(f"SHOW TABLES LIKE '{table}'")
                if cursor.fetchone():
                    cursor.execute(f"DELETE FROM {table}")

            # 清理測試用戶 (保留預設的 admin 用戶)
            cursor.execute("SHOW TABLES LIKE 'users'")
            if cursor.fetchone():
                cursor.execute("DELETE FROM users WHERE username != 'admin'")

            cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
            connection.commit()
        except Exception as e:
            # 忽略表不存在的錯誤
            if "doesn't exist" not in str(e):
                print(f"Error cleaning test data: {e}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()

    # 測試前清理
    clean_tables()

    yield

    # 測試後清理
    clean_tables()


@pytest.fixture(scope="function")
def test_db_connection(test_db_connection_pool):
    """
    獲取測試資料庫連接
    作用域: function - 每個測試函數都有獨立的連接
    """
    connection = test_db_connection_pool.get_connection()

    yield connection

    # 清理: 回滾並關閉連接
    try:
        connection.rollback()
    except:
        pass
    connection.close()


@pytest.fixture(scope="function")
def test_db_cursor(test_db_connection):
    """
    獲取測試資料庫游標
    作用域: function - 每個測試函數都有獨立的游標
    """
    cursor = test_db_connection.cursor(dictionary=True)

    yield cursor

    # 清理
    cursor.close()


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
def create_test_user(test_db_connection, test_user_data):
    """
    建立測試用戶並返回用戶物件
    """
    from utils.security import hash_password

    cursor = test_db_connection.cursor(dictionary=True)

    # 插入用戶
    insert_sql = """
        INSERT INTO users (username, email, password_hash, role, is_active)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(insert_sql, (
        test_user_data["username"],
        test_user_data["email"],
        hash_password(test_user_data["password"]),
        test_user_data["role"],
        True
    ))
    test_db_connection.commit()

    # 獲取插入的用戶 ID
    user_id = cursor.lastrowid

    # 查詢並返回用戶資料
    cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    cursor.close()

    # 將字典轉換為可以用屬性存取的物件
    return SimpleNamespace(**user) if user else None


@pytest.fixture(scope="function")
def create_test_admin(test_db_connection, test_admin_data):
    """
    建立測試管理員並返回用戶物件
    """
    from utils.security import hash_password

    cursor = test_db_connection.cursor(dictionary=True)

    # 插入管理員
    insert_sql = """
        INSERT INTO users (username, email, password_hash, role, is_active)
        VALUES (%s, %s, %s, %s, %s)
    """
    cursor.execute(insert_sql, (
        test_admin_data["username"],
        test_admin_data["email"],
        hash_password(test_admin_data["password"]),
        test_admin_data["role"],
        True
    ))
    test_db_connection.commit()

    # 獲取插入的管理員 ID
    admin_id = cursor.lastrowid

    # 查詢並返回管理員資料
    cursor.execute("SELECT * FROM users WHERE id = %s", (admin_id,))
    admin = cursor.fetchone()
    cursor.close()

    # 將字典轉換為可以用屬性存取的物件
    return SimpleNamespace(**admin) if admin else None


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
def create_test_opinion(test_db_connection, create_test_user, test_opinion_data):
    """
    建立測試意見並返回意見物件
    """
    cursor = test_db_connection.cursor(dictionary=True)

    # 插入意見
    insert_sql = """
        INSERT INTO opinions (user_id, title, content, category_id, region, status)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    cursor.execute(insert_sql, (
        create_test_user["id"],
        test_opinion_data["title"],
        test_opinion_data["content"],
        test_opinion_data["category_id"],
        test_opinion_data["region"],
        "pending"
    ))
    test_db_connection.commit()

    # 獲取插入的意見 ID
    opinion_id = cursor.lastrowid

    # 查詢並返回意見資料
    cursor.execute("SELECT * FROM opinions WHERE id = %s", (opinion_id,))
    opinion = cursor.fetchone()
    cursor.close()

    return opinion


@pytest.fixture(scope="function")
def create_multiple_opinions(test_db_connection, create_test_user, test_opinion_data):
    """
    建立多個測試意見
    """
    cursor = test_db_connection.cursor(dictionary=True)
    opinions = []
    statuses = ["draft", "pending", "approved", "rejected"]

    insert_sql = """
        INSERT INTO opinions (user_id, title, content, category_id, region, status)
        VALUES (%s, %s, %s, %s, %s, %s)
    """

    for i, status in enumerate(statuses):
        cursor.execute(insert_sql, (
            create_test_user["id"],
            f"{test_opinion_data['title']} {i+1}",
            f"{test_opinion_data['content']} {i+1}",
            test_opinion_data["category_id"],
            test_opinion_data["region"],
            status
        ))

    test_db_connection.commit()

    # 查詢並返回所有意見
    cursor.execute(
        "SELECT * FROM opinions WHERE user_id = %s ORDER BY id",
        (create_test_user["id"],)
    )
    opinions = cursor.fetchall()
    cursor.close()

    return opinions


# ==================== 工具 Fixtures ====================

@pytest.fixture(scope="function")
def cleanup_db(test_db_connection):
    """
    測試後清理資料庫
    """
    yield

    # 清理所有資料表 (按照外鍵相依性順序)
    cursor = test_db_connection.cursor()
    tables = [
        'opinion_history',
        'subscriptions',
        'notifications',
        'opinion_tags',
        'tags',
        'collections',
        'votes',
        'comments',
        'opinion_media',
        'opinions',
        'users'
    ]

    try:
        cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
        for table in tables:
            cursor.execute(f"DELETE FROM {table}")
        cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
        test_db_connection.commit()
    except Exception as e:
        print(f"Error cleaning up database: {e}")
        test_db_connection.rollback()
    finally:
        cursor.close()


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
