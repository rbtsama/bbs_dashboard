import sqlite3
from pathlib import Path

# 设置数据库路径
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / 'backend' / 'db' / 'forum_data.db'

def check_db_structure():
    """检查数据库结构"""
    print(f"连接数据库: {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    print("数据库中的表:")
    for table in tables:
        print(f"- {table[0]}")
        
        # 获取表结构
        cursor.execute(f"PRAGMA table_info({table[0]})")
        columns = cursor.fetchall()
        
        print("  列名:")
        for col in columns:
            print(f"    - {col[1]} ({col[2]})")
            
        # 获取表中的记录数
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"  记录数: {count}")
        
        # 获取前几行数据示例
        cursor.execute(f"SELECT * FROM {table[0]} LIMIT 3")
        rows = cursor.fetchall()
        
        if rows:
            print("  数据示例:")
            for row in rows:
                print(f"    {row}")
        
        print()
    
    conn.close()

if __name__ == "__main__":
    check_db_structure() 