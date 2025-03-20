import sqlite3
import os
import pandas as pd
from datetime import datetime
import traceback
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('db_optimize.log'),
        logging.StreamHandler()
    ]
)

class DatabaseOptimizer:
    def __init__(self, db_path):
        self.db_path = os.path.abspath(db_path)
        self.conn = None
        self.cursor = None
        
    def connect(self):
        """连接数据库"""
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f'数据库文件不存在: {self.db_path}')
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
        
    def close(self):
        """关闭数据库连接"""
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
            
    def backup_database(self):
        """备份数据库"""
        backup_path = f"{self.db_path}.bak.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        try:
            import shutil
            shutil.copy2(self.db_path, backup_path)
            logging.info(f"数据库已备份到: {backup_path}")
            return True
        except Exception as e:
            logging.error(f"备份数据库失败: {str(e)}")
            return False
            
    def optimize_car_info(self):
        """优化car_info表"""
        try:
            # 1. 创建新表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS car_info_new (
                    url TEXT PRIMARY KEY,
                    year TEXT,
                    make TEXT,
                    model TEXT,
                    miles TEXT,
                    price TEXT,
                    trade_type TEXT,
                    location TEXT
                )
            """)
            
            # 2. 创建索引
            indexes = [
                "CREATE INDEX idx_car_info_make ON car_info_new(make)",
                "CREATE INDEX idx_car_info_model ON car_info_new(model)",
                "CREATE INDEX idx_car_info_location ON car_info_new(location)"
            ]
            
            for index in indexes:
                try:
                    self.cursor.execute(index)
                except sqlite3.OperationalError as e:
                    if "already exists" not in str(e):
                        raise
            
            # 3. 迁移数据
            self.cursor.execute("""
                INSERT INTO car_info_new (
                    url, year, make, model, miles, price,
                    trade_type, location
                )
                SELECT 
                    url,
                    year,
                    make,
                    model,
                    miles,
                    price,
                    trade_type,
                    location
                FROM car_info
                WHERE url != ''
            """)
            
            # 4. 替换旧表
            self.cursor.execute("DROP TABLE IF EXISTS car_info_old")
            self.cursor.execute("ALTER TABLE car_info RENAME TO car_info_old")
            self.cursor.execute("ALTER TABLE car_info_new RENAME TO car_info")
            
            # 5. 提交更改
            self.conn.commit()
            logging.info("car_info表优化完成")
            
            # 6. 统计结果
            self.cursor.execute("SELECT COUNT(*) FROM car_info")
            total = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT COUNT(*) FROM car_info WHERE year != '' AND year IS NOT NULL")
            with_year = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT COUNT(*) FROM car_info WHERE price != '' AND price != '-' AND price IS NOT NULL")
            with_price = self.cursor.fetchone()[0]
            
            self.cursor.execute("SELECT COUNT(DISTINCT make) FROM car_info WHERE make != '' AND make IS NOT NULL")
            unique_makes = self.cursor.fetchone()[0]
            
            logging.info(f"car_info表统计:")
            logging.info(f"- 总记录数: {total}")
            logging.info(f"- 有年份记录: {with_year}")
            logging.info(f"- 有价格记录: {with_price}")
            logging.info(f"- 不同品牌数: {unique_makes}")
            
        except Exception as e:
            self.conn.rollback()
            logging.error(f"优化car_info表时出错: {str(e)}")
            logging.error(traceback.format_exc())
            raise
            
    def optimize_post_ranking(self):
        """优化post_ranking表"""
        try:
            # 1. 创建新表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS post_ranking_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    thread_id TEXT NOT NULL,
                    url TEXT NOT NULL,
                    title TEXT,
                    author TEXT,
                    author_link TEXT,
                    repost_count INTEGER DEFAULT 0,
                    reply_count INTEGER DEFAULT 0,
                    delete_reply_count INTEGER DEFAULT 0,
                    daysold INTEGER DEFAULT 0,
                    last_active INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 2. 创建索引
            indexes = [
                "CREATE INDEX idx_post_ranking_thread_id ON post_ranking_new(thread_id)",
                "CREATE INDEX idx_post_ranking_author ON post_ranking_new(author)",
                "CREATE INDEX idx_post_ranking_last_active ON post_ranking_new(last_active)"
            ]
            
            for index in indexes:
                try:
                    self.cursor.execute(index)
                except sqlite3.OperationalError as e:
                    if "already exists" not in str(e):
                        raise
            
            # 3. 迁移数据
            self.cursor.execute("""
                INSERT INTO post_ranking_new (
                    thread_id, url, title, author, author_link,
                    repost_count, reply_count, delete_reply_count,
                    daysold, last_active
                )
                SELECT 
                    thread_id,
                    url,
                    title,
                    author,
                    author_link,
                    CAST(CASE 
                        WHEN repost_count REGEXP '^[0-9]+$' THEN repost_count 
                        ELSE '0' 
                    END AS INTEGER) as repost_count,
                    CAST(CASE 
                        WHEN reply_count REGEXP '^[0-9]+$' THEN reply_count 
                        ELSE '0' 
                    END AS INTEGER) as reply_count,
                    CAST(CASE 
                        WHEN delete_reply_count REGEXP '^[0-9]+$' THEN delete_reply_count 
                        ELSE '0' 
                    END AS INTEGER) as delete_reply_count,
                    CAST(CASE 
                        WHEN daysold REGEXP '^[0-9]+$' THEN daysold 
                        ELSE '0' 
                    END AS INTEGER) as daysold,
                    CAST(CASE 
                        WHEN last_active REGEXP '^[0-9]+$' THEN last_active 
                        ELSE '0' 
                    END AS INTEGER) as last_active
                FROM post_ranking
            """)
            
            # 4. 替换旧表
            self.cursor.execute("DROP TABLE IF EXISTS post_ranking_old")
            self.cursor.execute("ALTER TABLE post_ranking RENAME TO post_ranking_old")
            self.cursor.execute("ALTER TABLE post_ranking_new RENAME TO post_ranking")
            
            # 5. 提交更改
            self.conn.commit()
            logging.info("post_ranking表优化完成")
            
            # 6. 统计结果
            self.cursor.execute("SELECT COUNT(*) FROM post_ranking")
            total = self.cursor.fetchone()[0]
            logging.info(f"post_ranking表统计:")
            logging.info(f"- 总记录数: {total}")
            
        except Exception as e:
            self.conn.rollback()
            logging.error(f"优化post_ranking表时出错: {str(e)}")
            logging.error(traceback.format_exc())
            raise
            
    def optimize_author_ranking(self):
        """优化author_ranking表"""
        try:
            # 1. 创建新表
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS author_ranking_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    author TEXT NOT NULL,
                    author_link TEXT,
                    post_count INTEGER DEFAULT 0,
                    repost_count INTEGER DEFAULT 0,
                    reply_count INTEGER DEFAULT 0,
                    delete_reply_count INTEGER DEFAULT 0,
                    last_active INTEGER DEFAULT 0,
                    active_posts INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # 2. 创建索引
            indexes = [
                "CREATE INDEX idx_author_ranking_author ON author_ranking_new(author)",
                "CREATE INDEX idx_author_ranking_post_count ON author_ranking_new(post_count)",
                "CREATE INDEX idx_author_ranking_active_posts ON author_ranking_new(active_posts)"
            ]
            
            for index in indexes:
                try:
                    self.cursor.execute(index)
                except sqlite3.OperationalError as e:
                    if "already exists" not in str(e):
                        raise
            
            # 3. 迁移数据
            self.cursor.execute("""
                INSERT INTO author_ranking_new (
                    author, author_link, post_count, repost_count,
                    reply_count, delete_reply_count, last_active, active_posts
                )
                SELECT 
                    author,
                    author_link,
                    CAST(CASE 
                        WHEN post_count REGEXP '^[0-9]+$' THEN post_count 
                        ELSE '0' 
                    END AS INTEGER) as post_count,
                    CAST(CASE 
                        WHEN repost_count REGEXP '^[0-9]+$' THEN repost_count 
                        ELSE '0' 
                    END AS INTEGER) as repost_count,
                    CAST(CASE 
                        WHEN reply_count REGEXP '^[0-9]+$' THEN reply_count 
                        ELSE '0' 
                    END AS INTEGER) as reply_count,
                    CAST(CASE 
                        WHEN delete_reply_count REGEXP '^[0-9]+$' THEN delete_reply_count 
                        ELSE '0' 
                    END AS INTEGER) as delete_reply_count,
                    CAST(CASE 
                        WHEN last_active REGEXP '^[0-9]+$' THEN last_active 
                        ELSE '0' 
                    END AS INTEGER) as last_active,
                    CAST(CASE 
                        WHEN active_posts REGEXP '^[0-9]+$' THEN active_posts 
                        ELSE '0' 
                    END AS INTEGER) as active_posts
                FROM author_ranking
            """)
            
            # 4. 替换旧表
            self.cursor.execute("DROP TABLE IF EXISTS author_ranking_old")
            self.cursor.execute("ALTER TABLE author_ranking RENAME TO author_ranking_old")
            self.cursor.execute("ALTER TABLE author_ranking_new RENAME TO author_ranking")
            
            # 5. 提交更改
            self.conn.commit()
            logging.info("author_ranking表优化完成")
            
            # 6. 统计结果
            self.cursor.execute("SELECT COUNT(*) FROM author_ranking")
            total = self.cursor.fetchone()[0]
            logging.info(f"author_ranking表统计:")
            logging.info(f"- 总记录数: {total}")
            
        except Exception as e:
            self.conn.rollback()
            logging.error(f"优化author_ranking表时出错: {str(e)}")
            logging.error(traceback.format_exc())
            raise

def optimize_db():
    """优化数据库主函数"""
    db_path = os.path.join('backend', 'db', 'forum_data.db')
    optimizer = None
    
    try:
        optimizer = DatabaseOptimizer(db_path)
        optimizer.connect()
        
        # 1. 备份数据库
        if not optimizer.backup_database():
            logging.error("数据库备份失败，终止优化")
            return
        
        # 2. 优化car_info表
        logging.info("开始优化car_info表...")
        optimizer.optimize_car_info()
        
        # 3. 优化post_ranking表
        logging.info("开始优化post_ranking表...")
        optimizer.optimize_post_ranking()
        
        # 4. 优化author_ranking表
        logging.info("开始优化author_ranking表...")
        optimizer.optimize_author_ranking()
        
        logging.info("数据库优化完成")
        
    except Exception as e:
        logging.error(f"数据库优化失败: {str(e)}")
        logging.error(traceback.format_exc())
        
    finally:
        if optimizer:
            optimizer.close()

if __name__ == '__main__':
    optimize_db() 