import sqlite3
import os

def check_car_info_table():
    try:
        # 连接数据库
        conn = sqlite3.connect('backend/db/forum_data.db')
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='car_info'")
        if not cursor.fetchone():
            print("car_info表不存在")
            return
            
        # 获取表结构
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='car_info'")
        table_schema = cursor.fetchone()[0]
        print("表结构:")
        print(table_schema)
        
        # 获取记录数
        cursor.execute("SELECT COUNT(*) FROM car_info")
        count = cursor.fetchone()[0]
        print(f"\n记录数: {count}")
        
        # 如果有记录，显示一条示例
        if count > 0:
            cursor.execute("SELECT * FROM car_info LIMIT 1")
            sample = cursor.fetchone()
            print("\n示例记录:")
            for i, desc in enumerate(cursor.description):
                print(f"{desc[0]}: {sample[i]}")
                
    except Exception as e:
        print(f"错误: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    check_car_info_table() 