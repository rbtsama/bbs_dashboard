import sqlite3
import os

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), 'db', 'forum_data.db')

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def check_ranking_tables():
    """检查排行榜相关表的结构"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查postranking表
    try:
        cursor.execute("PRAGMA table_info(postranking)")
        columns = cursor.fetchall()
        
        print("postranking表结构:")
        for col in columns:
            print(f"- {col[1]} ({col[2]})")
        
        # 获取示例数据
        cursor.execute("SELECT * FROM postranking LIMIT 1")
        row = cursor.fetchone()
        
        if row:
            print("\npostranking表示例数据:")
            for key in row.keys():
                print(f"  {key}: {row[key]}")
        else:
            print("\npostranking表中没有数据")
            
        # 特别查看Days_Old和last_active字段的计算方式
        cursor.execute("""
        SELECT 
            url, title, Days_Old, last_active, post_time
        FROM postranking
        ORDER BY Days_Old ASC
        LIMIT 5
        """)
        rows = cursor.fetchall()
        
        if rows:
            print("\n按Days_Old排序的记录:")
            for row in rows:
                print(f"  URL: {row['url']}")
                print(f"  标题: {row['title']}")
                print(f"  Days_Old: {row['Days_Old']}")
                print(f"  last_active: {row['last_active']}")
                print(f"  post_time: {row['post_time']}")
                print("")
        
    except Exception as e:
        print(f"检查postranking表时出错: {e}")
    
    conn.close()

if __name__ == "__main__":
    check_ranking_tables() 