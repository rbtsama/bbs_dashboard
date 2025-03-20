#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
导入car_info.csv数据到数据库的car_info表
这个脚本只操作car_info表，不会影响数据库中的其他表
"""

import os
import sqlite3
import pandas as pd
import re
import logging
import traceback
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("update_car_info_table")

def import_car_info_to_db():
    """导入car_info数据到数据库，仅操作car_info表"""
    try:
        # 获取项目根目录
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        
        # 数据文件路径
        car_info_path = os.path.join(project_root, "data/processed/car_info.csv")
        
        # 数据库路径
        db_path = os.path.join(project_root, "backend/db/forum_data.db")
        
        logger.info(f"数据库路径: {db_path}")
        logger.info(f"车辆信息文件路径: {car_info_path}")
        
        # 检查文件是否存在
        if not os.path.exists(car_info_path):
            logger.error(f"车辆信息文件不存在: {car_info_path}")
            return False
            
        # 读取CSV文件
        try:
            df = pd.read_csv(car_info_path)
            logger.info(f"成功读取车辆信息CSV文件: {car_info_path}, 共 {len(df)} 行")
        except Exception as e:
            logger.error(f"读取车辆信息文件时出错: {str(e)}")
            return False
        
        # 确保时间列是正确的格式
        if 'post_time' in df.columns:
            df['post_time'] = pd.to_datetime(df['post_time'])
        if 'scraping_time_R' in df.columns:
            df['scraping_time_R'] = pd.to_datetime(df['scraping_time_R'])
        
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 备份原有car_info表（如果存在）
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='car_info'")
        if cursor.fetchone():
            timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
            cursor.execute(f"ALTER TABLE car_info RENAME TO car_info_bak_{timestamp}")
            logger.info(f"已将原car_info表重命名为car_info_bak_{timestamp}")
        
        # 创建car_info表结构
        cursor.execute('''
        CREATE TABLE car_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            year TEXT,
            make TEXT,
            model TEXT,
            miles TEXT,
            price TEXT,
            trade_type TEXT,
            location TEXT,
            post_time TEXT,
            scraping_time_R TEXT,
            title TEXT,
            author TEXT,
            author_link TEXT,
            thread_id TEXT,
            daysold INTEGER DEFAULT 999,
            last_active INTEGER DEFAULT 999,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(url)
        )
        ''')
        
        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_car_info_url ON car_info(url)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_car_info_make ON car_info(make)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_car_info_model ON car_info(model)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_car_info_title ON car_info(title)")
        
        # 准备插入数据的SQL语句
        # 动态构建SQL插入语句，只包含df中存在的列
        columns = [col for col in df.columns if col != 'id']
        placeholders = ', '.join(['?' for _ in columns])
        columns_str = ', '.join(columns)
        
        insert_sql = f'''
        INSERT OR REPLACE INTO car_info (
            {columns_str}
        ) VALUES ({placeholders})
        '''
        
        # 逐行插入数据
        rows_inserted = 0
        for _, row in df.iterrows():
            try:
                url = row.get('url')
                if not url:
                    logger.warning("发现缺失URL的记录，跳过")
                    continue
                
                # 格式化时间字段
                if 'post_time' in row and pd.notna(row['post_time']):
                    post_time = row['post_time']
                    if isinstance(post_time, pd.Timestamp):
                        row['post_time'] = post_time.strftime('%Y-%m-%d %H:%M:%S')
                
                if 'scraping_time_R' in row and pd.notna(row['scraping_time_R']):
                    scraping_time = row['scraping_time_R']
                    if isinstance(scraping_time, pd.Timestamp):
                        row['scraping_time_R'] = scraping_time.strftime('%Y-%m-%d %H:%M:%S')
                
                # 提取thread_id（如果没有）
                if 'thread_id' not in row or pd.isna(row['thread_id']):
                    thread_id = None
                    thread_id_match = re.search(r't_(\d+)\.html', url)
                    if thread_id_match:
                        thread_id = thread_id_match.group(1)
                    row['thread_id'] = thread_id
                
                # 准备插入的数据
                values = [row.get(col) for col in columns]
                
                # 插入数据
                cursor.execute(insert_sql, values)
                rows_inserted += 1
                
            except Exception as e:
                logger.warning(f"插入记录时出错 [URL: {url}]: {str(e)}")
        
        conn.commit()
        logger.info(f"成功导入 {rows_inserted} 条车辆信息记录")
        
        # 验证导入结果
        cursor.execute("SELECT COUNT(*) FROM car_info")
        total_rows = cursor.fetchone()[0]
        if total_rows != rows_inserted:
            logger.warning(f"数据导入不完整：预期 {rows_inserted} 行，实际 {total_rows} 行")
        
        conn.close()
        return True
            
    except Exception as e:
        logger.error(f"导入车辆信息过程中出错: {str(e)}\n{traceback.format_exc()}")
        return False

if __name__ == "__main__":
    success = import_car_info_to_db()
    if success:
        logger.info("车辆信息导入成功")
    else:
        logger.error("车辆信息导入失败") 