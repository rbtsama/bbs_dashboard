import sqlite3
import os

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), 'db', 'forum_data.db')

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def check_car_info():
    """检查car_info表中的数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 获取记录总数
    cursor.execute("SELECT COUNT(*) FROM car_info")
    total_count = cursor.fetchone()[0]
    print(f"car_info表中共有 {total_count} 条记录")
    
    # 获取有完整关联信息的记录数
    cursor.execute("SELECT COUNT(*) FROM car_info WHERE author IS NOT NULL AND post_time IS NOT NULL")
    related_count = cursor.fetchone()[0]
    print(f"其中有完整关联信息的记录有 {related_count} 条 ({related_count/total_count*100:.2f}%)")
    
    # 获取年份分布
    cursor.execute("SELECT year, COUNT(*) as count FROM car_info WHERE year IS NOT NULL GROUP BY year ORDER BY year DESC")
    year_counts = cursor.fetchall()
    print("\n年份分布:")
    for year in year_counts:
        print(f"  {year['year']}: {year['count']} 条")
    
    # 获取品牌分布
    cursor.execute("SELECT make, COUNT(*) as count FROM car_info GROUP BY make ORDER BY count DESC LIMIT 10")
    make_counts = cursor.fetchall()
    print("\n品牌分布 (前10名):")
    for make in make_counts:
        print(f"  {make['make'] or '未知'}: {make['count']} 条")
    
    # 获取交易类型分布
    cursor.execute("SELECT trade_type, COUNT(*) as count FROM car_info GROUP BY trade_type ORDER BY count DESC")
    trade_type_counts = cursor.fetchall()
    print("\n交易类型分布:")
    for tt in trade_type_counts:
        print(f"  {tt['trade_type'] or '未知'}: {tt['count']} 条")
    
    # 获取示例记录
    cursor.execute("SELECT * FROM car_info WHERE author IS NOT NULL LIMIT 5")
    sample_records = cursor.fetchall()
    print("\n有关联信息的示例记录:")
    for i, record in enumerate(sample_records):
        print(f"\n示例 {i+1}:")
        for key in record.keys():
            print(f"  {key}: {record[key]}")
    
    conn.close()

if __name__ == "__main__":
    check_car_info() 