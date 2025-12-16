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
('交通局', NULL,
 '交通政策與管理（含道安）、交通工程與設施、停車治理與大眾運輸等議題。常見：號誌/路口設計與時相、標線標誌、交通管制與疏導、道路交通安全會報與宣導、停車場/路邊停車管理與費率、公共運輸（公車路線/班次/轉運）、計程車費率與管理、特種車輛行駛路線協調。容易混淆：違規取締與拖吊多屬警政（執法）；道路路面破損/人行道施工屬工務養護；都市計畫道路開闢/用地屬都發/工務。'
),
('環保局', NULL,
 '環境污染防制與稽查、廢棄物與資源循環、環境衛生與清潔隊執行等議題。常見：垃圾清運路線/時間、大型廢棄物、資源回收與源頭減量、環境清潔與病媒蚊防治、違規廣告物清除、廢棄車輛稽查/移置、噪音/空污/水污等污染陳情與查處、環保設施與相關許可/查核。容易混淆：純「鄰里吵鬧」若非可稽查噪音源，可能落到警政/民政調解；工地揚塵/泥漿外溢則多由環保稽查、但工地施工管理也會牽涉工務/都發。'
),
('工務局', NULL,
 '公共工程與市政基礎設施的興建、維護與管理。常見：道路/橋梁/人行道修繕、路面坑洞、排水溝/箱涵、水利工程、防汛整備、汙水下水道與接管、公共工程招標與施工查核、公共設施（含公園綠地或公共場域）修繕與工程協調。容易混淆：號誌/標線通常屬交通；建築物違建、建照、使照、都更多屬都發（建管/都更）；環境清潔與垃圾屬環保。'
),
('社會局', NULL,
 '社會福利與社會救助、弱勢與保護服務、老人/身障/兒少/婦女福利，以及社工服務與（部分縣市）勞工、青年相關業務。常見：急難救助、低收/中低收、津貼補助、育兒與托育資源、家暴/性侵通報與服務、老人照顧資源連結、身障鑑定與福利、社福中心/社工介入與個案管理。容易混淆：長照常與衛生/長照中心分工（不同縣市架構略有差）；治安/家暴現場處置屬警政，但後續保護與安置多回到社政體系。'
),
('衛生局', NULL,
 '公共衛生與醫政、食品藥物與健康促進、傳染病防治、長期照護（依縣市組織可能由衛生或專責中心承辦）。常見：醫療(事)機構開業/歇業/變更與督導考核、食品安全稽查與餐飲衛生、藥事管理、疫情通報與防疫、疫苗與健康篩檢、菸害/酒害防制、民眾健康諮詢、（可能含）長照資源與單一窗口服務。容易混淆：純消費糾紛不是衛生；餐廳噪音/占道多不是衛生。'
),
('警察局', NULL,
 '治安維護與警政執法、交通執法與事故處理、110報案、巡邏守望與重大案件偵辦等。常見：噪音糾紛（立即性擾亂/滋擾）、打架鬥毆、詐欺報案、違停/交通違規取締與申訴流程、交通事故處理、公共安全維護。容易混淆：若是「可量測/可稽查」之噪音源（營業場所、工地機具）通常環保可介入；社區糾紛若走調解，民政調解也可能承接。'
),
('教育局', NULL,
 '學校教育行政與校務管理、學生學習與輔導、特殊教育、校園安全、學區與入學、社教與終身學習，以及體育場館/運動活動（依縣市分工不同，可能另有運動發展單位）。常見：學區劃分、校園霸凌/輔導、特殊教育資源、課程與教學推動、幼兒園與托育（部分業務與社政分工）、圖書館/社教館舍、體育場館管理與賽事活動。容易混淆：公園步道/路燈不是教育；學校周邊交通改善常需交通+工務協作。'
),
('都發局', NULL,
 '都市計畫與土地使用、建築管理、都市更新/都市設計審議、開發案與分區管制。常見：土地使用分區/公共設施用地查詢、都市計畫通盤檢討或個案變更、建照/使照、違建查報（依縣市規劃）、工地/建築施工管理（就建管角度）、都市更新/危老重建、都市設計審議。容易混淆：道路「養護修補」多是工務；交通號誌標線是交通；環境污染是環保。'
),
('民政局', NULL,
 '戶政與國籍相關、里鄰與社區事務、地方自治與選務（依縣市）、宗教與寺廟管理、殯葬與公墓（多由民政或專責單位）、以及調解等便民服務。常見：戶籍遷徙與身分證、戶口名簿、國籍取得相關程序、里民活動與社區發展、宗教活動/宮廟、（可能含）公墓或殯葬管理、鄰里糾紛調解窗口。'
),
('其他', NULL,
 '無法明確歸屬單一局處或屬跨局處協作的議題：例如制度/流程/效率抱怨、跨局處工程協調、資訊系統與智慧城市（若另有智慧科技/資訊單位）、市政建議與不在上述範圍之公共政策討論。建議在後端加「轉案」機制：允許同案複選（主責+會辦），或先落到其他再由人工/規則轉派。'
);


-- Insert default admin user (password: admin123, please change in production)
-- Password hash for 'admin123' using bcrypt
INSERT INTO users (username, email, password_hash, full_name, role) VALUES
('admin', 'admin@citizenapp.local', '$2b$12$sQ6ZiVBOMRTEZW2ANU6fEOSWoXWbdhei3ZCnRw6qRl87w9pvITO4q', '系統管理員', 'admin'),
('ai_content_moderator', 'ai@citizenapp.local', '$2b$12$sQ6ZiVBOMRTEZW2ANU6fEOSWoXWbdhei3ZCnRw6qRl87w9pvITO4q', 'AI審核系統', 'admin');

UPDATE users SET id = '0'  WHERE username = 'ai_content_moderator';