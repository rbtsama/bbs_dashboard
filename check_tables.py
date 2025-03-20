import sqlite3
import json

def check_tables():
    try:
        # 连接数据库
        print("正在连接数据库:", "backend/db/forum_data.db")
        conn = sqlite3.connect('backend/db/forum_data.db')
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 获取car_info表的结构
        print("\n=== car_info表结构 ===")
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='car_info'")
        table_info = cursor.fetchone()
        if table_info:
            print(table_info[0])
        else:
            print("car_info表不存在")
            return
            
        # 获取记录数
        print("\n=== 记录数量 ===")
        cursor.execute("SELECT COUNT(*) as count FROM car_info")
        count = cursor.fetchone()['count']
        print(f"car_info表共有 {count} 条记录")
        
        # 获取前5条记录
        print("\n=== 前5条记录 ===")
        cursor.execute("SELECT * FROM car_info LIMIT 5")
        records = cursor.fetchall()
        for record in records:
            print(json.dumps(dict(record), ensure_ascii=False, indent=2))
            
    except Exception as e:
        print(f"发生错误: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    check_tables() 