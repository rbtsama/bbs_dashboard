# 数据库概览

## 数据库基本信息

数据库位置：`backend/db/forum_data.db`

系统使用SQLite数据库存储所有处理后的数据，主要包含以下类型的表：

## 表分类

1. **原始数据表**：存储经过预处理的原始数据
   - `post` - 发帖列表数据
   - `list` - 更新列表数据
   - `post_action` - 帖子行为记录数据
   - `car_info` - 车辆信息数据

2. **统计数据表**：存储聚合统计数据
   - `post_statistic` - 发帖量统计
   - `update_statistic` - 更新量统计
   - `view_statistic` - 浏览量统计
   - `post_ranking` - 帖子排行
   - `author_ranking` - 作者排行
   - `post_history` - 帖子历史记录
   - `author_history` - 作者历史记录
   - `car_detail` - 车辆详细信息

3. **功能数据表**：支持应用功能的数据
   - `thread_follow` - 帖子关注记录（用户关注的帖子和标记的帖子）
   - `thread_history_cache` - 帖子历史缓存
   - `wordcloud_cache` - 词云缓存
   - `wordcloud_job` - 词云生成任务队列

4. **版本控制表**：管理数据更新和变更
   - `data_version` - 数据版本信息（新增字段：affected_rows, details）
   - `data_change_log` - 数据变更日志（新增字段：old_values, new_values）

5. **用户数据表**：存储用户相关信息
   - `user_settings` - 用户设置
   - `user_favorites` - 用户收藏
   - `user_comments` - 用户评论
   - `user_votes` - 用户投票
   - `user_profile` - 用户个人资料
   - `user_notifications` - 用户通知

## 数据更新策略

系统采用三层更新策略：

1. **受保护表**：用户数据表和配置表，不会在自动更新中被修改
2. **合并表**：统计数据表，使用合并策略保留历史数据
3. **常规表**：原始数据表，可以完全替换

## 主要功能

1. **数据版本控制**：
   - 完整的数据变更追踪
   - 支持数据回滚
   - 详细的变更日志

2. **词云生成系统**：
   - 基于帖子标题的词频统计
   - 定期自动更新
   - 简单直观的展示

3. **帖子关注系统**：
   - 支持关注感兴趣的帖子
   - 支持标记自己的帖子
   - 实时更新帖子状态
   - 查看帖子更新历史

4. **数据备份恢复**：
   - 自动定时备份
   - 增量备份
   - 快速恢复机制

## 相关文档

- [数据来源与采集](./db_data_sources.md)
- [数据表定义](./db_table_definitions.md)
- [数据处理流程](./db_data_processing.md)
- [增量数据更新](./db_incremental_updates.md)
- [数据版本控制](./db_version_control.md)
- [数据备份与恢复](./db_backup_recovery.md)
- [定时任务管理](./db_scheduled_tasks.md)
- [词云生成系统](./db_wordcloud_system.md)
- [数据使用指南](./db_usage_guide.md) 