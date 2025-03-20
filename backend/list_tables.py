import sqlite3

# 连接数据库
conn = sqlite3.connect("../data.db")
cursor = conn.cursor()

# 列出所有表
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()

print("数据库中的所有表:")
for table in tables:
    # 获取表中的记录数
    try:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"- {table[0]}: {count} 条记录")
        
        # 获取表的结构
        cursor.execute(f"PRAGMA table_info({table[0]})")
        columns = cursor.fetchall()
        print(f"  表结构:")
        for col in columns:
            print(f"    {col[1]} ({col[2]})")
        print("")
    except sqlite3.OperationalError as e:
        print(f"- {table[0]}: 无法获取信息 ({str(e)})")

conn.close() 