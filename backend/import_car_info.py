import sqlite3
import pandas as pd
import os
from datetime import datetime
import sys

# 数据库路径
DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'database.db')

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_car_info_table():
    """初始化car_info表"""
    conn = get_db_connection()
    
    # 创建车辆信息表
    conn.execute('''
    CREATE TABLE IF NOT EXISTS car_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE,
        year INTEGER,
        make TEXT,
        model TEXT,
        miles TEXT,
        price TEXT,
        trade_type TEXT,
        location TEXT,
        thread_id TEXT,
        author TEXT,
        post_time TEXT,
        daysold INTEGER,
        last_active TEXT,
        FOREIGN KEY (url) REFERENCES posts(url)
    )
    ''')
    
    conn.commit()
    conn.close()

def import_car_info():
    """导入车辆信息"""
    try:
        conn = get_db_connection()
        
        # 读取CSV文件
        csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed', 'car_info.csv')
        print(f"读取CSV文件: {csv_path}")
        
        if not os.path.exists(csv_path):
            print(f"错误: CSV文件不存在: {csv_path}")
            return 0
            
        try:
            # 尝试读取文件的前几行
            with open(csv_path, 'r', encoding='utf-8') as f:
                print("CSV文件前5行:")
                for i, line in enumerate(f):
                    if i < 5:
                        print(f"  {i+1}: {line.strip()}")
                    else:
                        break
        except Exception as e:
            print(f"读取文件前几行时出错: {e}")
        
        try:
            df = pd.read_csv(csv_path, encoding='utf-8')
            print(f"CSV文件读取成功，共 {len(df)} 条记录")
            print("列名:", df.columns.tolist())
            print("前3行数据:")
            print(df.head(3))
        except Exception as e:
            print(f"读取CSV失败: {e}")
            raise
        
        # 获取帖子信息，用于关联
        posts_df = pd.read_sql("SELECT url, author, post_time FROM posts", conn)
        posts_dict = dict(zip(posts_df['url'], zip(posts_df['author'], posts_df['post_time'])))
        print(f"从posts表获取了 {len(posts_df)} 条记录")
        
        if len(posts_df) == 0:
            print("警告: posts表中没有数据，无法关联作者和发帖时间")
            # 即使没有关联数据，我们也应该导入车辆基本信息
        
        # 计算导入时间
        now = datetime.now()
        
        # 准备批量插入
        records = []
        for _, row in df.iterrows():
            # 跳过trade_type为"不知道"的记录
            if pd.isna(row['trade_type']) or row['trade_type'] == '不知道':
                continue
                
            url = row['url']
            thread_id = url.split('/')[-1].split('.')[0].replace('t_', '')
            
            # 从posts表获取作者和发帖时间
            author = None
            post_time = None
            last_active = None
            daysold = None
            
            if url in posts_dict:
                author, post_time = posts_dict[url]
                
                # 计算daysold
                if post_time:
                    try:
                        post_datetime = datetime.strptime(post_time, '%Y-%m-%d %H:%M:%S')
                        daysold = (now - post_datetime).days
                        # 假设最后活跃时间为当前时间，实际应从thread_history表获取
                        last_active = now.strftime('%Y-%m-%d %H:%M:%S')
                    except Exception as e:
                        print(f"日期转换出错 {post_time}: {e}")
            
            # 准备记录
            year_value = None
            try:
                if not pd.isna(row['year']):
                    year_value = int(row['year'])
            except Exception as e:
                print(f"年份转换出错 {row['year']}: {e}")
                
            record = (
                url,
                year_value,
                row['make'] if not pd.isna(row['make']) else None,
                row['model'] if not pd.isna(row['model']) else None,
                row['miles'] if not pd.isna(row['miles']) else None,
                row['price'] if not pd.isna(row['price']) else None,
                row['trade_type'] if not pd.isna(row['trade_type']) else None,
                row['location'] if not pd.isna(row['location']) else None,
                thread_id,
                author,
                post_time,
                daysold,
                last_active
            )
            records.append(record)
        
        print(f"准备插入 {len(records)} 条记录")
        
        # 先清空表
        conn.execute("DELETE FROM car_info")
        
        # 批量插入
        conn.executemany("""
            INSERT INTO car_info (url, year, make, model, miles, price, trade_type, location, thread_id, author, post_time, daysold, last_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, records)
        
        conn.commit()
        conn.close()
        
        print(f"成功导入 {len(records)} 条车辆信息记录")
        return len(records)
    except Exception as e:
        print(f"导入失败: {str(e)}")
        return 0

if __name__ == "__main__":
    init_car_info_table()
    count = import_car_info()
    print(f"导入完成，共导入 {count} 条记录")
    sys.exit(0 if count > 0 else 1) 