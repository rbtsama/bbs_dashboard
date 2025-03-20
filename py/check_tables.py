import sqlite3
from pathlib import Path

def check_tables():
    """检查数据库中的表"""
    db_path = Path(__file__).parent.parent / 'backend' / 'db' / 'forum_data.db'
    print(f"数据库文件: {db_path}")
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # 获取所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    print("\n当前表及其结构:")
    for table in sorted(tables):
        print(f"\n表名: {table}")
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        print("字段:")
        for col in columns:
            print(f"  - {col[1]} ({col[2]})")
            
        # 获取前几行数据
        try:
            cursor.execute(f"SELECT * FROM {table} LIMIT 1")
            row = cursor.fetchone()
            if row:
                print("数据示例:")
                for i, value in enumerate(row):
                    print(f"  - {columns[i][1]}: {value}")
        except:
            print("  无法获取数据示例")
    
    conn.close()

if __name__ == "__main__":
    check_tables() 