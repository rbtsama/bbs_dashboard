import sqlite3
import os
import time
import shutil

# 数据库路径
db_path = 'backend/db/forum_data.db'

# 创建备份
backup_time = time.strftime("%Y%m%d_%H%M%S")
backup_path = f'backup/db/pre_rename_{backup_time}.db'

# 确保备份目录存在
os.makedirs(os.path.dirname(backup_path), exist_ok=True)

print(f"创建数据库备份: {backup_path}")
shutil.copy2(db_path, backup_path)

# 连接到数据库
print("连接到数据库...")
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    # 开始事务
    cursor.execute("BEGIN TRANSACTION")
    
    # 步骤1: 创建一个新的list表，结构与updates表相同
    print("创建新的list表...")
    cursor.execute("""
    CREATE TABLE list(
      url TEXT,
      title TEXT,
      scraping_time_r NUM,
      list_time_r NUM,
      update_reason TEXT,
      page INT,
      num INT,
      author TEXT,
      author_link TEXT,
      read_count INT,
      reply_count INT,
      scraping_time NUM,
      list_time NUM,
      source_file TEXT,
      sheet_name INT
    )
    """)
    
    # 步骤2: 复制数据
    print("复制数据从updates表到list表...")
    cursor.execute("""
    INSERT INTO list
    SELECT * FROM updates
    """)
    
    # 步骤3: 删除旧表
    print("删除updates表...")
    cursor.execute("DROP TABLE updates")
    
    # 提交事务
    print("提交更改...")
    conn.commit()
    print("表重命名成功！")
    
except Exception as e:
    # 发生错误时回滚
    conn.rollback()
    print(f"发生错误: {str(e)}")
    print(f"已回滚更改，请使用备份: {backup_path}")
finally:
    # 关闭连接
    conn.close()
    print("数据库连接已关闭") 