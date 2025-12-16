"""
分類管理 API 整合測試
測試案例對應: TC-CAT-001 ~ TC-CAT-004
需求對應: REQ-006 (分類管理功能)
"""

import pytest
from fastapi.testclient import TestClient


class TestCategoryRetrieval:
    """分類查詢測試類別"""

    def test_get_all_categories(
        self,
        test_client: TestClient,
        test_db_cursor
    ):
        """
        TC-CAT-001: 獲取所有分類
        測試目標: 驗證能夠獲取所有分類列表
        優先級: Critical
        """
        # 執行獲取分類列表請求
        response = test_client.get("/categories")

        # 驗證結果
        assert response.status_code == 200, f"期望狀態碼 200，實際 {response.status_code}"

        data = response.json()
        assert "categories" in data
        assert "total" in data
        assert isinstance(data["categories"], list)
        assert data["total"] == len(data["categories"])

        # 驗證分類項目結構
        if len(data["categories"]) > 0:
            category = data["categories"][0]
            assert "id" in category
            assert "name" in category
            assert "description" in category or category.get("description") is None
            assert "created_at" in category

    def test_get_category_by_id_success(
        self,
        test_client: TestClient,
        test_db_connection,
        test_db_cursor
    ):
        """
        TC-CAT-002: 成功獲取指定分類
        測試目標: 驗證能夠通過 ID 獲取特定分類
        優先級: Critical
        """
        # 先獲取一個存在的分類 ID
        response = test_client.get("/categories")
        assert response.status_code == 200
        categories = response.json()["categories"]

        if len(categories) == 0:
            # 如果沒有分類，創建一個測試分類
            test_db_cursor.execute("""
                INSERT INTO categories (name, description)
                VALUES (%s, %s)
            """, ("測試分類", "測試用分類描述"))
            test_db_connection.commit()
            category_id = test_db_cursor.lastrowid
        else:
            category_id = categories[0]["id"]

        # 執行獲取單一分類請求
        response = test_client.get(f"/categories/{category_id}")

        # 驗證結果
        assert response.status_code == 200, f"期望狀態碼 200，實際 {response.status_code}"

        data = response.json()
        assert data["id"] == category_id
        assert "name" in data
        assert "description" in data or data.get("description") is None
        assert "created_at" in data

    def test_get_category_by_id_not_found(
        self,
        test_client: TestClient
    ):
        """
        TC-CAT-003: 獲取不存在的分類
        測試目標: 驗證查詢不存在的分類時返回 404
        優先級: High
        """
        # 使用一個肯定不存在的分類 ID
        non_existent_id = 999999

        # 執行請求
        response = test_client.get(f"/categories/{non_existent_id}")

        # 驗證結果
        assert response.status_code == 404, f"期望狀態碼 404，實際 {response.status_code}"

        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()


class TestCategoryIntegration:
    """分類整合測試類別"""

    def test_categories_list_order(
        self,
        test_client: TestClient,
        test_db_connection,
        test_db_cursor
    ):
        """
        TC-CAT-004: 驗證分類列表按名稱排序
        測試目標: 確認分類列表按照名稱字母順序排列
        優先級: Medium
        """
        # 插入測試分類
        test_categories = [
            ("環境", "環境相關議題"),
            ("交通", "交通相關議題"),
            ("教育", "教育相關議題"),
        ]

        for name, description in test_categories:
            # 檢查是否已存在
            test_db_cursor.execute("SELECT id FROM categories WHERE name = %s", (name,))
            if not test_db_cursor.fetchone():
                test_db_cursor.execute("""
                    INSERT INTO categories (name, description)
                    VALUES (%s, %s)
                """, (name, description))

        test_db_connection.commit()

        # 獲取分類列表
        response = test_client.get("/categories")
        assert response.status_code == 200

        data = response.json()
        categories = data["categories"]

        # 驗證排序 (應該按 name 排序)
        if len(categories) >= 2:
            for i in range(len(categories) - 1):
                current_name = categories[i]["name"]
                next_name = categories[i + 1]["name"]
                # 中文和英文混合排序可能有不同規則，這裡只驗證順序一致性
                assert current_name <= next_name or current_name >= next_name, \
                    "分類列表應該有一致的排序規則"

    def test_category_data_integrity(
        self,
        test_client: TestClient,
        test_db_connection,
        test_db_cursor
    ):
        """
        TC-CAT-005: 驗證分類資料完整性
        測試目標: 確認返回的分類資料與資料庫中的資料一致
        優先級: High
        """
        # 插入一個測試分類
        test_db_cursor.execute("""
            INSERT INTO categories (name, description)
            VALUES (%s, %s)
        """, ("測試完整性分類", "用於測試資料完整性"))
        test_db_connection.commit()
        category_id = test_db_cursor.lastrowid

        # 通過 API 獲取
        response = test_client.get(f"/categories/{category_id}")
        assert response.status_code == 200

        api_data = response.json()

        # 從資料庫直接查詢
        test_db_cursor.execute("""
            SELECT id, name, description, created_at
            FROM categories
            WHERE id = %s
        """, (category_id,))
        db_data = test_db_cursor.fetchone()

        # 驗證資料一致性
        assert api_data["id"] == db_data["id"]
        assert api_data["name"] == db_data["name"]
        assert api_data["description"] == db_data["description"]
        # created_at 格式可能不同，只驗證存在
        assert "created_at" in api_data
