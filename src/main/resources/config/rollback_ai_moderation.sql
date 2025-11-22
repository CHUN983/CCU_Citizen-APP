-- Rollback AI Moderation Migration
-- Use this if you need to clean up a partial migration
-- Note: This script will show errors for items that don't exist - this is normal and safe

SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0;

-- Drop tables first (they have foreign keys to opinions)
DROP TABLE IF EXISTS moderation_logs;
DROP TABLE IF EXISTS category_keywords;
DROP TABLE IF EXISTS sensitive_words;
DROP TABLE IF EXISTS moderation_config;

-- Drop foreign keys (will error if they don't exist - ignore these errors)
SET @drop_fk1 = (SELECT IF(
    EXISTS(
        SELECT * FROM information_schema.TABLE_CONSTRAINTS
        WHERE CONSTRAINT_SCHEMA = DATABASE()
        AND TABLE_NAME = 'opinions'
        AND CONSTRAINT_NAME = 'fk_auto_category'
        AND CONSTRAINT_TYPE = 'FOREIGN KEY'
    ),
    'ALTER TABLE opinions DROP FOREIGN KEY fk_auto_category',
    'SELECT "Foreign key fk_auto_category does not exist" AS info'
));
PREPARE stmt1 FROM @drop_fk1;
EXECUTE stmt1;
DEALLOCATE PREPARE stmt1;

SET @drop_fk2 = (SELECT IF(
    EXISTS(
        SELECT * FROM information_schema.TABLE_CONSTRAINTS
        WHERE CONSTRAINT_SCHEMA = DATABASE()
        AND TABLE_NAME = 'opinions'
        AND CONSTRAINT_NAME = 'fk_reviewed_by'
        AND CONSTRAINT_TYPE = 'FOREIGN KEY'
    ),
    'ALTER TABLE opinions DROP FOREIGN KEY fk_reviewed_by',
    'SELECT "Foreign key fk_reviewed_by does not exist" AS info'
));
PREPARE stmt2 FROM @drop_fk2;
EXECUTE stmt2;
DEALLOCATE PREPARE stmt2;

-- Drop indexes
SET @drop_idx1 = (SELECT IF(
    EXISTS(
        SELECT * FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = 'opinions'
        AND INDEX_NAME = 'idx_auto_moderation'
    ),
    'ALTER TABLE opinions DROP INDEX idx_auto_moderation',
    'SELECT "Index idx_auto_moderation does not exist" AS info'
));
PREPARE stmt3 FROM @drop_idx1;
EXECUTE stmt3;
DEALLOCATE PREPARE stmt3;

SET @drop_idx2 = (SELECT IF(
    EXISTS(
        SELECT * FROM information_schema.STATISTICS
        WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = 'opinions'
        AND INDEX_NAME = 'idx_manual_review'
    ),
    'ALTER TABLE opinions DROP INDEX idx_manual_review',
    'SELECT "Index idx_manual_review does not exist" AS info'
));
PREPARE stmt4 FROM @drop_idx2;
EXECUTE stmt4;
DEALLOCATE PREPARE stmt4;

-- Drop columns
SET @drop_col1 = (SELECT IF(
    EXISTS(SELECT * FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'opinions' AND COLUMN_NAME = 'auto_moderation_status'),
    'ALTER TABLE opinions DROP COLUMN auto_moderation_status',
    'SELECT "Column auto_moderation_status does not exist" AS info'
));
PREPARE stmt5 FROM @drop_col1;
EXECUTE stmt5;
DEALLOCATE PREPARE stmt5;

SET @drop_col2 = (SELECT IF(
    EXISTS(SELECT * FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'opinions' AND COLUMN_NAME = 'auto_moderation_score'),
    'ALTER TABLE opinions DROP COLUMN auto_moderation_score',
    'SELECT "Column auto_moderation_score does not exist" AS info'
));
PREPARE stmt6 FROM @drop_col2;
EXECUTE stmt6;
DEALLOCATE PREPARE stmt6;

SET @drop_col3 = (SELECT IF(
    EXISTS(SELECT * FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'opinions' AND COLUMN_NAME = 'auto_category_id'),
    'ALTER TABLE opinions DROP COLUMN auto_category_id',
    'SELECT "Column auto_category_id does not exist" AS info'
));
PREPARE stmt7 FROM @drop_col3;
EXECUTE stmt7;
DEALLOCATE PREPARE stmt7;

SET @drop_col4 = (SELECT IF(
    EXISTS(SELECT * FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'opinions' AND COLUMN_NAME = 'moderation_reason'),
    'ALTER TABLE opinions DROP COLUMN moderation_reason',
    'SELECT "Column moderation_reason does not exist" AS info'
));
PREPARE stmt8 FROM @drop_col4;
EXECUTE stmt8;
DEALLOCATE PREPARE stmt8;

SET @drop_col5 = (SELECT IF(
    EXISTS(SELECT * FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'opinions' AND COLUMN_NAME = 'needs_manual_review'),
    'ALTER TABLE opinions DROP COLUMN needs_manual_review',
    'SELECT "Column needs_manual_review does not exist" AS info'
));
PREPARE stmt9 FROM @drop_col5;
EXECUTE stmt9;
DEALLOCATE PREPARE stmt9;

SET @drop_col6 = (SELECT IF(
    EXISTS(SELECT * FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'opinions' AND COLUMN_NAME = 'reviewed_by'),
    'ALTER TABLE opinions DROP COLUMN reviewed_by',
    'SELECT "Column reviewed_by does not exist" AS info'
));
PREPARE stmt10 FROM @drop_col6;
EXECUTE stmt10;
DEALLOCATE PREPARE stmt10;

SET @drop_col7 = (SELECT IF(
    EXISTS(SELECT * FROM information_schema.COLUMNS WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = 'opinions' AND COLUMN_NAME = 'reviewed_at'),
    'ALTER TABLE opinions DROP COLUMN reviewed_at',
    'SELECT "Column reviewed_at does not exist" AS info'
));
PREPARE stmt11 FROM @drop_col7;
EXECUTE stmt11;
DEALLOCATE PREPARE stmt11;

SET SQL_NOTES=@OLD_SQL_NOTES;

SELECT '✅ Rollback completed. You can now run add_ai_moderation_safe.sql' AS status;
