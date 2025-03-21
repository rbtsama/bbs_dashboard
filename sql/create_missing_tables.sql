-- 创建post_history表
CREATE TABLE IF NOT EXISTS post_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id TEXT NOT NULL,
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    author_link TEXT,
    action_time DATETIME NOT NULL,
    action_type TEXT NOT NULL,
    read_count INTEGER NOT NULL DEFAULT 0,
    reply_count INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建author_history表
CREATE TABLE IF NOT EXISTS author_history (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_id TEXT NOT NULL,
    author TEXT NOT NULL,
    author_link TEXT,
    action_time DATETIME NOT NULL,
    action_type TEXT NOT NULL,
    post_count INTEGER NOT NULL DEFAULT 0,
    active_posts INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建car_detail表
CREATE TABLE IF NOT EXISTS car_detail (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id TEXT NOT NULL UNIQUE,
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    author_link TEXT,
    year INTEGER,
    make TEXT,
    model TEXT,
    miles INTEGER,
    price REAL,
    trade_type TEXT,
    location TEXT,
    days_old INTEGER NOT NULL DEFAULT 0,
    last_active INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建索引
-- post_history表索引
CREATE INDEX IF NOT EXISTS idx_post_history_thread_id ON post_history(thread_id);
CREATE INDEX IF NOT EXISTS idx_post_history_url ON post_history(url);
CREATE INDEX IF NOT EXISTS idx_post_history_author ON post_history(author);
CREATE INDEX IF NOT EXISTS idx_post_history_action_time ON post_history(action_time);
CREATE INDEX IF NOT EXISTS idx_post_history_action_type ON post_history(action_type);

-- author_history表索引
CREATE INDEX IF NOT EXISTS idx_author_history_author_id ON author_history(author_id);
CREATE INDEX IF NOT EXISTS idx_author_history_author ON author_history(author);
CREATE INDEX IF NOT EXISTS idx_author_history_action_time ON author_history(action_time);
CREATE INDEX IF NOT EXISTS idx_author_history_action_type ON author_history(action_type);

-- car_detail表索引
CREATE INDEX IF NOT EXISTS idx_car_detail_url ON car_detail(url);
CREATE INDEX IF NOT EXISTS idx_car_detail_author ON car_detail(author);
CREATE INDEX IF NOT EXISTS idx_car_detail_year ON car_detail(year);
CREATE INDEX IF NOT EXISTS idx_car_detail_make ON car_detail(make);
CREATE INDEX IF NOT EXISTS idx_car_detail_model ON car_detail(model);
CREATE INDEX IF NOT EXISTS idx_car_detail_price ON car_detail(price);
CREATE INDEX IF NOT EXISTS idx_car_detail_location ON car_detail(location);
CREATE INDEX IF NOT EXISTS idx_car_detail_days_old ON car_detail(days_old);
CREATE INDEX IF NOT EXISTS idx_car_detail_last_active ON car_detail(last_active);

-- 从car_info和detail表导入数据到car_detail表
INSERT INTO car_detail (
    thread_id, url, title, author, author_link,
    year, make, model, miles, price, trade_type, location,
    days_old, last_active
)
SELECT 
    c.thread_id, c.url, d.title, c.author, c.author_link,
    c.year, c.make, c.model, 
    CASE 
        WHEN c.miles LIKE '%,%' THEN CAST(REPLACE(REPLACE(c.miles, ',', ''), ' mi', '') AS INTEGER)
        WHEN c.miles LIKE '% mi' THEN CAST(REPLACE(c.miles, ' mi', '') AS INTEGER)
        ELSE NULL 
    END as miles,
    CASE 
        WHEN c.price LIKE '$%' THEN CAST(REPLACE(REPLACE(c.price, '$', ''), ',', '') AS REAL)
        ELSE NULL 
    END as price,
    c.trade_type, c.location,
    c.daysold, c.last_active
-- FROM car_info c -- 已由清理脚本注释
LEFT JOIN detail d ON c.url = d.url; 