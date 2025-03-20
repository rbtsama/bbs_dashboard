import sqlite3
import os
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), 'db', 'forum_data.db')

def create_thread_follow_table():
    """创建并初始化thread_follow表"""
    try:
        # 连接数据库
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 检查表是否已存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='thread_follow'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            logging.info("创建thread_follow表...")
            
            # 创建thread_follow表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS thread_follow (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT NOT NULL,
                url TEXT,
                title TEXT,
                author TEXT,
                author_link TEXT,
                days_old INTEGER,
                last_active INTEGER,
                read_count INTEGER,
                reply_count INTEGER,
                follow_status TEXT CHECK(follow_status IN ('not_followed', 'followed', 'my_thread')) DEFAULT 'not_followed',
                created_at TEXT,
                updated_at TEXT
            )
            ''')
            
            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_thread_follow_thread_id ON thread_follow(thread_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_thread_follow_follow_status ON thread_follow(follow_status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_thread_follow_created_at ON thread_follow(created_at)")
            
            logging.info("thread_follow表创建成功！")
        else:
            # 检查follow_status字段是否存在
            cursor.execute("PRAGMA table_info(thread_follow)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'follow_status' not in columns:
                logging.info("thread_follow表已存在，但缺少follow_status字段，正在添加...")
                cursor.execute('''
                ALTER TABLE thread_follow 
                ADD COLUMN follow_status TEXT CHECK(follow_status IN ('not_followed', 'followed', 'my_thread')) DEFAULT 'not_followed'
                ''')
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_thread_follow_follow_status ON thread_follow(follow_status)")
                logging.info("follow_status字段添加成功！")
            else:
                logging.info("thread_follow表及follow_status字段已存在")
        
        # 提交事务并关闭连接
        conn.commit()
        conn.close()
        logging.info("数据库操作完成")
        
    except Exception as e:
        logging.error(f"创建thread_follow表时出错: {str(e)}")
        if conn:
            conn.rollback()
            conn.close()

def get_db_connection():
    """获取数据库连接"""
    db_path = 'db/forum_data.db'
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return None
    return sqlite3.connect(db_path)

def create_thread_history_cache_table():
    """创建thread_history_cache表"""
    print(f"[{datetime.now()}] 检查并创建thread_history_cache表...")
    
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='thread_history_cache'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print(f"[{datetime.now()}] 创建thread_history_cache表...")
            cursor.execute('''
            CREATE TABLE thread_history_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT,
                title TEXT,
                history_data TEXT,
                generated_at DATETIME,
                created_at DATETIME,
                updated_at DATETIME
            )
            ''')
            conn.commit()
            print(f"[{datetime.now()}] thread_history_cache表创建成功")
            return True
        else:
            print(f"[{datetime.now()}] thread_history_cache表已存在")
            return True
    except Exception as e:
        print(f"[{datetime.now()}] 创建thread_history_cache表出错: {str(e)}")
        return False
    finally:
        if conn:
            conn.close()

def show_all_tables():
    """显示所有表"""
    print(f"[{datetime.now()}] 显示数据库中的所有表...")
    
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        print(f"[{datetime.now()}] 数据库中的表列表:")
        for i, table in enumerate(tables, 1):
            print(f"  {i}. {table[0]}")
    except Exception as e:
        print(f"[{datetime.now()}] 获取表列表出错: {str(e)}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    create_thread_follow_table()
    logging.info("脚本执行完成")
    
    print(f"[{datetime.now()}] 开始创建缺失的表...")
    
    # 创建thread_history_cache表
    create_thread_history_cache_table()
    
    # 显示所有表
    show_all_tables()
    
    print(f"[{datetime.now()}] 创建缺失的表完成") 