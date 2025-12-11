"""
媒體管理 API 整合測試
測試案例對應: TC-MED-001 ~ TC-MED-010
需求對應: REQ-006 (媒體管理系統)
"""

import pytest
import io
from pathlib import Path
from fastapi.testclient import TestClient
from PIL import Image


class TestMediaUpload:
    """媒體上傳測試類別"""

    def test_upload_image_success(self, test_client: TestClient, auth_headers_user):
        """
        TC-MED-001: 成功上傳圖片
        測試目標: 驗證用戶能夠成功上傳有效的圖片檔案
        優先級: Critical
        """
        # 建立測試圖片
        image = Image.new('RGB', (800, 600), color='red')
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        img_bytes.seek(0)

        # 準備檔案上傳
        files = {
            'file': ('test_image.jpg', img_bytes, 'image/jpeg')
        }

        # 執行上傳請求
        response = test_client.post("/media/upload", files=files, headers=auth_headers_user)

        # 驗證結果
        assert response.status_code == 201, f"期望狀態碼 201，實際 {response.status_code}"

        data = response.json()
        assert "filename" in data, "回應應包含檔案名稱"
        assert data["media_type"] == "image", "媒體類型應為 image"
        assert "url" in data, "回應應包含檔案 URL"
        assert "thumbnail_url" in data, "圖片應包含縮圖 URL"
        assert data["file_size"] > 0, "檔案大小應大於 0"

    def test_upload_image_without_auth(self, test_client: TestClient):
        """
        TC-MED-002: 未認證用戶無法上傳
        測試目標: 驗證未登入用戶無法上傳媒體
        優先級: High
        """
        # 建立測試圖片
        image = Image.new('RGB', (100, 100), color='blue')
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        img_bytes.seek(0)

        files = {'file': ('test.jpg', img_bytes, 'image/jpeg')}

        # 不提供認證標頭
        response = test_client.post("/media/upload", files=files)

        # 驗證結果
        assert response.status_code == 401, "應返回 401 Unauthorized"

    def test_upload_oversized_image(self, test_client: TestClient, auth_headers_user):
        """
        TC-MED-003: 上傳超大檔案失敗
        測試目標: 驗證系統拒絕超過大小限制的圖片
        優先級: High
        """
        # 建立一個大圖片 (模擬超過 10MB)
        # 注意: 實際測試中可能需要調整大小以真正超過限制
        large_image = Image.new('RGB', (5000, 5000), color='green')
        img_bytes = io.BytesIO()
        large_image.save(img_bytes, format='JPEG', quality=100)
        img_bytes.seek(0)

        # 如果生成的圖片小於 10MB，手動創建大於 10MB 的資料
        if len(img_bytes.getvalue()) < 10 * 1024 * 1024:
            # 創建超過 10MB 的資料
            img_bytes = io.BytesIO(b'0' * (10 * 1024 * 1024 + 1000))

        files = {'file': ('large_image.jpg', img_bytes, 'image/jpeg')}

        # 執行上傳請求
        response = test_client.post("/media/upload", files=files, headers=auth_headers_user)

        # 驗證結果
        assert response.status_code == 400, "應返回 400 Bad Request"
        assert "too large" in response.json()["detail"].lower(), "錯誤訊息應提示檔案過大"

    def test_upload_invalid_file_type(self, test_client: TestClient, auth_headers_user):
        """
        TC-MED-004: 上傳無效格式失敗
        測試目標: 驗證系統拒絕不支援的檔案格式
        優先級: High
        """
        # 建立無效格式的檔案 (.txt)
        invalid_file = io.BytesIO(b"This is a text file")

        files = {'file': ('test.txt', invalid_file, 'text/plain')}

        # 執行上傳請求
        response = test_client.post("/media/upload", files=files, headers=auth_headers_user)

        # 驗證結果
        assert response.status_code == 400, "應返回 400 Bad Request"
        assert "unsupported" in response.json()["detail"].lower(), "錯誤訊息應提示不支援的格式"

    def test_upload_png_image(self, test_client: TestClient, auth_headers_user):
        """
        TC-MED-005: 上傳 PNG 格式圖片
        測試目標: 驗證系統支援 PNG 格式
        優先級: Medium
        """
        # 建立 PNG 圖片
        image = Image.new('RGBA', (400, 300), color=(255, 0, 0, 128))
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='PNG')
        img_bytes.seek(0)

        files = {'file': ('test.png', img_bytes, 'image/png')}

        response = test_client.post("/media/upload", files=files, headers=auth_headers_user)

        assert response.status_code == 201, "PNG 上傳應該成功"
        assert response.json()["media_type"] == "image"


class TestMediaRetrieval:
    """媒體檔案獲取測試類別"""

    def test_get_uploaded_image(self, test_client: TestClient, auth_headers_user):
        """
        TC-MED-006: 獲取已上傳的圖片
        測試目標: 驗證能夠獲取已上傳的媒體檔案
        優先級: Critical
        """
        # 先上傳一張圖片
        image = Image.new('RGB', (200, 200), color='yellow')
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        img_bytes.seek(0)

        files = {'file': ('test.jpg', img_bytes, 'image/jpeg')}
        upload_response = test_client.post("/media/upload", files=files, headers=auth_headers_user)

        assert upload_response.status_code == 201

        # 獲取上傳的檔案名稱
        filename = upload_response.json()["filename"]

        # 嘗試獲取檔案
        get_response = test_client.get(f"/media/files/images/{filename}")

        # 驗證結果
        assert get_response.status_code == 200, "應該成功獲取檔案"
        assert get_response.headers["content-type"].startswith("image/"), "Content-Type 應為圖片類型"

    def test_get_nonexistent_file(self, test_client: TestClient):
        """
        TC-MED-007: 獲取不存在的檔案失敗
        測試目標: 驗證請求不存在的檔案返回 404
        優先級: Medium
        """
        # 請求不存在的檔案
        response = test_client.get("/media/files/images/nonexistent.jpg")

        # 驗證結果
        assert response.status_code == 404, "應返回 404 Not Found"
        assert "not found" in response.json()["detail"].lower()

    def test_get_thumbnail(self, test_client: TestClient, auth_headers_user):
        """
        TC-MED-008: 獲取圖片縮圖
        測試目標: 驗證能夠獲取圖片的縮圖
        優先級: Medium
        """
        # 上傳圖片
        image = Image.new('RGB', (1000, 800), color='purple')
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        img_bytes.seek(0)

        files = {'file': ('test.jpg', img_bytes, 'image/jpeg')}
        upload_response = test_client.post("/media/upload", files=files, headers=auth_headers_user)

        assert upload_response.status_code == 201

        filename = upload_response.json()["filename"]

        # 獲取縮圖
        thumbnail_response = test_client.get(f"/media/thumbnails/{filename}")

        # 驗證結果
        assert thumbnail_response.status_code == 200, "應該成功獲取縮圖"


class TestMultipleMediaUpload:
    """多檔案上傳測試類別"""

    def test_upload_multiple_files(self, test_client: TestClient, auth_headers_user):
        """
        TC-MED-009: 批次上傳多個檔案
        測試目標: 驗證能夠一次上傳多個檔案
        優先級: Medium
        """
        # 建立 3 張測試圖片
        files_to_upload = []
        for i in range(3):
            image = Image.new('RGB', (100, 100), color='red')
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            files_to_upload.append(('files', (f'test_{i}.jpg', img_bytes, 'image/jpeg')))

        # 執行批次上傳
        response = test_client.post("/media/upload-multiple", files=files_to_upload, headers=auth_headers_user)

        # 驗證結果
        assert response.status_code == 201, "批次上傳應該成功"

        data = response.json()
        assert "uploaded" in data, "回應應包含上傳成功數量"
        assert data["uploaded"] == 3, "應該成功上傳 3 個檔案"
        assert len(data["files"]) == 3, "應該返回 3 個檔案資訊"

    def test_upload_too_many_files(self, test_client: TestClient, auth_headers_user):
        """
        TC-MED-010: 上傳超過數量限制的檔案
        測試目標: 驗證系統拒絕超過 10 個檔案的批次上傳
        優先級: Medium
        """
        # 建立 11 張圖片（超過限制）
        files_to_upload = []
        for i in range(11):
            image = Image.new('RGB', (50, 50), color='blue')
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='JPEG')
            img_bytes.seek(0)
            files_to_upload.append(('files', (f'test_{i}.jpg', img_bytes, 'image/jpeg')))

        # 執行批次上傳
        response = test_client.post("/media/upload-multiple", files=files_to_upload, headers=auth_headers_user)

        # 驗證結果
        assert response.status_code == 400, "應返回 400 Bad Request"
        assert "maximum" in response.json()["detail"].lower(), "錯誤訊息應提示超過最大數量"


class TestMediaDeletion:
    """媒體檔案刪除測試類別"""

    def test_admin_delete_media(self, test_client: TestClient, auth_headers_admin, auth_headers_user):
        """
        TC-MED-011: 管理員刪除媒體檔案
        測試目標: 驗證管理員能夠刪除媒體檔案
        優先級: High
        """
        # 先以普通用戶上傳圖片
        image = Image.new('RGB', (100, 100), color='orange')
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        img_bytes.seek(0)

        files = {'file': ('test.jpg', img_bytes, 'image/jpeg')}
        upload_response = test_client.post("/media/upload", files=files, headers=auth_headers_user)

        assert upload_response.status_code == 201

        filename = upload_response.json()["filename"]

        # 管理員刪除檔案
        delete_response = test_client.delete(
            f"/media/files/images/{filename}",
            headers=auth_headers_admin
        )

        # 驗證結果
        assert delete_response.status_code == 200, "管理員應該能夠刪除檔案"
        assert "deleted" in delete_response.json()["message"].lower()

        # 驗證檔案已被刪除
        get_response = test_client.get(f"/media/files/images/{filename}")
        assert get_response.status_code == 404, "檔案應已被刪除"

    def test_regular_user_cannot_delete(self, test_client: TestClient, auth_headers_user):
        """
        TC-MED-012: 普通用戶無法刪除檔案
        測試目標: 驗證普通用戶沒有刪除檔案的權限
        優先級: High
        """
        # 上傳檔案
        image = Image.new('RGB', (100, 100), color='cyan')
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        img_bytes.seek(0)

        files = {'file': ('test.jpg', img_bytes, 'image/jpeg')}
        upload_response = test_client.post("/media/upload", files=files, headers=auth_headers_user)

        filename = upload_response.json()["filename"]

        # 嘗試刪除自己上傳的檔案（普通用戶無權限）
        delete_response = test_client.delete(
            f"/media/files/images/{filename}",
            headers=auth_headers_user
        )

        # 驗證結果
        assert delete_response.status_code == 403, "普通用戶應該無權刪除檔案"
        assert "not authorized" in delete_response.json()["detail"].lower()

    def test_delete_nonexistent_file(self, test_client: TestClient, auth_headers_admin):
        """
        TC-MED-013: 刪除不存在的檔案
        測試目標: 驗證刪除不存在的檔案返回 404
        優先級: Low
        """
        # 嘗試刪除不存在的檔案
        response = test_client.delete(
            "/media/files/images/nonexistent.jpg",
            headers=auth_headers_admin
        )

        # 驗證結果
        assert response.status_code == 404, "應返回 404 Not Found"


class TestMediaValidation:
    """媒體驗證測試類別"""

    def test_upload_video_file(self, test_client: TestClient, auth_headers_user):
        """
        TC-MED-014: 上傳影片檔案
        測試目標: 驗證系統支援影片檔案上傳
        優先級: Medium
        """
        # 建立模擬影片檔案 (實際應該是真正的影片檔案)
        video_data = io.BytesIO(b"FAKE_VIDEO_DATA_MP4")

        files = {'file': ('test_video.mp4', video_data, 'video/mp4')}

        response = test_client.post("/media/upload", files=files, headers=auth_headers_user)

        # 驗證結果
        assert response.status_code == 201, "影片上傳應該成功"
        assert response.json()["media_type"] == "video", "媒體類型應為 video"

    def test_upload_audio_file(self, test_client: TestClient, auth_headers_user):
        """
        TC-MED-015: 上傳音訊檔案
        測試目標: 驗證系統支援音訊檔案上傳
        優先級: Medium
        """
        # 建立模擬音訊檔案
        audio_data = io.BytesIO(b"FAKE_AUDIO_DATA_MP3")

        files = {'file': ('test_audio.mp3', audio_data, 'audio/mp3')}

        response = test_client.post("/media/upload", files=files, headers=auth_headers_user)

        # 驗證結果
        assert response.status_code == 201, "音訊上傳應該成功"
        assert response.json()["media_type"] == "audio", "媒體類型應為 audio"


# ==================== 性能測試 ====================

@pytest.mark.slow
class TestMediaPerformance:
    """媒體處理性能測試"""

    def test_concurrent_uploads(self, test_client: TestClient, auth_headers_user):
        """
        測試並發上傳
        測試目標: 驗證系統能處理多個同時上傳請求
        優先級: Medium
        """
        import concurrent.futures

        def upload_image():
            image = Image.new('RGB', (100, 100), color='red')
            img_bytes = io.BytesIO()
            image.save(img_bytes, format='JPEG')
            img_bytes.seek(0)

            files = {'file': ('test.jpg', img_bytes, 'image/jpeg')}
            return test_client.post("/media/upload", files=files, headers=auth_headers_user)

        # 執行 5 個並發上傳
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(upload_image) for _ in range(5)]
            results = [future.result() for future in futures]

        # 驗證所有請求都成功
        success_count = sum(1 for r in results if r.status_code == 201)
        assert success_count == 5, f"應該有 5 個成功上傳，實際 {success_count}"
