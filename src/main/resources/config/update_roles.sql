-- Update user roles to support 4-tier permission system
-- 訪客 (guest) - 不需登入，瀏覽公開內容
-- 市民 (citizen) - 一般市民，可發表意見
-- 行政人員 (government_staff) - 政府相關人員，可審核與合併意見
-- 管理員 (admin/moderator) - 系統管理員與版主

-- Modify users table to add government_staff role
ALTER TABLE users
MODIFY COLUMN role ENUM('citizen', 'government_staff', 'moderator', 'admin') DEFAULT 'citizen';

-- Add comment to explain roles
ALTER TABLE users
COMMENT = 'User table with 4-tier role system: citizen, government_staff, moderator, admin';
