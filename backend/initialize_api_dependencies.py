import sqlite3
import os
import json
from datetime import datetime, timedelta
import traceback

def get_db_connection():
    """获取数据库连接"""
    db_path = 'db/forum_data.db'
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return None
    return sqlite3.connect(db_path)

def initialize_post_ranking_data():
    """初始化post_ranking表"""
    print(f"[{datetime.now()}] 检查post_ranking表...")
    
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # 检查表中是否有数据
        cursor.execute("SELECT COUNT(*) FROM post_ranking")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print(f"[{datetime.now()}] post_ranking表为空，等待实际数据导入...")
            return True
        else:
            print(f"[{datetime.now()}] post_ranking表已有{count}条数据")
            return True
    except Exception as e:
        print(f"[{datetime.now()}] 检查post_ranking表出错: {str(e)}")
        traceback.print_exc()
        return False
    finally:
        if conn:
            conn.close()

def initialize_wordcloud_data():
    """初始化词云数据"""
    print(f"[{datetime.now()}] 检查词云数据...")
    
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        cursor = conn.cursor()
        
        # 检查wordcloud_cache表中是否有数据
        cursor.execute("SELECT COUNT(*) FROM wordcloud_cache")
        count = cursor.fetchone()[0]
        
        if count == 0:
            print(f"[{datetime.now()}] 词云缓存表为空，等待实际数据生成...")
            return True
        else:
            print(f"[{datetime.now()}] 词云缓存表已有{count}条数据")
            return True
    except Exception as e:
        print(f"[{datetime.now()}] 检查词云数据出错: {str(e)}")
        traceback.print_exc()
        return False
    finally:
        if conn:
            conn.close()

def initialize_thread_follows_data():
    """初始化thread_follows表"""
    print(f"[{datetime.now()}] 检查thread_follows表...")
    return True

if __name__ == "__main__":
    print(f"[{datetime.now()}] 开始初始化API依赖...")
    
    # 初始化post_ranking表数据
    initialize_post_ranking_data()
    
    # 初始化词云数据
    initialize_wordcloud_data()
    
    # 初始化thread_follows表数据
    initialize_thread_follows_data()
    
    print(f"[{datetime.now()}] API依赖初始化完成") 