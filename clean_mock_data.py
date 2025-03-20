"""
清理数据库中的模拟数据
"""
import sqlite3
import os
from datetime import datetime

def get_db_connection():
    """获取数据库连接"""
    db_path = 'backend/db/forum_data.db'
    if os.path.exists(db_path):
        print(f"找到数据库文件: {db_path}")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    print(f"数据库文件不存在: {db_path}")
    return None

def clean_post_ranking():
    """清理post_ranking表中的模拟数据"""
    print(f"[{datetime.now()}] 开始清理post_ranking表...")
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # 获取表中的总记录数
        cursor.execute("SELECT COUNT(*) FROM post_ranking")
        total_count = cursor.fetchone()[0]
        print(f"[{datetime.now()}] post_ranking表当前有{total_count}条记录")
        
        # 删除可能的模拟数据（根据特征识别）
        cursor.execute("""
        DELETE FROM post_ranking 
        WHERE thread_id LIKE 'test%' 
        OR thread_id LIKE 'mock%'
        OR thread_id LIKE 'example%'
        OR url LIKE '%example%'
        OR url LIKE '%test%'
        OR title LIKE '%测试%'
        OR title LIKE '%示例%'
        """)
        
        deleted_count = cursor.rowcount
        conn.commit()
        print(f"[{datetime.now()}] 已删除{deleted_count}条模拟数据")
        
    except Exception as e:
        print(f"[{datetime.now()}] 清理post_ranking表出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

def clean_author_ranking():
    """清理author_ranking表中的模拟数据"""
    print(f"[{datetime.now()}] 开始清理author_ranking表...")
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # 获取表中的总记录数
        cursor.execute("SELECT COUNT(*) FROM author_ranking")
        total_count = cursor.fetchone()[0]
        print(f"[{datetime.now()}] author_ranking表当前有{total_count}条记录")
        
        # 删除可能的模拟数据
        cursor.execute("""
        DELETE FROM author_ranking 
        WHERE author LIKE 'test%'
        OR author LIKE 'mock%'
        OR author LIKE 'example%'
        OR author_link LIKE '%test%'
        OR author_link LIKE '%example%'
        """)
        
        deleted_count = cursor.rowcount
        conn.commit()
        print(f"[{datetime.now()}] 已删除{deleted_count}条模拟数据")
        
    except Exception as e:
        print(f"[{datetime.now()}] 清理author_ranking表出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

def clean_statistic_data():
    """清理统计数据表中的模拟数据"""
    print(f"[{datetime.now()}] 开始清理统计数据表...")
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # 清理post_statistic表
        cursor.execute("DELETE FROM post_statistic")
        post_deleted = cursor.rowcount
        print(f"[{datetime.now()}] 已清理post_statistic表 {post_deleted}条记录")
        
        # 清理update_statistic表
        cursor.execute("DELETE FROM update_statistic")
        update_deleted = cursor.rowcount
        print(f"[{datetime.now()}] 已清理update_statistic表 {update_deleted}条记录")
        
        # 清理view_statistic表
        cursor.execute("DELETE FROM view_statistic")
        view_deleted = cursor.rowcount
        print(f"[{datetime.now()}] 已清理view_statistic表 {view_deleted}条记录")
        
        conn.commit()
        
    except Exception as e:
        print(f"[{datetime.now()}] 清理统计数据表出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    print(f"[{datetime.now()}] 开始清理数据库模拟数据...")
    
    # 清理排行榜数据
    clean_post_ranking()
    clean_author_ranking()
    
    # 清理统计数据
    clean_statistic_data()
    
    print(f"[{datetime.now()}] 数据库模拟数据清理完成") 