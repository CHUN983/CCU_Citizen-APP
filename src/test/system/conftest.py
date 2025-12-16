"""
系統測試 Fixtures 配置
提供 E2E 測試所需的環境設置
"""

import pytest
import time
import subprocess
import requests
from pathlib import Path


@pytest.fixture(scope="session")
def fastapi_server():
    """
    啟動 FastAPI 伺服器用於系統測試

    Yields:
        str: 伺服器 URL
    """
    # 啟動 FastAPI 伺服器
    process = subprocess.Popen(
        ["python3", "-m", "uvicorn", "src.main.python.core.app:app", "--host", "0.0.0.0", "--port", "8001"],
        cwd=Path(__file__).parent.parent.parent.parent,
        env={"PYTHONPATH": "src/main/python"}
    )

    # 等待伺服器啟動
    server_url = "http://localhost:8001"
    max_retries = 30
    for i in range(max_retries):
        try:
            response = requests.get(f"{server_url}/health", timeout=1)
            if response.status_code == 200:
                break
        except requests.exceptions.RequestException:
            if i == max_retries - 1:
                process.kill()
                raise RuntimeError("FastAPI server failed to start")
            time.sleep(1)

    yield server_url

    # 清理: 關閉伺服器
    process.terminate()
    process.wait(timeout=5)


@pytest.fixture(scope="function")
def api_client(fastapi_server):
    """
    創建 API 客戶端

    Args:
        fastapi_server: FastAPI 伺服器 URL

    Returns:
        dict: 包含 base_url 和 helper 方法的字典
    """
    class APIClient:
        def __init__(self, base_url):
            self.base_url = base_url
            self.token = None

        def login(self, username: str, password: str):
            """登入並保存 token"""
            response = requests.post(
                f"{self.base_url}/auth/login",
                json={"username": username, "password": password}
            )
            if response.status_code == 200:
                self.token = response.json()["access_token"]
            return response

        def get_headers(self):
            """獲取包含認證的 headers"""
            if self.token:
                return {"Authorization": f"Bearer {self.token}"}
            return {}

        def get(self, endpoint: str, **kwargs):
            """發送 GET 請求"""
            headers = kwargs.pop("headers", {})
            headers.update(self.get_headers())
            return requests.get(f"{self.base_url}{endpoint}", headers=headers, **kwargs)

        def post(self, endpoint: str, **kwargs):
            """發送 POST 請求"""
            headers = kwargs.pop("headers", {})
            headers.update(self.get_headers())
            return requests.post(f"{self.base_url}{endpoint}", headers=headers, **kwargs)

        def put(self, endpoint: str, **kwargs):
            """發送 PUT 請求"""
            headers = kwargs.pop("headers", {})
            headers.update(self.get_headers())
            return requests.put(f"{self.base_url}{endpoint}", headers=headers, **kwargs)

        def delete(self, endpoint: str, **kwargs):
            """發送 DELETE 請求"""
            headers = kwargs.pop("headers", {})
            headers.update(self.get_headers())
            return requests.delete(f"{self.base_url}{endpoint}", headers=headers, **kwargs)

    return APIClient(fastapi_server)


@pytest.fixture(scope="function")
def test_user_credentials():
    """
    測試用戶憑證

    Returns:
        dict: 包含測試用戶的用戶名和密碼
    """
    return {
        "username": "testuser",
        "password": "TestPassword123!"
    }


@pytest.fixture(scope="function")
def authenticated_client(api_client, test_user_credentials):
    """
    已認證的 API 客戶端

    Args:
        api_client: API 客戶端
        test_user_credentials: 測試用戶憑證

    Returns:
        APIClient: 已登入的 API 客戶端
    """
    # 嘗試登入
    response = api_client.login(
        test_user_credentials["username"],
        test_user_credentials["password"]
    )

    # 如果登入失敗，先註冊用戶
    if response.status_code != 200:
        # 註冊新用戶
        register_data = {
            "username": test_user_credentials["username"],
            "email": f"{test_user_credentials['username']}@test.com",
            "password": test_user_credentials["password"],
            "role": "citizen"
        }

        register_response = api_client.post("/auth/register", json=register_data)

        # 如果註冊成功或用戶已存在，再次嘗試登入
        if register_response.status_code in [200, 201, 400]:  # 400 可能表示用戶已存在
            response = api_client.login(
                test_user_credentials["username"],
                test_user_credentials["password"]
            )

        # 如果還是失敗，拋出錯誤
        if response.status_code != 200:
            raise RuntimeError(
                f"無法登入測試用戶: {response.status_code} - {response.text}"
            )

    return api_client
