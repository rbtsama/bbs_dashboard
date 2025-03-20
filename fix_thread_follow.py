import sqlite3
import os
import sys
from datetime import datetime

# 数据库路径
db_path = os.path.join('backend', 'db', 'forum_data.db')
print(f"数据库路径: {os.path.abspath(db_path)}")

# 连接数据库
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
except Exception as e:
    print(f"连接数据库失败: {e}")
    sys.exit(1)

# 检查thread_follow表是否存在
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='thread_follow'")
result = cursor.fetchall()

if not result:
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
        
        conn.commit()
        print("thread_follow表创建成功")
        
        # 添加测试数据
        now = datetime.now().isoformat()
        sample_data = [
            ('thread1', 'https://example.com/thread1', '出售2022款特斯拉Model 3', '张三', 'https://example.com/user/zhang', 'followed', now, now),
            ('thread2', 'https://example.com/thread2', '出售2018款宝马3系', '李四', 'https://example.com/user/li', 'my_thread', now, now)
        ]
        
        cursor.executemany("""
        INSERT INTO thread_follow (thread_id, url, title, author, author_link, follow_status, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, sample_data)
        
        conn.commit()
        print("添加了2条测试数据")
        
    except Exception as e:
        print(f"创建thread_follow表时出错: {e}")
        conn.rollback()
else:
    print("thread_follow表已存在，检查列结构")
    
    # 检查表结构是否完整
    cursor.execute("PRAGMA table_info(thread_follow)")
    columns = [col[1] for col in cursor.fetchall()]
    required_columns = ['thread_id', 'url', 'title', 'author', 'author_link', 'days_old', 'last_active', 'follow_status', 'created_at', 'updated_at']
    
    missing_columns = [col for col in required_columns if col not in columns]
    if missing_columns:
        print(f"表中缺少以下列: {missing_columns}")
        
        # 添加缺失的列
        for col in missing_columns:
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
        
        conn.commit()
        print("成功添加了缺失的列")
    else:
        print("表结构完整")
    
    # 检查是否有索引
    cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='thread_follow'")
    indexes = [idx[0] for idx in cursor.fetchall()]
    required_indexes = ['idx_thread_follow_thread_id', 'idx_thread_follow_url', 'idx_thread_follow_status']
    
    missing_indexes = [idx for idx in required_indexes if idx not in indexes]
    if missing_indexes:
        print(f"表中缺少以下索引: {missing_indexes}")
        
        # 添加缺失的索引
        for idx in missing_indexes:
            if idx == 'idx_thread_follow_thread_id':
                cursor.execute("CREATE INDEX idx_thread_follow_thread_id ON thread_follow(thread_id)")
            elif idx == 'idx_thread_follow_url':
                cursor.execute("CREATE INDEX idx_thread_follow_url ON thread_follow(url)")
            elif idx == 'idx_thread_follow_status':
                cursor.execute("CREATE INDEX idx_thread_follow_status ON thread_follow(follow_status)")
        
        conn.commit()
        print("成功添加了缺失的索引")
    else:
        print("索引完整")
    
    # 查看记录数
    cursor.execute("SELECT COUNT(*) FROM thread_follow")
    count = cursor.fetchone()[0]
    print(f"表中共有 {count} 条记录")

print("\n修复完成")
# 关闭连接
conn.close() 