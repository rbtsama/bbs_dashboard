# 此文件中的代码已被禁用（由car_info清理脚本处理）
# 原始功能已被移除，但保留文件以备参考
# 原始备份文件: import_car_info.py.bak_carinfo

import sqlite3
import pandas as pd
import os
from datetime import datetime
import sys
import logging

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库路径
DB_DIR = os.path.join(os.path.dirname(__file__), 'db')
DB_PATH = os.path.join(DB_DIR, 'forum_data.db')

# 数据文件路径
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed')
CAR_INFO_PATH = os.path.join(DATA_DIR, 'car_info.csv')
UPDATE_PATH = os.path.join(DATA_DIR, 'update.xlsx')
POST_PATH = os.path.join(DATA_DIR, 'post.xlsx')

def get_db_connection():
    """获取数据库连接"""
    os.makedirs(DB_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_car_info_table():
    """初始化car_info表"""
    conn = get_db_connection()
    
    # 创建车辆信息表
    conn.execute('''
    CREATE TABLE IF NOT EXISTS car_info (
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
    ''')
    
    conn.commit()
    conn.close()

def import_car_info():
    """导入车辆信息"""
    try:
        conn = get_db_connection()
        
        # 读取CSV文件
        logger.info(f"读取CSV文件: {CAR_INFO_PATH}")
        if not os.path.exists(CAR_INFO_PATH):
            logger.error(f"错误: CSV文件不存在: {CAR_INFO_PATH}")
            return 0
            
        # 读取car_info.csv
        df = pd.read_csv(CAR_INFO_PATH, encoding='utf-8')
        logger.info(f"CSV文件读取成功，共 {len(df)} 条记录")
        
        # 读取update.xlsx
        logger.info(f"读取update.xlsx: {UPDATE_PATH}")
        if not os.path.exists(UPDATE_PATH):
            logger.error(f"错误: update.xlsx不存在: {UPDATE_PATH}")
            return 0
            
        update_df = pd.read_excel(UPDATE_PATH)
        logger.info(f"update.xlsx读取成功，共 {len(update_df)} 条记录")
        
        # 读取post.xlsx
        logger.info(f"读取post.xlsx: {POST_PATH}")
        if not os.path.exists(POST_PATH):
            logger.error(f"错误: post.xlsx不存在: {POST_PATH}")
            return 0
            
        post_df = pd.read_excel(POST_PATH)
        logger.info(f"post.xlsx读取成功，共 {len(post_df)} 条记录")
        
        # 打印列名
        logger.info(f"update.xlsx的列名: {update_df.columns.tolist()}")
        logger.info(f"post.xlsx的列名: {post_df.columns.tolist()}")
        
        # 确保scraping_time列是datetime类型
        update_df['scraping_time'] = pd.to_datetime(update_df['scraping_time'])
        post_df['post_time'] = pd.to_datetime(post_df['post_time'])
        
        # 对于每个URL，只保留最新的记录
        latest_updates = update_df.sort_values('scraping_time').groupby('url').last().reset_index()
        logger.info(f"处理后的update.xlsx包含 {len(latest_updates)} 条记录")
        
        # 创建post_df的url索引，只保留post_time
        post_df_dict = dict(zip(post_df['url'], post_df['post_time']))
        
        # 计算当前时间
        now = datetime.now()
        
        # 准备批量插入
        records = []
        for _, row in df.iterrows():
            url = row['url']
            thread_id = url.split('/')[-1].split('.')[0].replace('t_', '')
            
            # 从update.xlsx获取额外信息
            update_info = latest_updates[latest_updates['url'] == url]
            
            title = "-"
            author = "-"
            author_link = "-"
            post_time = None
            post_age = "-"  # 帖龄
            last_active = "-"  # 活跃
            
            # 从update.xlsx获取标题和作者信息
            if not update_info.empty:
                title = update_info.iloc[0]['title'] if pd.notna(update_info.iloc[0]['title']) else "-"
                author = update_info.iloc[0]['author'] if pd.notna(update_info.iloc[0]['author']) else "-"
                author_link = update_info.iloc[0]['author_link'] if pd.notna(update_info.iloc[0]['author_link']) else "-"
            
            # 从post.xlsx获取发帖时间信息
            if url in post_df_dict:
                post_time = post_df_dict[url]
                if pd.notna(post_time):
                    post_age = f"{(now - post_time).days}天"
                
            # 从update.xlsx获取最新的scraping_time
            if not update_info.empty:
                latest_scraping_time = update_info['scraping_time'].max()
                if pd.notna(latest_scraping_time):
                    try:
                        days_diff = (now - latest_scraping_time).days
                        if days_diff == 0:
                            last_active = "今天"
                        else:
                            last_active = f"{days_diff}天前"
                    except Exception as e:
                        logger.error(f"计算活跃时间出错: {e}")
                        last_active = "-"
            
            # 准备记录
            year_value = "-"
            try:
                if not pd.isna(row['year']):
                    year_str = str(row['year'])
                    if year_str.isdigit():
                        year_value = int(year_str)
                        # 处理两位数年份
                        if year_value < 100:
                            year_value += 2000
                    else:
                        # 如果不是纯数字，保留原始值
                        year_value = year_str
            except Exception as e:
                logger.error(f"年份转换出错 {row['year']}: {e}")
                
            record = (
                url,
                title,
                year_value,
                row['make'] if pd.notna(row['make']) else "-",
                row['model'] if pd.notna(row['model']) else "-",
                row['miles'] if pd.notna(row['miles']) else "-",
                row['price'] if pd.notna(row['price']) else "-",
                row['trade_type'] if pd.notna(row['trade_type']) else "-",
                row['location'] if pd.notna(row['location']) else "-",
                thread_id,
                author,
                author_link,
                post_time.strftime('%Y-%m-%d %H:%M:%S') if pd.notna(post_time) else "-",
                post_age,
                last_active
            )
            records.append(record)
        
        logger.info(f"准备插入 {len(records)} 条记录")
        
        # 先清空表
        conn.execute("DELETE FROM car_info")
        
        # 批量插入
        conn.executemany("""
            INSERT INTO car_info (
                url, title, year, make, model, miles, price,
                trade_type, location, thread_id, author,
                author_link, post_time, daysold, last_active
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, records)
        
        conn.commit()
        conn.close()
        
        logger.info(f"成功导入 {len(records)} 条车辆信息记录")
        return len(records)
    except Exception as e:
        logger.error(f"导入失败: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        return 0

if __name__ == "__main__":
    init_car_info_table()
    count = import_car_info()
    logger.info(f"导入完成，共导入 {count} 条记录")
    sys.exit(0 if count > 0 else 1) 
