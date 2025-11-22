"""
Database connection and utilities
"""

import os
from contextlib import contextmanager
from typing import Generator, Optional
import mysql.connector
from mysql.connector import pooling
from mysql.connector.pooling import PooledMySQLConnection
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class DatabaseConfig:
    """Database configuration"""
    HOST = os.getenv("DB_HOST", "localhost")
    PORT = int(os.getenv("DB_PORT", "3306"))
    USER = os.getenv("DB_USER", "root")
    PASSWORD = os.getenv("DB_PASSWORD", "")
    DATABASE = os.getenv("DB_NAME", "citizen_app")
    POOL_NAME = "citizen_app_pool"
    POOL_SIZE = int(os.getenv("DB_POOL_SIZE", "5"))


# Create connection pool
connection_pool = pooling.MySQLConnectionPool(
    pool_name=DatabaseConfig.POOL_NAME,
    pool_size=DatabaseConfig.POOL_SIZE,
    pool_reset_session=True,
    host=DatabaseConfig.HOST,
    port=DatabaseConfig.PORT,
    user=DatabaseConfig.USER,
    password=DatabaseConfig.PASSWORD,
    database=DatabaseConfig.DATABASE,
    charset='utf8mb4',
    collation='utf8mb4_unicode_ci'
)

# 測試用連接池 (用於測試時覆蓋)
_test_connection_pool: Optional[pooling.MySQLConnectionPool] = None


def set_test_connection_pool(pool: Optional[pooling.MySQLConnectionPool]):
    """設置測試用連接池 (僅供測試使用)"""
    global _test_connection_pool
    _test_connection_pool = pool


def _get_connection_pool() -> pooling.MySQLConnectionPool:
    """獲取當前連接池 (測試模式下返回測試連接池)"""
    return _test_connection_pool if _test_connection_pool is not None else connection_pool


@contextmanager 
def get_db_connection() -> Generator[PooledMySQLConnection, None, None]: #
    """
    Get database connection from pool

    Usage:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users")
    """
    pool = _get_connection_pool()
    connection = pool.get_connection()
    try:
        yield connection
    finally:
        connection.close()


@contextmanager
def get_db_cursor(dictionary=True):
    """
    Get database cursor with automatic connection management

    Args:
        dictionary: Return rows as dictionaries (default: True)

    Usage:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT * FROM users")
            users = cursor.fetchall()
    """
    with get_db_connection() as conn:
        cursor = conn.cursor(dictionary=dictionary)
        try:
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()


def init_database():
    """Initialize database with schema"""
    schema_file = os.path.join(
        os.path.dirname(__file__),
        "../../resources/config/schema.sql"
    )

    if not os.path.exists(schema_file):
        raise FileNotFoundError(f"Schema file not found: {schema_file}")

    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    # Split by semicolon and execute each statement
    statements = [s.strip() for s in schema_sql.split(';') if s.strip()]

    with get_db_cursor() as cursor:
        for statement in statements:
            if statement:
                cursor.execute(statement)

    print("Database initialized successfully!")


if __name__ == "__main__":
    # Test connection
    try:
        with get_db_cursor() as cursor:
            cursor.execute("SELECT 1")
            print("Database connection successful!")
    except Exception as e:
        print(f"Database connection failed: {e}")
