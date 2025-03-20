import sqlite3
import os

def init_db():
    """初始化数据库"""
    try:
        # 确保db目录存在
        os.makedirs('db', exist_ok=True)
        
        # 连接数据库
        db_path = os.path.join('db', 'forum_data.db')
        conn = sqlite3.connect(db_path)
        
        # 读取schema.sql文件
        with open('schema.sql', 'r', encoding='utf-8') as f:
            schema = f.read()
            
        # 执行SQL语句
        conn.executescript(schema)
        
        # 提交更改
        conn.commit()
        print("数据库初始化成功！")
        
    except Exception as e:
        print(f"数据库初始化失败: {str(e)}")
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    init_db() 