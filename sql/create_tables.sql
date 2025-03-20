-- 删除旧表
DROP TABLE IF EXISTS detail;
DROP TABLE IF EXISTS thread_history_cache;
DROP TABLE IF EXISTS post_action;
DROP TABLE IF EXISTS post_statistic;
DROP TABLE IF EXISTS update_statistic;
DROP TABLE IF EXISTS view_statistic;
DROP TABLE IF EXISTS post_ranking;
DROP TABLE IF EXISTS author_ranking;
DROP TABLE IF EXISTS thread_follow;
DROP TABLE IF EXISTS post_history;
DROP TABLE IF EXISTS author_history;
DROP TABLE IF EXISTS car_detail;

-- 创建新表：post_action
CREATE TABLE IF NOT EXISTS post_action (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id TEXT NOT NULL,
    author_id TEXT NOT NULL,
    action_type TEXT NOT NULL,
    action_time DATETIME NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建新表：post_statistic
CREATE TABLE IF NOT EXISTS post_statistic (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id TEXT NOT NULL,
    author_id TEXT NOT NULL,
    type TEXT NOT NULL,
    datetime DATETIME NOT NULL,
    count INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建新表：update_statistic
CREATE TABLE IF NOT EXISTS update_statistic (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id TEXT NOT NULL,
    author_id TEXT NOT NULL,
    type TEXT NOT NULL,
    datetime DATETIME NOT NULL,
    count INTEGER NOT NULL,
    update_reason TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建新表：view_statistic
CREATE TABLE IF NOT EXISTS view_statistic (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id TEXT NOT NULL,
    author_id TEXT NOT NULL,
    type TEXT NOT NULL,
    datetime DATETIME NOT NULL,
    view_gap INTEGER NOT NULL,
    duplicate_posts INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建新表：post_ranking
CREATE TABLE IF NOT EXISTS post_ranking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id TEXT NOT NULL,
    author_id TEXT NOT NULL,
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    daysold INTEGER NOT NULL DEFAULT 0,
    post_last_active INTEGER NOT NULL DEFAULT 0,
    read_count INTEGER NOT NULL DEFAULT 0,
    repost_count INTEGER NOT NULL DEFAULT 0,
    reply_count INTEGER NOT NULL DEFAULT 0,
    delete_count INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建新表：author_ranking
CREATE TABLE IF NOT EXISTS author_ranking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id TEXT NOT NULL,
    author TEXT NOT NULL,
    daysold INTEGER NOT NULL DEFAULT 0,
    author_last_active INTEGER NOT NULL DEFAULT 0,
    repost_count INTEGER NOT NULL DEFAULT 0,
    reply_count INTEGER NOT NULL DEFAULT 0,
    delete_count INTEGER NOT NULL DEFAULT 0,
    active_posts INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建新表：thread_follow
CREATE TABLE IF NOT EXISTS thread_follow (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id TEXT NOT NULL,
    author_id TEXT NOT NULL,
    daysold INTEGER NOT NULL DEFAULT 0,
    post_last_active INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建新表：post_history
CREATE TABLE IF NOT EXISTS post_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id TEXT NOT NULL,
    url TEXT NOT NULL,
    title TEXT,
    author TEXT,
    author_id TEXT,
    action TEXT NOT NULL,
    action_time DATETIME NOT NULL,
    action_type TEXT,
    source TEXT,
    read_count INTEGER DEFAULT 0,
    reply_count INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建新表：author_history
CREATE TABLE IF NOT EXISTS author_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id TEXT NOT NULL,
    thread_id TEXT NOT NULL,
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    action_time DATETIME NOT NULL,
    action_type TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建新表：car_detail
CREATE TABLE IF NOT EXISTS car_detail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id TEXT NOT NULL UNIQUE,
    author_id TEXT NOT NULL,
    year INTEGER,
    make TEXT,
    model TEXT,
    miles INTEGER,
    price REAL,
    trade_type TEXT,
    location TEXT,
    daysold INTEGER NOT NULL DEFAULT 0,
    post_last_active INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建词云缓存表
CREATE TABLE IF NOT EXISTS wordcloud_cache (
    type TEXT PRIMARY KEY,  -- 词云类型（如'title'、'content'等）
    data TEXT NOT NULL,     -- 词云数据（JSON格式）
    created_at DATETIME NOT NULL  -- 创建时间
);

-- 创建索引
-- post_action表索引
CREATE INDEX idx_post_action_thread_id ON post_action(thread_id);
CREATE INDEX idx_post_action_author_id ON post_action(author_id);
CREATE INDEX idx_post_action_action_time ON post_action(action_time);

-- post_statistic表索引
CREATE INDEX idx_post_statistic_thread_id ON post_statistic(thread_id);
CREATE INDEX idx_post_statistic_author_id ON post_statistic(author_id);
CREATE INDEX idx_post_statistic_datetime ON post_statistic(datetime);

-- update_statistic表索引
CREATE INDEX idx_update_statistic_thread_id ON update_statistic(thread_id);
CREATE INDEX idx_update_statistic_author_id ON update_statistic(author_id);
CREATE INDEX idx_update_statistic_datetime ON update_statistic(datetime);

-- view_statistic表索引
CREATE INDEX idx_view_statistic_thread_id ON view_statistic(thread_id);
CREATE INDEX idx_view_statistic_author_id ON view_statistic(author_id);
CREATE INDEX idx_view_statistic_datetime ON view_statistic(datetime);

-- post_ranking表索引
CREATE INDEX idx_post_ranking_thread_id ON post_ranking(thread_id);
CREATE INDEX idx_post_ranking_author_id ON post_ranking(author_id);
CREATE INDEX idx_post_ranking_daysold ON post_ranking(daysold);
CREATE INDEX idx_post_ranking_post_last_active ON post_ranking(post_last_active);

-- author_ranking表索引
CREATE INDEX idx_author_ranking_author_id ON author_ranking(author_id);
CREATE INDEX idx_author_ranking_daysold ON author_ranking(daysold);
CREATE INDEX idx_author_ranking_author_last_active ON author_ranking(author_last_active);

-- thread_follow表索引
CREATE INDEX idx_thread_follow_thread_id ON thread_follow(thread_id);
CREATE INDEX idx_thread_follow_author_id ON thread_follow(author_id);
CREATE INDEX idx_thread_follow_daysold ON thread_follow(daysold);
CREATE INDEX idx_thread_follow_post_last_active ON thread_follow(post_last_active);

-- post_history表索引
CREATE INDEX idx_post_history_thread_id ON post_history(thread_id);
CREATE INDEX idx_post_history_author_id ON post_history(author_id);
CREATE INDEX idx_post_history_action_time ON post_history(action_time);
CREATE INDEX idx_post_history_action_type ON post_history(action_type);

-- author_history表索引
CREATE INDEX idx_author_history_author_id ON author_history(author_id);
CREATE INDEX idx_author_history_thread_id ON author_history(thread_id);
CREATE INDEX idx_author_history_action_time ON author_history(action_time);
CREATE INDEX idx_author_history_action_type ON author_history(action_type);

-- car_detail表索引
CREATE INDEX idx_car_detail_author_id ON car_detail(author_id);
CREATE INDEX idx_car_detail_year ON car_detail(year);
CREATE INDEX idx_car_detail_make ON car_detail(make);
CREATE INDEX idx_car_detail_model ON car_detail(model);
CREATE INDEX idx_car_detail_price ON car_detail(price);
CREATE INDEX idx_car_detail_location ON car_detail(location); 