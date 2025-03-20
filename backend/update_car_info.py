# 此文件中的代码已被禁用（由car_info清理脚本处理）
# 原始功能已被移除，但保留文件以备参考
# 原始备份文件: update_car_info.py.bak_carinfo

import sqlite3
import os
from datetime import datetime

def get_db_connection():
    """获取数据库连接"""
    db_path = os.path.join(os.path.dirname(__file__), 'db', 'forum_data.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def update_car_info():
    """更新car_info表中缺失或不正确的数据"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        print("开始更新car_info表中缺失的数据...")
        
        # 1. 更新缺失的作者信息和作者链接
        cursor.execute("""
            UPDATE car_info
            SET 
                author = (
                    SELECT post.author 
                    FROM post 
                    WHERE post.url = car_info.url
                ),
                author_link = (
                    SELECT post.author_link
                    FROM post 
                    WHERE post.url = car_info.url
                )
            WHERE (author IS NULL OR author_link IS NULL)
            AND EXISTS (
                SELECT 1 
                FROM post 
                WHERE post.url = car_info.url
            )
        """)
        
        print(f"更新了 {cursor.rowcount} 条缺失的作者信息")
        
        # 2. 更新缺失的发帖时间和帖龄
        cursor.execute("""
            UPDATE car_info
            SET post_time = (
                SELECT post.post_time 
                FROM post 
                WHERE post.url = car_info.url
            ),
            daysold = (
                SELECT CAST((julianday('now') - julianday(post.post_time)) AS INTEGER)
                FROM post 
                WHERE post.url = car_info.url
            )
            WHERE (post_time IS NULL OR daysold IS NULL)
            AND EXISTS (
                SELECT 1 
                FROM post 
                WHERE post.url = car_info.url
            )
        """)
        
        print(f"更新了 {cursor.rowcount} 条缺失的发帖时间和帖龄信息")
        
        # 3. 更新缺失的最后活跃时间
        cursor.execute("""
            UPDATE car_info
            SET last_active = (
                SELECT CAST((julianday('now') - julianday(MAX(detail.update_date))) AS INTEGER)
                FROM detail 
                WHERE detail.url = car_info.url
            )
            WHERE last_active IS NULL
            AND EXISTS (
                SELECT 1 
                FROM detail 
                WHERE detail.url = car_info.url
            )
        """)
        
        print(f"更新了 {cursor.rowcount} 条缺失的最后活跃时间信息")
        
        # 4. 显示更新后的统计信息
        cursor.execute("""
            SELECT 
                COUNT(*) as total,
                SUM(CASE WHEN author IS NOT NULL THEN 1 ELSE 0 END) as with_author,
                SUM(CASE WHEN author_link IS NOT NULL THEN 1 ELSE 0 END) as with_author_link,
                SUM(CASE WHEN post_time IS NOT NULL THEN 1 ELSE 0 END) as with_post_time,
                SUM(CASE WHEN daysold IS NOT NULL THEN 1 ELSE 0 END) as with_daysold,
                SUM(CASE WHEN last_active IS NOT NULL THEN 1 ELSE 0 END) as with_last_active
            FROM car_info
        """)
        
        stats = cursor.fetchone()
        print("\n更新后的统计信息:")
        print(f"总记录数: {stats[0]}")
        print(f"有作者信息的记录数: {stats[1]}")
        print(f"有作者链接的记录数: {stats[2]}")
        print(f"有发帖时间的记录数: {stats[3]}")
        print(f"有帖龄的记录数: {stats[4]}")
        print(f"有最后活跃时间的记录数: {stats[5]}")
        
        # 5. 显示一些示例记录
        cursor.execute("""
            SELECT *
            FROM car_info
            WHERE author IS NOT NULL 
                AND author_link IS NOT NULL 
                AND post_time IS NOT NULL 
                AND daysold IS NOT NULL 
                AND last_active IS NOT NULL
            LIMIT 3
        """)
        
        print("\n示例记录:")
        for row in cursor.fetchall():
            print("\n---")
            for key in row.keys():
                print(f"{key}: {row[key]}")
        
        conn.commit()
        print("\n更新完成!")
        
    except Exception as e:
        print(f"更新失败: {str(e)}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    update_car_info() 
