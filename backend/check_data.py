import sqlite3
import os

def check_data():
    # 使用正确的数据库路径
    db_path = os.path.join('db', 'forum_data.db')
    
    # 检查数据库文件是否存在
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        return
    
    print(f"数据库文件存在: {db_path}")
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 检查updatestatistics表中的不同时间点数量
    cursor.execute('SELECT COUNT(DISTINCT datetime) FROM updatestatistics')
    count = cursor.fetchone()[0]
    print(f"Number of distinct datetime points: {count}")
    
    # 检查最新的5个时间点
    cursor.execute('SELECT datetime FROM updatestatistics ORDER BY datetime DESC LIMIT 5')
    print("Latest 5 datetime points:")
    for row in cursor.fetchall():
        print(row[0])
    
    # 检查最早的5个时间点
    cursor.execute('SELECT datetime FROM updatestatistics ORDER BY datetime ASC LIMIT 5')
    print("\nEarliest 5 datetime points:")
    for row in cursor.fetchall():
        print(row[0])
    
    # 检查每个时间点的更新类型数量
    cursor.execute('''
    SELECT datetime, update_reason, COUNT(*) 
    FROM updatestatistics 
    GROUP BY datetime, update_reason 
    ORDER BY datetime DESC 
    LIMIT 15
    ''')
    print("\nUpdate types per datetime (latest 15 records):")
    for row in cursor.fetchall():
        print(f"Datetime: {row[0]}, Type: {row[1]}, Count: {row[2]}")
    
    conn.close()

if __name__ == "__main__":
    check_data() 