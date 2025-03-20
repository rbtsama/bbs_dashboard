-- 为post表添加索引
CREATE INDEX IF NOT EXISTS idx_post_url ON post(url);
CREATE INDEX IF NOT EXISTS idx_post_author ON post(author);
CREATE INDEX IF NOT EXISTS idx_post_scraping_time ON post(scraping_time);

-- 为detail表添加索引
CREATE INDEX IF NOT EXISTS idx_detail_url ON detail(url);
CREATE INDEX IF NOT EXISTS idx_detail_author ON detail(author); 