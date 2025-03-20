-- 数据版本控制表
CREATE TABLE IF NOT EXISTS data_version (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version_id TEXT NOT NULL,         -- 版本标识(如20250314_001)
    update_type TEXT NOT NULL,        -- 更新类型(incremental/full)
    started_at DATETIME NOT NULL,     -- 开始时间
    completed_at DATETIME,            -- 完成时间
    status TEXT NOT NULL,             -- 状态(in_progress/completed/failed)
    affected_rows INTEGER DEFAULT 0,  -- 影响的行数
    details TEXT,                     -- 详细信息
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 数据变更日志表
CREATE TABLE IF NOT EXISTS data_change_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version_id TEXT NOT NULL,         -- 关联的版本ID
    table_name TEXT NOT NULL,         -- 表名
    record_id TEXT NOT NULL,          -- 记录主键(url或其他ID)
    change_type TEXT NOT NULL,        -- 变更类型(insert/update/delete)
    old_values TEXT,                  -- 旧值(JSON格式)
    new_values TEXT,                  -- 新值(JSON格式)
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 词云缓存表结构调整
CREATE TABLE IF NOT EXISTS wordcloud_job (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    job_type TEXT NOT NULL,           -- 作业类型(author/thread)
    target_id TEXT NOT NULL,          -- 目标ID(作者名或thread_id)
    status TEXT NOT NULL,             -- 状态(pending/processing/completed/failed)
    last_updated DATETIME NOT NULL,   -- 上次更新时间
    next_update DATETIME NOT NULL,    -- 下次计划更新时间
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- 创建必要的索引
CREATE INDEX IF NOT EXISTS idx_data_version_version_id ON data_version(version_id);
CREATE INDEX IF NOT EXISTS idx_data_change_log_version_id ON data_change_log(version_id);
CREATE INDEX IF NOT EXISTS idx_data_change_log_table_record ON data_change_log(table_name, record_id);
CREATE INDEX IF NOT EXISTS idx_wordcloud_job_status ON wordcloud_job(status);
CREATE INDEX IF NOT EXISTS idx_wordcloud_job_next_update ON wordcloud_job(next_update); 