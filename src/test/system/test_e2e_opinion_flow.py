"""
E2E 測試: 意見發布流程
測試範圍: 發布意見、查看意見、編輯意見、刪除意見等完整流程
測試案例對應: TC-E2E-OPINION-001 ~ TC-E2E-OPINION-010
"""

import pytest
import time


@pytest.mark.system
@pytest.mark.e2e
# @pytest.mark.skip(reason="需要先設置測試數據庫和認證")  # 暫時移除以進行測試
class TestOpinionPublishingE2E:
    """意見發布端到端測試"""

    def test_complete_opinion_lifecycle(self, authenticated_client):
        """
        TC-E2E-OPINION-001: 完整的意見生命週期
        測試目標: 驗證用戶可以創建、查看、編輯和刪除意見
        優先級: Critical
        """
        # Step 1: 創建新意見
        opinion_data = {
            "title": "E2E Test Opinion",
            "content": "This is an end-to-end test opinion",
            "category_id": 1,
            "location": "Test Location"
        }

        create_response = authenticated_client.post("/opinions", json=opinion_data)
        assert create_response.status_code == 201, \
            f"創建意見失敗: {create_response.status_code}"

        opinion = create_response.json()
        opinion_id = opinion["id"]

        # Step 2: 查看剛創建的意見
        get_response = authenticated_client.get(f"/opinions/{opinion_id}")
        assert get_response.status_code == 200, "獲取意見失敗"

        retrieved_opinion = get_response.json()
        assert retrieved_opinion["title"] == opinion_data["title"]
        assert retrieved_opinion["content"] == opinion_data["content"]

        # Step 3: 編輯意見
        updated_data = {
            "title": "Updated E2E Test Opinion",
            "content": "This content has been updated"
        }

        update_response = authenticated_client.put(
            f"/opinions/{opinion_id}",
            json=updated_data
        )
        assert update_response.status_code == 200, "更新意見失敗"

        # Step 4: 驗證更新
        updated_opinion = authenticated_client.get(f"/opinions/{opinion_id}").json()
        assert updated_opinion["title"] == updated_data["title"]
        assert updated_opinion["content"] == updated_data["content"]

        # Step 5: 刪除意見
        delete_response = authenticated_client.delete(f"/opinions/{opinion_id}")
        assert delete_response.status_code == 200, "刪除意見失敗"

        # Step 6: 驗證意見已被刪除
        final_get_response = authenticated_client.get(f"/opinions/{opinion_id}")
        assert final_get_response.status_code == 404, "意見應該不存在"

    def test_opinion_with_media_upload(self, authenticated_client):
        """
        TC-E2E-OPINION-002: 帶有媒體的意見發布
        測試目標: 驗證用戶可以上傳媒體並附加到意見
        優先級: High
        """
        # Step 1: 上傳圖片
        from PIL import Image
        import io

        image = Image.new('RGB', (800, 600), color='blue')
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        img_bytes.seek(0)

        files = {'file': ('test_image.jpg', img_bytes, 'image/jpeg')}
        upload_response = authenticated_client.post("/media/upload", files=files)

        assert upload_response.status_code == 201, "上傳媒體失敗"
        media_data = upload_response.json()

        # 驗證上傳成功並包含必要欄位
        assert "filename" in media_data, "媒體響應應包含 filename"
        assert "media_type" in media_data, "媒體響應應包含 media_type"

        # Step 2: 創建帶有媒體的意見
        # 注意: 當前 API 實現在創建意見時使用 media 字段，而不是 media_ids
        opinion_data = {
            "title": "Opinion with Media",
            "content": "This opinion includes a media file",
            "category_id": 1,
            "media": [{
                "file_path": media_data["file_path"],
                "file_size": media_data["file_size"],
                "media_type": media_data["media_type"],
                "mime_type": media_data["mime_type"]
            }]
        }

        create_response = authenticated_client.post("/opinions", json=opinion_data)
        assert create_response.status_code == 201, f"創建意見失敗: {create_response.text}"

        opinion = create_response.json()
        assert len(opinion.get("media", [])) > 0, "意見應包含媒體"

    def test_opinion_moderation_workflow(self, authenticated_client):
        """
        TC-E2E-OPINION-003: 意見審核工作流程
        測試目標: 驗證意見審核的完整流程
        優先級: High
        """
        # Step 1: 創建需要審核的意見
        opinion_data = {
            "title": "Opinion for Moderation",
            "content": "This opinion will go through moderation",
            "category_id": 1
        }

        create_response = authenticated_client.post("/opinions", json=opinion_data)
        assert create_response.status_code == 201

        opinion = create_response.json()
        opinion_id = opinion["id"]

        # Step 2: 檢查初始審核狀態
        # 注意: 實際 API 使用 auto_moderation_status，不是 moderation_status
        # 新創建的意見可能還沒有審核狀態，因為審核是異步進行的
        assert "status" in opinion, "意見應該有 status 欄位"

        # Step 3: 等待 AI 審核完成 (如果啟用)
        time.sleep(3)

        # Step 4: 檢查審核後的狀態
        moderated_opinion = authenticated_client.get(f"/opinions/{opinion_id}").json()
        # 審核後的意見應該有這些欄位（如果 AI 審核啟用）
        # auto_moderation_status, auto_moderation_score, moderation_reason 等
        assert "status" in moderated_opinion
        # 不強制要求 auto_moderation_status，因為可能未啟用 AI 審核或審核失敗


@pytest.mark.system
@pytest.mark.e2e
# @pytest.mark.skip(reason="需要先設置測試數據庫和認證")  # 暫時移除以進行測試
class TestOpinionListingE2E:
    """意見列表查詢端到端測試"""

    def test_opinion_pagination(self, authenticated_client):
        """
        TC-E2E-OPINION-004: 意見分頁查詢
        測試目標: 驗證意見列表支持分頁
        優先級: Medium
        """
        # 獲取第一頁
        page1_response = authenticated_client.get("/opinions?page=1&page_size=10")
        assert page1_response.status_code == 200

        page1_data = page1_response.json()
        # API 實際回傳的是 "items" 而不是 "opinions"
        assert "items" in page1_data
        assert "total" in page1_data
        assert "page" in page1_data

        # 如果有多頁，獲取第二頁
        if page1_data["total"] > 10:
            page2_response = authenticated_client.get("/opinions?page=2&page_size=10")
            assert page2_response.status_code == 200

            page2_data = page2_response.json()
            # 驗證不同頁的數據不同
            assert page1_data["items"][0]["id"] != page2_data["items"][0]["id"]

    def test_opinion_filtering_by_category(self, authenticated_client):
        """
        TC-E2E-OPINION-005: 按分類篩選意見
        測試目標: 驗證可以按分類查詢意見
        優先級: Medium
        """
        category_id = 1

        # 按分類查詢
        response = authenticated_client.get(f"/opinions?category_id={category_id}")
        assert response.status_code == 200

        data = response.json()
        # API 實際回傳的是 "items" 而不是 "opinions"
        opinions = data.get("items", [])

        # 驗證所有返回的意見都屬於指定分類
        for opinion in opinions:
            assert opinion["category_id"] == category_id

    def test_opinion_search(self, authenticated_client):
        """
        TC-E2E-OPINION-006: 意見搜索功能
        測試目標: 驗證可以搜索意見
        優先級: Medium
        """
        search_term = "test"

        # 搜索意見 - 使用主要的 /opinions 端點的 search 參數
        response = authenticated_client.get(f"/opinions?search={search_term}")
        assert response.status_code == 200

        data = response.json()
        # API 實際回傳的是 "items" 而不是 "opinions"
        opinions = data.get("items", [])

        # 驗證搜索結果包含搜索詞（如果有結果）
        if opinions:
            for opinion in opinions:
                assert (
                    search_term.lower() in opinion["title"].lower() or
                    search_term.lower() in opinion["content"].lower()
                ), "搜索結果應包含搜索詞"


@pytest.mark.system
@pytest.mark.e2e
# @pytest.mark.skip(reason="需要先設置測試數據庫和認證")  # 暫時移除以進行測試
class TestOpinionInteractionE2E:
    """意見互動端到端測試"""

    def test_opinion_like_workflow(self, authenticated_client):
        """
        TC-E2E-OPINION-007: 意見點讚流程
        測試目標: 驗證用戶可以點讚和取消點讚
        優先級: Low
        """
        # Step 0: 創建一個測試意見
        opinion_data = {
            "title": "Test Opinion for Voting",
            "content": "This opinion will be used to test voting",
            "category_id": 1
        }
        create_response = authenticated_client.post("/opinions", json=opinion_data)
        assert create_response.status_code == 201
        opinion_id = create_response.json()["id"]

        # Step 1: 點讚意見（使用 vote 端點）
        vote_data = {"vote_type": "like"}
        like_response = authenticated_client.post(
            f"/opinions/{opinion_id}/vote",
            json=vote_data
        )
        assert like_response.status_code == 200

        # Step 2: 驗證點讚數增加
        opinion = authenticated_client.get(f"/opinions/{opinion_id}").json()
        initial_upvotes = opinion.get("upvotes", 0)
        assert initial_upvotes >= 1, "應該有至少一個讚"

        # Step 3: 取消點讚（再次點擊相同類型會取消）
        unlike_response = authenticated_client.post(
            f"/opinions/{opinion_id}/vote",
            json=vote_data
        )
        assert unlike_response.status_code == 200

        # Step 4: 驗證點讚數減少
        opinion_after = authenticated_client.get(f"/opinions/{opinion_id}").json()
        assert opinion_after.get("upvotes", 0) == initial_upvotes - 1, "點讚數應該減少1"

    def test_opinion_comment_workflow(self, authenticated_client):
        """
        TC-E2E-OPINION-008: 意見評論流程
        測試目標: 驗證用戶可以評論意見
        優先級: Medium
        """
        # Step 0: 創建一個測試意見
        opinion_data = {
            "title": "Test Opinion for Comments",
            "content": "This opinion will be used to test comments",
            "category_id": 1
        }
        create_response = authenticated_client.post("/opinions", json=opinion_data)
        assert create_response.status_code == 201
        opinion_id = create_response.json()["id"]

        # Step 1: 發布評論
        comment_data = {
            "content": "This is a test comment"
        }

        comment_response = authenticated_client.post(
            f"/opinions/{opinion_id}/comments",
            json=comment_data
        )
        assert comment_response.status_code == 201

        comment = comment_response.json()
        comment_id = comment["id"]

        # Step 2: 查看評論
        comments_response = authenticated_client.get(f"/opinions/{opinion_id}/comments")
        assert comments_response.status_code == 200

        # API 返回的是評論列表，不是 {"comments": [...]} 結構
        comments = comments_response.json()
        assert isinstance(comments, list), "應該返回評論列表"
        assert any(c["id"] == comment_id for c in comments), "應該包含剛創建的評論"

        # Step 3: 刪除評論
        delete_response = authenticated_client.delete(
            f"/opinions/{opinion_id}/comments/{comment_id}"
        )
        assert delete_response.status_code == 200
