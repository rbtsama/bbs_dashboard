import sqlite3
from pathlib import Path

def check_db():
    db_path = Path(__file__).parent.parent / 'backend' / 'db' / 'forum_data.db'
    print(f"检查数据库: {db_path}")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # 获取所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("\n现有表:")
    for table in tables:
        print(f"\n表名: {table[0]}")
        # 获取表结构
        cursor.execute(f"PRAGMA table_info({table[0]})")
        columns = cursor.fetchall()
        print("字段:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
    
    conn.close()

if __name__ == "__main__":
    check_db() 