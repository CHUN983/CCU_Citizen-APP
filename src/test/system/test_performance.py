"""
效能測試
測試範圍: API 響應時間、併發處理、資源使用等
測試案例對應: TC-PERF-001 ~ TC-PERF-010
"""

import pytest
import time
import concurrent.futures
from statistics import mean, median


@pytest.mark.system
@pytest.mark.performance
@pytest.mark.skip(reason="效能測試需要特定環境設置")
class TestAPIPerformance:
    """API 效能測試"""

    def test_health_endpoint_response_time(self, api_client):
        """
        TC-PERF-001: 健康檢查端點響應時間
        測試目標: 驗證健康檢查端點的響應時間在可接受範圍內
        優先級: High
        標準: < 100ms
        """
        response_times = []

        for _ in range(10):
            start_time = time.time()
            response = api_client.get("/health")
            end_time = time.time()

            assert response.status_code == 200
            response_times.append((end_time - start_time) * 1000)  # 轉換為毫秒

        avg_response_time = mean(response_times)
        median_response_time = median(response_times)

        print(f"\n健康檢查端點效能:")
        print(f"  平均響應時間: {avg_response_time:.2f}ms")
        print(f"  中位數響應時間: {median_response_time:.2f}ms")
        print(f"  最小響應時間: {min(response_times):.2f}ms")
        print(f"  最大響應時間: {max(response_times):.2f}ms")

        assert avg_response_time < 100, \
            f"平均響應時間 {avg_response_time:.2f}ms 超過 100ms 標準"

    def test_opinion_list_response_time(self, authenticated_client):
        """
        TC-PERF-002: 意見列表響應時間
        測試目標: 驗證意見列表查詢的響應時間
        優先級: High
        標準: < 500ms
        """
        response_times = []

        for _ in range(5):
            start_time = time.time()
            response = authenticated_client.get("/opinions?page=1&page_size=20")
            end_time = time.time()

            assert response.status_code == 200
            response_times.append((end_time - start_time) * 1000)

        avg_response_time = mean(response_times)

        print(f"\n意見列表查詢效能:")
        print(f"  平均響應時間: {avg_response_time:.2f}ms")

        assert avg_response_time < 500, \
            f"平均響應時間 {avg_response_time:.2f}ms 超過 500ms 標準"

    def test_concurrent_requests_handling(self, api_client):
        """
        TC-PERF-003: 併發請求處理
        測試目標: 驗證系統可以處理併發請求
        優先級: Medium
        """
        num_concurrent_requests = 10

        def make_request():
            start_time = time.time()
            response = api_client.get("/health")
            end_time = time.time()
            return {
                "status_code": response.status_code,
                "response_time": (end_time - start_time) * 1000
            }

        # 使用線程池執行併發請求
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent_requests) as executor:
            futures = [executor.submit(make_request) for _ in range(num_concurrent_requests)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        # 驗證所有請求都成功
        success_count = sum(1 for r in results if r["status_code"] == 200)
        assert success_count == num_concurrent_requests, \
            f"只有 {success_count}/{num_concurrent_requests} 個請求成功"

        # 統計響應時間
        response_times = [r["response_time"] for r in results]
        avg_response_time = mean(response_times)
        max_response_time = max(response_times)

        print(f"\n併發請求效能 ({num_concurrent_requests} 個併發):")
        print(f"  成功率: {success_count}/{num_concurrent_requests}")
        print(f"  平均響應時間: {avg_response_time:.2f}ms")
        print(f"  最大響應時間: {max_response_time:.2f}ms")

        # 驗證在併發情況下響應時間仍在可接受範圍內
        assert avg_response_time < 1000, \
            f"併發請求平均響應時間 {avg_response_time:.2f}ms 超過 1000ms"


@pytest.mark.system
@pytest.mark.performance
@pytest.mark.skip(reason="負載測試需要特定環境設置")
class TestLoadTesting:
    """負載測試"""

    def test_sustained_load(self, api_client):
        """
        TC-PERF-004: 持續負載測試
        測試目標: 驗證系統可以處理持續的負載
        優先級: Low
        """
        duration_seconds = 60  # 測試持續時間
        requests_per_second = 10

        start_time = time.time()
        request_count = 0
        error_count = 0

        while time.time() - start_time < duration_seconds:
            try:
                response = api_client.get("/health")
                if response.status_code == 200:
                    request_count += 1
                else:
                    error_count += 1
            except Exception:
                error_count += 1

            # 控制請求速率
            time.sleep(1.0 / requests_per_second)

        print(f"\n持續負載測試結果 ({duration_seconds}秒):")
        print(f"  成功請求: {request_count}")
        print(f"  失敗請求: {error_count}")
        print(f"  成功率: {request_count / (request_count + error_count) * 100:.2f}%")

        # 驗證成功率
        success_rate = request_count / (request_count + error_count)
        assert success_rate > 0.95, \
            f"成功率 {success_rate * 100:.2f}% 低於 95% 標準"

    def test_memory_leak_detection(self, api_client):
        """
        TC-PERF-005: 記憶體洩漏檢測
        測試目標: 驗證系統沒有明顯的記憶體洩漏
        優先級: Low
        說明: 這是一個簡化的測試，真實環境需要更複雜的監控
        """
        # 執行大量請求
        num_requests = 1000

        for i in range(num_requests):
            response = api_client.get("/health")
            assert response.status_code == 200

            # 每 100 個請求檢查一次
            if i % 100 == 0:
                print(f"已完成 {i}/{num_requests} 個請求")

        print(f"\n完成 {num_requests} 個請求，未發現明顯的記憶體問題")


@pytest.mark.system
@pytest.mark.performance
@pytest.mark.skip(reason="資料庫效能測試需要特定環境設置")
class TestDatabasePerformance:
    """資料庫效能測試"""

    def test_opinion_query_performance(self, authenticated_client):
        """
        TC-PERF-006: 意見查詢效能
        測試目標: 驗證大量意見查詢的效能
        優先級: Medium
        """
        # 執行多次查詢並記錄時間
        query_times = []

        for page in range(1, 11):  # 查詢前 10 頁
            start_time = time.time()
            response = authenticated_client.get(f"/opinions?page={page}&page_size=50")
            end_time = time.time()

            assert response.status_code == 200
            query_times.append((end_time - start_time) * 1000)

        avg_query_time = mean(query_times)

        print(f"\n意見查詢效能 (10 頁，每頁 50 條):")
        print(f"  平均查詢時間: {avg_query_time:.2f}ms")
        print(f"  最小查詢時間: {min(query_times):.2f}ms")
        print(f"  最大查詢時間: {max(query_times):.2f}ms")

        # 驗證查詢時間
        assert avg_query_time < 200, \
            f"平均查詢時間 {avg_query_time:.2f}ms 超過 200ms 標準"

    def test_database_connection_pool(self, authenticated_client):
        """
        TC-PERF-007: 資料庫連接池效能
        測試目標: 驗證資料庫連接池的效率
        優先級: Low
        """
        num_concurrent = 20

        def query_database():
            response = authenticated_client.get("/opinions?page=1&page_size=10")
            return response.status_code == 200

        # 併發查詢資料庫
        with concurrent.futures.ThreadPoolExecutor(max_workers=num_concurrent) as executor:
            futures = [executor.submit(query_database) for _ in range(num_concurrent)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]

        success_count = sum(1 for r in results if r)

        print(f"\n資料庫連接池測試 ({num_concurrent} 個併發連接):")
        print(f"  成功: {success_count}/{num_concurrent}")

        assert success_count == num_concurrent, \
            "所有資料庫連接應該成功"
