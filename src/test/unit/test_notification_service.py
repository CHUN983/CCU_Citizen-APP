"""
Notification Service 單元測試
測試目標: NotificationService 和 MilestoneNotificationService 的所有核心功能
測試策略: Mock 資料庫操作，專注測試業務邏輯
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
from services.notification_service import (
    NotificationService,
    MilestoneNotificationService,
    calculate_next_milestone
)
from models.notification import NotificationCreate, NotificationType


# ==================== 輔助函數測試 ====================

class TestCalculateNextMilestone:
    """測試里程碑計算函數"""

    def test_calculate_milestone_from_zero(self):
        """TC-NS-001: 從 0 開始計算下一個里程碑"""
        assert calculate_next_milestone(0) == 1

    def test_calculate_milestone_from_one(self):
        """TC-NS-002: 從 1 計算下一個里程碑"""
        assert calculate_next_milestone(1) == 2

    def test_calculate_milestone_from_power_of_two(self):
        """TC-NS-003: 從 2 的冪次計算下一個里程碑"""
        assert calculate_next_milestone(2) == 4
        assert calculate_next_milestone(4) == 8
        assert calculate_next_milestone(8) == 16
        assert calculate_next_milestone(16) == 32
        assert calculate_next_milestone(32) == 64

    def test_calculate_milestone_from_non_power_of_two(self):
        """TC-NS-004: 從非 2 的冪次計算下一個里程碑"""
        assert calculate_next_milestone(3) == 4
        assert calculate_next_milestone(5) == 8
        assert calculate_next_milestone(15) == 16
        assert calculate_next_milestone(17) == 32

    def test_calculate_milestone_large_numbers(self):
        """TC-NS-005: 測試大數值的里程碑計算"""
        assert calculate_next_milestone(100) == 128
        assert calculate_next_milestone(256) == 512
        assert calculate_next_milestone(1000) == 1024


# ==================== NotificationService 測試 ====================

class TestGetUserNotifications:
    """測試獲取用戶通知功能"""

    @patch('services.notification_service.get_db_cursor')
    def test_get_all_notifications_success(self, mock_get_cursor):
        """TC-NS-006: 成功獲取所有通知"""
        # 準備 mock 數據
        mock_notifications = [
            {
                'id': 1,
                'user_id': 1,
                'opinion_id': 10,
                'type': 'approved',
                'title': '通知 1',
                'content': '內容 1',
                'is_read': False,
                'created_at': '2025-10-24 10:00:00'
            },
            {
                'id': 2,
                'user_id': 1,
                'opinion_id': 20,
                'type': 'comment',
                'title': '通知 2',
                'content': '內容 2',
                'is_read': True,
                'created_at': '2025-10-24 11:00:00'
            }
        ]

        # 設置 mock cursor
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = mock_notifications
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        # 執行測試
        result = NotificationService.get_user_notifications(user_id=1, unread_only=False)

        # 驗證結果
        assert len(result) == 2
        assert result[0].id == 1
        assert result[0].title == '通知 1'
        assert result[1].id == 2
        assert result[1].is_read is True

        # 驗證 SQL 查詢
        executed_query = mock_cursor.execute.call_args[0][0]
        assert 'SELECT * FROM notifications' in executed_query
        assert 'WHERE user_id = %s' in executed_query
        assert 'ORDER BY created_at DESC LIMIT 50' in executed_query

    @patch('services.notification_service.get_db_cursor')
    def test_get_unread_notifications_only(self, mock_get_cursor):
        """TC-NS-007: 僅獲取未讀通知"""
        mock_notifications = [
            {
                'id': 1,
                'user_id': 1,
                'opinion_id': 10,
                'type': 'approved',
                'title': '未讀通知',
                'content': '內容',
                'is_read': False,
                'created_at': '2025-10-24 10:00:00'
            }
        ]

        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = mock_notifications
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        # 執行測試 - 僅未讀
        result = NotificationService.get_user_notifications(user_id=1, unread_only=True)

        # 驗證結果
        assert len(result) == 1
        assert result[0].is_read is False

        # 驗證 SQL 包含未讀條件
        executed_query = mock_cursor.execute.call_args[0][0]
        assert 'AND is_read = FALSE' in executed_query

    @patch('services.notification_service.get_db_cursor')
    def test_get_notifications_empty_result(self, mock_get_cursor):
        """TC-NS-008: 獲取空通知列表"""
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = []
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        result = NotificationService.get_user_notifications(user_id=999)

        assert result == []
        assert isinstance(result, list)


class TestMarkAsRead:
    """測試標記通知為已讀功能"""

    @patch('services.notification_service.get_db_cursor')
    def test_mark_as_read_success(self, mock_get_cursor):
        """TC-NS-009: 成功標記通知為已讀"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {'id': 1}  # 通知存在
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        result = NotificationService.mark_as_read(notification_id=1, user_id=1)

        assert result is True

        # 驗證執行了 UPDATE 和 SELECT
        assert mock_cursor.execute.call_count == 2
        update_query = mock_cursor.execute.call_args_list[0][0][0]
        assert 'UPDATE notifications' in update_query
        assert 'SET is_read = TRUE' in update_query
        assert 'WHERE id = %s AND user_id = %s' in update_query

    @patch('services.notification_service.get_db_cursor')
    def test_mark_as_read_notification_not_found(self, mock_get_cursor):
        """TC-NS-010: 標記不存在的通知"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None  # 通知不存在
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        result = NotificationService.mark_as_read(notification_id=999, user_id=1)

        assert result is False

    @patch('services.notification_service.get_db_cursor')
    def test_mark_as_read_idempotent(self, mock_get_cursor):
        """TC-NS-011: 測試標記為已讀的冪等性（重複標記已讀通知）"""
        mock_cursor = MagicMock()
        mock_cursor.rowcount = 0  # UPDATE 沒有修改任何行（已經是已讀）
        mock_cursor.fetchone.return_value = {'id': 1}  # 但通知存在
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        result = NotificationService.mark_as_read(notification_id=1, user_id=1)

        # 即使已經是已讀，也應該返回 True（冪等性）
        assert result is True

    @patch('services.notification_service.get_db_cursor')
    def test_mark_as_read_wrong_user(self, mock_get_cursor):
        """TC-NS-012: 嘗試標記其他用戶的通知"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = None  # user_id 不匹配，查詢不到
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        result = NotificationService.mark_as_read(notification_id=1, user_id=999)

        assert result is False


# ==================== MilestoneNotificationService 測試 ====================

@pytest.mark.no_db
class TestCheckAndNotifyMilestone:
    """測試里程碑通知功能"""

    @patch('services.notification_service.NotificationService.create_notification')
    @patch('utils.database.get_db_cursor')
    def test_first_milestone_like(self, mock_get_cursor, mock_create_notif):
        """TC-NS-013: 首次達到點讚里程碑（1 個讚）"""
        mock_cursor = MagicMock()
        # 第一次查詢：沒有里程碑記錄
        mock_cursor.fetchone.return_value = None
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        result = MilestoneNotificationService.check_and_notify_milestone(
            opinion_id=1,
            milestone_type='like',
            current_count=1,
            opinion_owner_id=10
        )

        # 驗證結果
        assert result is True

        # 驗證插入了初始里程碑記錄
        insert_call = mock_cursor.execute.call_args_list[1]
        assert 'INSERT INTO notification_milestones' in insert_call[0][0]

        # 驗證發送了通知
        assert mock_create_notif.called
        notif_arg = mock_create_notif.call_args[0][0]
        assert notif_arg.user_id == 10
        assert notif_arg.opinion_id == 1
        assert '1' in notif_arg.title
        assert '按讚' in notif_arg.title

        # 驗證更新了里程碑記錄
        update_call = mock_cursor.execute.call_args_list[-1]
        assert 'UPDATE notification_milestones' in update_call[0][0]

    @patch('services.notification_service.NotificationService.create_notification')
    @patch('utils.database.get_db_cursor')
    def test_next_milestone_comment(self, mock_get_cursor, mock_create_notif):
        """TC-NS-014: 達到下一個留言里程碑（4 則留言）"""
        mock_cursor = MagicMock()
        # 已有里程碑記錄：上次通知在 2，下一個里程碑是 4
        mock_cursor.fetchone.return_value = {
            'last_notified_count': 2,
            'next_milestone': 4
        }
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        result = MilestoneNotificationService.check_and_notify_milestone(
            opinion_id=2,
            milestone_type='comment',
            current_count=4,
            opinion_owner_id=20
        )

        # 驗證結果
        assert result is True

        # 驗證發送了通知
        assert mock_create_notif.called
        notif_arg = mock_create_notif.call_args[0][0]
        assert '4' in notif_arg.title
        assert '留言' in notif_arg.title

        # 驗證更新了里程碑：下一個應該是 8
        update_call = mock_cursor.execute.call_args_list[-1]
        update_params = update_call[0][1]
        assert update_params[0] == 4  # last_notified_count
        assert update_params[1] == 8  # next_milestone

    @patch('services.notification_service.NotificationService.create_notification')
    @patch('utils.database.get_db_cursor')
    def test_not_reached_milestone_yet(self, mock_get_cursor, mock_create_notif):
        """TC-NS-015: 尚未達到下一個里程碑"""
        mock_cursor = MagicMock()
        mock_cursor.fetchone.return_value = {
            'last_notified_count': 2,
            'next_milestone': 4
        }
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        result = MilestoneNotificationService.check_and_notify_milestone(
            opinion_id=1,
            milestone_type='like',
            current_count=3,  # 尚未達到 4
            opinion_owner_id=10
        )

        # 驗證結果
        assert result is False

        # 驗證沒有發送通知
        assert not mock_create_notif.called

        # 驗證沒有更新里程碑記錄
        # 只有 1 次 SELECT 查詢，沒有 UPDATE
        assert mock_cursor.execute.call_count == 1

    @patch('services.notification_service.NotificationService.create_notification')
    @patch('utils.database.get_db_cursor')
    def test_milestone_progression(self, mock_get_cursor, mock_create_notif):
        """TC-NS-016: 測試里程碑級數（1→2→4→8→16）"""
        mock_cursor = MagicMock()

        # 模擬從 8 到 16 的里程碑
        mock_cursor.fetchone.return_value = {
            'last_notified_count': 8,
            'next_milestone': 16
        }
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        result = MilestoneNotificationService.check_and_notify_milestone(
            opinion_id=1,
            milestone_type='like',
            current_count=16,
            opinion_owner_id=10
        )

        assert result is True

        # 驗證下一個里程碑是 32
        update_call = mock_cursor.execute.call_args_list[-1]
        update_params = update_call[0][1]
        assert update_params[1] == 32  # next_milestone

    @patch('utils.database.get_db_cursor')
    def test_milestone_database_error(self, mock_get_cursor):
        """TC-NS-017: 資料庫錯誤處理"""
        mock_cursor = MagicMock()
        mock_cursor.execute.side_effect = Exception("Database error")
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        result = MilestoneNotificationService.check_and_notify_milestone(
            opinion_id=1,
            milestone_type='like',
            current_count=1,
            opinion_owner_id=10
        )

        # 發生錯誤時應返回 False
        assert result is False


# ==================== 整合場景測試 ====================

@pytest.mark.no_db
class TestNotificationIntegrationScenarios:
    """通知服務整合場景測試"""

    @patch('services.notification_service.NotificationService.create_notification')
    @patch('utils.database.get_db_cursor')
    def test_like_milestone_progression_scenario(self, mock_get_cursor, mock_create_notif):
        """TC-NS-018: 完整的點讚里程碑級數場景"""
        mock_cursor = MagicMock()
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        # 場景 1: 第 1 個讚
        mock_cursor.fetchone.return_value = None
        result1 = MilestoneNotificationService.check_and_notify_milestone(
            opinion_id=1, milestone_type='like', current_count=1, opinion_owner_id=10
        )
        assert result1 is True

        # 場景 2: 第 2 個讚
        mock_cursor.fetchone.return_value = {'last_notified_count': 1, 'next_milestone': 2}
        result2 = MilestoneNotificationService.check_and_notify_milestone(
            opinion_id=1, milestone_type='like', current_count=2, opinion_owner_id=10
        )
        assert result2 is True

        # 場景 3: 第 3 個讚（未達到 4）
        mock_cursor.fetchone.return_value = {'last_notified_count': 2, 'next_milestone': 4}
        result3 = MilestoneNotificationService.check_and_notify_milestone(
            opinion_id=1, milestone_type='like', current_count=3, opinion_owner_id=10
        )
        assert result3 is False

    @patch('services.notification_service.get_db_cursor')
    def test_get_and_mark_workflow(self, mock_get_cursor):
        """TC-NS-019: 獲取通知並標記為已讀的完整流程"""
        mock_cursor = MagicMock()

        # 步驟 1: 獲取未讀通知
        mock_cursor.fetchall.return_value = [
            {
                'id': 1,
                'user_id': 1,
                'opinion_id': 10,
                'type': 'approved',
                'title': '通知',
                'content': '內容',
                'is_read': False,
                'created_at': '2025-10-24 10:00:00'
            }
        ]
        mock_get_cursor.return_value.__enter__.return_value = mock_cursor

        notifications = NotificationService.get_user_notifications(user_id=1, unread_only=True)
        assert len(notifications) == 1
        assert notifications[0].is_read is False

        # 步驟 2: 標記為已讀
        mock_cursor.fetchone.return_value = {'id': 1}
        result = NotificationService.mark_as_read(notification_id=1, user_id=1)
        assert result is True
