import sqlite3
import os

# 数据库路径
db_path = os.path.join('backend', 'db', 'forum_data.db')

# 连接数据库
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 检查thread_follow表是否存在
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='thread_follow'")
result = cursor.fetchall()
print(f"thread_follow表存在结果: {result}")

if not result:
    print("thread_follow表不存在，将创建该表")
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
        conn.commit()
        print("thread_follow表创建成功")
    except Exception as e:
        print(f"创建表时出错: {e}")
else:
    # 检查表结构
    cursor.execute("PRAGMA table_info(thread_follow)")
    columns = cursor.fetchall()
    
    # 提取列名和类型，打印更易读的结构
    col_info = []
    for col in columns:
        col_id, name, type_, notnull, default_value, pk = col
        col_info.append(f"{name} ({type_}), {'NOT NULL' if notnull else 'NULL'}, 默认值: {default_value or 'NULL'}")
    
    print("表结构:")
    for info in col_info:
        print(f"- {info}")
    
    # 检查follow_status列
    follow_status_info = next((col for col in columns if col[1] == 'follow_status'), None)
    if follow_status_info:
        print(f"\nfollow_status列信息: {follow_status_info}")
    else:
        print("\nfollow_status列不存在")
    
    # 检查表中是否有数据
    cursor.execute("SELECT COUNT(*) FROM thread_follow")
    count = cursor.fetchone()[0]
    print(f"\n表中共有 {count} 条记录")
    
    if count > 0:
        # 查看几条示例数据
        cursor.execute("SELECT id, thread_id, url, title, follow_status FROM thread_follow LIMIT 5")
        rows = cursor.fetchall()
        print("\n示例数据:")
        for row in rows:
            print(f"ID: {row[0]}, Thread ID: {row[1]}, URL: {row[2]}, Title: {row[3]}, Status: {row[4]}")

# 关闭连接
conn.close() 