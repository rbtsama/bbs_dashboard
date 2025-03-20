# 此文件中的代码已被禁用（由car_info清理脚本处理）
# 原始功能已被移除，但保留文件以备参考
# 原始备份文件: update_car_info.py.bak_carinfo

import sqlite3
import os
from datetime import datetime

def update_car_info_table():
    try:
        # 连接数据库
        conn = sqlite3.connect('backend/db/forum_data.db')
        cursor = conn.cursor()
        
        # 创建临时表
        cursor.execute("""
        CREATE TABLE car_info_temp (
            url TEXT,
            title TEXT,
            year TEXT,
            make TEXT,
            model TEXT,
            miles TEXT,
            price TEXT,
            trade_type TEXT,
            location TEXT,
            daysold INTEGER DEFAULT 0,
            last_active INTEGER DEFAULT 0,
            author TEXT,
            author_link TEXT,
            update_time DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)
        
        # 复制数据到临时表
        cursor.execute("""
        INSERT INTO car_info_temp (
            url, title, year, make, model, miles, price, trade_type, location
        )
        SELECT url, title, year, make, model, miles, price, trade_type, location
        FROM car_info
        """)
        
        # 删除旧表
        cursor.execute("DROP TABLE car_info")
        
        # 重命名临时表
        cursor.execute("ALTER TABLE car_info_temp RENAME TO car_info")
        
        # 更新daysold和last_active
        cursor.execute("UPDATE car_info SET daysold = 0, last_active = 0")
        
        # 提交更改
        conn.commit()
        print("成功更新car_info表结构")
        
    except Exception as e:
        print(f"更新表结构时出错: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == '__main__':
    update_car_info_table() 
