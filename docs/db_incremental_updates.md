# 增量数据更新流程

增量数据更新是系统的核心功能，通过 `py/update_db.py` 脚本实现。该流程设计为每日自动执行，确保数据库中的信息保持最新状态，同时不影响用户数据。

## 表分类管理

系统将数据库表分为三类，采用不同的更新策略：

1. **受保护表**：这些表包含用户数据，不会在更新过程中被修改
   ```
   thread_follow, user_settings, user_favorites, user_comments, 
   user_votes, user_profile, user_notifications, data_version, 
   data_change_log, wordcloud_cache
   ```

2. **合并表**：这些表使用合并策略更新，保留现有数据的同时添加或更新新数据
   ```
   post_ranking, car_detail, author_ranking, post_history, author_history
   ```

3. **常规表**：这些表在更新过程中可以完全替换
   ```
   post, detail, car_info, import, update
   ```

## 增量更新步骤

1. **初始化更新过程**
   - 创建新的版本记录，生成唯一的版本ID
   - 记录更新类型（增量/完全）和开始时间
   - 设置状态为"进行中"
   - 初始化变更日志记录

2. **创建临时数据库**
   - 复制主数据库的表结构到临时数据库
   - 复制受保护表的数据到临时数据库
   - 验证表结构完整性

3. **导入新数据**
   - 从Excel文件导入数据到临时数据库的相应表
   - 从CSV文件导入数据到临时数据库的相应表
   - 数据格式验证和清洗

4. **处理导入的数据**
   - 执行SQL脚本处理导入的数据
   - 生成派生字段和计算值
   - 更新关联表之间的关系
   - 数据一致性检查

5. **生成变更日志**
   - 比较临时数据库和主数据库中的数据
   - 记录所有插入、更新和删除操作
   - 保存旧值和新值用于审计和回滚
   - 统计变更数量

6. **应用更改**
   - 对于合并表，使用合并策略应用更改
   - 对于常规表，使用替换策略应用更改
   - 保护表不受影响
   - 事务管理确保原子性

7. **完成更新过程**
   - 更新版本记录的状态为"已完成"
   - 记录完成时间和影响的行数
   - 删除临时数据库
   - 触发后续处理（如词云更新）

## 错误处理机制

1. **数据验证错误**
   - 检查数据类型和格式
   - 验证必填字段
   - 检查外键约束
   - 记录错误详情

2. **更新失败处理**
   - 自动回滚事务
   - 保存失败状态和原因
   - 保留临时数据库供调试
   - 发送错误通知

3. **并发控制**
   - 使用文件锁防止并发更新
   - 检测长时间运行的更新
   - 强制结束超时任务
   - 清理孤立的临时文件

## 监控和日志

1. **更新过程日志**
   - 记录每个步骤的开始和结束时间
   - 统计处理的记录数
   - 记录重要的中间状态
   - 保存详细的错误信息

2. **性能监控**
   - 跟踪更新耗时
   - 监控数据库大小变化
   - 记录资源使用情况
   - 生成性能报告

3. **数据质量检查**
   - 验证数据完整性
   - 检查数据一致性
   - 统计异常值
   - 生成质量报告

## 相关配置

1. **更新策略配置**
   ```python
   PROTECTED_TABLES = [
       'thread_follow',       # 用户关注的主题
       'user_settings',       # 用户设置
       'user_favorites',      # 用户收藏
       'user_comments',       # 用户评论
       'user_votes',         # 用户投票
       'user_profile',       # 用户个人资料
       'user_notifications', # 用户通知
       'data_version',      # 数据版本信息
       'data_change_log',   # 数据变更日志
       'wordcloud_cache'    # 词云缓存
   ]

   MERGE_TABLES = [
       'post_ranking',      # 帖子排名
       'car_detail',       # 汽车详情
       'author_ranking',   # 作者排名
       'post_history',     # 帖子历史
       'author_history'    # 作者历史
   ]
   ```

2. **更新调度配置**
   ```python
   UPDATE_SCHEDULE = {
       'incremental': '0 */4 * * *',  # 每4小时
       'full': '0 0 * * 0',          # 每周日凌晨
       'backup': '0 2 * * *'         # 每天凌晨2点
   }
   ```

## 相关文档

- [数据库概览](./db_overview.md)
- [数据表定义](./db_table_definitions.md)
- [数据版本控制](./db_version_control.md)
- [数据备份与恢复](./db_backup_recovery.md)

## 增量更新SQL脚本

`sql/incremental_update.sql` 脚本包含以下主要操作：

1. **更新帖子排名表**
   ```sql
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
   ```

2. **更新汽车详情表**
   ```sql
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
   LEFT JOIN car_info ci ON p.url = ci.url
   LEFT JOIN car_detail cd ON p.url = cd.url
   WHERE cd.url IS NULL OR p.scraping_time > cd.updated_at;
   ```

3. **更新作者排名表**
   ```sql
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
   ```

4. **记录帖子历史数据**
   ```sql
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
   ```

5. **记录作者历史数据**
   ```sql
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
   ```

6. **更新词云任务队列**
   ```sql
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
   ```

## 更新脚本实现

`py/update_db.py` 脚本实现了完整的增量更新流程，主要功能包括：

1. **DatabaseUpdater 类**：管理整个更新过程
   - 初始化：设置数据库路径、临时数据库路径、版本ID
   - 表分类：定义受保护表和合并表列表
   - 更新流程：实现完整的增量更新步骤

2. **合并策略实现**：
   ```python
   def _merge_table_data(self, temp_cursor, main_cursor, table_name):
       """合并表数据而不是替换"""
       # 获取表的主键
       primary_key = self._get_table_primary_key(main_cursor, table_name)
       
       # 从临时数据库中获取所有记录
       temp_cursor.execute(f"SELECT * FROM {table_name}")
       temp_records = temp_cursor.fetchall()
       
       for record in temp_records:
           record_dict = dict(zip(columns, record))
           record_id = record_dict[primary_key]
           
           # 检查记录是否存在
           main_cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {primary_key} = ?", (record_id,))
           exists = main_cursor.fetchone()[0] > 0
           
           if exists:
               # 更新现有记录
               set_clause = ", ".join([f"{col} = ?" for col in columns if col != primary_key])
               values = [record_dict[col] for col in columns if col != primary_key]
               values.append(record_id)
               
               main_cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE {primary_key} = ?", 
                                   values)
           else:
               # 插入新记录
               placeholders = ", ".join(["?" for _ in columns])
               main_cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", record)
   ```

3. **变更日志生成**：
   ```python
   def generate_change_log(self, main_tables):
       """生成变更日志，比较临时数据库和主数据库中指定表的差异"""
       for table_name in main_tables:
           # 获取表的主键列
           primary_key = self._get_table_primary_key(main_cursor, table_name)
           
           # 获取临时数据库中的所有记录
           temp_cursor.execute(f"SELECT * FROM {table_name}")
           temp_records = temp_cursor.fetchall()
           
           # 获取主数据库中的所有记录ID
           main_cursor.execute(f"SELECT {primary_key} FROM {table_name}")
           main_record_ids = set(row[0] for row in main_cursor.fetchall())
           
           # 记录变更
           for record in temp_records:
               record_dict = dict(zip(columns, record))
               record_id = record_dict[primary_key]
               
               if record_id in main_record_ids:
                   # 记录存在，检查是否有更新
                   main_cursor.execute(
                       f"SELECT * FROM {table_name} WHERE {primary_key} = ?", 
                       (record_id,)
                   )
                   main_record = main_cursor.fetchone()
                   main_record_dict = dict(zip(columns, main_record))
                   
                   # 检查是否有变更
                   if main_record_dict != record_dict:
                       # 记录更新
                       main_cursor.execute(f'''
                       INSERT INTO data_change_log 
                       (version_id, table_name, record_id, change_type, old_values, new_values)
                       VALUES (?, ?, ?, ?, ?, ?)
                       ''', (
                           self.version_id, 
                           table_name, 
                           record_id, 
                           'update',
                           json.dumps(main_record_dict),
                           json.dumps(record_dict)
                       ))
               else:
                   # 新记录，记录插入
                   main_cursor.execute(f'''
                   INSERT INTO data_change_log 
                   (version_id, table_name, record_id, change_type, old_values, new_values)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ''', (
                       self.version_id, 
                       table_name, 
                       record_id, 
                       'insert',
                       None,
                       json.dumps(record_dict)
                   ))
   ```

## 手动触发更新

可以通过以下命令手动触发数据库更新：

```powershell
python py/update_db.py
```

该命令将执行完整的增量更新流程，包括：
1. 创建新的版本记录
2. 导入最新的数据
3. 生成变更日志
4. 应用更改到主数据库
5. 更新词云任务队列

## 相关文档

- [数据库概览](./db_overview.md)
- [数据处理流程](./db_data_processing.md)
- [数据版本控制](./db_version_control.md)
- [定时任务管理](./db_scheduled_tasks.md)

## 特殊字段处理

### 数值字段转换

在数据导入过程中，系统会对特定表的数值字段进行处理，确保其类型正确：

```python
# 确保处理post_ranking和author_ranking的特殊字段
if table_name in ['post_ranking', 'author_ranking']:
    print(f"处理{table_name}表的特殊字段...")
    try:
        # 检查表结构
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in cursor.fetchall()]
        
        # 确定delete字段名称
        delete_field = 'delete_count'
        if 'delete_reply_count' in columns:
            delete_field = 'delete_reply_count'
        
        # 确保数值字段为整数类型
        if 'repost_count' in columns and delete_field in columns:
            cursor.execute(f'''
            UPDATE {table_name} 
            SET repost_count = CAST(repost_count AS INTEGER),
                {delete_field} = CAST({delete_field} AS INTEGER)
            ''')
            print(f"已将{table_name}表的repost_count和{delete_field}字段转换为整数类型")
    except Exception as e:
        print(f"处理{table_name}表特殊字段时出错: {str(e)}")
```

这个处理确保了：
1. 正确识别delete_count或delete_reply_count字段
2. 将字符串值转换为整数值
3. 确保数值比较正确执行

### 词云表处理

在数据库更新完成后，系统会确保词云相关表结构正确，并生成新的词云数据：

```python
# 确保创建词云表
with sqlite3.connect(updater.temp_db_path) as conn:
    cursor = conn.cursor()
    # 确保词云表结构正确
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS wordcloud_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        data TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        version INTEGER DEFAULT 1
    )
    """)
    logger.info("已确保词云表结构正确")

# 生成词云
try:
    from generate_wordcloud import update_word_frequencies
    if update_word_frequencies():
        logger.info("成功生成词云数据")
    else:
        logger.warning("生成词云数据失败")
except Exception as e:
    logger.warning(f"生成词云数据过程中出错: {str(e)}")
```

## 修复工具

系统提供了专门的修复工具来解决特定问题：

### fix_limit_count.py

修复repost_count字段类型问题和数值限制：

```python
def fix_limit_count():
    """修复数据库中重发次数被限制为9的问题"""
    # 检查表结构
    # 转换表结构从TEXT到INTEGER
    # 从CSV更新数据
    # 修复SQL文件中的问题
```

### fix_wordcloud.py

修复词云表结构问题：

```python
def fix_wordcloud_table():
    """修复词云表结构问题"""
    # 检查表结构
    # 修复缺失的必要列
    # 恢复数据
```

## 保护用户数据表

在增量更新过程中，某些包含用户数据的表需要特别保护，以防止用户数据被覆盖或丢失。
这些表包括：

- `user_settings` - 用户设置
- `user_favorites` - 用户收藏
- `user_comments` - 用户评论
- `user_votes` - 用户投票
- `thread_follows` - 用户关注的帖子

处理步骤：

1. 在创建临时数据库时，复制这些表的所有数据
2. 在合并数据时，不进行覆盖操作，只添加新记录
3. 对于`thread_follows`表，还要确保字段结构完整性：
   - 检查`days_old`和`last_active`字段是否存在
   - 如果不存在，自动添加并设置合理的默认值
   - 创建必要的索引以提高查询性能

```python
# 受保护的表列表
protected_tables = [
    'user_settings',
    'user_favorites', 
    'user_comments',
    'user_votes',
    'thread_follows'  # 用户关注的帖子
]

# 特殊处理：确保thread_follows表结构完整
if 'thread_follows' in tables_to_merge:
    try:
        # 检查字段是否存在，如不存在则添加
        cursor.execute("SELECT days_old FROM thread_follows LIMIT 1")
    except:
        cursor.execute("ALTER TABLE thread_follows ADD COLUMN days_old INTEGER DEFAULT 0")
        logger.info("已添加days_old列到thread_follows表")
        
    try:
        cursor.execute("SELECT last_active FROM thread_follows LIMIT 1")
    except:
        cursor.execute("ALTER TABLE thread_follows ADD COLUMN last_active TEXT")
        logger.info("已添加last_active列到thread_follows表")
    
    # 创建必要的索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_thread_follows_user_id ON thread_follows(user_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_thread_follows_thread_id ON thread_follows(thread_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_thread_follows_thread_url ON thread_follows(thread_url)")
```

## 特殊表处理

### post_history表处理

对于`post_history`表，需要特殊处理以确保前端与后端的兼容性：

1. 确保`thread_id`字段为TEXT类型
2. 添加`event_type`和`event_time`字段，与`action`和`action_time`保持同步
3. 创建必要的索引以提高查询性能

```python
# 处理post_history表
if 'post_history' in tables_to_merge:
    # 确保event_type和event_time字段存在
    try:
        cursor.execute("SELECT event_type FROM post_history LIMIT 1")
    except:
        cursor.execute("ALTER TABLE post_history ADD COLUMN event_type TEXT")
        # 将action的值复制到event_type
        cursor.execute("UPDATE post_history SET event_type = action")
        logger.info("已添加event_type列到post_history表并从action复制数据")
        
    try:
        cursor.execute("SELECT event_time FROM post_history LIMIT 1")
    except:
        cursor.execute("ALTER TABLE post_history ADD COLUMN event_time TEXT")
        # 将action_time的值复制到event_time
        cursor.execute("UPDATE post_history SET event_time = action_time")
        logger.info("已添加event_time列到post_history表并从action_time复制数据")
    
    # 创建必要的索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_post_history_thread_id ON post_history(thread_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_post_history_event_type ON post_history(event_type)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_post_history_event_time ON post_history(event_time)")
``` 