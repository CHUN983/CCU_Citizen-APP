"""
Moderation Service 單元測試
測試目標: ModerationService 的核心功能
測試策略: Mock 資料庫操作，專注測試業務邏輯
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from services.moderation_service import ModerationService
from models.opinion import OpinionStatus
from models.opinion_history import OpinionHistoryList


# ==================== Dashboard Statistics 測試 ====================

class TestGetDashboardStats:
    """測試儀表板統計功能"""

    @patch('services.moderation_service.get_db_cursor')
    def test_get_dashboard_stats_success(self, mock_get_cursor):
        """TC-MS-001: 成功獲取儀表板統計"""
        mock_cursor = MagicMock()

        # Mock 三個查詢的結果
        mock_cursor.fetchone.side_effect = [
            # Overall stats
            {
                'total': 100,
                'approved': 60,
                'pending': 30,
                'rejected': 10
            },
            # Today stats
            {
                'total': 10,
                'approved': 5,
                'pending': 3,
                'rejected': 2
            }
        ]

        # Top categories
        mock_cursor.fetchall.return_value = [
            {'category_id': 1, 'category_name': '交通', 'count': 25},
            {'category_id': 2, 'category_name': '環境', 'count': 20},
            {'category_id': 3, 'category_name': '教育', 'count': 15}
        ]

        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        # 執行測試
        result = ModerationService.get_dashboard_stats()

        # 驗證結果
        assert result['overall']['total'] == 100
        assert result['overall']['approved'] == 60
        assert result['overall']['pending'] == 30
        assert result['overall']['rejected'] == 10

        assert result['today']['total'] == 10
        assert result['today']['approved'] == 5

        assert len(result['top_categories']) == 3
        assert result['top_categories'][0]['category_name'] == '交通'
        assert result['top_categories'][0]['count'] == 25

        # 驗證執行了 3 個查詢
        assert mock_cursor.execute.call_count == 3

    @patch('services.moderation_service.get_db_cursor')
    def test_get_dashboard_stats_empty_data(self, mock_get_cursor):
        """TC-MS-002: 獲取空統計數據"""
        mock_cursor = MagicMock()

        mock_cursor.fetchone.side_effect = [
            {'total': 0, 'approved': 0, 'pending': 0, 'rejected': 0},
            {'total': 0, 'approved': 0, 'pending': 0, 'rejected': 0}
        ]

        mock_cursor.fetchall.return_value = []

        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        result = ModerationService.get_dashboard_stats()

        assert result['overall']['total'] == 0
        assert result['today']['total'] == 0
        assert result['top_categories'] == []


# ==================== Moderation History 測試 ====================

class TestGetModerationHistory:
    """測試審核歷史查詢功能"""

    @patch('services.moderation_service.get_db_cursor')
    def test_get_history_basic(self, mock_get_cursor):
        """TC-MS-003: 基本歷史查詢（無篩選）"""
        mock_cursor = MagicMock()

        # Mock count query
        mock_cursor.fetchone.return_value = {'total': 25}

        # Mock data query
        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'opinion_id': 10,
                'user_id': 2,
                'action': 'status_changed',
                'old_status': 'pending',
                'new_status': 'approved',
                'changes': None,
                'created_at': datetime(2025, 10, 24, 10, 0, 0),
                'username': 'admin',
                'opinion_title': '改善公園設施'
            },
            {
                'id': 2,
                'opinion_id': 11,
                'user_id': 2,
                'action': 'updated',
                'old_status': None,
                'new_status': None,
                'changes': '{"category_id": 3}',
                'created_at': datetime(2025, 10, 24, 11, 0, 0),
                'username': 'admin',
                'opinion_title': '交通改善'
            }
        ]

        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        # 執行測試
        result = ModerationService.get_moderation_history(page=1, page_size=20)

        # 驗證結果
        assert isinstance(result, OpinionHistoryList)
        assert result.total == 25
        assert result.page == 1
        assert result.page_size == 20
        assert len(result.items) == 2

        # 驗證第一筆記錄
        assert result.items[0].opinion_id == 10
        assert result.items[0].action == 'status_changed'
        assert result.items[0].username == 'admin'

        # 驗證 SQL 參數（無篩選條件，只有分頁參數）
        data_query_call = mock_cursor.execute.call_args_list[1]
        params = data_query_call[0][1]
        assert params == [20, 0]  # page_size, offset

    @patch('services.moderation_service.get_db_cursor')
    def test_get_history_with_opinion_filter(self, mock_get_cursor):
        """TC-MS-004: 按意見 ID 篩選歷史"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {'total': 5}
        mock_cursor.fetchall.return_value = []

        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        result = ModerationService.get_moderation_history(
            page=1,
            page_size=20,
            opinion_id=123
        )

        # 驗證查詢中包含 opinion_id 篩選
        count_query_call = mock_cursor.execute.call_args_list[0]
        count_sql = count_query_call[0][0]
        count_params = count_query_call[0][1]

        assert 'h.opinion_id = %s' in count_sql
        assert 123 in count_params

    @patch('services.moderation_service.get_db_cursor')
    def test_get_history_with_time_range(self, mock_get_cursor):
        """TC-MS-005: 按時間範圍篩選歷史"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {'total': 10}
        mock_cursor.fetchall.return_value = []

        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        start_time = datetime(2025, 10, 1, 0, 0, 0)
        end_time = datetime(2025, 10, 31, 23, 59, 59)

        result = ModerationService.get_moderation_history(
            page=1,
            page_size=20,
            start_time=start_time,
            end_time=end_time
        )

        # 驗證查詢中包含時間篩選
        count_query_call = mock_cursor.execute.call_args_list[0]
        count_sql = count_query_call[0][0]
        count_params = count_query_call[0][1]

        assert 'h.created_at >= %s' in count_sql
        assert 'h.created_at <= %s' in count_sql
        assert start_time in count_params
        assert end_time in count_params

    @patch('services.moderation_service.get_db_cursor')
    def test_get_history_pagination(self, mock_get_cursor):
        """TC-MS-006: 測試分頁計算"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {'total': 100}
        mock_cursor.fetchall.return_value = []

        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        # 第 3 頁，每頁 10 筆
        result = ModerationService.get_moderation_history(page=3, page_size=10)

        # 驗證 offset 計算正確: (3-1) * 10 = 20
        data_query_call = mock_cursor.execute.call_args_list[1]
        params = data_query_call[0][1]
        assert params == [10, 20]  # page_size=10, offset=20

    @patch('services.moderation_service.get_db_cursor')
    def test_get_history_all_filters(self, mock_get_cursor):
        """TC-MS-007: 同時使用所有篩選條件"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {'total': 3}
        mock_cursor.fetchall.return_value = []

        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        start_time = datetime(2025, 10, 1, 0, 0, 0)
        end_time = datetime(2025, 10, 31, 23, 59, 59)

        result = ModerationService.get_moderation_history(
            page=2,
            page_size=15,
            opinion_id=456,
            start_time=start_time,
            end_time=end_time
        )

        # 驗證所有篩選條件都包含在查詢中
        count_query_call = mock_cursor.execute.call_args_list[0]
        count_sql = count_query_call[0][0]
        count_params = count_query_call[0][1]

        assert 'h.opinion_id = %s' in count_sql
        assert 'h.created_at >= %s' in count_sql
        assert 'h.created_at <= %s' in count_sql
        assert count_params == [456, start_time, end_time]

        # 驗證分頁參數
        data_query_call = mock_cursor.execute.call_args_list[1]
        data_params = data_query_call[0][1]
        assert data_params == [456, start_time, end_time, 15, 15]  # filters + page_size + offset


# ==================== Error Handling 測試 ====================

class TestErrorHandling:
    """測試錯誤處理路徑"""

    @patch('services.moderation_service.NotificationService.create_notification')
    @patch('services.moderation_service.get_db_cursor')
    def test_merge_opinions_notification_error(self, mock_get_cursor, mock_create_notif):
        """TC-MS-008: 合併意見時通知失敗（不應影響合併）"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {'user_id': 10}
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        # 模擬通知失敗
        mock_create_notif.side_effect = Exception("Notification service unavailable")

        # 執行合併
        result = ModerationService.merge_opinions(
            source_id=1,
            target_id=2,
            moderator_id=3
        )

        # 即使通知失敗，合併仍應成功
        assert result is True

        # 驗證仍然執行了 UPDATE 和 INSERT 操作
        assert mock_cursor.execute.call_count >= 2

    @patch('services.moderation_service.get_db_cursor')
    def test_delete_comment_error(self, mock_get_cursor):
        """TC-MS-009: 刪除留言時資料庫錯誤"""
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("Database error")
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        result = ModerationService.delete_comment(comment_id=1, moderator_id=2)

        # 應返回 False
        assert result is False

    @patch('services.moderation_service.NotificationService.create_notification')
    @patch('services.moderation_service.get_db_cursor')
    def test_change_status_notification_error(self, mock_get_cursor, mock_create_notif):
        """TC-MS-010: 狀態變更時通知失敗（不應影響狀態變更）"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            'status': 'pending',
            'user_id': 10
        }
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        # 模擬通知失敗
        mock_create_notif.side_effect = Exception("Notification failed")

        # 執行狀態變更
        result = ModerationService.approve_opinion(opinion_id=1, moderator_id=2)

        # 即使通知失敗，狀態變更仍應成功
        assert result is True

    @patch('services.moderation_service.get_db_cursor')
    def test_change_status_database_error(self, mock_get_cursor):
        """TC-MS-011: 狀態變更時資料庫錯誤"""
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("Database connection lost")
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        result = ModerationService.reject_opinion(
            opinion_id=1,
            moderator_id=2,
            reason="違反規範"
        )

        # 應返回 False
        assert result is False

    @patch('services.moderation_service.NotificationService.create_notification')
    @patch('services.moderation_service.get_db_cursor')
    def test_change_status_different_notification_types(self, mock_get_cursor, mock_create_notif):
        """TC-MS-012: 測試不同狀態變更的通知類型"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            'status': 'pending',
            'user_id': 10
        }
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        # 測試 APPROVED 狀態
        ModerationService.approve_opinion(opinion_id=1, moderator_id=2)
        notif_call = mock_create_notif.call_args[0][0]
        from models.notification import NotificationType
        assert notif_call.type == NotificationType.APPROVED

        # 重置 mock
        mock_create_notif.reset_mock()
        mock_cursor.fetchone.return_value = {
            'status': 'pending',
            'user_id': 10
        }

        # 測試 REJECTED 狀態
        ModerationService.reject_opinion(opinion_id=2, moderator_id=2, reason="測試")
        notif_call = mock_create_notif.call_args[0][0]
        assert notif_call.type == NotificationType.REJECTED


# ==================== Integration Scenarios 測試 ====================

class TestModerationIntegrationScenarios:
    """審核服務整合場景測試"""

    @patch('services.moderation_service.get_db_cursor')
    def test_dashboard_with_active_moderation(self, mock_get_cursor):
        """TC-MS-013: 活躍審核狀態下的儀表板"""
        mock_cursor = MagicMock()

        mock_cursor.fetchone.side_effect = [
            {'total': 500, 'approved': 300, 'pending': 150, 'rejected': 50},
            {'total': 50, 'approved': 30, 'pending': 15, 'rejected': 5}
        ]

        mock_cursor.fetchall.return_value = [
            {'category_id': 1, 'category_name': '交通', 'count': 120},
            {'category_id': 2, 'category_name': '環境', 'count': 100},
            {'category_id': 3, 'category_name': '教育', 'count': 80},
            {'category_id': 4, 'category_name': '醫療', 'count': 60},
            {'category_id': 5, 'category_name': '其他', 'count': 40}
        ]

        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        result = ModerationService.get_dashboard_stats()

        # 驗證數據結構完整性
        assert 'overall' in result
        assert 'today' in result
        assert 'top_categories' in result

        # 驗證今日與總體比例合理
        assert result['today']['total'] <= result['overall']['total']

        # 驗證分類排序
        counts = [cat['count'] for cat in result['top_categories']]
        assert counts == sorted(counts, reverse=True)
