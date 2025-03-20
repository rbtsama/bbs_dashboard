import sqlite3
import os

# 数据库目录和路径
DB_DIR = os.path.join(os.path.dirname(__file__), 'db')
DB_PATH = os.path.join(DB_DIR, 'forum_data.db')

def drop_table():
    """删除car_info表"""
    # 确保数据库目录存在
    os.makedirs(DB_DIR, exist_ok=True)
    
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        cursor.execute('DROP TABLE IF EXISTS car_info')
        conn.commit()
        print('已删除car_info表')
    except Exception as e:
        print(f'删除表时出错: {str(e)}')
    finally:
        conn.close()

if __name__ == '__main__':
    drop_table() 