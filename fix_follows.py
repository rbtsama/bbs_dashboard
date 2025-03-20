import sqlite3
import os
from datetime import datetime

# 数据库路径
db_path = os.path.join('backend', 'db', 'forum_data.db')
print(f"数据库路径: {os.path.abspath(db_path)}")

# 连接数据库
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print("已连接到数据库")
except Exception as e:
    print(f"连接数据库失败: {e}")
    exit(1)

# 检查thread_follow表是否存在
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='thread_follow'")
if not cursor.fetchone():
    print("thread_follow表不存在，将创建该表")
    
    try:
        # 创建thread_follow表
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
        
        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_thread_follow_thread_id ON thread_follow(thread_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_thread_follow_url ON thread_follow(url)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_thread_follow_status ON thread_follow(follow_status)")
        
        print("thread_follow表创建成功")
    except Exception as e:
        print(f"创建thread_follow表时出错: {e}")
else:
    print("thread_follow表已存在，检查表结构")
    
    # 检查表结构
    cursor.execute("PRAGMA table_info(thread_follow)")
    columns = [col[1] for col in cursor.fetchall()]
    required_columns = ['thread_id', 'url', 'title', 'author', 'author_link', 'days_old', 'last_active', 'follow_status', 'created_at', 'updated_at']
    
    missing_columns = [col for col in required_columns if col not in columns]
    if missing_columns:
        print(f"表中缺少以下列: {missing_columns}")
        
        # 添加缺失的列
        for col in missing_columns:
            try:
                if col == 'days_old':
                    cursor.execute("ALTER TABLE thread_follow ADD COLUMN days_old INTEGER DEFAULT 0")
                elif col == 'last_active':
                    cursor.execute("ALTER TABLE thread_follow ADD COLUMN last_active INTEGER DEFAULT 0")
                elif col == 'follow_status':
                    cursor.execute("ALTER TABLE thread_follow ADD COLUMN follow_status TEXT CHECK(follow_status IN ('followed', 'my_thread', 'not_followed')) DEFAULT 'not_followed'")
                elif col == 'created_at':
                    cursor.execute("ALTER TABLE thread_follow ADD COLUMN created_at TEXT DEFAULT CURRENT_TIMESTAMP")
                elif col == 'updated_at':
                    cursor.execute("ALTER TABLE thread_follow ADD COLUMN updated_at TEXT DEFAULT CURRENT_TIMESTAMP")
                else:
                    cursor.execute(f"ALTER TABLE thread_follow ADD COLUMN {col} TEXT")
                print(f"已添加列: {col}")
            except Exception as e:
                print(f"添加列 {col} 时出错: {e}")
    else:
        print("表结构完整")
    
    # 检查是否有示例/模拟数据
    print("\n检查示例数据...")
    cursor.execute("SELECT * FROM thread_follow WHERE url LIKE '%example.com%'")
    example_data = cursor.fetchall()
    
    if example_data:
        print(f"发现 {len(example_data)} 条示例数据，将删除")
        cursor.execute("DELETE FROM thread_follow WHERE url LIKE '%example.com%'")
        print(f"已删除 {cursor.rowcount} 条示例数据")
    else:
        print("未发现示例数据")
    
    # 查看目前有多少条记录
    cursor.execute("SELECT COUNT(*) FROM thread_follow")
    count = cursor.fetchone()[0]
    print(f"\n当前thread_follow表中有 {count} 条记录")
    
    if count > 0:
        print("\n查看数据样本:")
        cursor.execute("SELECT id, thread_id, url, title, follow_status FROM thread_follow LIMIT 5")
        rows = cursor.fetchall()
        for row in rows:
            print(f"ID: {row[0]}, Thread ID: {row[1]}, URL: {row[2]}, Title: {row[3]}, Status: {row[4]}")

# 提交更改
conn.commit()
print("\n所有更改已提交到数据库")
conn.close()
print("数据库连接已关闭") 