import sqlite3
import os
from datetime import datetime, timedelta

def check_update_data():
    # 使用正确的数据库路径
    db_path = os.path.join('db', 'forum_data.db')
    
    # 检查数据库文件是否存在
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    print(f"数据库文件存在: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查updatestatistics表中的数据
    cursor.execute("SELECT COUNT(*) FROM updatestatistics")
    count = cursor.fetchone()[0]
    print(f"updatestatistics表中的记录数: {count}")
    
    # 检查不同的type值
    cursor.execute("SELECT DISTINCT type FROM updatestatistics")
    types = [row[0] for row in cursor.fetchall()]
    print(f"不同的type值: {types}")
    
    # 检查每种type的记录数
    for type_value in types:
        cursor.execute(f"SELECT COUNT(*) FROM updatestatistics WHERE type = ?", (type_value,))
        type_count = cursor.fetchone()[0]
        print(f"  - {type_value}: {type_count}条记录")
    
    # 检查最早和最晚的时间点
    cursor.execute("SELECT MIN(datetime), MAX(datetime) FROM updatestatistics WHERE type LIKE 'list_%'")
    min_max = cursor.fetchone()
    print(f"\n最早的时间点: {min_max[0]}")
    print(f"最晚的时间点: {min_max[1]}")
    
    # 计算有多少个不同的小时时间点
    cursor.execute("SELECT COUNT(DISTINCT datetime) FROM updatestatistics WHERE type LIKE 'list_%'")
    distinct_hours = cursor.fetchone()[0]
    print(f"不同的小时时间点数量: {distinct_hours}")
    
    # 获取最近60个小时的时间点
    cursor.execute("""
    SELECT DISTINCT datetime 
    FROM updatestatistics 
    WHERE type LIKE 'list_%' 
    ORDER BY datetime DESC 
    LIMIT 60
    """)
    recent_hours = [row[0] for row in cursor.fetchall()]
    
    print("\n最近60个小时的时间点:")
    for i, hour in enumerate(recent_hours):
        print(f"  {i+1}. {hour}")
    
    # 计算期望的60个小时时间点
    latest_hour_str = recent_hours[0] if recent_hours else "2025-03-06 23:00:00"
    latest_hour = datetime.strptime(latest_hour_str, "%Y-%m-%d %H:%M:%S")
    
    expected_hours = []
    for i in range(60):
        hour = latest_hour - timedelta(hours=i)
        expected_hours.append(hour.strftime("%Y-%m-%d %H:%M:%S"))
    
    print("\n期望的60个小时时间点:")
    for i, hour in enumerate(expected_hours):
        print(f"  {i+1}. {hour}")
    
    # 比较实际和期望的时间点
    missing_hours = [hour for hour in expected_hours if hour not in recent_hours]
    extra_hours = [hour for hour in recent_hours if hour not in expected_hours]
    
    if missing_hours:
        print("\n缺少的时间点:")
        for hour in missing_hours:
            print(f"  - {hour}")
    
    if extra_hours:
        print("\n多余的时间点:")
        for hour in extra_hours:
            print(f"  - {hour}")
    
    conn.close()

if __name__ == "__main__":
    check_update_data() 