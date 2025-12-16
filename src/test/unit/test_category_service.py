"""
分類服務單元測試
測試範圍: 分類查詢、驗證等核心功能
測試案例對應: TC-CAT-SERVICE-001 ~ TC-CAT-SERVICE-015
"""

import pytest
from services.category_service import CategoryService


@pytest.mark.unit
class TestCategoryQueries:
    """分類查詢測試"""

    def test_get_all_categories_success(self, db_connection):
        """TC-CAT-SERVICE-001: 成功獲取所有分類"""
        categories = CategoryService.get_all_categories()

        assert isinstance(categories, list)
        assert len(categories) > 0

        # 驗證分類結構
        for category in categories:
            assert 'id' in category
            assert 'name' in category
            assert 'description' in category

    def test_get_all_categories_sorted_by_name(self, db_connection):
        """TC-CAT-SERVICE-002: 分類按名稱排序"""
        categories = CategoryService.get_all_categories()

        if len(categories) > 1:
            names = [cat['name'] for cat in categories]
            assert names == sorted(names), "分類應按名稱排序"

    def test_get_category_by_id_success(self, db_connection):
        """TC-CAT-SERVICE-003: 成功根據 ID 獲取分類"""
        # 先獲取所有分類
        categories = CategoryService.get_all_categories()
        assert len(categories) > 0

        # 獲取第一個分類的 ID
        first_category_id = categories[0]['id']

        # 根據 ID 獲取分類
        category = CategoryService.get_category_by_id(first_category_id)

        assert category is not None
        assert category['id'] == first_category_id
        assert 'name' in category
        assert 'description' in category

    def test_get_category_by_id_not_found(self, db_connection):
        """TC-CAT-SERVICE-004: 獲取不存在的分類返回 None"""
        non_existent_id = 999999

        category = CategoryService.get_category_by_id(non_existent_id)

        assert category is None

    def test_get_category_by_id_invalid_input(self, db_connection):
        """TC-CAT-SERVICE-005: 無效的 ID 類型處理"""
        # 測試負數 ID
        category = CategoryService.get_category_by_id(-1)
        assert category is None

        # 測試 0
        category = CategoryService.get_category_by_id(0)
        assert category is None


@pytest.mark.unit
class TestCategoryExistence:
    """分類存在性檢查測試"""

    def test_category_exists_true(self, db_connection):
        """TC-CAT-SERVICE-006: 存在的分類返回 True"""
        # 先獲取一個存在的分類
        categories = CategoryService.get_all_categories()
        assert len(categories) > 0

        category_id = categories[0]['id']

        # 檢查是否存在
        exists = CategoryService.category_exists(category_id)

        assert exists is True

    def test_category_exists_false(self, db_connection):
        """TC-CAT-SERVICE-007: 不存在的分類返回 False"""
        non_existent_id = 999999

        exists = CategoryService.category_exists(non_existent_id)

        assert exists is False

    def test_category_exists_invalid_id(self, db_connection):
        """TC-CAT-SERVICE-008: 無效 ID 返回 False"""
        exists = CategoryService.category_exists(-1)
        assert exists is False

        exists = CategoryService.category_exists(0)
        assert exists is False


@pytest.mark.unit
class TestCategoryCount:
    """分類計數測試"""

    def test_get_category_count_positive(self, db_connection):
        """TC-CAT-SERVICE-009: 獲取分類總數"""
        count = CategoryService.get_category_count()

        assert isinstance(count, int)
        assert count > 0

    def test_get_category_count_matches_list_length(self, db_connection):
        """TC-CAT-SERVICE-010: 分類計數與列表長度一致"""
        categories = CategoryService.get_all_categories()
        count = CategoryService.get_category_count()

        assert count == len(categories)


@pytest.mark.unit
@pytest.mark.no_db
class TestCategoryValidation:
    """分類驗證測試 (不需要數據庫)"""

    def test_validate_category_name_valid(self):
        """TC-CAT-SERVICE-011: 有效的分類名稱"""
        assert CategoryService.validate_category_name("交通建設") is True
        assert CategoryService.validate_category_name("環境保護") is True
        assert CategoryService.validate_category_name("AB") is True  # 最短 2 字符

    def test_validate_category_name_too_short(self):
        """TC-CAT-SERVICE-012: 分類名稱過短"""
        assert CategoryService.validate_category_name("A") is False
        assert CategoryService.validate_category_name("") is False

    def test_validate_category_name_too_long(self):
        """TC-CAT-SERVICE-013: 分類名稱過長"""
        long_name = "A" * 51  # 超過 50 字符
        assert CategoryService.validate_category_name(long_name) is False

    def test_validate_category_name_whitespace(self):
        """TC-CAT-SERVICE-014: 只有空白字符的名稱無效"""
        assert CategoryService.validate_category_name("   ") is False
        assert CategoryService.validate_category_name("\t\n") is False

    def test_validate_category_name_invalid_type(self):
        """TC-CAT-SERVICE-015: 無效的名稱類型"""
        assert CategoryService.validate_category_name(None) is False
        assert CategoryService.validate_category_name(123) is False
        assert CategoryService.validate_category_name([]) is False


@pytest.mark.unit
class TestCategoryDataIntegrity:
    """分類數據完整性測試"""

    def test_all_categories_have_required_fields(self, db_connection):
        """TC-CAT-SERVICE-016: 所有分類包含必要欄位"""
        categories = CategoryService.get_all_categories()

        for category in categories:
            assert category['id'] is not None
            assert category['name'] is not None
            assert len(category['name']) > 0
            # description 可以為 None
            assert 'created_at' in category

    def test_category_ids_are_unique(self, db_connection):
        """TC-CAT-SERVICE-017: 分類 ID 唯一"""
        categories = CategoryService.get_all_categories()

        category_ids = [cat['id'] for cat in categories]
        unique_ids = set(category_ids)

        assert len(category_ids) == len(unique_ids), "分類 ID 應該唯一"

    def test_category_names_not_empty(self, db_connection):
        """TC-CAT-SERVICE-018: 分類名稱不為空"""
        categories = CategoryService.get_all_categories()

        for category in categories:
            assert category['name'].strip() != "", "分類名稱不應為空"
