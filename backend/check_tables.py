import sqlite3
import os

def check_tables():
    # 使用正确的数据库路径
    db_path = os.path.join('db', 'forum_data.db')
    
    # 检查数据库文件是否存在
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    print(f"数据库文件存在: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("Tables in database:")
    for table in tables:
        print(table[0])
        
        # 获取每个表的行数
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
            count = cursor.fetchone()[0]
            print(f"  - Row count: {count}")
            
            # 获取表的列名
            cursor.execute(f"PRAGMA table_info({table[0]})")
            columns = cursor.fetchall()
            print(f"  - Columns: {', '.join(col[1] for col in columns)}")
            
            # 获取前3行数据
            cursor.execute(f"SELECT * FROM {table[0]} LIMIT 3")
            rows = cursor.fetchall()
            if rows:
                print(f"  - Sample data (first 3 rows):")
                for row in rows:
                    print(f"    {row}")
        except Exception as e:
            print(f"  - Error getting info: {e}")
        
        print()
    
    conn.close()

if __name__ == "__main__":
    check_tables() 