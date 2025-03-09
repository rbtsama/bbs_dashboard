-- 帖子关注表
CREATE TABLE IF NOT EXISTS thread_follows (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thread_id TEXT NOT NULL,
    follow_type TEXT NOT NULL CHECK(follow_type IN ('my_follow', 'my_thread')),
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(thread_id)
); 