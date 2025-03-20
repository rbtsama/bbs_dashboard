import sqlite3
from datetime import datetime, timedelta
import pandas as pd

def generate_statistics():
    conn = sqlite3.connect('backend/db/forum_data.db')
    cursor = conn.cursor()
    
    # 清空import表中的统计数据
    cursor.execute("""
        DELETE FROM import 
        WHERE data_category IN ('update_statistics', 'view_statistics', 'author_ranking')
    """)
    
    # 生成更新统计数据
    cursor.execute("""
        WITH daily_stats AS (
            SELECT 
                DATE(list_time) as date,
                update_reason,
                COUNT(*) as count
            FROM list
            WHERE list_time IS NOT NULL
                AND update_reason IS NOT NULL
                AND update_reason IN ('重发', '回帖', '删回帖')
            GROUP BY DATE(list_time), update_reason
            ORDER BY date
        )
        SELECT * FROM daily_stats
    """)
    update_stats = cursor.fetchall()
    
    # 插入更新统计数据
    for stat in update_stats:
        date, update_type, count = stat
        date_str = f"{date}T00:00:00"
        
        # 插入更新统计
        cursor.execute("""
            INSERT INTO import (type, datetime, count, data_category)
            VALUES (?, ?, ?, ?)
        """, (update_type, date_str, count, 'update_statistics'))
    
    # 生成浏览统计数据
    cursor.execute("""
        WITH daily_views AS (
            SELECT 
                DATE(list_time) as date,
                url,
                MAX(read_count) as max_views
            FROM list
            WHERE list_time IS NOT NULL
            GROUP BY DATE(list_time), url
        ),
        prev_day_views AS (
            SELECT 
                date,
                url,
                max_views,
                LAG(max_views) OVER (PARTITION BY url ORDER BY date) as prev_views
            FROM daily_views
        )
        SELECT 
            date,
            SUM(max_views) as total_views,
            SUM(CASE 
                WHEN prev_views IS NULL THEN max_views 
                ELSE max_views - prev_views 
            END) as view_increase
        FROM prev_day_views
        GROUP BY date
        ORDER BY date
    """)
    view_stats = cursor.fetchall()
    
    # 插入浏览统计数据
    for stat in view_stats:
        date, total_views, view_increase = stat
        date_str = f"{date}T00:00:00"
        
        # 插入总浏览量
        cursor.execute("""
            INSERT INTO import (type, datetime, count, data_category)
            VALUES (?, ?, ?, ?)
        """, ('total_view', date_str, total_views, 'view_statistics'))
        
        # 插入浏览增量
        cursor.execute("""
            INSERT INTO import (type, datetime, count, data_category)
            VALUES (?, ?, ?, ?)
        """, ('view', date_str, view_increase, 'view_statistics'))
    
    # 生成作者排名数据
    cursor.execute("""
        WITH author_stats AS (
            SELECT 
                author,
                COUNT(*) as total_posts,
                SUM(reply_count) as total_replies,
                SUM(read_count) as total_views
            FROM list
            WHERE author IS NOT NULL
            GROUP BY author
        )
        SELECT * FROM author_stats
        ORDER BY total_posts DESC, total_replies DESC, total_views DESC
        LIMIT 100
    """)
    author_stats = cursor.fetchall()
    
    # 插入作者排名数据
    current_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    for rank, (author, posts, replies, views) in enumerate(author_stats, 1):
        cursor.execute("""
            INSERT INTO import (
                type, datetime, author, total_posts, reply_count, 
                view_count, data_category
            )
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, ('author_rank', current_time, author, posts, replies, 
              views, 'author_ranking'))
    
    conn.commit()
    conn.close()
    print("统计数据生成完成！")

if __name__ == "__main__":
    generate_statistics() 