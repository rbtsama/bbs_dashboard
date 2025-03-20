# 数据表定义

本文档详细描述了数据库中各个表的结构和字段定义。

## 版本控制表

### data_version 表
- `id` - 自增主键
- `version_id` - 版本标识(如20250314_001)
- `update_type` - 更新类型(incremental/full)
- `started_at` - 开始时间
- `completed_at` - 完成时间
- `status` - 状态(in_progress/completed/failed)
- `affected_rows` - 影响的行数
- `details` - 详细信息
- `created_at` - 创建时间

### data_change_log 表
- `id` - 自增主键
- `version_id` - 关联的版本ID
- `table_name` - 表名
- `record_id` - 记录主键(url或其他ID)
- `change_type` - 变更类型(insert/update/delete)
- `old_values` - 旧值(JSON格式)
- `new_values` - 新值(JSON格式)
- `created_at` - 创建时间

## 原始数据表

### post 表
- `url` - 帖子URL (主键)
- `title` - 帖子标题
- `author` - 作者名
- `author_link` - 作者链接
- `post_time` - 发帖时间
- `scraping_time` - 抓取时间
- `scraping_time_R` - 抓取时间(四舍五入到15分钟)
- `read_count` - 阅读数
- `reply_count` - 回复数
- `source_file` - 来源文件
- `sheet_name` - 工作表名

### list 表
- `url` - 帖子URL
- `title` - 帖子标题
- `author` - 作者名
- `author_link` - 作者链接
- `list_time` - 列表时间
- `list_time_R` - 列表时间(四舍五入到15分钟)
- `scraping_time` - 抓取时间
- `scraping_time_R` - 抓取时间(四舍五入到15分钟)
- `read_count` - 阅读数
- `reply_count` - 回复数
- `num` - 序号
- `update_reason` - 更新原因
- `source_file` - 来源文件
- `sheet_name` - 工作表名

### detail 表
- `url` - 帖子URL (主键)
- `title` - 帖子标题
- `author` - 作者名
- `author_link` - 作者链接
- `post_time` - 发帖时间
- `scraping_time` - 抓取时间
- `scraping_time_R` - 抓取时间(四舍五入到15分钟)
- `content` - 帖子内容
- `tags` - 标签
- `related_tags` - 相关标签
- `car_description` - 车辆描述
- `source_file` - 来源文件
- `sheet_name` - 工作表名

### car_info 表
- `url` - 帖子URL (主键)
- `title` - 帖子标题
- `year` - 车辆年份
- `make` - 品牌
- `model` - 型号
- `miles` - 里程
- `price` - 价格
- `trade_type` - 交易类型
- `location` - 地点
- `daysold` - 已发布天数
- `last_active` - 最后活跃时间戳

## 统计数据表

### post_ranking 表
- `url` - 帖子URL (主键)
- `title` - 帖子标题
- `author` - 作者名
- `author_link` - 作者链接
- `thread_id` - 帖子ID (从URL提取，TEXT类型)
- `days_old` - 已发布天数 (INTEGER)
- `daysold` - 已发布天数 (INTEGER，历史字段，与days_old保持同步)
- `last_active` - 最后活跃时间戳 (INTEGER)
- `read_count` - 阅读数 (INTEGER)
- `reply_count` - 回复数 (INTEGER)
- `repost_count` - 重发次数 (INTEGER)
- `delete_reply_count` - 删除回复次数 (INTEGER)
- `created_at` - 创建时间
- `updated_at` - 更新时间

### author_ranking 表
- `author` - 作者名 (主键)
- `author_link` - 作者链接
- `url` - 最新帖子URL
- `title` - 最新帖子标题
- `days_old` - 首次发帖距今天数 (INTEGER)
- `daysold` - 首次发帖距今天数 (INTEGER，历史字段，与days_old保持同步)
- `last_active` - 最后活跃时间戳 (INTEGER)
- `active_posts` - 活跃帖子数 (INTEGER)
- `repost_count` - 重发次数 (INTEGER)
- `reply_count` - 回复总数 (INTEGER)
- `delete_reply_count` - 删除回复次数 (INTEGER)
- `created_at` - 创建时间
- `updated_at` - 更新时间

### post_history 表
- `id` - 自增主键
- `thread_id` - 帖子ID (TEXT类型)
- `url` - 帖子URL
- `title` - 帖子标题
- `author` - 作者名
- `author_id` - 作者ID
- `author_link` - 作者链接
- `action` - 动作类型(新发布/重发/回帖/删回帖)
- `action_time` - 动作时间
- `action_type` - 动作类型(与action相同，兼容性字段)
- `event_type` - 事件类型(与action相同，前端使用)
- `event_time` - 事件时间(与action_time相同，前端使用)
- `source` - 数据来源
- `read_count` - 当时的阅读数
- `reply_count` - 当时的回复数
- `details` - 详细信息(JSON格式)
- `created_at` - 创建时间
- `updated_at` - 更新时间

索引：
- `idx_post_history_thread_id` - 在thread_id上创建索引
- `idx_post_history_url` - 在url上创建索引
- `idx_post_history_action_time` - 在action_time上创建索引
- `idx_post_history_action` - 在action上创建索引
- `idx_post_history_event_type` - 在event_type上创建索引
- `idx_post_history_event_time` - 在event_time上创建索引

### author_history 表
- `id` - 自增主键
- `author_id` - 作者ID
- `author` - 作者名
- `author_link` - 作者链接
- `action_type` - 动作类型
- `action_time` - 动作时间
- `active_posts` - 当时的活跃帖子数
- `post_count` - 当时的发帖总数
- `created_at` - 创建时间
- `updated_at` - 更新时间

### car_detail 表
- `thread_id` - 帖子ID (主键)
- `url` - 帖子URL
- `title` - 帖子标题
- `author` - 作者名
- `author_link` - 作者链接
- `days_old` - 已发布天数
- `last_active` - 最后活跃时间戳
- `price` - 价格
- `miles` - 里程
- `year` - 车辆年份
- `model` - 车型
- `created_at` - 创建时间
- `updated_at` - 更新时间

## 功能数据表

### wordcloud_job 表
- `id` - 自增主键
- `job_type` - 作业类型(author/thread)
- `target_id` - 目标ID(作者名或thread_id)
- `status` - 状态(pending/processing/completed/failed)
- `last_updated` - 上次更新时间
- `next_update` - 下次计划更新时间
- `priority` - 优先级(1-5，默认3)
- `retry_count` - 重试次数
- `error_message` - 错误信息
- `created_at` - 创建时间
- `updated_at` - 更新时间

### wordcloud_cache 表
- `id` - 自增主键
- `type` - 缓存类型(wordcloud/author/thread)
- `data` - 词云数据(JSON格式)
- `created_at` - 创建时间
- `version` - 版本号 (INTEGER, 默认为1)

### wordcloud_stats 表
- `id` - 自增主键
- `cache_type` - 缓存类型(author/thread)
- `target_id` - 目标ID
- `total_words` - 总词数
- `unique_words` - 不重复词数
- `top_words` - 热门词(JSON格式)
- `word_cloud_history` - 历史记录(JSON格式)
- `created_at` - 创建时间
- `updated_at` - 更新时间

### thread_follow 表
- `id` - 自增主键
- `thread_id` - 帖子ID
- `url` - 帖子URL
- `title` - 帖子标题
- `author` - 作者名
- `author_link` - 作者链接
- `type` - 关注类型，可选值: 'my_follow'（我的关注）或'marked'（我的帖子）
- `follow_status` - 关注状态，默认为active
- `daysold` - 已发布天数
- `last_active` - 最后活跃天数（距今）
- `repost_count` - 重发次数
- `reply_count` - 回复数
- `delete_reply_count` - 删除回复次数
- `created_at` - 创建时间
- `updated_at` - 更新时间

### thread_history_cache 表
- `id` - 自增主键
- `url` - 帖子URL
- `title` - 帖子标题
- `history_data` - 历史数据(JSON格式)
- `generated_at` - 生成时间
- `created_at` - 创建时间
- `updated_at` - 更新时间

## 用户数据表

### user_settings 表
- `id` - 自增主键
- `user_id` - 用户ID (唯一)
- `theme` - 主题设置
- `notification_enabled` - 通知开关
- `data_preferences` - 数据偏好设置(JSON格式)
- `created_at` - 创建时间
- `updated_at` - 更新时间

### user_favorites 表
- `id` - 自增主键
- `user_id` - 用户ID
- `url` - 收藏的URL
- `title` - 收藏的标题
- `note` - 用户笔记
- `created_at` - 创建时间
- `updated_at` - 更新时间

### user_comments 表
- `id` - 自增主键
- `user_id` - 用户ID
- `url` - 评论的URL
- `content` - 评论内容
- `parent_id` - 父评论ID
- `created_at` - 创建时间
- `updated_at` - 更新时间

### user_votes 表
- `id` - 自增主键
- `user_id` - 用户ID
- `url` - 投票的URL
- `vote_type` - 投票类型(1: 赞, -1: 踩)
- `created_at` - 创建时间
- `updated_at` - 更新时间

### user_profile 表
- `id` - 自增主键
- `user_id` - 用户ID (唯一)
- `display_name` - 显示名称
- `avatar_url` - 头像URL
- `bio` - 个人简介
- `created_at` - 创建时间
- `updated_at` - 更新时间

### user_notifications 表
- `id` - 自增主键
- `user_id` - 用户ID
- `type` - 通知类型
- `content` - 通知内容
- `is_read` - 是否已读
- `related_url` - 相关URL
- `created_at` - 创建时间
- `updated_at` - 更新时间

### thread_follows 表
- `id` - 自增主键
- `thread_id` - 帖子ID (TEXT类型)
- `url` - 帖子URL
- `title` - 帖子标题
- `author` - 作者名
- `author_id` - 作者ID
- `author_link` - 作者链接
- `type` - 关注类型：'my_follow'(我的关注)或'marked'(我的帖子)
- `follow_status` - 关注状态，默认为'active'
- `days_old` - 已发布天数 (INTEGER类型)
- `last_active` - 最后活跃时间 (TEXT类型，如"3天前")
- `repost_count` - 重发次数
- `reply_count` - 回复数
- `delete_reply_count` - 删除回复次数
- `created_at` - 创建时间
- `updated_at` - 更新时间

索引：
- `idx_thread_follows_user_id` - 用户ID索引
- `idx_thread_follows_thread_id` - 帖子ID索引
- `idx_thread_follows_thread_url` - 帖子URL索引

## 相关文档

- [数据库概览](./db_overview.md)
- [数据来源与采集](./db_data_sources.md)
- [数据处理流程](./db_data_processing.md)
- [增量数据更新](./db_incremental_updates.md)

## 索引定义

### 版本控制索引
```sql
CREATE INDEX IF NOT EXISTS idx_data_version_version_id ON data_version(version_id);
CREATE INDEX IF NOT EXISTS idx_data_change_log_version_id ON data_change_log(version_id);
CREATE INDEX IF NOT EXISTS idx_data_change_log_table_record ON data_change_log(table_name, record_id);
```

### 词云系统索引
```sql
CREATE INDEX IF NOT EXISTS idx_wordcloud_job_status ON wordcloud_job(status);
CREATE INDEX IF NOT EXISTS idx_wordcloud_job_next_update ON wordcloud_job(next_update);
CREATE INDEX IF NOT EXISTS idx_wordcloud_cache_type_target ON wordcloud_cache(cache_type, target_id);
CREATE INDEX IF NOT EXISTS idx_wordcloud_cache_expire ON wordcloud_cache(expire_at);
CREATE INDEX IF NOT EXISTS idx_wordcloud_stats_type_target ON wordcloud_stats(cache_type, target_id);
```