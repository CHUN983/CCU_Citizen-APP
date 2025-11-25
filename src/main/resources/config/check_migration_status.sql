-- Check migration status

-- Check if columns exist in opinions table
SELECT
    COLUMN_NAME,
    COLUMN_TYPE,
    IS_NULLABLE,
    COLUMN_DEFAULT
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_SCHEMA = 'citizen_app'
  AND TABLE_NAME = 'opinions'
  AND COLUMN_NAME IN (
    'auto_moderation_status',
    'auto_moderation_score',
    'auto_category_id',
    'moderation_reason',
    'needs_manual_review',
    'reviewed_by',
    'reviewed_at'
  )
ORDER BY ORDINAL_POSITION;

-- Check if new tables exist
SELECT
    TABLE_NAME,
    TABLE_ROWS,
    CREATE_TIME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_SCHEMA = 'citizen_app'
  AND TABLE_NAME IN (
    'moderation_logs',
    'sensitive_words',
    'category_keywords',
    'moderation_config'
  );
