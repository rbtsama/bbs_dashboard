-- 增量数据处理脚本
-- 该脚本仅处理需要更新的数据，不会影响用户相关表

-- 1. 更新帖子排名表 (post_ranking)
INSERT OR REPLACE INTO post_ranking (
    url, title, author, author_link, thread_id, days_old, last_active,
    read_count, reply_count, repost_count, delete_count,
    created_at, updated_at
)
SELECT 
    p.url, 
    COALESCE(d.title, p.title, '无标题') as title, 
    p.author, 
    p.author_link,
    SUBSTR(p.url, -10, 7) as thread_id,
    CAST(JULIANDAY('now') - JULIANDAY(p.post_time) AS INTEGER) as days_old,
    CAST(JULIANDAY(p.scraping_time) - JULIANDAY('1970-01-01') AS INTEGER) as last_active,
    p.read_count, 
    p.reply_count, 
    COALESCE(pr.repost_count, 0) as repost_count, 
    COALESCE(pr.delete_count, 0) as delete_count,
    COALESCE(pr.created_at, DATETIME('now')) as created_at,
    DATETIME('now') as updated_at
FROM post p
LEFT JOIN detail d ON p.url = d.url
LEFT JOIN post_ranking pr ON p.url = pr.url
WHERE pr.url IS NULL OR p.scraping_time > pr.updated_at;

-- 2. 更新汽车详情表 (car_detail)
INSERT OR REPLACE INTO car_detail (
    thread_id, url, title, author, author_link,
    days_old, last_active, price, miles, year, model,
    created_at, updated_at
)
SELECT 
    SUBSTR(p.url, -10, 7) as thread_id,
    p.url, 
    COALESCE(d.title, p.title, '无标题') as title,
    p.author, 
    p.author_link,
    CAST(JULIANDAY('now') - JULIANDAY(p.post_time) AS INTEGER) as days_old,
    CAST(JULIANDAY(p.scraping_time) - JULIANDAY('1970-01-01') AS INTEGER) as last_active,
    CAST(ci.price AS REAL) as price,
    CAST(ci.miles AS REAL) as miles,
    CASE WHEN ci.year < 1900 OR ci.year > 2100 THEN NULL ELSE CAST(ci.year AS INTEGER) END as year,
    ci.model,
    COALESCE(cd.created_at, DATETIME('now')) as created_at,
    DATETIME('now') as updated_at
FROM post p
LEFT JOIN detail d ON p.url = d.url
-- LEFT JOIN car_info ci ON p.url = ci.url -- 已由清理脚本注释
LEFT JOIN car_detail cd ON p.url = cd.url
WHERE cd.url IS NULL OR p.scraping_time > cd.updated_at;

-- 3. 更新作者排名表 (author_ranking)
INSERT OR REPLACE INTO author_ranking (
    author, author_link, url, title, days_old, last_active,
    active_posts, repost_count, reply_count, delete_count,
    created_at, updated_at
)
SELECT 
    p.author, 
    p.author_link,
    (SELECT url FROM post_ranking WHERE author = p.author ORDER BY last_active DESC LIMIT 1),
    (SELECT title FROM post_ranking WHERE author = p.author ORDER BY last_active DESC LIMIT 1),
    MIN(CAST(JULIANDAY('now') - JULIANDAY(p.post_time) AS INTEGER)) as days_old,
    MAX(CAST(JULIANDAY(p.scraping_time) - JULIANDAY('1970-01-01') AS INTEGER)) as last_active,
    COUNT(DISTINCT p.url) as active_posts,
    COALESCE(ar.repost_count, 0) as repost_count,
    SUM(p.reply_count) as reply_count,
    COALESCE(ar.delete_count, 0) as delete_count,
    COALESCE(ar.created_at, DATETIME('now')) as created_at,
    DATETIME('now') as updated_at
FROM post p
LEFT JOIN author_ranking ar ON p.author = ar.author
GROUP BY p.author, p.author_link;

-- 4. 记录帖子历史数据 (post_history)
INSERT INTO post_history (
    thread_id, url, title, author, author_link, action_type, action_time,
    read_count, reply_count, created_at, updated_at
)
SELECT 
    SUBSTR(p.url, -10, 7) as thread_id,
    p.url, 
    COALESCE(d.title, p.title, '无标题') as title,
    p.author, 
    p.author_link,
    'update' as action_type,
    p.scraping_time as action_time,
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

-- 5. 记录作者历史数据 (author_history)
INSERT INTO author_history (
    author_id, author, author_link, action_type, action_time,
    active_posts, post_count, created_at, updated_at
)
SELECT 
    p.author as author_id,
    p.author,
    p.author_link,
    'update' as action_type,
    MAX(p.scraping_time) as action_time,
    COUNT(DISTINCT p.url) as active_posts,
    COUNT(DISTINCT p.url) as post_count,
    DATETIME('now') as created_at,
    DATETIME('now') as updated_at
FROM post p
GROUP BY p.author, p.author_link
HAVING MAX(p.scraping_time) > (
    SELECT MAX(action_time) FROM author_history ah WHERE ah.author = p.author
) OR NOT EXISTS (
    SELECT 1 FROM author_history ah WHERE ah.author = p.author
);

-- 6. 更新词云任务队列
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
    COALESCE(
        (SELECT created_at FROM wordcloud_job WHERE job_type = 'thread' AND target_id = thread_id), 
        DATETIME('now')
    ) as created_at,
    DATETIME('now') as updated_at
FROM (
    SELECT DISTINCT thread_id 
    FROM car_detail 
    WHERE thread_id IS NOT NULL AND thread_id != ''
    ORDER BY last_active DESC
    LIMIT 50  -- 只为最活跃的50个主题生成词云
); 