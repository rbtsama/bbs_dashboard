import sqlite3
import os
from datetime import datetime

def get_db_connection():
    """获取数据库连接"""
    db_path = 'db/forum_data.db'
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return None
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def analyze_database_tables():
    """分析数据库表结构"""
    print(f"[{datetime.now()}] 开始分析数据库表结构...")
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        # 获取所有表名
        cursor = conn.cursor()
        tables = cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        print(f"[{datetime.now()}] 数据库中存在的表:")
        for table in tables:
            print(f"  - {table['name']}")
            
            # 获取表结构
            try:
                columns = cursor.execute(f"PRAGMA table_info({table['name']})").fetchall()
                print(f"    列结构:")
                for col in columns:
                    print(f"      {col['name']} ({col['type']})")
                
                # 获取表中的行数
                count = cursor.execute(f"SELECT COUNT(*) FROM {table['name']}").fetchone()[0]
                print(f"    行数: {count}")
                
                # 示例数据
                if count > 0:
                    sample = cursor.execute(f"SELECT * FROM {table['name']} LIMIT 1").fetchone()
                    print(f"    示例数据: {dict(sample)}")
            except Exception as e:
                print(f"    获取表 {table['name']} 的结构时出错: {str(e)}")
            
            print("")
    
    except Exception as e:
        print(f"[{datetime.now()}] 分析数据库表结构出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

def find_specific_data():
    """查找用户指定的特定数据"""
    print(f"[{datetime.now()}] 开始查询特定数据...")
    conn = get_db_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # 1. 查询2月8日的发帖量(type=post,post_count)
        print(f"\n[{datetime.now()}] 查询1: 2025年2月8日的发帖量")
        
        # 尝试按小时聚合
        query1_hourly = """
        SELECT 
            datetime,
            SUM(count) as total_count
        FROM post_statistic
        WHERE datetime LIKE '2025-02-08%' AND type = 'post'
        GROUP BY DATE(datetime)
        """
        
        # 尝试直接查找日数据
        query1_daily = """
        SELECT 
            datetime,
            count as total_count
        FROM post_statistic
        WHERE datetime = '2025-02-08' AND type = 'post'
        """
        
        # 尝试使用不同的日期格式
        query1_alt = """
        SELECT 
            datetime,
            count as total_count
        FROM post_statistic
        WHERE (datetime = '2025-02-08' OR datetime LIKE '2025-02-08%') AND type = 'post'
        """
        
        result1 = cursor.execute(query1_alt).fetchall()
        if result1:
            print(f"  找到 {len(result1)} 条记录:")
            for row in result1:
                print(f"  - 日期: {row['datetime']}, 发帖量: {row['total_count']}")
        else:
            print("  未找到2025年2月8日的发帖数据")
            
            # 查找可能的日期格式
            sample_dates = cursor.execute("""
            SELECT DISTINCT datetime FROM post_statistic LIMIT 10
            """).fetchall()
            print("  数据库中的日期格式示例:")
            for date in sample_dates:
                print(f"  - {date['datetime']}")
        
        # 2. 查询2月9日的重发量(repost_count)
        print(f"\n[{datetime.now()}] 查询2: 2025年2月9日的重发量")
        
        query2 = """
        SELECT 
            datetime,
            update_reason,
            count as repost_count
        FROM update_statistic
        WHERE (datetime = '2025-02-09' OR datetime LIKE '2025-02-09%') 
        AND (update_reason = '重发' OR type LIKE '%重发%')
        """
        
        result2 = cursor.execute(query2).fetchall()
        if result2:
            print(f"  找到 {len(result2)} 条记录:")
            for row in result2:
                print(f"  - 日期: {row['datetime']}, 重发量: {row['repost_count']}, 类型: {row['update_reason']}")
        else:
            print("  未找到2025年2月9日的重发数据")
            
            # 查找可能的类型
            update_types = cursor.execute("""
            SELECT DISTINCT update_reason, type FROM update_statistic LIMIT 10
            """).fetchall()
            print("  数据库中的更新类型示例:")
            for row in update_types:
                print(f"  - 原因: {row['update_reason']}, 类型: {row['type']}")
        
        # 3. 查询2月10日的阅读增量(view_gap)
        print(f"\n[{datetime.now()}] 查询3: 2025年2月10日的阅读增量")
        
        query3 = """
        SELECT 
            datetime,
            count as view_count,
            type
        FROM view_statistic
        WHERE (datetime = '2025-02-10' OR datetime LIKE '2025-02-10%')
        """
        
        result3 = cursor.execute(query3).fetchall()
        if result3:
            print(f"  找到 {len(result3)} 条记录:")
            for row in result3:
                print(f"  - 日期: {row['datetime']}, 阅读量: {row['view_count']}, 类型: {row['type']}")
        else:
            print("  未找到2025年2月10日的阅读量数据")
            
            # 查找可能的表和列
            tables_with_view = cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='table' AND 
            (name LIKE '%view%' OR name LIKE '%read%')
            """).fetchall()
            print("  可能包含阅读数据的表:")
            for table in tables_with_view:
                print(f"  - {table['name']}")
        
        # 查找最早和最新的数据日期
        print(f"\n[{datetime.now()}] 查询数据库中的日期范围:")
        
        # 发帖数据范围
        post_range = cursor.execute("""
        SELECT MIN(datetime) as min_date, MAX(datetime) as max_date 
        FROM post_statistic
        """).fetchone()
        print(f"  发帖数据日期范围: {post_range['min_date']} 至 {post_range['max_date']}")
        
        # 更新数据范围
        update_range = cursor.execute("""
        SELECT MIN(datetime) as min_date, MAX(datetime) as max_date 
        FROM update_statistic
        """).fetchone()
        print(f"  更新数据日期范围: {update_range['min_date']} 至 {update_range['max_date']}")
        
        # 阅读数据范围
        view_range = cursor.execute("""
        SELECT MIN(datetime) as min_date, MAX(datetime) as max_date 
        FROM view_statistic
        """).fetchone()
        print(f"  阅读数据日期范围: {view_range['min_date']} 至 {view_range['max_date']}")
        
    except Exception as e:
        print(f"[{datetime.now()}] 查询特定数据出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

def generate_api_fix_guidance():
    """根据数据库分析生成API修复指南"""
    print(f"\n[{datetime.now()}] 生成API修复指南:")
    
    print("""
修复API实现的建议：

1. 针对日期聚合问题：
   - 检查数据库中的日期格式，看是否需要处理包含时间部分的ISO格式
   - 对于按小时存储的数据，需要使用GROUP BY聚合为日/周/月数据

2. 实现聚合的SQL示例:
   ```sql
   -- 按日聚合
   SELECT DATE(datetime) as date, SUM(count) as total
   FROM statistic_table
   WHERE type = 'required_type'
   GROUP BY DATE(datetime)
   ORDER BY date ASC
   
   -- 按周聚合 (SQLite)
   SELECT strftime('%Y-%W', datetime) as week, SUM(count) as total
   FROM statistic_table
   WHERE type = 'required_type'
   GROUP BY strftime('%Y-%W', datetime)
   ORDER BY week ASC
   
   -- 按月聚合
   SELECT strftime('%Y-%m', datetime) as month, SUM(count) as total
   FROM statistic_table
   WHERE type = 'required_type'
   GROUP BY strftime('%Y-%m', datetime)
   ORDER BY month ASC
   ```

3. 确保查询返回的数据:
   - 日期格式一致
   - 排序正确 (ORDER BY datetime ASC)
   - 不限制数据量，确保返回所有历史数据
   - 对缺失的日期填充0值
    """)

if __name__ == "__main__":
    print(f"[{datetime.now()}] 开始分析数据库...")
    analyze_database_tables()
    find_specific_data()
    generate_api_fix_guidance()
    print(f"[{datetime.now()}] 分析完成") 