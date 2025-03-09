import pandas as pd
import sqlite3
import os
from datetime import datetime
import sys
import traceback

# 添加项目根目录到 Python 路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import DATABASE_PATH, LIST_FILE, POST_FILE, IMPORT_FILE

def import_data_from_excel(list_file_path, post_file_path, db_path):
    """导入Excel数据到SQLite数据库"""
    try:
        print(f"正在读取列表文件: {list_file_path}")
        if not os.path.exists(list_file_path):
            return False, f"列表文件不存在: {list_file_path}"
        
        print(f"正在读取更新文件: {post_file_path}")
        if not os.path.exists(post_file_path):
            return False, f"更新文件不存在: {post_file_path}"
        
        # 读取Excel文件
        list_df = pd.read_excel(list_file_path)
        print(f"列表文件列名: {list_df.columns.tolist()}")
        print(f"列表文件行数: {len(list_df)}")
        
        post_df = pd.read_excel(post_file_path)
        print(f"更新文件列名: {post_df.columns.tolist()}")
        print(f"更新文件行数: {len(post_df)}")
        
        # 连接数据库
        print(f"连接数据库: {db_path}")
        conn = sqlite3.connect(db_path)
        
        # 导入list.xlsx数据到posts表
        print("开始导入列表数据到posts表...")
        for _, row in list_df.iterrows():
            try:
                conn.execute('''
                INSERT OR IGNORE INTO posts 
                (thread_id, title, author, author_url, post_time, forum, views, page_num, num) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(row.get('thread_id', '')),
                    str(row.get('title', '')),
                    str(row.get('author', '')),
                    str(row.get('author_url', '')),
                    str(row.get('post_time', '')),
                    str(row.get('forum', '')),
                    int(row.get('views', 0)),
                    int(row.get('page_num', 0)),
                    int(row.get('num', 0))
                ))
            except Exception as e:
                print(f"导入行时出错: {e}")
                print(f"行数据: {row}")
                continue
        
        # 导入post.xlsx数据到thread_history表
        print("开始导入更新数据到thread_history表...")
        for _, row in post_df.iterrows():
            try:
                conn.execute('''
                INSERT OR IGNORE INTO thread_history 
                (thread_id, scraping_time, update_reason, view_count, page_num, num) 
                VALUES (?, ?, ?, ?, ?, ?)
                ''', (
                    str(row.get('thread_id', '')),
                    str(row.get('scraping_time', '')),
                    str(row.get('update_reason', '')),
                    int(row.get('view_count', 0)),
                    int(row.get('page_num', 0)),
                    int(row.get('num', 0))
                ))
            except Exception as e:
                print(f"导入行时出错: {e}")
                print(f"行数据: {row}")
                continue
        
        conn.commit()
        conn.close()
        
        return True, "数据导入成功"
    except Exception as e:
        print(f"导入数据时出错: {e}")
        traceback.print_exc()
        return False, f"数据导入失败: {str(e)}"

def import_data_from_csv(import_file_path, db_path):
    """从CSV文件导入数据到SQLite数据库"""
    try:
        print(f"正在读取CSV文件: {import_file_path}")
        if not os.path.exists(import_file_path):
            return False, f"CSV文件不存在: {import_file_path}"
        
        # 读取CSV文件
        import_df = pd.read_csv(import_file_path)
        print(f"CSV文件列名: {import_df.columns.tolist()}")
        print(f"CSV文件行数: {len(import_df)}")
        
        # 连接数据库
        print(f"连接数据库: {db_path}")
        conn = sqlite3.connect(db_path)
        
        # 创建数据趋势表（如果不存在）
        conn.execute('''
        CREATE TABLE IF NOT EXISTS data_trends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            datetime TEXT,
            month TEXT,
            week TEXT,
            date TEXT,
            hour TEXT,
            count INTEGER,
            update_reason TEXT,
            view_gap INTEGER,
            duplicate_posts INTEGER,
            url TEXT,
            title TEXT,
            days_old INTEGER,
            author TEXT,
            author_link TEXT,
            repost_count INTEGER,
            reply_count INTEGER,
            delete_count INTEGER,
            last_active TEXT
        )
        ''')
        
        # 导入数据到data_trends表
        print("开始导入CSV数据到data_trends表...")
        for _, row in import_df.iterrows():
            try:
                conn.execute('''
                INSERT OR IGNORE INTO data_trends 
                (type, datetime, month, week, date, hour, count, update_reason, 
                view_gap, duplicate_posts, url, title, days_old, author, 
                author_link, repost_count, reply_count, delete_count, last_active) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    str(row.get('type', '')),
                    str(row.get('datetime', '')),
                    str(row.get('month', '')),
                    str(row.get('week', '')),
                    str(row.get('date', '')),
                    str(row.get('hour', '')),
                    int(float(row.get('count', 0)) if pd.notna(row.get('count', 0)) else 0),
                    str(row.get('update_reason', '')),
                    int(float(row.get('view_gap', 0)) if pd.notna(row.get('view_gap', 0)) else 0),
                    int(float(row.get('duplicate_posts', 0)) if pd.notna(row.get('duplicate_posts', 0)) else 0),
                    str(row.get('url', '')),
                    str(row.get('title', '')),
                    int(float(row.get('Days_Old', 0)) if pd.notna(row.get('Days_Old', 0)) else 0),
                    str(row.get('author', '')),
                    str(row.get('author_link', '')),
                    int(float(row.get('repost_count', 0)) if pd.notna(row.get('repost_count', 0)) else 0),
                    int(float(row.get('reply_count', 0)) if pd.notna(row.get('reply_count', 0)) else 0),
                    int(float(row.get('delete_count', 0)) if pd.notna(row.get('delete_count', 0)) else 0),
                    str(row.get('last_active', ''))
                ))
            except Exception as e:
                print(f"导入行时出错: {e}")
                print(f"行数据: {row}")
                continue
        
        conn.commit()
        conn.close()
        
        return True, "CSV数据导入成功"
    except Exception as e:
        print(f"导入CSV数据时出错: {e}")
        traceback.print_exc()
        return False, f"CSV数据导入失败: {str(e)}"

# 可以添加定时导入脚本
if __name__ == "__main__":
    print(f"使用数据文件:\n列表文件: {LIST_FILE}\n更新文件: {POST_FILE}\nCSV文件: {IMPORT_FILE}")
    
    # 确保数据库目录存在
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    # 导入Excel数据
    success, message = import_data_from_excel(LIST_FILE, POST_FILE, DATABASE_PATH)
    print(message)
    
    # 导入CSV数据
    success, message = import_data_from_csv(IMPORT_FILE, DATABASE_PATH)
    print(message) 