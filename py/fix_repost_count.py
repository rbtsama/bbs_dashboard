import sqlite3
import pandas as pd
import os
from pathlib import Path

# 设置数据路径
BASE_DIR = Path(__file__).parent.parent
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'
DB_PATH = BASE_DIR / 'backend' / 'db' / 'forum_data.db'

def fix_repost_count():
    """修复数据库中重发次数被限制为9的问题"""
    print("开始修复重发次数限制问题...")
    
    # 检查CSV文件是否存在
    post_ranking_file = PROCESSED_DIR / 'post_ranking.csv'
    author_ranking_file = PROCESSED_DIR / 'author_ranking.csv'
    
    if not post_ranking_file.exists() or not author_ranking_file.exists():
        print("错误：无法找到所需的CSV文件")
        return False
    
    try:
        # 连接数据库
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 读取post_ranking.csv
        post_df = pd.read_csv(post_ranking_file)
        
        # 检查数据库中的post_ranking表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='post_ranking'")
        if cursor.fetchone() is None:
            print("错误：数据库中不存在post_ranking表")
            return False
        
        # 获取数据库中的当前值
        cursor.execute("SELECT url, repost_count FROM post_ranking ORDER BY repost_count DESC LIMIT 10")
        rows = cursor.fetchall()
        if rows:
            print("修复前数据库中的repost_count（前10条）：")
            for row in rows:
                print(f"  {row['url']}: {row['repost_count']}")
        
        # 更新post_ranking表中的repost_count
        print(f"开始更新post_ranking表中的{len(post_df)}条记录...")
        updated_count = 0
        
        for _, row in post_df.iterrows():
            if 'url' in row and 'repost_count' in row:
                url = row['url']
                repost_count = int(row['repost_count'])
                
                cursor.execute(
                    "UPDATE post_ranking SET repost_count = ? WHERE url = ?",
                    (repost_count, url)
                )
                if cursor.rowcount > 0:
                    updated_count += 1
        
        print(f"更新了{updated_count}条post_ranking记录")
        
        # 读取author_ranking.csv
        author_df = pd.read_csv(author_ranking_file)
        
        # 检查数据库中的author_ranking表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='author_ranking'")
        if cursor.fetchone() is None:
            print("错误：数据库中不存在author_ranking表")
            conn.commit()
            return False
        
        # 获取数据库中的当前值
        cursor.execute("SELECT author, repost_count FROM author_ranking ORDER BY repost_count DESC LIMIT 10")
        rows = cursor.fetchall()
        if rows:
            print("修复前数据库中的author repost_count（前10条）：")
            for row in rows:
                print(f"  {row['author']}: {row['repost_count']}")
        
        # 更新author_ranking表中的repost_count
        print(f"开始更新author_ranking表中的{len(author_df)}条记录...")
        author_updated_count = 0
        
        for _, row in author_df.iterrows():
            if 'author' in row and 'repost_count' in row:
                author = row['author']
                repost_count = int(row['repost_count'])
                
                cursor.execute(
                    "UPDATE author_ranking SET repost_count = ? WHERE author = ?",
                    (repost_count, author)
                )
                if cursor.rowcount > 0:
                    author_updated_count += 1
        
        print(f"更新了{author_updated_count}条author_ranking记录")
        
        # 提交更改
        conn.commit()
        
        # 验证更新结果
        cursor.execute("SELECT url, repost_count FROM post_ranking ORDER BY repost_count DESC LIMIT 10")
        rows = cursor.fetchall()
        if rows:
            print("修复后数据库中的repost_count（前10条）：")
            for row in rows:
                print(f"  {row['url']}: {row['repost_count']}")
        
        cursor.execute("SELECT author, repost_count FROM author_ranking ORDER BY repost_count DESC LIMIT 10")
        rows = cursor.fetchall()
        if rows:
            print("修复后数据库中的author repost_count（前10条）：")
            for row in rows:
                print(f"  {row['author']}: {row['repost_count']}")
        
        # 查找所有repost_count大于9的记录
        cursor.execute("SELECT COUNT(*) as count FROM post_ranking WHERE repost_count > 9")
        gt_9_count = cursor.fetchone()['count']
        cursor.execute("SELECT COUNT(*) as count FROM post_ranking")
        total_count = cursor.fetchone()['count']
        
        print(f"数据库中repost_count大于9的帖子有{gt_9_count}条，占总数的{gt_9_count/total_count*100:.2f}%")
        
        return True
    except Exception as e:
        print(f"修复过程中出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    if fix_repost_count():
        print("修复完成！现在重发次数应该能正确显示超过9的值了")
    else:
        print("修复失败，请检查错误信息") 