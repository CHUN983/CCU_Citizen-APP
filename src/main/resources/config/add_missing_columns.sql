-- Add missing moderation columns to opinions table
-- Run this if some columns are missing after initial migration

-- Add missing columns (will error if already exist - that's ok)
ALTER TABLE opinions
ADD COLUMN auto_category_id INT DEFAULT NULL COMMENT 'AI建議的分類';

ALTER TABLE opinions
ADD COLUMN needs_manual_review BOOLEAN DEFAULT FALSE COMMENT '是否需要人工審核';

ALTER TABLE opinions
ADD COLUMN reviewed_by INT DEFAULT NULL COMMENT '人工審核者ID';

ALTER TABLE opinions
ADD COLUMN reviewed_at TIMESTAMP NULL COMMENT '人工審核時間';

-- Add foreign keys (if not already added)
ALTER TABLE opinions
ADD CONSTRAINT fk_auto_category
FOREIGN KEY (auto_category_id) REFERENCES categories(id) ON DELETE SET NULL;

ALTER TABLE opinions
ADD CONSTRAINT fk_reviewed_by
FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL;

SELECT '✅ Missing columns added successfully!' AS status;
