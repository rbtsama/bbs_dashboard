-- 词云任务表
CREATE TABLE IF NOT EXISTS wordcloud_job (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_type TEXT NOT NULL,           -- 作业类型(thread)
    target_id TEXT NOT NULL,          -- 目标ID(thread_id)
    status TEXT NOT NULL,             -- 状态(pending/processing/completed/failed)
    last_updated DATETIME NOT NULL,   -- 上次更新时间
    next_update DATETIME NOT NULL,    -- 下次计划更新时间
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 词云缓存表
DROP TABLE IF EXISTS wordcloud_cache;
CREATE TABLE IF NOT EXISTS wordcloud_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id TEXT NOT NULL,          -- 主题ID
    title TEXT,                       -- 主题标题
    image_path TEXT NOT NULL,         -- 词云图片路径
    data_path TEXT NOT NULL,          -- 词云数据路径
    generated_at DATETIME NOT NULL,   -- 生成时间
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建必要的索引
CREATE INDEX IF NOT EXISTS idx_wordcloud_job_status ON wordcloud_job(status);
CREATE INDEX IF NOT EXISTS idx_wordcloud_job_next_update ON wordcloud_job(next_update);
CREATE INDEX IF NOT EXISTS idx_wordcloud_cache_thread_id ON wordcloud_cache(thread_id); 