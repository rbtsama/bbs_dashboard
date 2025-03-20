-- 帖子列表表
CREATE TABLE IF NOT EXISTS list (
    url TEXT PRIMARY KEY,
    title TEXT,
    scraping_time_r TIMESTAMP,
    list_time_r TIMESTAMP,
    update_reason TEXT,
    page INTEGER,
    num INTEGER,
    author TEXT,
    author_link TEXT,
    read_count INTEGER,
    reply_count INTEGER,
    scraping_time TIMESTAMP,
    list_time TIMESTAMP,
    source_file TEXT,
    sheet_name INTEGER
);

-- 帖子详情表
CREATE TABLE IF NOT EXISTS post (
    url TEXT PRIMARY KEY,
    title TEXT,
    scraping_time_r TIMESTAMP,
    post_time TIMESTAMP,
    list_time TIMESTAMP,
    page INTEGER,
    num INTEGER,
    author TEXT,
    author_link TEXT,
    read_count INTEGER,
    reply_count INTEGER,
    scraping_time TIMESTAMP,
    list_time_1 TIMESTAMP,
    source_file TEXT,
    sheet_name INTEGER
);

-- 车辆信息表
DROP TABLE IF EXISTS car_info;
CREATE TABLE car_info (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  url TEXT NOT NULL,
  title TEXT,
  year TEXT,
  make TEXT,
  model TEXT,
  miles TEXT,
  price TEXT,
  trade_type TEXT,
  location TEXT,
  author TEXT,
  author_link TEXT,
  post_time DATETIME,
  daysold INTEGER,
  last_active INTEGER,
  read_count INTEGER DEFAULT 0,
  reply_count INTEGER DEFAULT 0,
  created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(url)
);

-- 创建car_info表的索引
CREATE INDEX IF NOT EXISTS idx_car_info_url ON car_info(url);
CREATE INDEX IF NOT EXISTS idx_car_info_year ON car_info(year);
CREATE INDEX IF NOT EXISTS idx_car_info_make ON car_info(make);
CREATE INDEX IF NOT EXISTS idx_car_info_model ON car_info(model);
CREATE INDEX IF NOT EXISTS idx_car_info_price ON car_info(price);
CREATE INDEX IF NOT EXISTS idx_car_info_location ON car_info(location);
CREATE INDEX IF NOT EXISTS idx_car_info_author ON car_info(author);
CREATE INDEX IF NOT EXISTS idx_car_info_post_time ON car_info(post_time);
CREATE INDEX IF NOT EXISTS idx_car_info_daysold ON car_info(daysold);
CREATE INDEX IF NOT EXISTS idx_car_info_last_active ON car_info(last_active);

-- 帖子关注表
CREATE TABLE IF NOT EXISTS thread_follows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id TEXT NOT NULL,
    follow_type TEXT NOT NULL CHECK(follow_type IN ('my_follow', 'my_thread')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(thread_id)
);

-- 帖子统计表
CREATE TABLE IF NOT EXISTS poststatistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    post_count INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date)
);

-- 更新统计表
CREATE TABLE IF NOT EXISTS updatestatistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    update_count INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date)
);

-- 浏览统计表
CREATE TABLE IF NOT EXISTS viewstatistics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    view_count INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date)
);

-- 帖子排行表
CREATE TABLE IF NOT EXISTS postranking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id TEXT NOT NULL,
    url TEXT NOT NULL,
    title TEXT NOT NULL,
    author TEXT NOT NULL,
    author_link TEXT,
    repost_count INTEGER NOT NULL DEFAULT 0,
    reply_count INTEGER NOT NULL DEFAULT 0,
    delete_reply_count INTEGER NOT NULL DEFAULT 0,
    daysold INTEGER NOT NULL DEFAULT 0,
    last_active INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(thread_id)
);

-- 作者排行表
CREATE TABLE IF NOT EXISTS authorranking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author TEXT NOT NULL,
    author_link TEXT,
    post_count INTEGER NOT NULL DEFAULT 0,
    repost_count INTEGER NOT NULL DEFAULT 0,
    reply_count INTEGER NOT NULL DEFAULT 0,
    delete_reply_count INTEGER NOT NULL DEFAULT 0,
    active_posts INTEGER NOT NULL DEFAULT 0,
    last_active INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(author)
);

-- 词云缓存表
CREATE TABLE IF NOT EXISTS wordcloud_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT NOT NULL,
    version INTEGER NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- 帖子历史缓存表
CREATE TABLE IF NOT EXISTS thread_history_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id TEXT NOT NULL,
    data TEXT NOT NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(thread_id)
);

-- 创建线程关注表
CREATE TABLE IF NOT EXISTS thread_follow (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id TEXT NOT NULL,
    url TEXT NOT NULL,
    title TEXT,
    author TEXT,
    author_link TEXT,
    days_old INTEGER DEFAULT 0,
    last_active INTEGER DEFAULT 0,
    read_count INTEGER DEFAULT 0,
    reply_count INTEGER DEFAULT 0,
    follow_status TEXT CHECK(follow_status IN ('followed', 'my_thread', 'not_followed')) DEFAULT 'not_followed',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_thread_follow_thread_id ON thread_follow(thread_id);
CREATE INDEX IF NOT EXISTS idx_thread_follow_url ON thread_follow(url);
CREATE INDEX IF NOT EXISTS idx_thread_follow_status ON thread_follow(follow_status); 