import sqlite3
import os
import csv
import logging
from datetime import datetime
import pandas as pd

# 设置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# 数据库目录和路径
DB_DIR = os.path.join(os.path.dirname(__file__), 'db')
DB_PATH = os.path.join(DB_DIR, 'forum_data.db')

# 数据文件路径
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed')
CAR_INFO_PATH = os.path.join(DATA_DIR, 'car_info.csv')
UPDATE_PATH = os.path.join(DATA_DIR, 'update.xlsx')

def init_db():
    """初始化数据库，创建必要的表"""
    # 确保数据库目录存在
    os.makedirs(DB_DIR, exist_ok=True)
    
    # 连接数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 创建car_info表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS car_info (
            url TEXT PRIMARY KEY,
            title TEXT,
            year INTEGER,
            make TEXT,
            model TEXT,
            price REAL,
            miles INTEGER,
            trade_type TEXT,
            location TEXT,
            daysold INTEGER,
            last_active INTEGER,
            author TEXT,
            author_link TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 检查表是否为空
        cursor.execute('SELECT COUNT(*) FROM car_info')
        count = cursor.fetchone()[0]
        
        if count == 0:
            logger.info("开始导入car_info.csv数据")
            
            # 读取car_info.csv
            logger.info(f"从 {CAR_INFO_PATH} 读取数据")
            car_df = pd.read_csv(CAR_INFO_PATH)
            logger.info(f"car_info.csv包含 {len(car_df)} 条记录")
            
            # 读取update.xlsx
            logger.info(f"从 {UPDATE_PATH} 读取数据")
            update_df = pd.read_excel(UPDATE_PATH)
            logger.info(f"update.xlsx包含 {len(update_df)} 条记录")
            
            # 确保scraping_time列是datetime类型
            update_df['scraping_time'] = pd.to_datetime(update_df['scraping_time'])
            
            # 对于每个URL，只保留最新的记录
            logger.info("处理update.xlsx数据，保留每个URL的最新记录...")
            latest_updates = update_df.sort_values('scraping_time').groupby('url').last().reset_index()
            logger.info(f"处理后的update.xlsx包含 {len(latest_updates)} 条记录")
            
            # 计算每个URL的首次出现时间和最后出现时间
            first_seen = update_df.groupby('url')['scraping_time'].min()
            last_seen = update_df.groupby('url')['scraping_time'].max()
            
            # 计算daysold和last_active
            now = datetime.now()
            first_seen = first_seen.reset_index()
            last_seen = last_seen.reset_index()
            
            first_seen['daysold'] = (now - first_seen['scraping_time']).dt.total_seconds() / (24*3600)
            last_seen['last_active'] = (now - last_seen['scraping_time']).dt.total_seconds() / (24*3600)
            
            # 转换为整数
            first_seen['daysold'] = first_seen['daysold'].fillna(0).astype(int)
            last_seen['last_active'] = last_seen['last_active'].fillna(0).astype(int)
            
            # 合并数据
            logger.info("合并数据...")
            merged_df = pd.merge(car_df, latest_updates, on='url', how='left')
            merged_df = pd.merge(merged_df, first_seen[['url', 'daysold']], on='url', how='left')
            merged_df = pd.merge(merged_df, last_seen[['url', 'last_active']], on='url', how='left')
            logger.info(f"合并后共有 {len(merged_df)} 条记录")
            
            # 遍历合并后的数据并插入数据库
            for _, row in merged_df.iterrows():
                cursor.execute('''
                INSERT INTO car_info (
                    url, title, year, make, model, price, miles, trade_type,
                    location, daysold, last_active, author, author_link
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['url'],
                    row.get('title', ''),  # 从update.xlsx获取
                    row['year'],
                    row['make'],
                    row['model'],
                    row['price'],
                    row['miles'],
                    row['trade_type'],
                    row['location'],
                    row.get('daysold', 0),  # 计算得到的帖龄
                    row.get('last_active', 0),  # 计算得到的最后活跃时间
                    row.get('author', ''),  # 从update.xlsx获取
                    row.get('author_link', '')  # 从update.xlsx获取
                ))
            
            conn.commit()
            logger.info(f"导入完成，共导入{len(merged_df)}条数据")
        
    except Exception as e:
        logger.error(f"初始化数据库时发生错误: {str(e)}")
        raise
    finally:
        conn.close()

if __name__ == '__main__':
    init_db()
    print("数据库初始化完成") 