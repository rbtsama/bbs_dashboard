-- 车辆信息表
CREATE TABLE IF NOT EXISTS car_info (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    url TEXT NOT NULL,
    year INTEGER,
    make TEXT,
    model TEXT,
    miles INTEGER,
    price REAL,
    trade_type TEXT,
    location TEXT,
    thread_id TEXT,
    author TEXT,
    author_link TEXT,
    post_time DATETIME,
    daysold INTEGER,
    last_active INTEGER,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(url)
); 