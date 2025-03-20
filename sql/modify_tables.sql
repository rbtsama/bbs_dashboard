-- 修改表结构以适应增量更新需求

-- 为post_ranking表添加thread_id列
ALTER TABLE post_ranking ADD COLUMN thread_id TEXT;

-- 更新thread_id值
UPDATE post_ranking SET thread_id = SUBSTR(url, -10, 7);

-- 为thread_id创建索引
CREATE INDEX IF NOT EXISTS idx_post_ranking_thread_id ON post_ranking(thread_id); 