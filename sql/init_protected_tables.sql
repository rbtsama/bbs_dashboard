-- 初始化被保护的表结构
-- 这些表不会被数据更新流程替换或修改

-- 用户关注的主题表
CREATE TABLE IF NOT EXISTS thread_follow (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    author_link TEXT,
    days_old INTEGER NOT NULL DEFAULT 0,
    last_active INTEGER NOT NULL DEFAULT 0,
    read_count INTEGER NOT NULL DEFAULT 0,
    reply_count INTEGER NOT NULL DEFAULT 0,
    repost_count INTEGER NOT NULL DEFAULT 0,
    delete_count INTEGER NOT NULL DEFAULT 0,
    follow_type TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 用户设置表
CREATE TABLE IF NOT EXISTS user_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL UNIQUE,    -- 用户ID
    theme TEXT DEFAULT 'light',      -- 主题设置
    notification_enabled INTEGER DEFAULT 1, -- 通知开关
    data_preferences TEXT,           -- 数据偏好设置 (JSON格式)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 用户收藏表
CREATE TABLE IF NOT EXISTS user_favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,           -- 用户ID
    url TEXT NOT NULL,               -- 收藏的URL
    title TEXT,                      -- 收藏的标题
    note TEXT,                       -- 用户笔记
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, url)             -- 确保用户对同一URL只能收藏一次
);

-- 用户评论表
CREATE TABLE IF NOT EXISTS user_comments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,           -- 用户ID
    url TEXT NOT NULL,               -- 评论的URL
    content TEXT NOT NULL,           -- 评论内容
    parent_id INTEGER,               -- 父评论ID（用于回复）
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 用户投票表
CREATE TABLE IF NOT EXISTS user_votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,           -- 用户ID
    url TEXT NOT NULL,               -- 投票的URL
    vote_type INTEGER NOT NULL,      -- 投票类型(1: 赞, -1: 踩)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id, url)             -- 确保用户对同一URL只能投票一次
);

-- 用户个人资料表
CREATE TABLE IF NOT EXISTS user_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL UNIQUE,    -- 用户ID
    display_name TEXT,               -- 显示名称
    avatar_url TEXT,                 -- 头像URL
    bio TEXT,                        -- 个人简介
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 用户通知表
CREATE TABLE IF NOT EXISTS user_notifications (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,           -- 用户ID
    type TEXT NOT NULL,              -- 通知类型
    content TEXT NOT NULL,           -- 通知内容
    is_read INTEGER DEFAULT 0,       -- 是否已读
    related_url TEXT,                -- 相关URL
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建必要的索引
CREATE INDEX IF NOT EXISTS idx_thread_follow_url ON thread_follow(url);
CREATE INDEX IF NOT EXISTS idx_thread_follow_author ON thread_follow(author);
CREATE INDEX IF NOT EXISTS idx_thread_follow_days_old ON thread_follow(days_old);
CREATE INDEX IF NOT EXISTS idx_thread_follow_last_active ON thread_follow(last_active);

CREATE INDEX IF NOT EXISTS idx_user_favorites_user_id ON user_favorites(user_id);
CREATE INDEX IF NOT EXISTS idx_user_comments_user_id ON user_comments(user_id);
CREATE INDEX IF NOT EXISTS idx_user_comments_url ON user_comments(url);
CREATE INDEX IF NOT EXISTS idx_user_votes_user_id ON user_votes(user_id);
CREATE INDEX IF NOT EXISTS idx_user_votes_url ON user_votes(url);
CREATE INDEX IF NOT EXISTS idx_user_notifications_user_id ON user_notifications(user_id);
CREATE INDEX IF NOT EXISTS idx_user_notifications_is_read ON user_notifications(is_read); 