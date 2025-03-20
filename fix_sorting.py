import sqlite3
import os

# 数据库路径
db_path = os.path.join('backend', 'db', 'forum_data.db')
print(f"数据库路径: {os.path.abspath(db_path)}")

# 连接数据库
try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    print("已连接到数据库")
except Exception as e:
    print(f"连接数据库失败: {e}")
    exit(1)

# 修复排序字段数据类型
tables_to_fix = ['post_ranking', 'author_ranking']

for table in tables_to_fix:
    # 检查表是否存在
    cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
    if not cursor.fetchone():
        print(f"表 {table} 不存在，跳过")
        continue
        
    print(f"\n处理表: {table}")
    
    # 检查表结构
    cursor.execute(f"PRAGMA table_info({table})")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    print(f"表结构: {column_names}")
    
    # 需要确保是数字类型的列
    numeric_columns = ['repost_count', 'reply_count', 'delete_reply_count', 'active_posts']
    
    for col in numeric_columns:
        if col not in column_names:
            print(f"列 {col} 不存在于表 {table} 中，跳过")
            continue
            
        try:
            # 检查当前数据类型
            cursor.execute(f"SELECT typeof({col}) FROM {table} LIMIT 1")
            current_type = cursor.fetchone()
            print(f"列 {col} 当前类型: {current_type}")
            
            # 将文本值转换为整数
            cursor.execute(f"UPDATE {table} SET {col} = CAST({col} AS INTEGER) WHERE typeof({col}) != 'integer'")
            rows_affected = cursor.rowcount
            print(f"已修复 {table} 表的 {col} 列数据类型，影响了 {rows_affected} 行")
        except Exception as e:
            print(f"修复 {col} 列时出错: {e}")

conn.commit()
print("\n所有修复已提交到数据库")

# 验证修复效果
for table in tables_to_fix:
    if table not in [row[0] for row in cursor.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()]:
        continue
        
    numeric_columns = ['repost_count', 'reply_count', 'delete_reply_count', 'active_posts']
    for col in numeric_columns:
        try:
            cursor.execute(f"SELECT typeof({col}) FROM {table} LIMIT 5")
            types = cursor.fetchall()
            if types:
                print(f"表 {table} 的列 {col} 的数据类型样本: {types}")
        except Exception:
            pass

conn.close()
print("数据库连接已关闭") 