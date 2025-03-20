from modules.db_utils import get_table_info, get_db_connection, get_all_tables
import sqlite3
import os

def main():
    print("当前工作目录:", os.getcwd())
    print("\n数据库文件路径:", os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db', 'forum_data.db'))
    
    print("\n所有表:")
    tables = get_all_tables()
    print(tables)
    
    print("\ncar_info表结构:")
    table_info = get_table_info('car_info')
    for row in table_info:
        print(row)
    
    print("\n尝试直接连接数据库:")
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM car_info LIMIT 1")
        row = cursor.fetchone()
        print("示例数据:", row)
        conn.close()
    except Exception as e:
        print("错误:", str(e))

if __name__ == '__main__':
    main() 