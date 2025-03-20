import sqlite3
import os

def show_tables():
    # 数据库路径
    db_path = os.path.join('db', 'forum_data.db')
    
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
        
    try:
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = cursor.fetchall()
        
        if tables:
            print(f"数据库中的所有表（共 {len(tables)} 个）:")
            for idx, table in enumerate(tables):
                print(f"{idx+1}. {table[0]}")
        else:
            print("数据库中没有表")
            
        # 关闭连接
        conn.close()
    except Exception as e:
        print(f"查询出错: {str(e)}")

if __name__ == "__main__":
    show_tables() 