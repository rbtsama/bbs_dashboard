import sqlite3
import os

# 获取数据库路径
db_path = os.path.join(os.path.dirname(__file__), 'db', 'forum_data.db')

# 连接数据库
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 删除thread_follow表中的所有记录
    cursor.execute("DELETE FROM thread_follow")
    deleted_count = conn.total_changes
    
    # 提交更改
    conn.commit()
    
    print(f"已清空关注列表，共删除 {deleted_count} 条记录")
    
    # 可选：重置自增ID
    cursor.execute("DELETE FROM sqlite_sequence WHERE name='thread_follow'")
    conn.commit()
    
except Exception as e:
    print(f"清空关注列表时出错: {e}")
finally:
    if 'conn' in locals():
        conn.close() 