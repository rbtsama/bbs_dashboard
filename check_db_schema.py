import sqlite3
import os

# 设置路径
DB_PATH = "F:/pj/bbs_data/backend/db/forum_data.db"

def main():
    """检查数据库表结构"""
    print(f"连接到数据库: {DB_PATH}")
    
    if not os.path.exists(DB_PATH):
        print(f"错误: 数据库文件不存在: {DB_PATH}")
        return
        
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # 获取所有表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    # 打印每个表的结构
    for table in tables:
        table_name = table[0]
        print(f"\n表 {table_name} 的结构:")
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        for col in columns:
            print(f"- {col[1]} ({col[2]})")
    
    conn.close()

if __name__ == "__main__":
    main() 