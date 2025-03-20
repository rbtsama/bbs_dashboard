import sqlite3
import os
from datetime import datetime, timedelta

def get_db_connection():
    """获取数据库连接"""
    db_path = 'db/forum_data.db'
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return None
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def generate_post_statistic_data(days=30, start_from_now=True):
    """生成发帖趋势的历史数据"""
    print(f"[{datetime.now()}] 此功能已禁用，不再生成模拟数据")
    return True

def generate_update_statistic_data(days=30, start_from_now=True):
    """生成更新趋势的历史数据"""
    print(f"[{datetime.now()}] 此功能已禁用，不再生成模拟数据")
    return True

def generate_view_statistic_data(days=30, start_from_now=True):
    """生成浏览趋势的历史数据"""
    print(f"[{datetime.now()}] 此功能已禁用，不再生成模拟数据")
    return True

def check_chart_data():
    """检查图表数据情况"""
    print(f"[{datetime.now()}] 开始检查图表数据...")
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # 检查发帖趋势数据
        cursor.execute("SELECT COUNT(*) FROM post_statistic WHERE type='post'")
        post_count = cursor.fetchone()[0]
        cursor.execute("SELECT MIN(datetime), MAX(datetime) FROM post_statistic WHERE type='post'")
        post_range = cursor.fetchone()
        print(f"[{datetime.now()}] 发帖趋势数据: {post_count}条记录，日期范围: {post_range[0]} 至 {post_range[1]}")
        
        # 检查更新趋势数据
        cursor.execute("SELECT COUNT(*), COUNT(DISTINCT datetime) FROM update_statistic WHERE type LIKE 'list_%'")
        update_stats = cursor.fetchone()
        cursor.execute("SELECT MIN(datetime), MAX(datetime) FROM update_statistic WHERE type LIKE 'list_%'")
        update_range = cursor.fetchone()
        print(f"[{datetime.now()}] 更新趋势数据: {update_stats[0]}条记录，{update_stats[1]}个不同日期，日期范围: {update_range[0]} 至 {update_range[1]}")
        
        # 按更新类型统计
        cursor.execute("SELECT update_reason, COUNT(*) FROM update_statistic WHERE type LIKE 'list_%' GROUP BY update_reason")
        update_type_stats = cursor.fetchall()
        for update_type, count in update_type_stats:
            print(f"[{datetime.now()}] 更新类型 '{update_type}': {count}条记录")
        
        # 检查浏览趋势数据
        cursor.execute("SELECT COUNT(*) FROM view_statistic WHERE type='view'")
        view_count = cursor.fetchone()[0]
        cursor.execute("SELECT MIN(datetime), MAX(datetime) FROM view_statistic WHERE type='view'")
        view_range = cursor.fetchone()
        print(f"[{datetime.now()}] 浏览趋势数据: {view_count}条记录，日期范围: {view_range[0]} 至 {view_range[1]}")
        
    except Exception as e:
        print(f"[{datetime.now()}] 检查图表数据出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

if __name__ == "__main__":
    print(f"[{datetime.now()}] 开始生成图表数据...")
    
    # 为最近30天生成数据
    generate_post_statistic_data(days=30, start_from_now=True)
    generate_update_statistic_data(days=30, start_from_now=True)
    generate_view_statistic_data(days=30, start_from_now=True)
    
    # 为更早的30天生成数据
    generate_post_statistic_data(days=30, start_from_now=False)
    generate_update_statistic_data(days=30, start_from_now=False)
    generate_view_statistic_data(days=30, start_from_now=False)
    
    # 为更早的30天生成数据
    generate_post_statistic_data(days=30, start_from_now=False)
    generate_update_statistic_data(days=30, start_from_now=False)
    generate_view_statistic_data(days=30, start_from_now=False)
    
    print(f"[{datetime.now()}] 图表数据生成完成")
    print(f"\n[{datetime.now()}] 检查图表数据情况:")
    check_chart_data() 