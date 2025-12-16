"""
分類管理服務
提供分類的業務邏輯處理
"""

from typing import List, Optional, Dict, Any
from utils.database import get_db_cursor


class CategoryService:
    """分類服務類別"""

    @staticmethod
    def get_all_categories() -> List[Dict[str, Any]]:
        """
        獲取所有分類

        Returns:
            List[Dict]: 分類列表
        """
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT id, name, description, created_at
                FROM categories
                ORDER BY name
            """)

            categories = cursor.fetchall()
            return categories

    @staticmethod
    def get_category_by_id(category_id: int) -> Optional[Dict[str, Any]]:
        """
        根據 ID 獲取分類

        Args:
            category_id: 分類 ID

        Returns:
            Optional[Dict]: 分類資訊，如果不存在返回 None
        """
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT id, name, description, created_at
                FROM categories
                WHERE id = %s
            """, (category_id,))

            category = cursor.fetchone()
            return category

    @staticmethod
    def category_exists(category_id: int) -> bool:
        """
        檢查分類是否存在

        Args:
            category_id: 分類 ID

        Returns:
            bool: 分類是否存在
        """
        with get_db_cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) as count
                FROM categories
                WHERE id = %s
            """, (category_id,))

            result = cursor.fetchone()
            return result['count'] > 0 if result else False

    @staticmethod
    def get_category_count() -> int:
        """
        獲取分類總數

        Returns:
            int: 分類總數
        """
        with get_db_cursor() as cursor:
            cursor.execute("SELECT COUNT(*) as count FROM categories")
            result = cursor.fetchone()
            return result['count'] if result else 0

    @staticmethod
    def validate_category_name(name: str) -> bool:
        """
        驗證分類名稱格式

        Args:
            name: 分類名稱

        Returns:
            bool: 名稱是否有效
        """
        if not name or not isinstance(name, str):
            return False

        # 名稱長度限制
        if len(name.strip()) < 2 or len(name.strip()) > 50:
            return False

        return True
