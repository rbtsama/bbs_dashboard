import sqlite3
import os
import logging
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库路径
DB_DIR = os.path.join(os.path.dirname(__file__), 'db')
DB_PATH = os.path.join(DB_DIR, 'forum_data.db')

def update_car_info_structure():
    """更新car_info表结构"""
    try:
        # 确保数据库目录存在
        os.makedirs(DB_DIR, exist_ok=True)
        
        # 连接数据库
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 检查car_info表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='car_info'")
        table_exists = cursor.fetchone() is not None
        
        if table_exists:
            # 创建新表
            cursor.execute("""
            CREATE TABLE car_info_new (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT,
                year INTEGER,
                make TEXT,
                model TEXT,
                miles TEXT,
                price TEXT,
                trade_type TEXT,
                location TEXT,
                thread_id TEXT,
                author TEXT,
                author_link TEXT,
                post_time TEXT,
                daysold INTEGER,
                last_active TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(url)
            )
            """)
            
            # 复制数据
            cursor.execute("""
            INSERT INTO car_info_new (
                url, title, year, make, model, miles, price,
                trade_type, location, thread_id, author,
                author_link, post_time, daysold, last_active
            )
            SELECT 
                url, title, year, make, model, miles, price,
                trade_type, location, thread_id, author,
                author_link, post_time, daysold, last_active
            FROM car_info
            """)
            
            # 删除旧表
            cursor.execute("DROP TABLE car_info")
            
            # 重命名新表
            cursor.execute("ALTER TABLE car_info_new RENAME TO car_info")
            
            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_car_info_url ON car_info(url)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_car_info_make ON car_info(make)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_car_info_year ON car_info(year)")
            
        else:
            # 如果表不存在，直接创建新表
            cursor.execute("""
            CREATE TABLE car_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                title TEXT,
                year INTEGER,
                make TEXT,
                model TEXT,
                miles TEXT,
                price TEXT,
                trade_type TEXT,
                location TEXT,
                thread_id TEXT,
                author TEXT,
                author_link TEXT,
                post_time TEXT,
                daysold INTEGER,
                last_active TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(url)
            )
            """)
            
            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_car_info_url ON car_info(url)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_car_info_make ON car_info(make)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_car_info_year ON car_info(year)")
        
        # 提交更改
        conn.commit()
        
        # 验证表结构
        cursor.execute("PRAGMA table_info(car_info)")
        columns = cursor.fetchall()
        logger.info("\n更新后的car_info表结构:")
        for col in columns:
            logger.info(f"- {col[1]} ({col[2]})")
            
        conn.close()
        logger.info("表结构更新完成")
        return True
        
    except Exception as e:
        logger.error(f"更新表结构失败: {str(e)}")
        if 'conn' in locals():
            conn.close()
        return False

if __name__ == "__main__":
    update_car_info_structure() 