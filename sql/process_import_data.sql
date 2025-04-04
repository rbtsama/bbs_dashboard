-- 处理post_ranking表
INSERT OR REPLACE INTO post_ranking (
    thread_id, url, title, author_id, author,
    daysold, post_last_active,
    read_count, reply_count, repost_count, delete_count,
    created_at, updated_at
)
SELECT 
    SUBSTR(p.url, -10, 7) as thread_id,
    p.url, 
    COALESCE(d.title, p.title, '无标题') as title,
    p.author_link as author_id,
    p.author,
    CAST(JULIANDAY('now') - JULIANDAY(p.post_time) AS INTEGER) as daysold,
    CAST(JULIANDAY(p.scraping_time) - JULIANDAY('1970-01-01') AS INTEGER) as post_last_active,
    p.read_count, 
    p.reply_count, 
    COALESCE(ar.repost_count, 0) as repost_count, 
    COALESCE(ar.delete_count, 0) as delete_count,
    DATETIME('now') as created_at,
    DATETIME('now') as updated_at
FROM post p
LEFT JOIN detail d ON p.url = d.url
LEFT JOIN post_ranking pr ON p.url = pr.url
WHERE pr.url IS NULL OR p.scraping_time > pr.updated_at;

-- 处理car_detail表
INSERT OR REPLACE INTO car_detail (
    thread_id, author_id, year, model, miles, price,
    daysold, post_last_active,
    created_at, updated_at
)
SELECT 
    SUBSTR(p.url, -10, 7) as thread_id,
    p.author_link as author_id,
    CASE WHEN ci.year < 1900 OR ci.year > 2100 THEN NULL ELSE CAST(ci.year AS INTEGER) END as year,
    ci.model,
    CAST(ci.miles AS INTEGER) as miles,
    CAST(ci.price AS REAL) as price,
    CAST(JULIANDAY('now') - JULIANDAY(p.post_time) AS INTEGER) as daysold,
    CAST(JULIANDAY(p.scraping_time) - JULIANDAY('1970-01-01') AS INTEGER) as post_last_active,
    DATETIME('now') as created_at,
    DATETIME('now') as updated_at
FROM post p
LEFT JOIN detail d ON p.url = d.url
-- LEFT JOIN car_info ci ON p.url = ci.url -- 已由清理脚本注释
LEFT JOIN car_detail cd ON SUBSTR(p.url, -10, 7) = cd.thread_id
WHERE cd.thread_id IS NULL OR p.scraping_time > cd.updated_at;

-- 处理author_ranking表
INSERT OR REPLACE INTO author_ranking (
    author_id, author, daysold, author_last_active,
    active_posts, repost_count, reply_count, delete_count,
    created_at, updated_at
)
SELECT 
    p.author_link as author_id,
    p.author,
    MIN(CAST(JULIANDAY('now') - JULIANDAY(p.post_time) AS INTEGER)) as daysold,
    MAX(CAST(JULIANDAY(p.scraping_time) - JULIANDAY('1970-01-01') AS INTEGER)) as author_last_active,
    COUNT(DISTINCT p.url) as active_posts,
    COALESCE(ar.repost_count, 0) as repost_count,
    SUM(p.reply_count) as reply_count,
    COALESCE(ar.delete_count, 0) as delete_count,
    DATETIME('now') as created_at,
    DATETIME('now') as updated_at
FROM post p
GROUP BY p.author_link, p.author;

-- 记录post历史
INSERT INTO post_history (
    thread_id, url, title, author, author_id, 
    action, action_time, action_type, source,
    read_count, reply_count, created_at, updated_at
)
SELECT 
    SUBSTR(p.url, -10, 7) as thread_id,
    p.url, 
    COALESCE(d.title, p.title, '无标题') as title,
    p.author,
    p.author_link as author_id,
    'update' as action,
    p.scraping_time as action_time,
    'update' as action_type,
    'system' as source,
    p.read_count,
    p.reply_count,
    DATETIME('now') as created_at,
    DATETIME('now') as updated_at
FROM post p
LEFT JOIN detail d ON p.url = d.url
WHERE p.scraping_time > (
    SELECT MAX(action_time) FROM post_history ph WHERE ph.url = p.url
) OR NOT EXISTS (
    SELECT 1 FROM post_history ph WHERE ph.url = p.url
);

-- 记录author历史
INSERT INTO author_history (
    author_id, thread_id, url, title,
    action_time, action_type,
    created_at, updated_at
)
SELECT 
    p.author_link as author_id,
    SUBSTR(p.url, -10, 7) as thread_id,
    p.url,
    COALESCE(d.title, p.title, '无标题') as title,
    p.scraping_time as action_time,
    'update' as action_type,
    DATETIME('now') as created_at,
    DATETIME('now') as updated_at
FROM post p
LEFT JOIN detail d ON p.url = d.url
WHERE p.scraping_time > (
    SELECT MAX(action_time) FROM author_history ah WHERE ah.author_id = p.author_link
) OR NOT EXISTS (
    SELECT 1 FROM author_history ah WHERE ah.author_id = p.author_link
);

-- 更新词云任务队列
INSERT OR REPLACE INTO wordcloud_job (
    job_type, target_id, status, last_updated, next_update, 
    created_at, updated_at
)
SELECT 
    'thread' as job_type,
    thread_id as target_id,
    'pending' as status,
    DATETIME('now') as last_updated,
    DATETIME('now', '+1 day') as next_update,
    COALESCE((SELECT created_at FROM wordcloud_job WHERE job_type = 'thread' AND target_id = thread_id), DATETIME('now')) as created_at,
    DATETIME('now') as updated_at
FROM (
    SELECT DISTINCT thread_id 
    FROM car_detail 
    WHERE thread_id IS NOT NULL AND thread_id != ''
    ORDER BY post_last_active DESC
); 