import sqlite3
import os
import pandas as pd
from datetime import datetime

def get_db_connection():
    """获取数据库连接"""
    # 使用绝对路径
    current_dir = os.path.dirname(os.path.abspath(__file__))
    db_path = os.path.join(current_dir, 'db', 'forum_data.db')
    print(f"[{datetime.now()}] 使用数据库路径: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def create_statistic_tables():
    """创建并填充统计表"""
    print(f"[{datetime.now()}] 开始创建统计表...")
    
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 1. 创建/重建 update_statistic 表
        print(f"[{datetime.now()}] 处理 update_statistic 表...")
        cursor.execute("DROP TABLE IF EXISTS update_statistic")
        cursor.execute('''
        CREATE TABLE update_statistic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id TEXT,
            author_id TEXT,
            type TEXT,
            datetime DATETIME,
            count INTEGER,
            update_reason TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 从import表导入数据到update_statistic
        cursor.execute('''
        SELECT COUNT(*) FROM import 
        WHERE data_category = 'update_statistics'
        ''')
        count = cursor.fetchone()[0]
        print(f"[{datetime.now()}] import表中有 {count} 条update_statistics数据")
        
        if count > 0:
            cursor.execute('''
            INSERT INTO update_statistic (datetime, type, count, update_reason)
            SELECT 
                datetime,
                type,
                count,
                type AS update_reason
            FROM import
            WHERE data_category = 'update_statistics'
            ''')
            
            # 检查导入结果
            cursor.execute("SELECT COUNT(*) FROM update_statistic")
            new_count = cursor.fetchone()[0]
            print(f"[{datetime.now()}] 成功导入 {new_count} 条数据到update_statistic表")
            
            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_update_statistic_datetime ON update_statistic(datetime)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_update_statistic_type ON update_statistic(type)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_update_statistic_update_reason ON update_statistic(update_reason)")
        
        # 2. 创建/重建 view_statistic 表
        print(f"[{datetime.now()}] 处理 view_statistic 表...")
        cursor.execute("DROP TABLE IF EXISTS view_statistic")
        cursor.execute('''
        CREATE TABLE view_statistic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id TEXT,
            author_id TEXT,
            type TEXT,
            datetime DATETIME,
            count INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 从import表导入数据到view_statistic
        cursor.execute('''
        SELECT COUNT(*) FROM import 
        WHERE data_category = 'view_statistics'
        ''')
        count = cursor.fetchone()[0]
        print(f"[{datetime.now()}] import表中有 {count} 条view_statistics数据")
        
        if count > 0:
            cursor.execute('''
            INSERT INTO view_statistic (datetime, type, count)
            SELECT 
                datetime,
                type,
                count
            FROM import
            WHERE data_category = 'view_statistics'
            ''')
            
            # 检查导入结果
            cursor.execute("SELECT COUNT(*) FROM view_statistic")
            new_count = cursor.fetchone()[0]
            print(f"[{datetime.now()}] 成功导入 {new_count} 条数据到view_statistic表")
            
            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_view_statistic_datetime ON view_statistic(datetime)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_view_statistic_type ON view_statistic(type)")
        
        # 3. 创建/重建 post_statistic 表
        print(f"[{datetime.now()}] 处理 post_statistic 表...")
        cursor.execute("DROP TABLE IF EXISTS post_statistic")
        cursor.execute('''
        CREATE TABLE post_statistic (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id TEXT,
            author_id TEXT,
            type TEXT,
            datetime DATETIME,
            count INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 从import表导入数据到post_statistic
        cursor.execute('''
        SELECT COUNT(*) FROM import 
        WHERE data_category = 'post_statistics'
        ''')
        count = cursor.fetchone()[0]
        print(f"[{datetime.now()}] import表中有 {count} 条post_statistics数据")
        
        if count > 0:
            cursor.execute('''
            INSERT INTO post_statistic (datetime, type, count)
            SELECT 
                datetime,
                type,
                count
            FROM import
            WHERE data_category = 'post_statistics'
            ''')
            
            # 检查导入结果
            cursor.execute("SELECT COUNT(*) FROM post_statistic")
            new_count = cursor.fetchone()[0]
            print(f"[{datetime.now()}] 成功导入 {new_count} 条数据到post_statistic表")
            
            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_post_statistic_datetime ON post_statistic(datetime)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_post_statistic_type ON post_statistic(type)")
        
        # 提交事务
        conn.commit()
        print(f"[{datetime.now()}] 所有统计表创建和数据导入完成")
        
        # 打印示例数据
        print(f"[{datetime.now()}] 显示每个表的示例数据:")
        
        for table in ["update_statistic", "view_statistic", "post_statistic"]:
            print(f"\n{table} 表前3条记录:")
            cursor.execute(f"SELECT * FROM {table} LIMIT 3")
            rows = cursor.fetchall()
            for row in rows:
                row_dict = {k: row[k] for k in row.keys()}
                print(f"  {row_dict}")
        
    except Exception as e:
        print(f"[{datetime.now()}] 创建表或导入数据时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()
        print(f"[{datetime.now()}] 处理完成")

if __name__ == "__main__":
    create_statistic_tables() 