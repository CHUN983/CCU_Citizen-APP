-- Add Missing AI Moderation Columns to opinions table
-- This script safely adds the missing columns that were not added during previous migration
-- Date: 2025-12-15

USE citizen_app;

-- ============================================================================
-- Add missing AI moderation columns to opinions table
-- ============================================================================

-- Add auto_category_id (AI建議的分類)
SET @check_column = (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = 'citizen_app'
    AND TABLE_NAME = 'opinions'
    AND COLUMN_NAME = 'auto_category_id'
);

SET @sql = IF(@check_column = 0,
    'ALTER TABLE opinions ADD COLUMN auto_category_id INT DEFAULT NULL COMMENT "AI建議的分類"',
    'SELECT "Column auto_category_id already exists" AS status'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add moderation_reason (AI審核原因或標記說明)
SET @check_column = (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = 'citizen_app'
    AND TABLE_NAME = 'opinions'
    AND COLUMN_NAME = 'moderation_reason'
);

SET @sql = IF(@check_column = 0,
    'ALTER TABLE opinions ADD COLUMN moderation_reason TEXT DEFAULT NULL COMMENT "AI審核原因或標記說明"',
    'SELECT "Column moderation_reason already exists" AS status'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add needs_manual_review (是否需要人工審核)
SET @check_column = (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = 'citizen_app'
    AND TABLE_NAME = 'opinions'
    AND COLUMN_NAME = 'needs_manual_review'
);

SET @sql = IF(@check_column = 0,
    'ALTER TABLE opinions ADD COLUMN needs_manual_review BOOLEAN DEFAULT FALSE COMMENT "是否需要人工審核"',
    'SELECT "Column needs_manual_review already exists" AS status'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add reviewed_by (人工審核者ID)
SET @check_column = (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = 'citizen_app'
    AND TABLE_NAME = 'opinions'
    AND COLUMN_NAME = 'reviewed_by'
);

SET @sql = IF(@check_column = 0,
    'ALTER TABLE opinions ADD COLUMN reviewed_by INT DEFAULT NULL COMMENT "人工審核者ID"',
    'SELECT "Column reviewed_by already exists" AS status'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add reviewed_at (人工審核時間)
SET @check_column = (
    SELECT COUNT(*)
    FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = 'citizen_app'
    AND TABLE_NAME = 'opinions'
    AND COLUMN_NAME = 'reviewed_at'
);

SET @sql = IF(@check_column = 0,
    'ALTER TABLE opinions ADD COLUMN reviewed_at TIMESTAMP NULL COMMENT "人工審核時間"',
    'SELECT "Column reviewed_at already exists" AS status'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ============================================================================
-- Add indexes (only if they don't exist)
-- ============================================================================

-- Add index on needs_manual_review
SET @check_index = (
    SELECT COUNT(*)
    FROM information_schema.STATISTICS
    WHERE TABLE_SCHEMA = 'citizen_app'
    AND TABLE_NAME = 'opinions'
    AND INDEX_NAME = 'idx_manual_review'
);

SET @sql = IF(@check_index = 0,
    'ALTER TABLE opinions ADD INDEX idx_manual_review (needs_manual_review)',
    'SELECT "Index idx_manual_review already exists" AS status'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ============================================================================
-- Add foreign key constraints (only if they don't exist)
-- ============================================================================

-- Add foreign key for auto_category_id
SET @check_fk = (
    SELECT COUNT(*)
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = 'citizen_app'
    AND TABLE_NAME = 'opinions'
    AND CONSTRAINT_NAME = 'fk_auto_category'
);

SET @sql = IF(@check_fk = 0,
    'ALTER TABLE opinions ADD CONSTRAINT fk_auto_category FOREIGN KEY (auto_category_id) REFERENCES categories(id) ON DELETE SET NULL',
    'SELECT "Foreign key fk_auto_category already exists" AS status'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- Add foreign key for reviewed_by
SET @check_fk = (
    SELECT COUNT(*)
    FROM information_schema.KEY_COLUMN_USAGE
    WHERE TABLE_SCHEMA = 'citizen_app'
    AND TABLE_NAME = 'opinions'
    AND CONSTRAINT_NAME = 'fk_reviewed_by'
);

SET @sql = IF(@check_fk = 0,
    'ALTER TABLE opinions ADD CONSTRAINT fk_reviewed_by FOREIGN KEY (reviewed_by) REFERENCES users(id) ON DELETE SET NULL',
    'SELECT "Foreign key fk_reviewed_by already exists" AS status'
);
PREPARE stmt FROM @sql;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;

-- ============================================================================
-- Verification
-- ============================================================================

SELECT 'Migration completed! Checking new columns...' AS status;

SELECT
    COLUMN_NAME,
    COLUMN_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT,
    COLUMN_COMMENT
FROM information_schema.COLUMNS
WHERE TABLE_SCHEMA = 'citizen_app'
AND TABLE_NAME = 'opinions'
AND COLUMN_NAME IN ('auto_category_id', 'moderation_reason', 'needs_manual_review', 'reviewed_by', 'reviewed_at')
ORDER BY COLUMN_NAME;
