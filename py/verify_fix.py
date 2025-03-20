import sqlite3
import pandas as pd
from pathlib import Path

# 设置数据路径
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / 'backend' / 'db' / 'forum_data.db'

def verify_fix():
    """验证修复是否有效"""
    print("验证数据库修复情况...")
    
    # 连接到数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 检查post_ranking表结构
    cursor.execute("PRAGMA table_info(post_ranking)")
    post_columns = cursor.fetchall()
    print("post_ranking表结构:")
    for col in post_columns:
        print(f"  {col[1]}: {col[2]} (主键: {col[5]})")
    
    # 检查最大值
    cursor.execute("SELECT MAX(repost_count) FROM post_ranking")
    max_repost = cursor.fetchone()[0]
    print(f"\npost_ranking.repost_count最大值: {max_repost}")
    
    # 检查大于9的记录数
    cursor.execute("SELECT COUNT(*) FROM post_ranking WHERE repost_count > 9")
    gt_9_count = cursor.fetchone()[0]
    print(f"repost_count > 9的记录数: {gt_9_count}")
    
    # 获取前10条repost_count最大的记录
    cursor.execute("""
        SELECT url, title, author, repost_count 
        FROM post_ranking 
        ORDER BY repost_count DESC
        LIMIT 10
    """)
    top_records = cursor.fetchall()
    print("\nrepost_count最高的10条记录:")
    for i, (url, title, author, count) in enumerate(top_records, 1):
        print(f"{i}. {title[:30]}... (作者: {author}) - 重发次数: {count}")
    
    # 关闭连接
    conn.close()
    print("\n验证完成！")

if __name__ == "__main__":
    verify_fix() 