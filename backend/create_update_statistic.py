import sqlite3
import os
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

def create_update_statistic_table():
    """创建update_statistic表"""
    print(f"[{datetime.now()}] 开始创建update_statistic表...")
    
    conn = get_db_connection()
    try:
        # 检查表是否已存在
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='update_statistic'")
        if cursor.fetchone():
            print(f"[{datetime.now()}] update_statistic表已存在，先删除")
            conn.execute("DROP TABLE update_statistic")
            print(f"[{datetime.now()}] update_statistic表已删除")
            
        # 创建表
        conn.execute('''
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
        print(f"[{datetime.now()}] update_statistic表创建成功")
        
        # 从import表导入数据
        cursor.execute('''
        SELECT COUNT(*) FROM import
        WHERE data_category = 'update_statistics'
        ''')
        count = cursor.fetchone()[0]
        print(f"[{datetime.now()}] import表中有 {count} 条update_statistics数据")
        
        if count > 0:
            # 导入数据
            conn.execute('''
            INSERT INTO update_statistic (datetime, type, count, update_reason)
            SELECT 
                datetime,
                type,
                count,
                type AS update_reason
            FROM import
            WHERE data_category = 'update_statistics'
            ''')
            
            # 提交事务
            conn.commit()
            
            # 检查导入结果
            cursor.execute("SELECT COUNT(*) FROM update_statistic")
            new_count = cursor.fetchone()[0]
            print(f"[{datetime.now()}] 成功导入 {new_count} 条数据到update_statistic表")
            
            # 创建索引以提高查询效率
            conn.execute("CREATE INDEX IF NOT EXISTS idx_update_statistic_datetime ON update_statistic(datetime)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_update_statistic_type ON update_statistic(type)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_update_statistic_update_reason ON update_statistic(update_reason)")
            print(f"[{datetime.now()}] 创建索引完成")
            
        else:
            print(f"[{datetime.now()}] import表中没有update_statistics数据，跳过导入")
            
    except Exception as e:
        print(f"[{datetime.now()}] 创建表或导入数据时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        conn.rollback()
    finally:
        conn.close()
        print(f"[{datetime.now()}] 处理完成")

if __name__ == "__main__":
    create_update_statistic_table() 