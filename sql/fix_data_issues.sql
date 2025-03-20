-- 修复car_detail表中的无效year值
UPDATE car_detail
SET year = NULL
WHERE year < 1900 OR year > 2100;

-- 修复post_ranking和car_detail之间的数据不一致
INSERT INTO car_detail (
    thread_id, url, title, author, author_link,
    days_old, last_active
)
SELECT 
    SUBSTR(p.url, -10, 7) as thread_id,
    p.url, 
    COALESCE(d.title, p.title, '无标题') as title,
    p.author, p.author_link,
    p.days_old, p.last_active
FROM post_ranking p
LEFT JOIN car_detail c ON p.url = c.url
LEFT JOIN detail d ON p.url = d.url
WHERE c.url IS NULL;

-- 修改author_ranking表结构
ALTER TABLE author_ranking RENAME TO author_ranking_old;

CREATE TABLE author_ranking (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    author TEXT NOT NULL,
    author_link TEXT,
    url TEXT,
    title TEXT,
    days_old INTEGER NOT NULL DEFAULT 0,
    last_active INTEGER NOT NULL DEFAULT 0,
    active_posts INTEGER NOT NULL DEFAULT 0,
    repost_count INTEGER NOT NULL DEFAULT 0,
    reply_count INTEGER NOT NULL DEFAULT 0,
    delete_count INTEGER NOT NULL DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO author_ranking (
    author, author_link, days_old, last_active,
    active_posts, repost_count, reply_count, delete_count,
    created_at, updated_at
)
SELECT 
    author, author_link, days_old, last_active,
    active_posts, repost_count, reply_count, delete_count,
    created_at, updated_at
FROM author_ranking_old;

DROP TABLE author_ranking_old;

-- 更新author_ranking表中的url和title字段
UPDATE author_ranking
SET url = (
    SELECT url
    FROM post_ranking
    WHERE post_ranking.author = author_ranking.author
    ORDER BY post_ranking.last_active DESC
    LIMIT 1
),
title = (
    SELECT title
    FROM post_ranking
    WHERE post_ranking.author = author_ranking.author
    ORDER BY post_ranking.last_active DESC
    LIMIT 1
);

-- 重新创建索引
CREATE INDEX idx_author_ranking_author ON author_ranking(author);
CREATE INDEX idx_author_ranking_days_old ON author_ranking(days_old);
CREATE INDEX idx_author_ranking_last_active ON author_ranking(last_active);