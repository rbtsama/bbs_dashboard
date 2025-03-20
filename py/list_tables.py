import sqlite3
import os

def list_tables(db_path):
    """列出数据库中的所有表"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        print(f"数据库中的表:")
        for table in tables:
            print(f"  {table[0]}")
        
        conn.close()
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    db_path = os.path.join("backend", "db", "forum_data.db")
    list_tables(db_path) 