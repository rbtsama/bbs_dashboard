import sqlite3
import os

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), 'db', 'forum_data.db')

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def get_tables():
    """获取数据库中的所有表"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    print("数据库中的表:")
    for table in tables:
        print(f"- {table[0]}")
    
    conn.close()

def get_table_schema(table_name):
    """获取表的结构"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # 获取表结构
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print(f"\n表 '{table_name}' 的结构:")
        for col in columns:
            print(f"- {col[1]} ({col[2]})")
        
        # 获取表中的记录数
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        print(f"\n表 '{table_name}' 中共有 {count} 条记录")
        
        # 如果表中有记录，获取第一条记录的示例
        if count > 0:
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 1")
            row = cursor.fetchone()
            print(f"\n表 '{table_name}' 的示例记录:")
            for key in row.keys():
                print(f"  {key}: {row[key]}")
    except Exception as e:
        print(f"获取表 '{table_name}' 结构时出错: {e}")
    
    conn.close()

if __name__ == "__main__":
    print(f"检查数据库: {DB_PATH}")
    get_tables()
    
    # 自动检查几个关键表的结构
    tables_to_check = ['list', 'post', 'car_info']
    for table in tables_to_check:
        try:
            get_table_schema(table)
        except Exception as e:
            print(f"检查表 '{table}' 时出错: {e}")
            continue 