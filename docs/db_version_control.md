# 数据版本控制

系统使用版本控制表跟踪所有数据更改，确保数据完整性和可追溯性。

## 版本控制表结构

1. **data_version 表**：记录每次更新的元数据
   ```sql
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
   ```

2. **data_change_log 表**：记录每个记录的具体变更
   ```sql
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
   ```

## 版本控制流程

1. **版本创建**：每次更新开始时，创建新的版本记录
   ```python
   def start_update_process(self, update_type="incremental"):
       """开始更新过程，记录版本信息"""
       conn = sqlite3.connect(self.db_path)
       cursor = conn.cursor()
       
       # 确保版本表存在
       cursor.execute('''
       CREATE TABLE IF NOT EXISTS data_version (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           version_id TEXT NOT NULL,
           update_type TEXT NOT NULL,
           started_at DATETIME NOT NULL,
           completed_at DATETIME,
           status TEXT NOT NULL,
           affected_rows INTEGER DEFAULT 0,
           details TEXT,
           created_at DATETIME DEFAULT CURRENT_TIMESTAMP
       )
       ''')
       
       # 插入新版本记录
       cursor.execute('''
       INSERT INTO data_version 
       (version_id, update_type, started_at, status) 
       VALUES (?, ?, ?, ?)
       ''', (self.version_id, update_type, datetime.datetime.now(), 'in_progress'))
       
       conn.commit()
       conn.close()
       
       logger.info(f"开始数据更新，版本ID: {self.version_id}, 类型: {update_type}")
       return self.version_id
   ```

2. **变更记录**：记录每个表的每条记录的变更
   ```python
   def generate_change_log(self, main_tables):
       """生成变更日志，比较临时数据库和主数据库中指定表的差异"""
       # 对于每个表
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

3. **版本完成**：更新完成后，更新版本状态
   ```python
   # 更新版本记录
   main_cursor.execute('''
   UPDATE data_version 
   SET completed_at = ?, status = ?, affected_rows = ?
   WHERE version_id = ?
   ''', (datetime.datetime.now(), 'completed', affected_rows, self.version_id))
   ```

4. **版本失败处理**：如果更新过程失败，记录失败状态
   ```python
   # 记录失败状态
   try:
       fail_conn = sqlite3.connect(self.db_path)
       fail_cursor = fail_conn.cursor()
       
       fail_cursor.execute('''
       UPDATE data_version 
       SET completed_at = ?, status = ?, details = ?
       WHERE version_id = ?
       ''', (datetime.datetime.now(), 'failed', str(e), self.version_id))
       
       fail_conn.commit()
       fail_conn.close()
   except:
       pass
   ```

## 版本查询与回滚

系统支持查询历史版本信息和变更日志，便于审计和问题排查。

1. **查询版本历史**：
   ```sql
   SELECT 
       version_id, 
       update_type, 
       started_at, 
       completed_at, 
       status, 
       affected_rows 
   FROM data_version 
   ORDER BY started_at DESC 
   LIMIT 10;
   ```

2. **查询特定版本的变更**：
   ```sql
   SELECT 
       table_name, 
       record_id, 
       change_type, 
       old_values, 
       new_values 
   FROM data_change_log 
   WHERE version_id = '20250314_001' 
   ORDER BY table_name, record_id;
   ```

3. **查询特定记录的变更历史**：
   ```sql
   SELECT 
       dcl.version_id, 
       dv.started_at, 
       dcl.change_type, 
       dcl.old_values, 
       dcl.new_values 
   FROM data_change_log dcl
   JOIN data_version dv ON dcl.version_id = dv.version_id
   WHERE dcl.table_name = 'post_ranking' 
   AND dcl.record_id = 'https://example.com/thread/1234567'
   ORDER BY dv.started_at DESC;
   ```

## 版本控制的优势

1. **数据追溯**：可以追踪每条记录的完整变更历史
2. **审计支持**：记录谁在什么时间做了什么变更
3. **问题排查**：当数据出现问题时，可以查看历史变更找出原因
4. **回滚能力**：理论上可以基于变更日志实现数据回滚

## 相关文档

- [数据库概览](./db_overview.md)
- [增量数据更新](./db_incremental_updates.md)
- [数据备份与恢复](./db_backup_recovery.md) 