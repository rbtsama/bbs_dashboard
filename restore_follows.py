import sqlite3
import os
import json
import glob
from datetime import datetime

# 数据库路径
db_path = os.path.join('backend', 'db', 'forum_data.db')
print(f"数据库路径: {os.path.abspath(db_path)}")

# 备份目录
backup_dir = os.path.join('backend', 'backups', 'follows')
print(f"备份目录: {os.path.abspath(backup_dir)}")

# 检查目录是否存在
if not os.path.exists(backup_dir):
    print(f"备份目录不存在: {backup_dir}")
    os.makedirs(backup_dir, exist_ok=True)
    print(f"创建了备份目录")

# 查找最新的备份文件
backup_files = glob.glob(os.path.join(backup_dir, 'follows_backup_*.json'))
if not backup_files:
    print("未找到备份文件，无法恢复")
    exit(1)

# 按修改时间排序，获取最新的备份
backup_files.sort(key=lambda x: os.path.getmtime(x), reverse=True)
latest_backup = backup_files[0]
print(f"找到最新备份文件: {os.path.basename(latest_backup)}")

# 读取备份数据
try:
    with open(latest_backup, 'r', encoding='utf-8') as f:
        follows_data = json.load(f)
    print(f"成功读取备份数据，共 {len(follows_data)} 条记录")
except Exception as e:
    print(f"读取备份文件时出错: {e}")
    exit(1)

# 连接数据库
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print("已连接到数据库")
except Exception as e:
    print(f"连接数据库失败: {e}")
    exit(1)

# 确保thread_follow表存在
try:
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS thread_follow (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        thread_id TEXT NOT NULL,
        url TEXT NOT NULL,
        title TEXT,
        author TEXT,
        author_link TEXT,
        days_old INTEGER DEFAULT 0,
        last_active INTEGER DEFAULT 0,
        read_count INTEGER DEFAULT 0,
        reply_count INTEGER DEFAULT 0,
        follow_status TEXT CHECK(follow_status IN ('followed', 'my_thread', 'not_followed')) DEFAULT 'not_followed',
        created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
    """)
    print("确保thread_follow表存在")
except Exception as e:
    print(f"创建thread_follow表时出错: {e}")

# 检查表结构
cursor.execute("PRAGMA table_info(thread_follow)")
columns = [col[1] for col in cursor.fetchall()]
print(f"表结构: {columns}")

# 查看当前表中的数据
cursor.execute("SELECT COUNT(*) FROM thread_follow")
current_count = cursor.fetchone()[0]
print(f"当前表中有 {current_count} 条数据")

# 确认是否继续恢复
if current_count > 0:
    print("\n警告: 当前表中已有数据。恢复操作会删除现有数据并替换为备份数据。")
    confirm = input("是否继续恢复操作？(y/n): ")
    if confirm.lower() != 'y':
        print("操作已取消")
        conn.close()
        exit(0)

# 备份当前数据
if current_count > 0:
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    cursor.execute("SELECT * FROM thread_follow")
    current_data = []
    for row in cursor.fetchall():
        item = {}
        for i, col in enumerate(columns):
            item[col] = row[i]
        current_data.append(item)
    
    backup_file = os.path.join(backup_dir, f'follows_backup_before_restore_{timestamp}.json')
    with open(backup_file, 'w', encoding='utf-8') as f:
        json.dump(current_data, f, ensure_ascii=False, indent=2)
    print(f"已备份当前数据到: {backup_file}")

# 开始恢复
try:
    # 清空当前表
    cursor.execute("DELETE FROM thread_follow")
    print(f"已清空thread_follow表，删除了 {cursor.rowcount} 条记录")
    
    # 恢复数据
    restored_count = 0
    for follow in follows_data:
        # 排除id字段
        if 'id' in follow:
            del follow['id']
        
        # 准备SQL语句
        fields = list(follow.keys())
        placeholders = ','.join(['?' for _ in fields])
        values = [follow[field] for field in fields]
        
        fields_str = ','.join(fields)
        sql = f"INSERT INTO thread_follow ({fields_str}) VALUES ({placeholders})"
        
        try:
            cursor.execute(sql, values)
            restored_count += 1
        except Exception as e:
            print(f"插入数据时出错: {e}")
            print(f"问题数据: {follow}")
    
    conn.commit()
    print(f"已成功恢复 {restored_count} 条数据")
    
    # 验证恢复
    cursor.execute("SELECT COUNT(*) FROM thread_follow")
    final_count = cursor.fetchone()[0]
    print(f"恢复后表中有 {final_count} 条数据")
    
    # 创建索引
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_thread_follow_thread_id ON thread_follow(thread_id)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_thread_follow_url ON thread_follow(url)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_thread_follow_status ON thread_follow(follow_status)")
    print("已确保所有必要的索引都存在")
    
except Exception as e:
    print(f"恢复数据时出错: {e}")
    conn.rollback()

conn.close()
print("数据库连接已关闭") 