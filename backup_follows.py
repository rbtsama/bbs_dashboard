import sqlite3
import os
import json
from datetime import datetime

# 创建备份目录
backup_dir = os.path.join('backend', 'backups', 'follows')
os.makedirs(backup_dir, exist_ok=True)
print(f"备份目录: {os.path.abspath(backup_dir)}")

# 数据库路径
db_path = os.path.join('backend', 'db', 'forum_data.db')
print(f"数据库路径: {os.path.abspath(db_path)}")

# 连接数据库
try:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # 启用字典行工厂
    cursor = conn.cursor()
    print("已连接到数据库")
except Exception as e:
    print(f"连接数据库失败: {e}")
    exit(1)

# 检查thread_follow表是否存在
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='thread_follow'")
if cursor.fetchone():
    print("找到thread_follow表，准备备份数据")
    
    # 导出全部关注数据
    cursor.execute("SELECT * FROM thread_follow")
    follows = [dict(row) for row in cursor.fetchall()]
    
    if follows:
        print(f"找到 {len(follows)} 条关注记录")
        
        # 创建备份文件
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        backup_file = os.path.join(backup_dir, f'follows_backup_{timestamp}.json')
        
        with open(backup_file, 'w', encoding='utf-8') as f:
            json.dump(follows, f, ensure_ascii=False, indent=2)
        
        print(f"已备份关注数据到: {backup_file}")
        
        # 显示备份的数据类型统计
        follow_types = {}
        for follow in follows:
            status = follow.get('follow_status', 'unknown')
            if status not in follow_types:
                follow_types[status] = 0
            follow_types[status] += 1
        
        print("\n关注数据统计:")
        for status, count in follow_types.items():
            print(f"- {status}: {count}条")
    else:
        print("thread_follow表中没有数据，无需备份")
else:
    print("thread_follow表不存在，无法备份")

conn.close()
print("\n备份过程完成，数据库连接已关闭")

# 显示之前的备份文件
previous_backups = [f for f in os.listdir(backup_dir) if f.startswith('follows_backup_') and f.endswith('.json')]
if previous_backups:
    previous_backups.sort(reverse=True)
    print(f"\n找到 {len(previous_backups)} 个以前的备份文件:")
    for i, backup in enumerate(previous_backups[:5]):
        backup_path = os.path.join(backup_dir, backup)
        backup_size = os.path.getsize(backup_path) / 1024
        backup_time = os.path.getmtime(backup_path)
        backup_time_str = datetime.fromtimestamp(backup_time).strftime('%Y-%m-%d %H:%M:%S')
        print(f"{i+1}. {backup} ({backup_size:.2f} KB, {backup_time_str})")
    
    if len(previous_backups) > 5:
        print(f"... 还有 {len(previous_backups) - 5} 个更早的备份文件")
else:
    print("\n没有找到以前的备份文件") 