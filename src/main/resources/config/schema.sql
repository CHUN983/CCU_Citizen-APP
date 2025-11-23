-- Citizen Urban Planning Participation System - Database Schema
-- MVP Version 1.0

-- Users table (市民、行政人員、管理員)
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(100),
    role ENUM('citizen', 'admin', 'moderator') DEFAULT 'citizen',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_email (email),
    INDEX idx_username (username),
    INDEX idx_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Categories table (分類/處室 - 兩層樹狀結構)
CREATE TABLE IF NOT EXISTS categories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    parent_id INT NULL,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (parent_id) REFERENCES categories(id) ON DELETE SET NULL,
    INDEX idx_parent (parent_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Opinions table (意見系統)
CREATE TABLE IF NOT EXISTS opinions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    category_id INT,
    status ENUM('draft', 'pending', 'approved', 'rejected', 'resolved') DEFAULT 'draft',
    region VARCHAR(100),
    latitude DECIMAL(10, 8),
    longitude DECIMAL(11, 8),
    view_count INT DEFAULT 0,
    is_public BOOLEAN DEFAULT TRUE,
    merged_to_id INT NULL COMMENT '合併到哪個意見',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE SET NULL,
    FOREIGN KEY (merged_to_id) REFERENCES opinions(id) ON DELETE SET NULL,
    INDEX idx_user (user_id),
    INDEX idx_category (category_id),
    INDEX idx_status (status),
    INDEX idx_created (created_at),
    FULLTEXT idx_content (title, content)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Opinion media attachments (多媒體附件)
CREATE TABLE IF NOT EXISTS opinion_media (
    id INT AUTO_INCREMENT PRIMARY KEY,
    opinion_id INT NOT NULL,
    media_type ENUM('image', 'video', 'audio') NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_size INT,
    mime_type VARCHAR(100),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (opinion_id) REFERENCES opinions(id) ON DELETE CASCADE,
    INDEX idx_opinion (opinion_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Comments table (留言系統)
CREATE TABLE IF NOT EXISTS comments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    opinion_id INT NOT NULL,
    user_id INT NOT NULL,
    content TEXT NOT NULL,
    is_deleted BOOLEAN DEFAULT FALSE,
    deleted_by INT NULL COMMENT '被哪個管理員刪除',
    deleted_at TIMESTAMP NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (opinion_id) REFERENCES opinions(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (deleted_by) REFERENCES users(id) ON DELETE SET NULL,
    INDEX idx_opinion (opinion_id),
    INDEX idx_user (user_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Votes table (投票/按讚)
CREATE TABLE IF NOT EXISTS votes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    opinion_id INT NOT NULL,
    user_id INT NOT NULL,
    vote_type ENUM('like', 'support') DEFAULT 'like',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (opinion_id) REFERENCES opinions(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_opinion (user_id, opinion_id),
    INDEX idx_opinion (opinion_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Collections/Bookmarks table (收藏)
CREATE TABLE IF NOT EXISTS collections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    opinion_id INT NOT NULL,
    user_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (opinion_id) REFERENCES opinions(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_collection (user_id, opinion_id),
    INDEX idx_user (user_id),
    INDEX idx_opinion (opinion_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tags table (標籤系統)
CREATE TABLE IF NOT EXISTS tags (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Opinion tags (意見與標籤的多對多關係)
CREATE TABLE IF NOT EXISTS opinion_tags (
    opinion_id INT NOT NULL,
    tag_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (opinion_id, tag_id),
    FOREIGN KEY (opinion_id) REFERENCES opinions(id) ON DELETE CASCADE,
    FOREIGN KEY (tag_id) REFERENCES tags(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Notifications table (通知系統)
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    opinion_id INT NULL,
    type ENUM('comment', 'like', 'status_change', 'merged', 'approved', 'rejected') NOT NULL,
    title VARCHAR(200) NOT NULL,
    content TEXT,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (opinion_id) REFERENCES opinions(id) ON DELETE CASCADE,
    INDEX idx_user (user_id),
    INDEX idx_read (is_read),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Notification milestones tracking table (通知級距追蹤表)
-- 用於追蹤按讚和留言的級距通知（1, 2, 4, 8, 16...）
CREATE TABLE IF NOT EXISTS notification_milestones (
    id INT AUTO_INCREMENT PRIMARY KEY,
    opinion_id INT NOT NULL,
    milestone_type ENUM('like', 'comment') NOT NULL,
    last_notified_count INT DEFAULT 0 COMMENT '上次通知時的數量',
    next_milestone INT DEFAULT 1 COMMENT '下次通知的目標數量',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (opinion_id) REFERENCES opinions(id) ON DELETE CASCADE,
    UNIQUE KEY unique_milestone (opinion_id, milestone_type),
    INDEX idx_opinion (opinion_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Opinion history/audit log (歷史紀錄)
CREATE TABLE IF NOT EXISTS opinion_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    opinion_id INT NOT NULL,
    user_id INT NOT NULL COMMENT '執行操作的用戶',
    action ENUM('created', 'updated', 'approved', 'rejected', 'merged', 'status_changed') NOT NULL,
    old_status VARCHAR(50),
    new_status VARCHAR(50),
    changes JSON COMMENT '變更內容的 JSON 格式',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (opinion_id) REFERENCES opinions(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    INDEX idx_opinion (opinion_id),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Subscriptions table (訂閱功能)
CREATE TABLE IF NOT EXISTS subscriptions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    opinion_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (opinion_id) REFERENCES opinions(id) ON DELETE CASCADE,
    UNIQUE KEY unique_user_subscription (user_id, opinion_id),
    INDEX idx_user (user_id),
    INDEX idx_opinion (opinion_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Insert default categories (初始分類)
INSERT INTO categories (name, parent_id, description) VALUES
('交通局', NULL, '道路、大眾運輸、停車等相關議題'),
('環保局', NULL, '環境清潔、綠化、污染等議題'),
('工務局', NULL, '公園、施工、路燈、運動場等設施'),
('社會局', NULL, '社會服務、福利政策等議題'),
('衛生局', NULL, '醫療、食品安全、衛生檢舉'),
('警察局', NULL, '治安、噪音糾紛、違停檢舉'),
('教育局', NULL, '體育場所、圖書館、教育事務、學區劃分'),
('都發局', NULL, '都市規劃、土地、開發案'),
('民政局', NULL, '社區事務、公墓、鄰里投訴'),
('其他', NULL, '制度、行政流程、抱怨政府效率、其他城市規劃相關議題');

-- Insert default admin user (password: admin123, please change in production)
-- Password hash for 'admin123' using bcrypt
INSERT INTO users (username, email, password_hash, full_name, role) VALUES
('admin', 'admin@citizenapp.local', '$2b$12$sQ6ZiVBOMRTEZW2ANU6fEOSWoXWbdhei3ZCnRw6qRl87w9pvITO4q', '系統管理員', 'admin')
