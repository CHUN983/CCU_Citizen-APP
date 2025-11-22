-- AI Content Moderation System - Database Migration (Safe Version)
-- Description: Add tables and columns for AI-powered content moderation
-- Date: 2025-11-21
-- Version: 1.1 (Compatible with all MySQL 8.0+)

-- ============================================================================
-- 1. Add moderation-related columns to opinions table
-- ============================================================================

-- Add columns one by one (safer approach)
ALTER TABLE opinions ADD COLUMN auto_moderation_status ENUM('pending', 'approved', 'rejected', 'flagged', 'reviewing') DEFAULT 'pending' COMMENT 'AI自動審核狀態';
ALTER TABLE opinions ADD COLUMN auto_moderation_score DECIMAL(5, 2) DEFAULT NULL COMMENT 'AI審核信心度分數(0-100)';
ALTER TABLE opinions ADD COLUMN auto_category_id INT DEFAULT NULL COMMENT 'AI建議的分類';
ALTER TABLE opinions ADD COLUMN moderation_reason TEXT DEFAULT NULL COMMENT 'AI審核原因或標記說明';
ALTER TABLE opinions ADD COLUMN needs_manual_review BOOLEAN DEFAULT FALSE COMMENT '是否需要人工審核';
ALTER TABLE opinions ADD COLUMN reviewed_by INT DEFAULT NULL COMMENT '人工審核者ID';
ALTER TABLE opinions ADD COLUMN reviewed_at TIMESTAMP NULL COMMENT '人工審核時間';

-- Add indexes
ALTER TABLE opinions ADD INDEX idx_auto_moderation (auto_moderation_status);
ALTER TABLE opinions ADD INDEX idx_manual_review (needs_manual_review);

-- Add foreign keys
ALTER TABLE opinions ADD CONSTRAINT fk_auto_category FOREIGN KEY (auto_category_id) REFERENCES categories(id) ON DELETE SET NULL;
ALTER TABLE opinions ADD CONSTRAINT fk_reviewed_by FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL;


-- ============================================================================
-- 2. Create moderation_logs table - 記錄所有AI審核決策
-- ============================================================================

CREATE TABLE IF NOT EXISTS moderation_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    opinion_id INT NOT NULL,
    moderation_type ENUM('text', 'image', 'video') NOT NULL COMMENT '審核類型',
    service_provider ENUM('openai', 'google', 'custom') DEFAULT 'openai' COMMENT 'AI服務提供商',

    -- 審核結果
    decision ENUM('approve', 'reject', 'flag', 'review') NOT NULL COMMENT '審核決策',
    confidence_score DECIMAL(5, 2) NOT NULL COMMENT '信心度分數(0-100)',

    -- 分類建議
    suggested_category_id INT DEFAULT NULL COMMENT 'AI建議分類',
    category_confidence DECIMAL(5, 2) DEFAULT NULL COMMENT '分類信心度',

    -- 安全檢測結果
    is_safe BOOLEAN NOT NULL COMMENT '是否安全',
    detected_issues JSON COMMENT '檢測到的問題(JSON格式): {violence: 0.1, hate: 0.9, ...}',

    -- API回應詳情
    api_request JSON COMMENT 'API請求內容',
    api_response JSON COMMENT 'API完整回應',
    processing_time_ms INT COMMENT '處理時間(毫秒)',

    -- 規則引擎結果
    blocked_by_keywords TEXT COMMENT '觸發的黑名單關鍵字',
    matched_category_keywords TEXT COMMENT '匹配的分類關鍵字',

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (opinion_id) REFERENCES opinions(id) ON DELETE CASCADE,
    FOREIGN KEY (suggested_category_id) REFERENCES categories(id) ON DELETE SET NULL,
    INDEX idx_opinion (opinion_id),
    INDEX idx_decision (decision),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================================
-- 3. Create sensitive_words table - 敏感詞黑名單
-- ============================================================================

CREATE TABLE IF NOT EXISTS sensitive_words (
    id INT AUTO_INCREMENT PRIMARY KEY,
    word VARCHAR(100) NOT NULL UNIQUE COMMENT '敏感詞',
    category ENUM('violence', 'hate', 'sexual', 'spam', 'political', 'other') NOT NULL COMMENT '類別',
    severity ENUM('high', 'medium', 'low') DEFAULT 'high' COMMENT '嚴重程度',
    action ENUM('reject', 'flag', 'review') DEFAULT 'reject' COMMENT '觸發動作',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否啟用',
    description TEXT COMMENT '說明',
    added_by INT NOT NULL COMMENT '添加者',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (added_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_word (word),
    INDEX idx_category (category),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================================
-- 4. Create category_keywords table - 分類關鍵字庫
-- ============================================================================

CREATE TABLE IF NOT EXISTS category_keywords (
    id INT AUTO_INCREMENT PRIMARY KEY,
    category_id INT NOT NULL,
    keyword VARCHAR(100) NOT NULL COMMENT '關鍵字',
    weight DECIMAL(3, 2) DEFAULT 1.0 COMMENT '權重(0.1-2.0)',
    is_active BOOLEAN DEFAULT TRUE COMMENT '是否啟用',
    added_by INT NOT NULL COMMENT '添加者',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    FOREIGN KEY (added_by) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_category_keyword (category_id, keyword),
    INDEX idx_keyword (keyword),
    INDEX idx_category (category_id),
    INDEX idx_active (is_active)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================================
-- 5. Create moderation_config table - 審核配置
-- ============================================================================

CREATE TABLE IF NOT EXISTS moderation_config (
    id INT AUTO_INCREMENT PRIMARY KEY,
    config_key VARCHAR(100) NOT NULL UNIQUE COMMENT '配置鍵',
    config_value TEXT NOT NULL COMMENT '配置值',
    value_type ENUM('string', 'number', 'boolean', 'json') DEFAULT 'string' COMMENT '值類型',
    description TEXT COMMENT '配置說明',
    updated_by INT NOT NULL COMMENT '更新者',
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

    FOREIGN KEY (updated_by) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_key (config_key)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- ============================================================================
-- 6. Insert default moderation configurations
-- ============================================================================

INSERT INTO moderation_config (config_key, config_value, value_type, description, updated_by) VALUES
('ai_moderation_enabled', 'true', 'boolean', '是否啟用AI審核', 1),
('auto_approve_threshold', '80', 'number', '自動通過閾值(信心度>=此值自動通過)', 1),
('auto_reject_threshold', '90', 'number', '自動拒絕閾值(惡意內容信心度>=此值自動拒絕)', 1),
('manual_review_threshold', '60', 'number', '人工審核閾值(信心度<此值需人工審核)', 1),
('openai_api_key', '', 'string', 'OpenAI API金鑰', 1),
('openai_model', 'gpt-4o-mini', 'string', 'OpenAI模型名稱(用於分類)', 1),
('enable_keyword_filter', 'true', 'boolean', '是否啟用關鍵字過濾', 1),
('enable_category_keywords', 'true', 'boolean', '是否啟用分類關鍵字輔助', 1),
('async_moderation', 'true', 'boolean', '是否使用異步審核', 1),
('moderation_timeout_seconds', '10', 'number', 'AI審核超時時間(秒)', 1)
ON DUPLICATE KEY UPDATE
    config_value = VALUES(config_value),
    updated_at = CURRENT_TIMESTAMP;


-- ============================================================================
-- 7. Insert sample sensitive words (範例敏感詞)
-- ============================================================================

INSERT INTO sensitive_words (word, category, severity, action, added_by, description) VALUES
-- 暴力相關
('殺人', 'violence', 'high', 'reject', 1, '暴力威脅'),
('殺害', 'violence', 'high', 'reject', 1, '暴力威脅'),
('自殺', 'violence', 'high', 'flag', 1, '自殺相關內容需要關注'),

-- 仇恨與歧視
('種族歧視', 'hate', 'high', 'reject', 1, '種族歧視內容'),
('性別歧視', 'hate', 'high', 'reject', 1, '性別歧視內容'),

-- 不雅內容
('色情', 'sexual', 'high', 'reject', 1, '色情內容'),
('裸露', 'sexual', 'medium', 'flag', 1, '可能不當內容'),

-- 垃圾與詐騙
('詐騙', 'spam', 'high', 'flag', 1, '可能詐騙內容'),
('廣告', 'spam', 'medium', 'review', 1, '廣告內容')
ON DUPLICATE KEY UPDATE word = VALUES(word);


-- ============================================================================
-- 8. Insert sample category keywords (範例分類關鍵字)
-- ============================================================================

-- 交通局 (id=1)
INSERT INTO category_keywords (category_id, keyword, weight, added_by) VALUES
(1, '交通', 1.5, 1),
(1, '道路', 1.5, 1),
(1, '紅綠燈', 1.8, 1),
(1, '公車', 1.5, 1),
(1, '捷運', 1.5, 1),
(1, '停車', 1.5, 1),
(1, '路面', 1.3, 1),
(1, '號誌', 1.5, 1),
(1, '斑馬線', 1.5, 1)
ON DUPLICATE KEY UPDATE keyword = VALUES(keyword);

-- 環保局 (id=2)
INSERT INTO category_keywords (category_id, keyword, weight, added_by) VALUES
(2, '環保', 1.5, 1),
(2, '垃圾', 1.5, 1),
(2, '清潔', 1.3, 1),
(2, '污染', 1.5, 1),
(2, '空氣', 1.3, 1),
(2, '噪音', 1.5, 1),
(2, '回收', 1.5, 1),
(2, '綠化', 1.3, 1),
(2, '樹木', 1.2, 1)
ON DUPLICATE KEY UPDATE keyword = VALUES(keyword);

-- 工務局 (id=3)
INSERT INTO category_keywords (category_id, keyword, weight, added_by) VALUES
(3, '公園', 1.5, 1),
(3, '施工', 1.5, 1),
(3, '路燈', 1.5, 1),
(3, '運動場', 1.5, 1),
(3, '人行道', 1.3, 1),
(3, '下水道', 1.5, 1),
(3, '水溝', 1.3, 1),
(3, '路面', 1.2, 1),
(3, '坑洞', 1.5, 1)
ON DUPLICATE KEY UPDATE keyword = VALUES(keyword);

-- 社會局 (id=4)
INSERT INTO category_keywords (category_id, keyword, weight, added_by) VALUES
(4, '社會福利', 1.8, 1),
(4, '老人', 1.3, 1),
(4, '兒童', 1.3, 1),
(4, '身障', 1.5, 1),
(4, '弱勢', 1.3, 1),
(4, '補助', 1.5, 1),
(4, '照顧', 1.2, 1),
(4, '托育', 1.5, 1)
ON DUPLICATE KEY UPDATE keyword = VALUES(keyword);

-- 衛生局 (id=5)
INSERT INTO category_keywords (category_id, keyword, weight, added_by) VALUES
(5, '衛生', 1.5, 1),
(5, '醫療', 1.5, 1),
(5, '食品安全', 1.8, 1),
(5, '餐廳', 1.3, 1),
(5, '診所', 1.3, 1),
(5, '藥局', 1.3, 1),
(5, '疫苗', 1.5, 1),
(5, '傳染病', 1.5, 1)
ON DUPLICATE KEY UPDATE keyword = VALUES(keyword);

-- 警察局 (id=6)
INSERT INTO category_keywords (category_id, keyword, weight, added_by) VALUES
(6, '治安', 1.5, 1),
(6, '警察', 1.5, 1),
(6, '噪音', 1.3, 1),
(6, '違停', 1.5, 1),
(6, '檢舉', 1.3, 1),
(6, '安全', 1.2, 1),
(6, '巡邏', 1.3, 1),
(6, '犯罪', 1.5, 1)
ON DUPLICATE KEY UPDATE keyword = VALUES(keyword);

-- 教育局 (id=7)
INSERT INTO category_keywords (category_id, keyword, weight, added_by) VALUES
(7, '教育', 1.5, 1),
(7, '學校', 1.5, 1),
(7, '圖書館', 1.5, 1),
(7, '體育場', 1.5, 1),
(7, '學區', 1.5, 1),
(7, '課程', 1.3, 1),
(7, '教師', 1.3, 1),
(7, '學生', 1.2, 1)
ON DUPLICATE KEY UPDATE keyword = VALUES(keyword);

-- 都發局 (id=8)
INSERT INTO category_keywords (category_id, keyword, weight, added_by) VALUES
(8, '都市規劃', 1.8, 1),
(8, '土地', 1.5, 1),
(8, '開發', 1.5, 1),
(8, '建築', 1.3, 1),
(8, '容積', 1.5, 1),
(8, '分區', 1.5, 1),
(8, '變更', 1.3, 1),
(8, '使用執照', 1.5, 1)
ON DUPLICATE KEY UPDATE keyword = VALUES(keyword);

-- 民政局 (id=9)
INSERT INTO category_keywords (category_id, keyword, weight, added_by) VALUES
(9, '民政', 1.5, 1),
(9, '社區', 1.3, 1),
(9, '鄰里', 1.5, 1),
(9, '里長', 1.3, 1),
(9, '公墓', 1.8, 1),
(9, '殯葬', 1.8, 1),
(9, '宗教', 1.3, 1),
(9, '活動中心', 1.5, 1)
ON DUPLICATE KEY UPDATE keyword = VALUES(keyword);


-- ============================================================================
-- Migration complete!
-- ============================================================================

SELECT 'AI Moderation System migration completed successfully!' AS status;
