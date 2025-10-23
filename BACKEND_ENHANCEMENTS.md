# 後端補強更新報告

## 🎯 更新日期：2025-10-24

## ✅ 已完成的補強功能

### 1. **檔案上傳系統（Media Upload API）**

#### 新增端點：
- `POST /media/upload` - 上傳單一媒體檔案（圖片/影片/音訊）
- `POST /media/upload-multiple` - 批次上傳多個檔案（最多 10 個）
- `GET /media/files/{media_type}/{filename}` - 取得媒體檔案
- `GET /media/thumbnails/{filename}` - 取得圖片縮圖
- `DELETE /media/files/{media_type}/{filename}` - 刪除媒體檔案（限管理員）

#### 功能特色：
✅ **多媒體支援**：
  - 圖片：.jpg, .jpeg, .png, .gif, .webp（最大 10MB）
  - 影片：.mp4, .avi, .mov, .wmv, .flv, .webm（最大 50MB）
  - 音訊：.mp3, .wav, .ogg, .m4a, .aac（最大 50MB）

✅ **圖片自動處理**：
  - 自動壓縮（最大 1920x1080，品質 85%）
  - 自動生成縮圖（300x300）
  - RGBA 轉 RGB 處理

✅ **安全機制**：
  - 檔案大小驗證
  - 檔案類型檢查
  - UUID 唯一檔名
  - 用戶認證要求

#### 檔案結構：
```
uploads/
├── images/          # 圖片儲存
├── videos/          # 影片儲存
├── audio/           # 音訊儲存
└── thumbnails/      # 縮圖儲存
```

---

### 2. **4 層權限控制系統**

#### 角色定義：
1. **訪客（Guest）**：
   - 不需登入
   - 只能瀏覽公開內容
   - 無法發表意見或留言

2. **市民（Citizen）**：
   - 一般註冊用戶
   - 可發表意見
   - 可留言、投票、收藏
   - 預設角色

3. **行政人員（Government Staff）**：
   - 政府相關人員
   - 可審核意見（核准/拒絕）
   - 可合併相似意見
   - 可修改分類與標籤

4. **管理員（Admin/Moderator）**：
   - 系統管理員與版主
   - 最高權限
   - 可刪除留言
   - 可管理用戶

#### 權限依賴函數：
```python
# 使用方式
@router.post("/admin/opinions/{id}/approve")
async def approve_opinion(
    current_user: User = Depends(require_government_staff)  # 限政府人員以上
):
    ...

@router.delete("/comments/{id}")
async def delete_comment(
    current_user: User = Depends(require_admin)  # 限管理員
):
    ...
```

#### 可用依賴：
- `get_current_user()` - 取得當前用戶（任何已登入用戶）
- `require_government_staff()` - 需要行政人員權限
- `require_moderator()` - 需要版主權限
- `require_admin()` - 需要管理員權限

---

## 📊 更新的檔案清單

### 新增檔案：
1. `src/main/python/api/media.py` - 媒體上傳 API
2. `src/main/resources/config/update_roles.sql` - 角色更新腳本
3. `BACKEND_ENHANCEMENTS.md` - 本文件

### 修改檔案：
1. `src/main/python/core/app.py` - 註冊 media router
2. `src/main/python/utils/security.py` - 新增權限依賴函數
3. `src/main/python/models/user.py` - 更新 UserRole 枚舉
4. `requirements.txt` - 新增 Pillow 依賴

### 資料庫變更：
```sql
-- users 表的 role 欄位更新
role ENUM('citizen', 'government_staff', 'moderator', 'admin')
```

---

## 🔧 安裝與使用

### 1. 安裝新依賴：
```bash
source venv/bin/activate
pip install Pillow==10.2.0
```

### 2. 更新資料庫：
```bash
mysql -u root -p citizen_app < src/main/resources/config/update_roles.sql
```

### 3. 啟動伺服器：
```bash
./setup_and_run.sh
# 或
python -m uvicorn src.main.python.core.app:app --host 0.0.0.0 --port 8000 --reload
```

---

## 📝 API 使用範例

### 上傳圖片：
```bash
curl -X POST "http://localhost:8000/media/upload" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -F "file=@photo.jpg"
```

### 回應範例：
```json
{
  "filename": "550e8400-e29b-41d4-a716-446655440000.jpg",
  "media_type": "image",
  "file_path": "images/550e8400-e29b-41d4-a716-446655440000.jpg",
  "file_size": 245678,
  "mime_type": "image/jpeg",
  "url": "/media/files/images/550e8400-e29b-41d4-a716-446655440000.jpg",
  "thumbnail_url": "/media/thumbnails/550e8400-e29b-41d4-a716-446655440000.jpg"
}
```

### 取得圖片：
```bash
# 原圖
http://localhost:8000/media/files/images/550e8400-e29b-41d4-a716-446655440000.jpg

# 縮圖
http://localhost:8000/media/thumbnails/550e8400-e29b-41d4-a716-446655440000.jpg
```

---

## 🎯 接下來要做的

### 優先級 1：AI 自動分類服務
- [ ] 整合 NLP 模型（情緒分析）
- [ ] 惡意內容偵測
- [ ] 自動分類建議
- [ ] 相似意見偵測

### 優先級 2：意見系統整合
- [ ] 在發表意見時上傳媒體
- [ ] 顯示媒體附件
- [ ] 媒體與意見的關聯

### 優先級 3：通知系統
- [ ] WebSocket 即時通知
- [ ] 推播通知整合
- [ ] Email 通知

---

## 📊 當前 API 端點總覽（共 24 個）

### 認證（3 個）
- `POST /auth/register` - 註冊
- `POST /auth/login` - 登入
- `GET /auth/me` - 取得當前用戶

### 意見（8 個）
- `POST /opinions` - 建立意見
- `GET /opinions` - 意見列表
- `GET /opinions/{id}` - 意見詳情
- `POST /opinions/{id}/comments` - 新增留言
- `POST /opinions/{id}/vote` - 投票
- `POST /opinions/{id}/collect` - 收藏
- `DELETE /opinions/{id}/collect` - 取消收藏

### 通知（2 個）
- `GET /notifications` - 通知列表
- `POST /notifications/{id}/read` - 標記已讀

### 管理（5 個）
- `POST /admin/opinions/{id}/approve` - 核准
- `POST /admin/opinions/{id}/reject` - 拒絕
- `POST /admin/opinions/{id}/merge` - 合併
- `DELETE /admin/comments/{id}` - 刪除留言
- `PUT /admin/opinions/{id}/category` - 更新分類

### 媒體（NEW - 6 個）
- `POST /media/upload` - 上傳單一檔案
- `POST /media/upload-multiple` - 批次上傳
- `GET /media/files/{type}/{filename}` - 取得檔案
- `GET /media/thumbnails/{filename}` - 取得縮圖
- `DELETE /media/files/{type}/{filename}` - 刪除檔案

---

## 🔐 權限矩陣

| 功能 | 訪客 | 市民 | 行政人員 | 管理員 |
|------|------|------|---------|--------|
| 瀏覽公開意見 | ✅ | ✅ | ✅ | ✅ |
| 發表意見 | ❌ | ✅ | ✅ | ✅ |
| 留言/投票 | ❌ | ✅ | ✅ | ✅ |
| 上傳媒體 | ❌ | ✅ | ✅ | ✅ |
| 審核意見 | ❌ | ❌ | ✅ | ✅ |
| 合併意見 | ❌ | ❌ | ✅ | ✅ |
| 刪除留言 | ❌ | ❌ | ❌ | ✅ |
| 刪除媒體 | ❌ | ❌ | ❌ | ✅ |
| 用戶管理 | ❌ | ❌ | ❌ | ✅ |

---

## 📞 互動式 API 文件

啟動伺服器後訪問：
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

所有新功能都已自動加入文件，可直接測試！

---

**更新者**: Claude Code
**版本**: 1.1.0
**狀態**: ✅ 已完成並測試
