# 数据备份与恢复

本文档描述系统的数据备份策略、恢复流程和日常维护计划，确保数据安全和系统稳定性。

## 备份策略

系统采用多层次备份策略，确保数据安全：

### 1. 自动定时备份

系统通过Windows计划任务自动执行以下备份：

1. **每日增量备份**：每天凌晨3:00执行
   ```powershell
   # 备份脚本示例
   $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
   $backupPath = "backup\db\forum_data_$timestamp.db"
   
   # 复制数据库文件
   Copy-Item "backend\db\forum_data.db" $backupPath
   
   # 记录备份日志
   Add-Content "logs\backup_log.txt" "$(Get-Date) - 每日备份完成: $backupPath"
   
   # 保留最近30天的备份，删除更早的备份
   Get-ChildItem "backup\db\forum_data_*.db" | 
       Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } | 
       ForEach-Object { Remove-Item $_.FullName }
   ```

2. **每周完整备份**：每周日凌晨4:00执行
   ```powershell
   # 备份脚本示例
   $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
   $weeklyBackupPath = "backup\db\weekly_forum_data_$timestamp.db"
   
   # 复制数据库文件
   Copy-Item "backend\db\forum_data.db" $weeklyBackupPath
   
   # 压缩备份文件
   Compress-Archive -Path $weeklyBackupPath -DestinationPath "$weeklyBackupPath.zip"
   Remove-Item $weeklyBackupPath
   
   # 记录备份日志
   Add-Content "logs\backup_log.txt" "$(Get-Date) - 每周备份完成: $weeklyBackupPath.zip"
   
   # 保留最近12周的备份
   Get-ChildItem "backup\db\weekly_forum_data_*.db.zip" | 
       Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-84) } | 
       ForEach-Object { Remove-Item $_.FullName }
   ```

### 2. 更新前自动备份

每次执行数据更新前，系统会自动创建备份：

```python
def backup_database(self):
    """在更新前备份数据库"""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"backup/db/pre_update_{self.version_id}_{timestamp}.db"
    
    try:
        shutil.copy2(self.db_path, backup_path)
        logger.info(f"数据库备份成功: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"数据库备份失败: {str(e)}")
        return None
```

### 3. 手动备份

管理员可以随时执行手动备份：

```powershell
# 手动备份脚本
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$manualBackupPath = "backup\db\manual_forum_data_$timestamp.db"

# 复制数据库文件
Copy-Item "backend\db\forum_data.db" $manualBackupPath

# 记录备份日志
Add-Content "logs\backup_log.txt" "$(Get-Date) - 手动备份完成: $manualBackupPath"

Write-Host "手动备份已完成: $manualBackupPath"
```

## 恢复流程

当需要恢复数据时，可以按照以下流程操作：

### 1. 从备份恢复

```powershell
# 恢复脚本示例
param(
    [Parameter(Mandatory=$true)]
    [string]$BackupFile
)

# 验证备份文件存在
if (-not (Test-Path $BackupFile)) {
    Write-Error "备份文件不存在: $BackupFile"
    exit 1
}

# 停止可能正在访问数据库的服务
# [此处添加停止相关服务的命令]

# 创建当前数据库的备份，以防恢复出错
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$preRestoreBackup = "backup\db\pre_restore_$timestamp.db"
Copy-Item "backend\db\forum_data.db" $preRestoreBackup

# 恢复数据库
Copy-Item $BackupFile "backend\db\forum_data.db" -Force

# 记录恢复日志
Add-Content "logs\backup_log.txt" "$(Get-Date) - 从备份恢复完成: $BackupFile"

Write-Host "数据库已从备份恢复: $BackupFile"
Write-Host "恢复前的备份已保存: $preRestoreBackup"

# 重启相关服务
# [此处添加启动相关服务的命令]
```

### 2. 部分数据恢复

对于需要恢复特定表或记录的情况：

```python
def restore_specific_data(backup_db_path, main_db_path, table_name, condition=None):
    """从备份恢复特定表或记录"""
    try:
        # 连接备份数据库
        backup_conn = sqlite3.connect(backup_db_path)
        backup_cursor = backup_conn.cursor()
        
        # 连接主数据库
        main_conn = sqlite3.connect(main_db_path)
        main_cursor = main_conn.cursor()
        
        # 获取表结构
        backup_cursor.execute(f"PRAGMA table_info({table_name})")
        columns = [row[1] for row in backup_cursor.fetchall()]
        columns_str = ", ".join(columns)
        
        # 构建查询条件
        where_clause = f"WHERE {condition}" if condition else ""
        
        # 从备份中获取数据
        backup_cursor.execute(f"SELECT {columns_str} FROM {table_name} {where_clause}")
        records = backup_cursor.fetchall()
        
        # 开始事务
        main_conn.execute("BEGIN TRANSACTION")
        
        # 删除主数据库中的对应记录
        if condition:
            main_cursor.execute(f"DELETE FROM {table_name} {where_clause}")
        else:
            main_cursor.execute(f"DELETE FROM {table_name}")
        
        # 插入备份中的记录
        placeholders = ", ".join(["?" for _ in columns])
        for record in records:
            main_cursor.execute(
                f"INSERT INTO {table_name} ({columns_str}) VALUES ({placeholders})",
                record
            )
        
        # 提交事务
        main_conn.commit()
        
        # 关闭连接
        backup_conn.close()
        main_conn.close()
        
        return True, f"成功从备份恢复{len(records)}条记录到{table_name}表"
    except Exception as e:
        # 回滚事务
        if 'main_conn' in locals():
            main_conn.rollback()
            main_conn.close()
        if 'backup_conn' in locals():
            backup_conn.close()
        
        return False, f"恢复失败: {str(e)}"
```

## 数据库维护计划

为确保数据库性能和稳定性，系统定期执行以下维护任务：

### 1. 数据库优化

每周执行一次，优化数据库性能：

```powershell
# 数据库优化脚本
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupPath = "backup\db\pre_optimize_$timestamp.db"

# 备份当前数据库
Copy-Item "backend\db\forum_data.db" $backupPath

# 执行VACUUM操作
python -c "import sqlite3; conn = sqlite3.connect('backend/db/forum_data.db'); conn.execute('VACUUM'); conn.close()"

# 执行ANALYZE操作
python -c "import sqlite3; conn = sqlite3.connect('backend/db/forum_data.db'); conn.execute('ANALYZE'); conn.close()"

# 记录优化日志
Add-Content "logs\maintenance_log.txt" "$(Get-Date) - 数据库优化完成"
```

### 2. 索引维护

每月执行一次，重建索引：

```python
def rebuild_indexes():
    """重建数据库索引"""
    conn = sqlite3.connect('backend/db/forum_data.db')
    cursor = conn.cursor()
    
    # 获取所有索引
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index'")
    indexes = cursor.fetchall()
    
    for index in indexes:
        index_name = index[0]
        try:
            # 重建索引
            cursor.execute(f"REINDEX {index_name}")
            print(f"重建索引成功: {index_name}")
        except Exception as e:
            print(f"重建索引失败 {index_name}: {str(e)}")
    
    conn.close()
```

### 3. 数据清理

每季度执行一次，清理过期数据：

```python
def clean_old_data():
    """清理过期数据"""
    conn = sqlite3.connect('backend/db/forum_data.db')
    cursor = conn.cursor()
    
    # 清理过期的变更日志（保留最近1年的数据）
    one_year_ago = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime('%Y-%m-%d')
    
    cursor.execute(f'''
    DELETE FROM data_change_log 
    WHERE created_at < '{one_year_ago}'
    ''')
    
    deleted_logs = cursor.rowcount
    print(f"已清理 {deleted_logs} 条过期变更日志")
    
    # 清理过期的版本记录（保留最近1年的数据）
    cursor.execute(f'''
    DELETE FROM data_version 
    WHERE created_at < '{one_year_ago}'
    ''')
    
    deleted_versions = cursor.rowcount
    print(f"已清理 {deleted_versions} 条过期版本记录")
    
    # 提交更改
    conn.commit()
    conn.close()
```

## 监控与告警

系统设置了以下监控和告警机制：

1. **备份监控**：检查备份是否按计划执行
   ```powershell
   # 检查最近24小时内是否有备份文件生成
   $recentBackups = Get-ChildItem "backup\db\forum_data_*.db" | 
       Where-Object { $_.LastWriteTime -gt (Get-Date).AddHours(-24) }
   
   if ($recentBackups.Count -eq 0) {
       # 发送告警
       Send-MailMessage -From "system@example.com" -To "admin@example.com" -Subject "数据库备份失败告警" -Body "过去24小时内未检测到数据库备份文件"
   }
   ```

2. **数据库大小监控**：监控数据库大小变化
   ```powershell
   # 获取数据库文件大小
   $dbFile = Get-Item "backend\db\forum_data.db"
   $dbSizeMB = $dbFile.Length / 1MB
   
   # 记录大小
   Add-Content "logs\db_size_log.txt" "$(Get-Date) - 数据库大小: $dbSizeMB MB"
   
   # 检查是否超过阈值
   if ($dbSizeMB -gt 1000) {
       # 发送告警
       Send-MailMessage -From "system@example.com" -To "admin@example.com" -Subject "数据库大小告警" -Body "数据库大小已超过1GB，当前大小: $dbSizeMB MB"
   }
   ```

## 相关文档

- [数据库概览](./db_overview.md)
- [数据版本控制](./db_version_control.md)
- [增量数据更新](./db_incremental_updates.md) 