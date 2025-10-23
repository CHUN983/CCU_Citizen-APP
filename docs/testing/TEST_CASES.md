# 市民參與城市規劃 APP - 測試案例文件 (Test Cases)

**文件版本**: 1.0
**建立日期**: 2025-10-24
**專案名稱**: 市民參與城市規劃 APP
**測試負責人**: V&V Team

---

## 目錄
1. [認證系統測試案例 (AUTH)](#1-認證系統測試案例-auth)
2. [意見系統測試案例 (OPINION)](#2-意見系統測試案例-opinion)
3. [媒體系統測試案例 (MEDIA)](#3-媒體系統測試案例-media)
4. [管理系統測試案例 (ADMIN)](#4-管理系統測試案例-admin)
5. [前端測試案例 (FRONTEND)](#5-前端測試案例-frontend)
6. [測試資料參考](#6-測試資料參考)

---

## 1. 認證系統測試案例 (AUTH)

### TC-AUTH-001: 用戶註冊成功

**測試案例 ID**: TC-AUTH-001
**測試案例名稱**: 用戶註冊成功
**測試目標**: 驗證新用戶能夠成功註冊系統
**優先級**: High
**測試類型**: Positive

#### 前置條件
- API 服務正常運行
- 資料庫連線正常
- 測試用戶名稱尚未被註冊

#### 測試步驟
1. 發送 POST 請求到 `/api/auth/register`
2. 使用有效的註冊資料：
   ```json
   {
     "username": "test_user_001",
     "password": "SecurePass123!",
     "email": "test001@example.com",
     "role": "citizen"
   }
   ```
3. 檢查 HTTP 回應狀態碼
4. 檢查回應內容包含用戶資訊
5. 驗證資料庫中已建立用戶記錄

#### 預期結果
- HTTP 狀態碼: 201 Created
- 回應包含用戶資訊（不含密碼）
- 回應包含 JWT token
- 資料庫中存在新用戶記錄
- 密碼已正確 hash 儲存

#### 實際結果
_待測試執行後填寫_

#### 測試資料
```python
test_data = {
    "username": "test_user_001",
    "password": "SecurePass123!",
    "email": "test001@example.com",
    "role": "citizen"
}
```

---

### TC-AUTH-002: 用戶註冊失敗（重複帳號）

**測試案例 ID**: TC-AUTH-002
**測試案例名稱**: 用戶註冊失敗（重複帳號）
**測試目標**: 驗證系統能正確拒絕重複的用戶名稱
**優先級**: High
**測試類型**: Negative

#### 前置條件
- API 服務正常運行
- 資料庫中已存在用戶名稱 "existing_user"

#### 測試步驟
1. 發送 POST 請求到 `/api/auth/register`
2. 使用已存在的用戶名稱：
   ```json
   {
     "username": "existing_user",
     "password": "SecurePass123!",
     "email": "new@example.com",
     "role": "citizen"
   }
   ```
3. 檢查 HTTP 回應狀態碼
4. 檢查錯誤訊息內容

#### 預期結果
- HTTP 狀態碼: 400 Bad Request
- 錯誤訊息: "Username already exists"
- 資料庫記錄數量未增加

#### 實際結果
_待測試執行後填寫_

#### 測試資料
```python
# 第一步：建立已存在的用戶
existing_user = {
    "username": "existing_user",
    "password": "Pass123!",
    "email": "existing@example.com"
}

# 第二步：嘗試重複註冊
duplicate_user = {
    "username": "existing_user",
    "password": "SecurePass123!",
    "email": "new@example.com"
}
```

---

### TC-AUTH-003: 用戶登入成功

**測試案例 ID**: TC-AUTH-003
**測試案例名稱**: 用戶登入成功
**測試目標**: 驗證已註冊用戶能夠成功登入系統
**優先級**: High
**測試類型**: Positive

#### 前置條件
- API 服務正常運行
- 資料庫中存在測試用戶
- 測試用戶帳號為啟用狀態

#### 測試步驟
1. 發送 POST 請求到 `/api/auth/login`
2. 使用正確的登入憑證：
   ```json
   {
     "username": "test_user_001",
     "password": "SecurePass123!"
   }
   ```
3. 檢查 HTTP 回應狀態碼
4. 檢查回應包含 JWT token
5. 驗證 token 結構正確
6. 解碼 token 並驗證 payload 內容

#### 預期結果
- HTTP 狀態碼: 200 OK
- 回應包含有效的 JWT token
- Token payload 包含用戶 ID 和角色
- Token 過期時間設定正確（通常 24 小時）
- 回應包含用戶基本資訊

#### 實際結果
_待測試執行後填寫_

#### 測試資料
```python
login_data = {
    "username": "test_user_001",
    "password": "SecurePass123!"
}

# 預期的 token payload
expected_payload = {
    "sub": "user_id",
    "username": "test_user_001",
    "role": "citizen",
    "exp": "timestamp + 24h"
}
```

---

### TC-AUTH-004: 用戶登入失敗（錯誤密碼）

**測試案例 ID**: TC-AUTH-004
**測試案例名稱**: 用戶登入失敗（錯誤密碼）
**測試目標**: 驗證系統能正確拒絕錯誤密碼的登入嘗試
**優先級**: High
**測試類型**: Negative

#### 前置條件
- API 服務正常運行
- 資料庫中存在測試用戶
- 測試用戶帳號為啟用狀態

#### 測試步驟
1. 發送 POST 請求到 `/api/auth/login`
2. 使用錯誤的密碼：
   ```json
   {
     "username": "test_user_001",
     "password": "WrongPassword123!"
   }
   ```
3. 檢查 HTTP 回應狀態碼
4. 檢查錯誤訊息內容
5. 驗證未回傳 JWT token
6. 確認未洩漏敏感資訊

#### 預期結果
- HTTP 狀態碼: 401 Unauthorized
- 錯誤訊息: "Invalid username or password"
- 不回傳 JWT token
- 不洩漏用戶是否存在的資訊
- 不提供密碼提示

#### 實際結果
_待測試執行後填寫_

#### 測試資料
```python
invalid_login = {
    "username": "test_user_001",
    "password": "WrongPassword123!"
}

# 測試多種錯誤密碼情境
test_cases = [
    {"password": ""},                    # 空密碼
    {"password": "wrong"},               # 錯誤密碼
    {"password": "SecurePass123"},       # 缺少特殊字元
    {"password": "SECUREPASS123!"},      # 大小寫錯誤
]
```

---

### TC-AUTH-005: JWT Token 驗證

**測試案例 ID**: TC-AUTH-005
**測試案例名稱**: JWT Token 驗證
**測試目標**: 驗證 JWT token 的正確性與安全性
**優先級**: High
**測試類型**: Positive/Negative

#### 前置條件
- API 服務正常運行
- 已獲取有效的 JWT token

#### 測試步驟
1. **有效 Token 測試**:
   - 使用有效 token 訪問受保護的 endpoint
   - 驗證請求成功
2. **無效 Token 測試**:
   - 使用格式錯誤的 token
   - 驗證請求被拒絕
3. **過期 Token 測試**:
   - 使用已過期的 token
   - 驗證請求被拒絕
4. **Token 篡改測試**:
   - 修改 token payload
   - 驗證請求被拒絕

#### 預期結果
- 有效 token: HTTP 200, 成功訪問資源
- 無效格式: HTTP 401, "Invalid token format"
- 過期 token: HTTP 401, "Token expired"
- 篡改 token: HTTP 401, "Invalid token signature"

#### 實際結果
_待測試執行後填寫_

#### 測試資料
```python
# 有效 token（測試時需真實生成）
valid_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# 無效 token 範例
invalid_tokens = {
    "malformed": "not.a.valid.token",
    "expired": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...[expired]",
    "tampered": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...[modified_payload]",
    "wrong_signature": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...[wrong_sig]"
}
```

---

## 2. 意見系統測試案例 (OPINION)

### TC-OPN-001: 建立意見

**測試案例 ID**: TC-OPN-001
**測試案例名稱**: 建立意見
**測試目標**: 驗證用戶能夠成功建立新意見
**優先級**: High
**測試類型**: Positive

#### 前置條件
- API 服務正常運行
- 用戶已登入並獲取有效 JWT token
- 資料庫連線正常

#### 測試步驟
1. 使用有效 JWT token 發送 POST 請求到 `/api/opinions`
2. 提供完整的意見資料：
   ```json
   {
     "title": "改善市中心交通",
     "description": "建議增加公車班次並優化紅綠燈時間",
     "category": "交通",
     "location": {
       "latitude": 25.0330,
       "longitude": 121.5654,
       "address": "台北市中正區"
     },
     "tags": ["交通", "公車", "紅綠燈"]
   }
   ```
3. 檢查 HTTP 回應狀態碼
4. 驗證回應內容包含意見 ID
5. 確認資料庫中已建立記錄

#### 預期結果
- HTTP 狀態碼: 201 Created
- 回應包含新建意見的完整資訊
- 回應包含自動生成的 opinion_id
- 意見狀態為 "pending"（待審核）
- 建立時間已正確記錄
- 資料庫中存在對應記錄

#### 實際結果
_待測試執行後填寫_

#### 測試資料
```python
opinion_data = {
    "title": "改善市中心交通",
    "description": "建議增加公車班次並優化紅綠燈時間",
    "category": "交通",
    "location": {
        "latitude": 25.0330,
        "longitude": 121.5654,
        "address": "台北市中正區"
    },
    "tags": ["交通", "公車", "紅綠燈"]
}
```

---

### TC-OPN-002: 查詢意見列表

**測試案例 ID**: TC-OPN-002
**測試案例名稱**: 查詢意見列表
**測試目標**: 驗證系統能正確返回意見列表，並支援分頁、過濾、排序
**優先級**: High
**測試類型**: Positive

#### 前置條件
- API 服務正常運行
- 資料庫中存在多筆意見記錄（至少 20 筆）

#### 測試步驟
1. **基本查詢**:
   - GET `/api/opinions?page=1&limit=10`
2. **分類過濾**:
   - GET `/api/opinions?category=交通&page=1&limit=10`
3. **狀態過濾**:
   - GET `/api/opinions?status=approved&page=1&limit=10`
4. **排序測試**:
   - GET `/api/opinions?sort_by=created_at&order=desc`
5. **搜尋測試**:
   - GET `/api/opinions?search=交通&page=1&limit=10`

#### 預期結果
- HTTP 狀態碼: 200 OK
- 回應包含意見陣列
- 回應包含分頁資訊（total, page, limit）
- 過濾功能正常運作
- 排序功能正常運作
- 每個意見包含完整資訊

#### 實際結果
_待測試執行後填寫_

#### 測試資料
```python
# 查詢參數測試案例
query_params = {
    "basic": {"page": 1, "limit": 10},
    "filter_category": {"category": "交通", "page": 1, "limit": 10},
    "filter_status": {"status": "approved", "page": 1, "limit": 10},
    "sort_desc": {"sort_by": "created_at", "order": "desc"},
    "search": {"search": "交通", "page": 1, "limit": 10}
}

# 預期的回應結構
expected_response = {
    "data": [],  # 意見陣列
    "pagination": {
        "total": 0,
        "page": 1,
        "limit": 10,
        "total_pages": 0
    }
}
```

---

### TC-OPN-003: 查詢意見詳情

**測試案例 ID**: TC-OPN-003
**測試案例名稱**: 查詢意見詳情
**測試目標**: 驗證系統能正確返回單一意見的詳細資訊
**優先級**: High
**測試類型**: Positive

#### 前置條件
- API 服務正常運行
- 資料庫中存在測試意見（ID: test_opinion_001）

#### 測試步驟
1. 發送 GET 請求到 `/api/opinions/{opinion_id}`
2. 使用有效的意見 ID
3. 檢查 HTTP 回應狀態碼
4. 驗證回應包含完整的意見資訊
5. 驗證包含相關的留言和投票資訊

#### 預期結果
- HTTP 狀態碼: 200 OK
- 回應包含意見完整資訊
- 包含作者資訊（不含密碼）
- 包含位置資訊
- 包含媒體檔案列表（如有）
- 包含投票統計
- 包含留言數量
- 包含收藏數量

#### 實際結果
_待測試執行後填寫_

#### 測試資料
```python
opinion_id = "test_opinion_001"

# 預期的回應結構
expected_response = {
    "id": "test_opinion_001",
    "title": "改善市中心交通",
    "description": "建議增加公車班次並優化紅綠燈時間",
    "category": "交通",
    "status": "approved",
    "author": {
        "id": "user_001",
        "username": "test_user"
    },
    "location": {
        "latitude": 25.0330,
        "longitude": 121.5654,
        "address": "台北市中正區"
    },
    "media": [],
    "votes": {
        "upvotes": 10,
        "downvotes": 2
    },
    "comments_count": 5,
    "bookmarks_count": 3,
    "created_at": "2025-10-24T10:00:00Z",
    "updated_at": "2025-10-24T10:00:00Z"
}
```

---

### TC-OPN-004: 更新意見

**測試案例 ID**: TC-OPN-004
**測試案例名稱**: 更新意見
**測試目標**: 驗證意見作者能夠成功更新自己的意見
**優先級**: High
**測試類型**: Positive

#### 前置條件
- API 服務正常運行
- 用戶已登入並擁有該意見
- 意見狀態允許編輯（pending 或 draft）

#### 測試步驟
1. 使用意見作者的 JWT token
2. 發送 PUT 請求到 `/api/opinions/{opinion_id}`
3. 提供更新的資料：
   ```json
   {
     "title": "改善市中心交通（更新版）",
     "description": "建議增加公車班次並優化紅綠燈時間，同時增設腳踏車道",
     "category": "交通",
     "tags": ["交通", "公車", "紅綠燈", "腳踏車道"]
   }
   ```
4. 檢查 HTTP 回應狀態碼
5. 驗證資料已更新
6. 確認 updated_at 時間已更新

#### 預期結果
- HTTP 狀態碼: 200 OK
- 回應包含更新後的意見資訊
- 標題和內容已正確更新
- updated_at 時間戳已更新
- created_at 時間戳保持不變
- 資料庫中記錄已更新

#### 實際結果
_待測試執行後填寫_

#### 測試資料
```python
opinion_id = "test_opinion_001"
update_data = {
    "title": "改善市中心交通（更新版）",
    "description": "建議增加公車班次並優化紅綠燈時間，同時增設腳踏車道",
    "category": "交通",
    "tags": ["交通", "公車", "紅綠燈", "腳踏車道"]
}
```

---

### TC-OPN-005: 刪除意見

**測試案例 ID**: TC-OPN-005
**測試案例名稱**: 刪除意見
**測試目標**: 驗證意見作者或管理員能夠成功刪除意見
**優先級**: High
**測試類型**: Positive

#### 前置條件
- API 服務正常運行
- 用戶已登入（作者或管理員）
- 意見存在於資料庫中

#### 測試步驟
1. 使用有效的 JWT token（作者或管理員）
2. 發送 DELETE 請求到 `/api/opinions/{opinion_id}`
3. 檢查 HTTP 回應狀態碼
4. 驗證資料庫中記錄已刪除或標記為已刪除
5. 嘗試再次查詢該意見，應該失敗

#### 預期結果
- HTTP 狀態碼: 204 No Content
- 資料庫中記錄已軟刪除（deleted_at 有值）
- 相關的留言和投票也被標記為刪除
- 再次查詢返回 404 Not Found
- 媒體檔案已從儲存中移除

#### 實際結果
_待測試執行後填寫_

#### 測試資料
```python
opinion_id = "test_opinion_002"
author_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# 驗證刪除後的查詢
verify_deletion = {
    "method": "GET",
    "url": f"/api/opinions/{opinion_id}",
    "expected_status": 404
}
```

---

### TC-OPN-006: 意見投票

**測試案例 ID**: TC-OPN-006
**測試案例名稱**: 意見投票
**測試目標**: 驗證用戶能夠對意見進行投票（贊成/反對）
**優先級**: High
**測試類型**: Positive

#### 前置條件
- API 服務正常運行
- 用戶已登入
- 意見存在且狀態為 "approved"
- 用戶尚未對該意見投票

#### 測試步驟
1. **首次投票（贊成）**:
   - POST `/api/opinions/{opinion_id}/vote`
   - Body: `{"vote_type": "upvote"}`
2. **變更投票（改為反對）**:
   - POST `/api/opinions/{opinion_id}/vote`
   - Body: `{"vote_type": "downvote"}`
3. **取消投票**:
   - DELETE `/api/opinions/{opinion_id}/vote`
4. 檢查投票統計是否正確更新

#### 預期結果
- 首次投票: HTTP 201, upvotes +1
- 變更投票: HTTP 200, upvotes -1, downvotes +1
- 取消投票: HTTP 204, downvotes -1
- 投票統計實時更新
- 防止重複投票

#### 實際結果
_待測試執行後填寫_

#### 測試資料
```python
opinion_id = "test_opinion_001"
user_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

vote_actions = {
    "upvote": {"vote_type": "upvote"},
    "downvote": {"vote_type": "downvote"}
}

# 預期的投票統計變化
expected_vote_changes = {
    "initial": {"upvotes": 10, "downvotes": 2},
    "after_upvote": {"upvotes": 11, "downvotes": 2},
    "after_change": {"upvotes": 10, "downvotes": 3},
    "after_cancel": {"upvotes": 10, "downvotes": 2}
}
```

---

### TC-OPN-007: 意見留言

**測試案例 ID**: TC-OPN-007
**測試案例名稱**: 意見留言
**測試目標**: 驗證用戶能夠對意見進行留言
**優先級**: High
**測試類型**: Positive

#### 前置條件
- API 服務正常運行
- 用戶已登入
- 意見存在且狀態為 "approved"

#### 測試步驟
1. **建立留言**:
   - POST `/api/opinions/{opinion_id}/comments`
   - Body: `{"content": "我也有同樣的想法，支持這個提案！"}`
2. **查詢留言列表**:
   - GET `/api/opinions/{opinion_id}/comments?page=1&limit=10`
3. **回覆留言**:
   - POST `/api/opinions/{opinion_id}/comments`
   - Body: `{"content": "感謝支持", "parent_id": "comment_001"}`
4. **刪除留言**:
   - DELETE `/api/comments/{comment_id}`

#### 預期結果
- 建立留言: HTTP 201, 回應包含留言 ID
- 查詢留言: HTTP 200, 回應包含留言列表
- 回覆留言: HTTP 201, 顯示為子留言
- 刪除留言: HTTP 204, 留言已移除

#### 實際結果
_待測試執行後填寫_

#### 測試資料
```python
opinion_id = "test_opinion_001"
comment_data = {
    "content": "我也有同樣的想法，支持這個提案！"
}

reply_data = {
    "content": "感謝支持",
    "parent_id": "comment_001"
}

# 預期的留言結構
expected_comment = {
    "id": "comment_001",
    "content": "我也有同樣的想法，支持這個提案！",
    "author": {
        "id": "user_002",
        "username": "supporter"
    },
    "parent_id": None,
    "replies": [],
    "created_at": "2025-10-24T11:00:00Z"
}
```

---

### TC-OPN-008: 意見收藏

**測試案例 ID**: TC-OPN-008
**測試案例名稱**: 意見收藏
**測試目標**: 驗證用戶能夠收藏和取消收藏意見
**優先級**: Medium
**測試類型**: Positive

#### 前置條件
- API 服務正常運行
- 用戶已登入
- 意見存在且狀態為 "approved"

#### 測試步驟
1. **收藏意見**:
   - POST `/api/opinions/{opinion_id}/bookmark`
2. **查詢收藏列表**:
   - GET `/api/users/me/bookmarks`
3. **取消收藏**:
   - DELETE `/api/opinions/{opinion_id}/bookmark`
4. 驗證收藏統計正確更新

#### 預期結果
- 收藏: HTTP 201, 收藏成功
- 查詢: HTTP 200, 列表包含已收藏的意見
- 取消: HTTP 204, 收藏已移除
- 收藏統計實時更新
- 防止重複收藏

#### 實際結果
_待測試執行後填寫_

#### 測試資料
```python
opinion_id = "test_opinion_001"
user_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# 預期的收藏統計變化
expected_bookmark_changes = {
    "initial": {"bookmarks_count": 3},
    "after_bookmark": {"bookmarks_count": 4},
    "after_unbookmark": {"bookmarks_count": 3}
}
```

---

## 3. 媒體系統測試案例 (MEDIA)

### TC-MED-001: 上傳圖片

**測試案例 ID**: TC-MED-001
**測試案例名稱**: 上傳圖片
**測試目標**: 驗證用戶能夠成功上傳圖片檔案
**優先級**: High
**測試類型**: Positive

#### 前置條件
- API 服務正常運行
- 用戶已登入
- 儲存空間足夠
- 圖片檔案有效（JPEG/PNG）

#### 測試步驟
1. 準備測試圖片檔案（test_image.jpg, 2MB）
2. 發送 POST 請求到 `/api/media/upload`
3. 使用 multipart/form-data 格式：
   ```
   Content-Type: multipart/form-data
   file: [binary image data]
   type: "image"
   ```
4. 檢查 HTTP 回應狀態碼
5. 驗證回應包含檔案 URL
6. 確認檔案已儲存到指定位置
7. 驗證縮圖已自動生成

#### 預期結果
- HTTP 狀態碼: 201 Created
- 回應包含檔案 URL
- 回應包含檔案 ID
- 原始圖片已儲存
- 縮圖已自動生成（800x600, 400x300）
- 資料庫記錄已建立

#### 實際結果
_待測試執行後填寫_

#### 測試資料
```python
# 測試圖片
test_images = {
    "jpg": {
        "filename": "test_image.jpg",
        "size": 2 * 1024 * 1024,  # 2MB
        "mime_type": "image/jpeg"
    },
    "png": {
        "filename": "test_image.png",
        "size": 1.5 * 1024 * 1024,  # 1.5MB
        "mime_type": "image/png"
    }
}

# 預期的回應
expected_response = {
    "id": "media_001",
    "url": "https://storage.example.com/media/images/test_image.jpg",
    "thumbnail_urls": {
        "large": "https://storage.example.com/media/thumbs/test_image_800x600.jpg",
        "medium": "https://storage.example.com/media/thumbs/test_image_400x300.jpg"
    },
    "filename": "test_image.jpg",
    "size": 2097152,
    "mime_type": "image/jpeg",
    "uploaded_at": "2025-10-24T12:00:00Z"
}
```

---

### TC-MED-002: 上傳影片

**測試案例 ID**: TC-MED-002
**測試案例名稱**: 上傳影片
**測試目標**: 驗證用戶能夠成功上傳影片檔案
**優先級**: High
**測試類型**: Positive

#### 前置條件
- API 服務正常運行
- 用戶已登入
- 儲存空間足夠
- 影片檔案有效（MP4/MOV）
- 影片大小在限制內（< 100MB）

#### 測試步驟
1. 準備測試影片檔案（test_video.mp4, 50MB）
2. 發送 POST 請求到 `/api/media/upload`
3. 使用 multipart/form-data 格式：
   ```
   Content-Type: multipart/form-data
   file: [binary video data]
   type: "video"
   ```
4. 檢查 HTTP 回應狀態碼
5. 驗證回應包含檔案 URL
6. 確認影片已儲存
7. 驗證影片縮圖（首幀）已生成

#### 預期結果
- HTTP 狀態碼: 201 Created
- 回應包含影片 URL
- 回應包含檔案 ID
- 影片已儲存
- 影片縮圖（首幀截圖）已生成
- 影片長度資訊已記錄
- 資料庫記錄已建立

#### 實際結果
_待測試執行後填寫_

#### 測試資料
```python
# 測試影片
test_video = {
    "filename": "test_video.mp4",
    "size": 50 * 1024 * 1024,  # 50MB
    "mime_type": "video/mp4",
    "duration": 120  # 2 分鐘
}

# 預期的回應
expected_response = {
    "id": "media_002",
    "url": "https://storage.example.com/media/videos/test_video.mp4",
    "thumbnail_url": "https://storage.example.com/media/thumbs/test_video_frame.jpg",
    "filename": "test_video.mp4",
    "size": 52428800,
    "mime_type": "video/mp4",
    "duration": 120,
    "uploaded_at": "2025-10-24T12:00:00Z"
}
```

---

### TC-MED-003: 批次上傳

**測試案例 ID**: TC-MED-003
**測試案例名稱**: 批次上傳
**測試目標**: 驗證系統能夠處理多個檔案的批次上傳
**優先級**: Medium
**測試類型**: Positive

#### 前置條件
- API 服務正常運行
- 用戶已登入
- 儲存空間足夠
- 準備多個有效的圖片檔案（3-5 張）

#### 測試步驟
1. 準備 5 張測試圖片
2. 發送 POST 請求到 `/api/media/upload/batch`
3. 使用 multipart/form-data 格式包含多個檔案
4. 檢查 HTTP 回應狀態碼
5. 驗證所有檔案都已成功上傳
6. 確認回應包含所有檔案的 URL

#### 預期結果
- HTTP 狀態碼: 201 Created
- 回應包含所有檔案的資訊陣列
- 所有檔案都已儲存
- 每個檔案都有獨立的 ID 和 URL
- 批次操作是原子性的（全部成功或全部失敗）

#### 實際結果
_待測試執行後填寫_

#### 測試資料
```python
# 批次上傳測試資料
batch_files = [
    {"filename": "image1.jpg", "size": 2 * 1024 * 1024},
    {"filename": "image2.jpg", "size": 1.8 * 1024 * 1024},
    {"filename": "image3.png", "size": 2.2 * 1024 * 1024},
    {"filename": "image4.jpg", "size": 1.5 * 1024 * 1024},
    {"filename": "image5.png", "size": 2.5 * 1024 * 1024}
]

# 預期的回應
expected_response = {
    "uploaded_files": [
        {"id": "media_003", "url": "...", "filename": "image1.jpg"},
        {"id": "media_004", "url": "...", "filename": "image2.jpg"},
        {"id": "media_005", "url": "...", "filename": "image3.png"},
        {"id": "media_006", "url": "...", "filename": "image4.jpg"},
        {"id": "media_007", "url": "...", "filename": "image5.png"}
    ],
    "total": 5,
    "success": 5,
    "failed": 0
}
```

---

### TC-MED-004: 取得媒體檔案

**測試案例 ID**: TC-MED-004
**測試案例名稱**: 取得媒體檔案
**測試目標**: 驗證系統能夠正確提供媒體檔案存取
**優先級**: High
**測試類型**: Positive

#### 前置條件
- API 服務正常運行
- 媒體檔案已存在於儲存系統
- 檔案 ID 有效

#### 測試步驟
1. **取得原始檔案**:
   - GET `/api/media/{media_id}`
2. **取得縮圖**:
   - GET `/api/media/{media_id}/thumbnail?size=medium`
3. **驗證檔案內容**:
   - 檢查 Content-Type header
   - 檢查檔案大小
   - 驗證檔案可正常顯示

#### 預期結果
- HTTP 狀態碼: 200 OK
- Content-Type 正確
- 檔案內容完整
- 支援斷點續傳（Accept-Ranges header）
- 正確的 Cache-Control headers

#### 實際結果
_待測試執行後填寫_

#### 測試資料
```python
media_id = "media_001"

# 測試不同的存取方式
access_tests = {
    "original": f"/api/media/{media_id}",
    "thumbnail_large": f"/api/media/{media_id}/thumbnail?size=large",
    "thumbnail_medium": f"/api/media/{media_id}/thumbnail?size=medium"
}

# 預期的 headers
expected_headers = {
    "Content-Type": "image/jpeg",
    "Content-Length": "2097152",
    "Accept-Ranges": "bytes",
    "Cache-Control": "public, max-age=31536000"
}
```

---

### TC-MED-005: 刪除媒體

**測試案例 ID**: TC-MED-005
**測試案例名稱**: 刪除媒體
**測試目標**: 驗證用戶或管理員能夠刪除媒體檔案
**優先級**: High
**測試類型**: Positive

#### 前置條件
- API 服務正常運行
- 用戶已登入（檔案擁有者或管理員）
- 媒體檔案存在
- 媒體未被其他資源引用（或已處理關聯）

#### 測試步驟
1. 使用有效的 JWT token
2. 發送 DELETE 請求到 `/api/media/{media_id}`
3. 檢查 HTTP 回應狀態碼
4. 驗證檔案已從儲存中移除
5. 驗證縮圖也已移除
6. 驗證資料庫記錄已刪除
7. 嘗試再次存取檔案，應該失敗

#### 預期結果
- HTTP 狀態碼: 204 No Content
- 原始檔案已從儲存中移除
- 所有縮圖已移除
- 資料庫記錄已刪除
- 再次存取返回 404 Not Found
- 如有引用，相關記錄已更新

#### 實際結果
_待測試執行後填寫_

#### 測試資料
```python
media_id = "media_008"
owner_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

# 驗證刪除後的存取
verify_deletion = {
    "method": "GET",
    "url": f"/api/media/{media_id}",
    "expected_status": 404
}

# 檢查檔案系統
check_filesystem = [
    f"/storage/media/images/{media_id}.jpg",
    f"/storage/media/thumbs/{media_id}_800x600.jpg",
    f"/storage/media/thumbs/{media_id}_400x300.jpg"
]
```

---

## 4. 管理系統測試案例 (ADMIN)

### TC-ADM-001: 核准意見

**測試案例 ID**: TC-ADM-001
**測試案例名稱**: 核准意見
**測試目標**: 驗證管理員能夠核准待審核的意見
**優先級**: High
**測試類型**: Positive

#### 前置條件
- API 服務正常運行
- 管理員已登入
- 存在狀態為 "pending" 的意見

#### 測試步驟
1. 使用管理員 JWT token
2. 發送 POST 請求到 `/api/admin/opinions/{opinion_id}/approve`
3. 提供核准資料：
   ```json
   {
     "comment": "意見內容符合規範，予以核准",
     "category": "交通",
     "priority": "high"
   }
   ```
4. 檢查 HTTP 回應狀態碼
5. 驗證意見狀態已更新為 "approved"
6. 確認通知已發送給意見作者

#### 預期結果
- HTTP 狀態碼: 200 OK
- 意見狀態更新為 "approved"
- approved_at 時間戳已記錄
- approved_by 已記錄管理員 ID
- 作者收到核准通知
- 意見在公開列表中可見

#### 實際結果
_待測試執行後填寫_

#### 測試資料
```python
opinion_id = "test_opinion_pending_001"
admin_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

approval_data = {
    "comment": "意見內容符合規範，予以核准",
    "category": "交通",
    "priority": "high"
}

# 預期的狀態變化
expected_changes = {
    "status": "approved",
    "approved_at": "2025-10-24T13:00:00Z",
    "approved_by": "admin_001"
}
```

---

### TC-ADM-002: 拒絕意見

**測試案例 ID**: TC-ADM-002
**測試案例名稱**: 拒絕意見
**測試目標**: 驗證管理員能夠拒絕不符合規範的意見
**優先級**: High
**測試類型**: Positive

#### 前置條件
- API 服務正常運行
- 管理員已登入
- 存在狀態為 "pending" 的意見

#### 測試步驟
1. 使用管理員 JWT token
2. 發送 POST 請求到 `/api/admin/opinions/{opinion_id}/reject`
3. 提供拒絕原因：
   ```json
   {
     "reason": "內容不符合社群規範",
     "details": "意見內容包含不當言論，違反使用條款第3條"
   }
   ```
4. 檢查 HTTP 回應狀態碼
5. 驗證意見狀態已更新為 "rejected"
6. 確認通知已發送給意見作者

#### 預期結果
- HTTP 狀態碼: 200 OK
- 意見狀態更新為 "rejected"
- rejected_at 時間戳已記錄
- rejected_by 已記錄管理員 ID
- rejection_reason 已記錄
- 作者收到拒絕通知（包含原因）
- 意見在公開列表中不可見

#### 實際結果
_待測試執行後填寫_

#### 測試資料
```python
opinion_id = "test_opinion_pending_002"
admin_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

rejection_data = {
    "reason": "內容不符合社群規範",
    "details": "意見內容包含不當言論，違反使用條款第3條"
}

# 預期的狀態變化
expected_changes = {
    "status": "rejected",
    "rejected_at": "2025-10-24T13:00:00Z",
    "rejected_by": "admin_001",
    "rejection_reason": "內容不符合社群規範"
}
```

---

### TC-ADM-003: 合併意見

**測試案例 ID**: TC-ADM-003
**測試案例名稱**: 合併意見
**測試目標**: 驗證管理員能夠將相似的意見合併
**優先級**: Medium
**測試類型**: Positive

#### 前置條件
- API 服務正常運行
- 管理員已登入
- 存在多個相似的意見

#### 測試步驟
1. 使用管理員 JWT token
2. 識別需要合併的意見
3. 發送 POST 請求到 `/api/admin/opinions/merge`
4. 提供合併資料：
   ```json
   {
     "source_opinion_ids": ["opinion_001", "opinion_002", "opinion_003"],
     "target_opinion_id": "opinion_001",
     "merge_reason": "三個意見討論相同的交通問題，合併以便統一討論"
   }
   ```
5. 檢查 HTTP 回應狀態碼
6. 驗證意見已正確合併

#### 預期結果
- HTTP 狀態碼: 200 OK
- 被合併的意見狀態更新為 "merged"
- 目標意見包含所有合併意見的參考
- 投票和留言已合併
- 所有作者收到通知
- 合併記錄已記錄

#### 實際結果
_待測試執行後填寫_

#### 測試資料
```python
merge_data = {
    "source_opinion_ids": ["opinion_001", "opinion_002", "opinion_003"],
    "target_opinion_id": "opinion_001",
    "merge_reason": "三個意見討論相同的交通問題，合併以便統一討論"
}

# 預期的合併結果
expected_merge = {
    "merged_opinion": {
        "id": "opinion_001",
        "votes": {
            "upvotes": 35,  # 10 + 15 + 10
            "downvotes": 5   # 2 + 2 + 1
        },
        "comments_count": 15,  # 5 + 6 + 4
        "merged_from": ["opinion_002", "opinion_003"]
    }
}
```

---

### TC-ADM-004: 刪除留言

**測試案例 ID**: TC-ADM-004
**測試案例名稱**: 刪除留言
**測試目標**: 驗證管理員能夠刪除違規的留言
**優先級**: High
**測試類型**: Positive

#### 前置條件
- API 服務正常運行
- 管理員已登入
- 存在需要刪除的留言

#### 測試步驟
1. 使用管理員 JWT token
2. 發送 DELETE 請求到 `/api/admin/comments/{comment_id}`
3. 提供刪除原因：
   ```json
   {
     "reason": "違反社群規範",
     "details": "留言包含攻擊性言論"
   }
   ```
4. 檢查 HTTP 回應狀態碼
5. 驗證留言已被刪除
6. 確認通知已發送給留言作者

#### 預期結果
- HTTP 狀態碼: 204 No Content
- 留言已從列表中移除
- 留言資料庫記錄標記為已刪除
- 刪除原因已記錄
- 作者收到通知
- 意見的留言統計已更新

#### 實際結果
_待測試執行後填寫_

#### 測試資料
```python
comment_id = "comment_violating_001"
admin_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."

deletion_data = {
    "reason": "違反社群規範",
    "details": "留言包含攻擊性言論"
}

# 驗證刪除後的狀態
verify_deletion = {
    "comment_visible": False,
    "comments_count_decreased": True,
    "deletion_record_exists": True
}
```

---

### TC-ADM-005: 更新分類

**測試案例 ID**: TC-ADM-005
**測試案例名稱**: 更新分類
**測試目標**: 驗證管理員能夠管理意見分類
**優先級**: Medium
**測試類型**: Positive

#### 前置條件
- API 服務正常運行
- 管理員已登入
- 分類系統已初始化

#### 測試步驟
1. **新增分類**:
   - POST `/api/admin/categories`
   - Body: `{"name": "環境保護", "description": "環保相關提案", "color": "#00AA00"}`
2. **更新分類**:
   - PUT `/api/admin/categories/{category_id}`
   - Body: `{"name": "環保與永續", "description": "更新後的描述"}`
3. **刪除分類**:
   - DELETE `/api/admin/categories/{category_id}`
4. 驗證分類變更已生效

#### 預期結果
- 新增: HTTP 201, 分類已建立
- 更新: HTTP 200, 分類資訊已更新
- 刪除: HTTP 204, 分類已移除
- 分類變更不影響現有意見
- 或現有意見已重新分類

#### 實際結果
_待測試執行後填寫_

#### 測試資料
```python
# 新增分類
new_category = {
    "name": "環境保護",
    "description": "環保相關提案",
    "color": "#00AA00",
    "icon": "leaf"
}

# 更新分類
update_category = {
    "name": "環保與永續",
    "description": "環境保護與永續發展相關提案",
    "color": "#00BB00"
}

# 預期的分類列表
expected_categories = [
    {"id": "cat_001", "name": "交通"},
    {"id": "cat_002", "name": "都市規劃"},
    {"id": "cat_003", "name": "環保與永續"},
    {"id": "cat_004", "name": "公共設施"}
]
```

---

## 5. 前端測試案例 (FRONTEND)

### TC-FE-001: 登入頁面

**測試案例 ID**: TC-FE-001
**測試案例名稱**: 登入頁面功能測試
**測試目標**: 驗證前端登入頁面功能正常運作
**優先級**: High
**測試類型**: Positive/Negative

#### 前置條件
- 前端應用已啟動
- API 服務正常運行
- 測試用戶已存在於資料庫

#### 測試步驟
1. **訪問登入頁面**:
   - 開啟瀏覽器訪問 `http://localhost:5173/login`
2. **正確登入**:
   - 輸入有效的用戶名稱和密碼
   - 點擊登入按鈕
   - 驗證跳轉到儀表板
3. **錯誤登入**:
   - 輸入無效的密碼
   - 點擊登入按鈕
   - 驗證顯示錯誤訊息
4. **表單驗證**:
   - 測試空白欄位驗證
   - 測試密碼長度驗證
5. **UI/UX 測試**:
   - 檢查 loading 狀態顯示
   - 檢查錯誤訊息樣式
   - 檢查響應式設計

#### 預期結果
- 登入頁面正確載入
- 表單驗證功能正常
- 正確憑證能成功登入
- 錯誤憑證顯示錯誤訊息
- Loading 狀態正確顯示
- 響應式設計在各尺寸設備正常

#### 實際結果
_待測試執行後填寫_

#### 測試資料
```javascript
// 測試案例
const testCases = {
  valid_login: {
    username: "admin",
    password: "admin123",
    expectedResult: "redirect to dashboard"
  },
  invalid_password: {
    username: "admin",
    password: "wrong_password",
    expectedResult: "error message displayed"
  },
  empty_fields: {
    username: "",
    password: "",
    expectedResult: "validation error"
  }
};

// 響應式測試尺寸
const viewportSizes = [
  { name: "Mobile", width: 375, height: 667 },
  { name: "Tablet", width: 768, height: 1024 },
  { name: "Desktop", width: 1920, height: 1080 }
];
```

---

### TC-FE-002: 儀表板顯示

**測試案例 ID**: TC-FE-002
**測試案例名稱**: 儀表板頁面顯示測試
**測試目標**: 驗證儀表板能正確顯示統計資訊
**優先級**: High
**測試類型**: Positive

#### 前置條件
- 用戶已成功登入
- API 服務正常運行
- 資料庫中存在測試資料

#### 測試步驟
1. **頁面載入**:
   - 登入後自動跳轉到儀表板
   - 檢查頁面是否正確載入
2. **統計卡片**:
   - 驗證顯示待審核數量
   - 驗證顯示已核准數量
   - 驗證顯示總意見數量
   - 驗證顯示本月新增數量
3. **圖表顯示**:
   - 檢查分類統計圖表
   - 檢查趨勢圖表
4. **資料更新**:
   - 驗證資料實時更新
   - 檢查重新整理功能

#### 預期結果
- 儀表板頁面正確載入
- 所有統計卡片顯示正確數據
- 圖表正確渲染
- 數據與後端 API 一致
- 響應式設計正常

#### 實際結果
_待測試執行後填寫_

#### 測試資料
```javascript
// 預期的儀表板資料
const expectedDashboardData = {
  statistics: {
    pending: 5,
    approved: 25,
    total: 35,
    thisMonth: 10
  },
  categories: [
    { name: "交通", count: 12 },
    { name: "環境", count: 8 },
    { name: "公共設施", count: 10 },
    { name: "其他", count: 5 }
  ],
  trend: {
    labels: ["1月", "2月", "3月", "4月", "5月"],
    data: [5, 8, 12, 15, 10]
  }
};
```

---

### TC-FE-003: 意見列表

**測試案例 ID**: TC-FE-003
**測試案例名稱**: 意見列表頁面測試
**測試目標**: 驗證意見列表能正確顯示和過濾
**優先級**: High
**測試類型**: Positive

#### 前置條件
- 用戶已成功登入
- API 服務正常運行
- 資料庫中存在多筆意見記錄

#### 測試步驟
1. **列表顯示**:
   - 導航到意見列表頁面
   - 驗證意見列表正確顯示
2. **分頁功能**:
   - 測試頁碼切換
   - 測試每頁顯示數量調整
3. **過濾功能**:
   - 測試按分類過濾
   - 測試按狀態過濾
   - 測試搜尋功能
4. **排序功能**:
   - 測試按時間排序
   - 測試按熱門度排序
5. **響應式設計**:
   - 測試在不同設備上的顯示

#### 預期結果
- 列表正確顯示所有意見
- 分頁功能正常運作
- 過濾功能正確篩選資料
- 排序功能正常
- 搜尋功能正確
- 響應式設計正常

#### 實際結果
_待測試執行後填寫_

#### 測試資料
```javascript
// 測試過濾參數
const filterTests = {
  category: {
    filter: { category: "交通" },
    expectedCount: 12
  },
  status: {
    filter: { status: "pending" },
    expectedCount: 5
  },
  search: {
    filter: { search: "公車" },
    expectedCount: 3
  }
};

// 測試排序
const sortTests = [
  { sortBy: "created_at", order: "desc" },
  { sortBy: "votes", order: "desc" },
  { sortBy: "comments", order: "desc" }
];
```

---

### TC-FE-004: 意見詳情

**測試案例 ID**: TC-FE-004
**測試案例名稱**: 意見詳情頁面測試
**測試目標**: 驗證意見詳情頁面能完整顯示資訊
**優先級**: High
**測試類型**: Positive

#### 前置條件
- 用戶已成功登入
- API 服務正常運行
- 測試意見存在於資料庫

#### 測試步驟
1. **頁面顯示**:
   - 從列表點擊意見進入詳情頁
   - 驗證所有資訊正確顯示
2. **內容檢查**:
   - 檢查標題、描述、分類
   - 檢查作者資訊
   - 檢查位置資訊
   - 檢查媒體檔案顯示
3. **互動功能**:
   - 檢查圖片預覽功能
   - 檢查地圖顯示
   - 檢查留言區顯示
4. **投票統計**:
   - 驗證投票數量顯示
   - 檢查投票趨勢圖表

#### 預期結果
- 詳情頁面正確載入
- 所有資訊完整顯示
- 媒體檔案正確渲染
- 地圖正確顯示位置
- 留言列表正確載入
- 投票統計正確顯示

#### 實際結果
_待測試執行後填寫_

#### 測試資料
```javascript
// 測試意見資料
const testOpinion = {
  id: "opinion_test_001",
  title: "改善市中心交通",
  description: "建議增加公車班次並優化紅綠燈時間",
  category: "交通",
  status: "approved",
  author: {
    id: "user_001",
    username: "test_user"
  },
  location: {
    latitude: 25.0330,
    longitude: 121.5654,
    address: "台北市中正區"
  },
  media: [
    { id: "media_001", type: "image", url: "https://..." },
    { id: "media_002", type: "image", url: "https://..." }
  ],
  votes: {
    upvotes: 25,
    downvotes: 3
  },
  comments_count: 12,
  created_at: "2025-10-24T10:00:00Z"
};
```

---

### TC-FE-005: 審核功能

**測試案例 ID**: TC-FE-005
**測試案例名稱**: 意見審核功能測試
**測試目標**: 驗證管理員能通過前端介面審核意見
**優先級**: High
**測試類型**: Positive

#### 前置條件
- 管理員已成功登入
- API 服務正常運行
- 存在待審核的意見

#### 測試步驟
1. **進入審核頁面**:
   - 導航到待審核意見列表
   - 選擇一個待審核意見
2. **核准操作**:
   - 點擊核准按鈕
   - 填寫核准意見
   - 確認核准
   - 驗證狀態更新
3. **拒絕操作**:
   - 選擇另一個待審核意見
   - 點擊拒絕按鈕
   - 填寫拒絕原因
   - 確認拒絕
   - 驗證狀態更新
4. **批次操作**:
   - 選擇多個意見
   - 執行批次核准
   - 驗證所有選擇的意見狀態更新

#### 預期結果
- 審核介面正確顯示
- 核准功能正常運作
- 拒絕功能正常運作
- 批次操作功能正常
- 狀態實時更新
- 確認對話框正確顯示
- 操作回饋訊息清晰

#### 實際結果
_待測試執行後填寫_

#### 測試資料
```javascript
// 審核操作測試資料
const reviewTests = {
  approve: {
    opinionId: "opinion_pending_001",
    action: "approve",
    comment: "內容符合規範，予以核准",
    expectedStatus: "approved"
  },
  reject: {
    opinionId: "opinion_pending_002",
    action: "reject",
    reason: "內容不符合社群規範",
    expectedStatus: "rejected"
  },
  batchApprove: {
    opinionIds: ["opinion_pending_003", "opinion_pending_004", "opinion_pending_005"],
    action: "approve",
    expectedCount: 3
  }
};

// UI 互動測試
const uiTests = {
  confirmDialog: {
    displayed: true,
    hasTitle: true,
    hasMessage: true,
    hasButtons: ["確認", "取消"]
  },
  successMessage: {
    displayed: true,
    autoClose: true,
    duration: 3000
  }
};
```

---

## 6. 測試資料參考

### 6.1 測試用戶

```python
test_users = {
    "citizen": {
        "username": "test_citizen",
        "password": "Citizen123!",
        "email": "citizen@test.com",
        "role": "citizen"
    },
    "admin": {
        "username": "test_admin",
        "password": "Admin123!",
        "email": "admin@test.com",
        "role": "admin"
    },
    "government": {
        "username": "test_gov",
        "password": "Gov123!",
        "email": "gov@test.com",
        "role": "government"
    }
}
```

### 6.2 測試意見

```python
test_opinions = [
    {
        "id": "opinion_001",
        "title": "改善市中心交通",
        "description": "建議增加公車班次",
        "category": "交通",
        "status": "approved"
    },
    {
        "id": "opinion_002",
        "title": "增設公園綠地",
        "description": "社區需要更多綠地空間",
        "category": "環境",
        "status": "pending"
    },
    {
        "id": "opinion_003",
        "title": "修復人行道",
        "description": "多處人行道破損需要修復",
        "category": "公共設施",
        "status": "approved"
    }
]
```

### 6.3 測試分類

```python
test_categories = [
    {"id": "cat_001", "name": "交通", "color": "#FF5733"},
    {"id": "cat_002", "name": "環境", "color": "#33FF57"},
    {"id": "cat_003", "name": "公共設施", "color": "#3357FF"},
    {"id": "cat_004", "name": "都市規劃", "color": "#F333FF"},
    {"id": "cat_005", "name": "其他", "color": "#888888"}
]
```

### 6.4 測試媒體檔案

```python
test_media = {
    "image_jpeg": {
        "filename": "test_image.jpg",
        "size": 2 * 1024 * 1024,  # 2MB
        "mime_type": "image/jpeg"
    },
    "image_png": {
        "filename": "test_image.png",
        "size": 1.5 * 1024 * 1024,  # 1.5MB
        "mime_type": "image/png"
    },
    "video_mp4": {
        "filename": "test_video.mp4",
        "size": 50 * 1024 * 1024,  # 50MB
        "mime_type": "video/mp4"
    }
}
```

### 6.5 測試環境變數

```bash
# API 端點
API_BASE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:5173

# 資料庫
DB_HOST=localhost
DB_PORT=3306
DB_NAME=citizen_app_test
DB_USER=test_user
DB_PASSWORD=test_password

# JWT
JWT_SECRET=test_secret_key_for_testing_only
JWT_EXPIRATION=86400  # 24 hours

# 儲存
MEDIA_STORAGE_PATH=/tmp/test_media
MAX_FILE_SIZE=104857600  # 100MB
```

---

## 附錄

### A. 測試執行記錄範本

```markdown
| 測試案例 ID | 執行日期 | 執行人 | 狀態 | 備註 |
|-----------|---------|-------|------|------|
| TC-AUTH-001 | 2025-10-24 | Tester A | PASS | - |
| TC-AUTH-002 | 2025-10-24 | Tester A | PASS | - |
| TC-AUTH-003 | 2025-10-24 | Tester A | FAIL | 詳見缺陷 #001 |
```

### B. 缺陷報告範本

```markdown
**缺陷 ID**: BUG-001
**測試案例**: TC-AUTH-003
**嚴重性**: High
**優先級**: High
**狀態**: Open

**描述**: 用戶登入失敗時返回 500 錯誤而非 401

**重現步驟**:
1. 使用錯誤的密碼嘗試登入
2. 觀察返回的 HTTP 狀態碼

**預期結果**: HTTP 401 Unauthorized
**實際結果**: HTTP 500 Internal Server Error

**環境**: Development
**測試人員**: Tester A
**發現日期**: 2025-10-24
```

### C. 測試覆蓋率目標

| 模組 | 單元測試 | 整合測試 | 系統測試 |
|-----|---------|---------|---------|
| 認證系統 | 90%+ | 100% | 100% |
| 意見系統 | 85%+ | 100% | 100% |
| 媒體系統 | 80%+ | 100% | 80% |
| 管理系統 | 85%+ | 100% | 100% |
| 前端系統 | 75%+ | 80% | 100% |

---

**文件狀態**: ✅ 已完成
**下次審查日期**: 測試執行後
**批准人**: V&V Team Lead
**版本歷史**:
- v1.0 (2025-10-24): 初版建立，包含 25 個詳細測試案例
