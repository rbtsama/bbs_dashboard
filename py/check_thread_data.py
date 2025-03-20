import sqlite3
import json
from pathlib import Path

# 数据库路径
DB_PATH = Path(__file__).parent.parent / 'backend' / 'db' / 'forum_data.db'

def check_thread_data():
    """检查帖子排行数据是否被限制为9"""
    try:
        # 连接到数据库
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 检查post_ranking表
        print("检查post_ranking表...")
        cursor.execute("""
            SELECT * FROM post_ranking
            ORDER BY repost_count DESC
            LIMIT 10
        """)
        
        rows = cursor.fetchall()
        if rows:
            print(f"post_ranking表中有{len(rows)}条记录。")
            print("repost_count最大的10条记录:")
            for i, row in enumerate(rows):
                row_dict = dict(row)
                print(f"{i+1}. {row_dict.get('title', '无标题')[:30]}...: repost_count={row_dict.get('repost_count', 'N/A')}")
        else:
            print("post_ranking表中没有数据")
            
            # 检查import表中的post_ranking数据
            print("\n检查import表中的post_ranking数据...")
            cursor.execute("""
                SELECT * FROM import
                WHERE data_category = 'post_ranking'
                ORDER BY repost_count DESC
                LIMIT 10
            """)
            
            rows = cursor.fetchall()
            if rows:
                print(f"import表中有{len(rows)}条post_ranking记录。")
                print("repost_count最大的10条记录:")
                for i, row in enumerate(rows):
                    row_dict = dict(row)
                    print(f"{i+1}. {row_dict.get('title', '无标题')[:30]}...: repost_count={row_dict.get('repost_count', 'N/A')}")
            else:
                print("import表中没有post_ranking数据")
        
        # 关闭数据库连接
        conn.close()
        
    except Exception as e:
        print(f"检查数据时出错: {str(e)}")

if __name__ == "__main__":
    check_thread_data() 