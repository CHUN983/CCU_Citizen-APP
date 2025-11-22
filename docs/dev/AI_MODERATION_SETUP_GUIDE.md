# AI 自動審核系統 - 部署與配置指南

> **版本**: 1.0
> **更新日期**: 2025-11-21
> **適用範圍**: citizenApp AI內容審核功能

## 📋 目錄

1. [系統概述](#系統概述)
2. [功能特點](#功能特點)
3. [資料庫遷移](#資料庫遷移)
4. [配置步驟](#配置步驟)
5. [使用說明](#使用說明)
6. [管理與維護](#管理與維護)
7. [故障排除](#故障排除)

---

## 系統概述

AI自動審核系統是一個智能內容審核解決方案,用於自動化市民意見的分類與內容安全檢測。系統包含以下核心功能:

### 主要組件

```
┌─────────────────────────────────────────────────────┐
│                  意見提交流程                         │
├─────────────────────────────────────────────────────┤
│                                                     │
│  用戶提交意見                                        │
│       ↓                                             │
│  保存到資料庫 (status: pending)                      │
│       ↓                                             │
│  [後台異步] AI審核任務啟動                           │
│       ├─→ 文本內容審核 (OpenAI Moderation API)      │
│       │   ├─ 安全檢測 (暴力、仇恨、色情等)           │
│       │   ├─ 敏感詞黑名單檢查                        │
│       │   └─ 自動分類 (OpenAI GPT + 關鍵字)         │
│       │                                             │
│       └─→ 多媒體內容審核 (OpenAI Vision API)        │
│           ├─ 圖片內容檢測                           │
│           └─ 視頻內容檢測 (未來支持)                │
│       ↓                                             │
│  AI決策引擎                                          │
│       ├─→ auto_reject (惡意內容, 直接拒絕)          │
│       ├─→ auto_approve (高信心度, 自動通過)         │
│       ├─→ flagged (標記, 需關注)                    │
│       └─→ reviewing (低信心度, 需人工審核)          │
│       ↓                                             │
│  更新意見審核狀態                                     │
│  記錄審核日誌                                         │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 功能特點

### ✅ 已實現功能

1. **文本安全檢測**
   - 使用 OpenAI Moderation API 檢測不當內容
   - 檢測類別: 暴力、仇恨、色情、自殘、騷擾等
   - 完全免費

2. **智能自動分類**
   - 關鍵字匹配分類 (速度快, 基於預設規則)
   - AI智能分類 (準確度高, 使用 GPT-4o-mini)
   - 混合策略 (關鍵字+AI, 平衡速度與準確度)

3. **敏感詞黑名單**
   - 可自定義敏感詞列表
   - 支持不同嚴重等級 (high/medium/low)
   - 支持不同處理動作 (reject/flag/review)

4. **圖片內容檢測**
   - 使用 OpenAI Vision API 分析圖片
   - 檢測不當圖片內容

5. **異步處理**
   - 用戶提交不需等待AI審核
   - 後台線程處理, 不影響用戶體驗

6. **完整審核日誌**
   - 記錄所有AI決策過程
   - 可追溯、可審計

---

## 資料庫遷移

### 步驟 1: 執行SQL遷移腳本

```bash
# 連接到MySQL資料庫
mysql -u your_username -p your_database < src/main/resources/config/add_ai_moderation.sql
```

### 步驟 2: 驗證表創建

```sql
-- 檢查新表是否創建成功
SHOW TABLES LIKE '%moderation%';
SHOW TABLES LIKE '%sensitive%';
SHOW TABLES LIKE '%category_keywords%';

-- 應該看到以下表:
-- - moderation_logs
-- - sensitive_words
-- - category_keywords
-- - moderation_config

-- 檢查opinions表是否添加了新欄位
DESC opinions;
-- 應該看到以下新欄位:
-- - auto_moderation_status
-- - auto_moderation_score
-- - auto_category_id
-- - moderation_reason
-- - needs_manual_review
-- - reviewed_by
-- - reviewed_at
```

### 步驟 3: 確認預設數據

```sql
-- 檢查預設配置
SELECT * FROM moderation_config;

-- 檢查範例敏感詞
SELECT * FROM sensitive_words;

-- 檢查分類關鍵字
SELECT * FROM category_keywords LIMIT 20;
```

---

## 配置步驟

### 1. 設置 OpenAI API 金鑰

```sql
-- 更新OpenAI API金鑰
UPDATE moderation_config
SET config_value = 'sk-your-api-key-here'
WHERE config_key = 'openai_api_key';
```

> **獲取API金鑰**: 前往 [OpenAI Platform](https://platform.openai.com/api-keys) 創建API金鑰

### 2. 安裝Python依賴

確保安裝了 `requests` 庫:

```bash
pip install requests
```

### 3. 配置審核參數

根據您的需求調整審核閾值:

```sql
-- 自動通過閾值 (信心度 >= 80 自動通過)
UPDATE moderation_config
SET config_value = '80'
WHERE config_key = 'auto_approve_threshold';

-- 自動拒絕閾值 (惡意內容信心度 >= 90 自動拒絕)
UPDATE moderation_config
SET config_value = '90'
WHERE config_key = 'auto_reject_threshold';

-- 人工審核閾值 (信心度 < 60 需人工審核)
UPDATE moderation_config
SET config_value = '60'
WHERE config_key = 'manual_review_threshold';

-- 啟用/停用AI審核
UPDATE moderation_config
SET config_value = 'true'  -- 或 'false' 停用
WHERE config_key = 'ai_moderation_enabled';
```

### 4. 自定義敏感詞黑名單

```sql
-- 添加敏感詞
INSERT INTO sensitive_words (word, category, severity, action, added_by, description)
VALUES
('不當詞彙', 'hate', 'high', 'reject', 1, '種族歧視內容'),
('垃圾廣告', 'spam', 'medium', 'flag', 1, '廣告內容');

-- 停用某個敏感詞
UPDATE sensitive_words
SET is_active = FALSE
WHERE word = '某個詞';
```

### 5. 配置分類關鍵字

```sql
-- 為交通局添加關鍵字
INSERT INTO category_keywords (category_id, keyword, weight, added_by)
VALUES
(1, '塞車', 1.5, 1),
(1, '紅燈', 1.5, 1);

-- 調整關鍵字權重
UPDATE category_keywords
SET weight = 2.0
WHERE keyword = '塞車';
```

---

## 使用說明

### API使用

系統會自動在用戶提交意見時觸發AI審核,無需額外API調用。

**提交意見API** (已集成AI審核):

```bash
POST /api/opinions
Authorization: Bearer <token>
Content-Type: application/json

{
  "title": "道路坑洞問題",
  "content": "某某路段有嚴重坑洞,影響行車安全",
  "category_id": 1,
  "region": "大安區",
  "tags": ["道路", "安全"],
  "media_files": []
}
```

**回應**:

```json
{
  "id": 123,
  "title": "道路坑洞問題",
  "content": "某某路段有嚴重坑洞,影響行車安全",
  "status": "pending",
  "auto_moderation_status": "pending",  // AI審核正在進行
  "category_id": 1,
  ...
}
```

### 查看審核狀態

```sql
-- 查看特定意見的審核狀態
SELECT
    id, title, status,
    auto_moderation_status,
    auto_moderation_score,
    needs_manual_review,
    moderation_reason
FROM opinions
WHERE id = 123;

-- 查看審核日誌
SELECT
    moderation_type,
    decision,
    confidence_score,
    suggested_category_id,
    is_safe,
    detected_issues,
    processing_time_ms,
    created_at
FROM moderation_logs
WHERE opinion_id = 123;
```

### 審核狀態說明

| 狀態 | 說明 | 需要人工處理 |
|------|------|-------------|
| `pending` | 審核中 | 否 |
| `approved` | 自動通過 | 否 |
| `rejected` | 自動拒絕 | 否 |
| `flagged` | 已標記 | 是 |
| `reviewing` | 需審核 | 是 |

---

## 管理與維護

### 1. 監控審核效能

```sql
-- 查看今日審核統計
SELECT
    auto_moderation_status,
    COUNT(*) as count,
    AVG(auto_moderation_score) as avg_confidence
FROM opinions
WHERE DATE(created_at) = CURDATE()
GROUP BY auto_moderation_status;

-- 查看需要人工審核的意見數量
SELECT COUNT(*)
FROM opinions
WHERE needs_manual_review = TRUE
  AND reviewed_by IS NULL;

-- 查看平均處理時間
SELECT
    moderation_type,
    AVG(processing_time_ms) as avg_ms,
    MAX(processing_time_ms) as max_ms
FROM moderation_logs
WHERE DATE(created_at) = CURDATE()
GROUP BY moderation_type;
```

### 2. 審核日誌分析

```sql
-- 查看被拒絕的內容分類
SELECT
    detected_issues,
    COUNT(*) as count
FROM moderation_logs
WHERE decision = 'reject'
  AND DATE(created_at) >= DATE_SUB(CURDATE(), INTERVAL 7 DAY)
GROUP BY detected_issues;

-- 查看誤判案例 (人工審核通過但AI拒絕的)
SELECT o.id, o.title, o.auto_moderation_status, o.status
FROM opinions o
WHERE o.auto_moderation_status = 'rejected'
  AND o.status = 'approved'
  AND o.reviewed_by IS NOT NULL;
```

### 3. 優化分類準確度

基於審核日誌優化關鍵字:

```sql
-- 查看AI建議的分類與實際分類的差異
SELECT
    o.category_id as actual_category,
    o.auto_category_id as suggested_category,
    COUNT(*) as count
FROM opinions o
WHERE o.category_id != o.auto_category_id
  AND o.auto_category_id IS NOT NULL
GROUP BY o.category_id, o.auto_category_id
ORDER BY count DESC;
```

---

## 故障排除

### 問題 1: API金鑰無效

**症狀**: 所有意見都標記為 `needs_manual_review`

**解決方案**:
```sql
-- 檢查API金鑰
SELECT config_value FROM moderation_config WHERE config_key = 'openai_api_key';

-- 確保金鑰有效且有餘額
-- 前往 https://platform.openai.com/account/usage 檢查
```

### 問題 2: 審核速度過慢

**症狀**: 用戶提交後很久才完成審核

**可能原因**:
- OpenAI API延遲
- 網絡問題
- 圖片檔案過大

**解決方案**:
```sql
-- 檢查處理時間
SELECT
    opinion_id,
    processing_time_ms,
    moderation_type
FROM moderation_logs
WHERE processing_time_ms > 5000
ORDER BY created_at DESC
LIMIT 20;

-- 考慮調整超時設置
UPDATE moderation_config
SET config_value = '15'
WHERE config_key = 'moderation_timeout_seconds';
```

### 問題 3: 審核未執行

**症狀**: `auto_moderation_status` 一直是 `NULL`

**檢查清單**:
1. 確認AI審核已啟用:
```sql
SELECT config_value FROM moderation_config WHERE config_key = 'ai_moderation_enabled';
```

2. 檢查後端日誌是否有錯誤訊息

3. 確認 `requests` 庫已安裝:
```bash
python -c "import requests; print('OK')"
```

### 問題 4: 分類不準確

**解決方案**:
1. 增加更多分類關鍵字
2. 調整關鍵字權重
3. 更新OpenAI模型 (使用更強大的模型)

```sql
-- 切換到更強大的模型 (成本較高)
UPDATE moderation_config
SET config_value = 'gpt-4o'
WHERE config_key = 'openai_model';
```

---

## 成本估算

### OpenAI API 定價 (2025年估算)

| 服務 | 模型 | 價格 | 使用量估算 |
|------|------|------|----------|
| Moderation API | text-moderation-latest | **免費** | 無限制 |
| Text Classification | gpt-4o-mini | ~$0.00015/1K tokens | 每筆意見 ~0.0003元 |
| Vision API | gpt-4o-mini | ~$0.001/image | 每張圖片 ~0.001元 |

**估算範例** (每月1000筆意見):
- 文本審核: 1000 × $0.0003 = **$0.30 USD**
- 圖片審核(假設500張): 500 × $0.001 = **$0.50 USD**
- **總計: ~$0.80 USD/月**

---

## 下一步

1. ✅ 完成基礎部署
2. 🔄 測試各種案例
3. 📊 收集數據,優化閾值
4. 🎯 添加管理後台界面
5. 📈 持續優化分類準確度

---

## 支援與聯繫

如有問題,請查閱:
- [API文檔](../api/API_DOCUMENTATION.md)
- [系統設計規格](../design/SYSTEM_DESIGN_SPECIFICATION.txt)
- [專案總覽](PROJECT_SUMMARY.md)

---

**文檔版本**: 1.0
**最後更新**: 2025-11-21
