-- 初始化保护表结构脚本
-- 该脚本创建在数据库更新过程中需要保留的表结构

-- 词云缓存表
CREATE TABLE IF NOT EXISTS wordcloud_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    cache_key TEXT NOT NULL,
    word_data TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(cache_key)
);

-- 在词云缓存表上创建索引
CREATE INDEX IF NOT EXISTS idx_wordcloud_cache_key ON wordcloud_cache(cache_key);

-- 用户数据表
CREATE TABLE IF NOT EXISTS user_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id TEXT NOT NULL,
    preferences TEXT,
    saved_filters TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(user_id)
);

-- 在用户数据表上创建索引
CREATE INDEX IF NOT EXISTS idx_user_data_user_id ON user_data(user_id);

-- 数据库维护记录表
CREATE TABLE IF NOT EXISTS db_maintenance_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_type TEXT NOT NULL,
    start_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    end_time TIMESTAMP,
    status TEXT,
    details TEXT,
    error_message TEXT
);

-- 在维护记录表上创建索引
CREATE INDEX IF NOT EXISTS idx_db_maintenance_operation ON db_maintenance_log(operation_type);
CREATE INDEX IF NOT EXISTS idx_db_maintenance_status ON db_maintenance_log(status);

-- 在这里可以添加更多保护表

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_wordcloud_cache_key ON wordcloud_cache(cache_key);
CREATE INDEX IF NOT EXISTS idx_user_data_user_id ON user_data(user_id); 