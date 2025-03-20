-- 删除旧表
DROP TABLE IF EXISTS post_action_new;
DROP TABLE IF EXISTS post_statistic_new;
DROP TABLE IF EXISTS update_statistic_new;
DROP TABLE IF EXISTS view_statistic_new;
DROP TABLE IF EXISTS post_ranking_new;
DROP TABLE IF EXISTS author_ranking_new;
DROP TABLE IF EXISTS thread_follow_new;

-- 重命名表
ALTER TABLE action RENAME TO post_action;
ALTER TABLE poststatistics RENAME TO post_statistic;
ALTER TABLE updatestatistics RENAME TO update_statistic;
ALTER TABLE viewstatistics RENAME TO view_statistic;

-- 处理post_ranking表
DROP TABLE IF EXISTS post_ranking_new;
CREATE TABLE post_ranking_new (
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
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO post_ranking_new (
    url, title, author, author_link, days_old, last_active,
    read_count, reply_count, repost_count, delete_count
)
SELECT 
    url, title, author, author_link,
    COALESCE(Days_Old, 0) as days_old,
    COALESCE(last_active, 0) as last_active,
    COALESCE(count, 0) as read_count,
    COALESCE(reply_count, 0) as reply_count,
    COALESCE(repost_count, 0) as repost_count,
    COALESCE(delete_count, 0) as delete_count
FROM postranking;

DROP TABLE IF EXISTS postranking;
DROP TABLE IF EXISTS post_ranking;
ALTER TABLE post_ranking_new RENAME TO post_ranking;

-- 处理author_ranking表
DROP TABLE IF EXISTS author_ranking_new;
CREATE TABLE author_ranking_new (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author TEXT NOT NULL,
    author_link TEXT,
    days_old INTEGER NOT NULL DEFAULT 0,
    last_active INTEGER NOT NULL DEFAULT 0,
    active_posts INTEGER NOT NULL DEFAULT 0,
    repost_count INTEGER NOT NULL DEFAULT 0,
    reply_count INTEGER NOT NULL DEFAULT 0,
    delete_count INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO author_ranking_new (
    author, author_link, days_old, last_active,
    active_posts, repost_count, reply_count, delete_count
)
SELECT 
    author, author_link,
    COALESCE(Days_Old, 0) as days_old,
    COALESCE(last_active, 0) as last_active,
    COALESCE(active_posts, 0) as active_posts,
    COALESCE(repost_count, 0) as repost_count,
    COALESCE(reply_count, 0) as reply_count,
    COALESCE(delete_count, 0) as delete_count
FROM authorranking;

DROP TABLE IF EXISTS authorranking;
DROP TABLE IF EXISTS author_ranking;
ALTER TABLE author_ranking_new RENAME TO author_ranking;

-- 处理thread_follow表
DROP TABLE IF EXISTS thread_follow_new;
CREATE TABLE thread_follow_new (
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

INSERT INTO thread_follow_new (
    url, title, author, author_link, days_old, last_active,
    read_count, reply_count, repost_count, delete_count, follow_type
)
SELECT 
    url, title, author, author_link,
    COALESCE(days_old, 0) as days_old,
    COALESCE(last_active, 0) as last_active,
    COALESCE(read_count, 0) as read_count,
    COALESCE(reply_count, 0) as reply_count,
    COALESCE(repost_count, 0) as repost_count,
    COALESCE(delete_count, 0) as delete_count,
    follow_type
FROM thread_follows;

DROP TABLE IF EXISTS thread_follows;
DROP TABLE IF EXISTS thread_follow;
ALTER TABLE thread_follow_new RENAME TO thread_follow;

-- 删除旧的索引
DROP INDEX IF EXISTS idx_post_ranking_url;
DROP INDEX IF EXISTS idx_post_ranking_author;
DROP INDEX IF EXISTS idx_post_ranking_days_old;
DROP INDEX IF EXISTS idx_post_ranking_last_active;

DROP INDEX IF EXISTS idx_author_ranking_author;
DROP INDEX IF EXISTS idx_author_ranking_days_old;
DROP INDEX IF EXISTS idx_author_ranking_last_active;

DROP INDEX IF EXISTS idx_thread_follow_url;
DROP INDEX IF EXISTS idx_thread_follow_author;
DROP INDEX IF EXISTS idx_thread_follow_days_old;
DROP INDEX IF EXISTS idx_thread_follow_last_active;

-- 创建新的索引
CREATE INDEX idx_post_ranking_url ON post_ranking(url);
CREATE INDEX idx_post_ranking_author ON post_ranking(author);
CREATE INDEX idx_post_ranking_days_old ON post_ranking(days_old);
CREATE INDEX idx_post_ranking_last_active ON post_ranking(last_active);

CREATE INDEX idx_author_ranking_author ON author_ranking(author);
CREATE INDEX idx_author_ranking_days_old ON author_ranking(days_old);
CREATE INDEX idx_author_ranking_last_active ON author_ranking(last_active);

CREATE INDEX idx_thread_follow_url ON thread_follow(url);
CREATE INDEX idx_thread_follow_author ON thread_follow(author);
CREATE INDEX idx_thread_follow_days_old ON thread_follow(days_old);
CREATE INDEX idx_thread_follow_last_active ON thread_follow(last_active); 