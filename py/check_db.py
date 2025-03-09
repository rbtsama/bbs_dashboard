import sqlite3
from pathlib import Path

# 设置路径
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / 'backend' / 'db' / 'forum_data.db'

def main():
    """检查数据库中的表和记录数"""
    print(f"连接到数据库: {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()
    
    # 获取所有表和视图
    cursor.execute("SELECT name, type FROM sqlite_master WHERE type='table' OR type='view'")
    objects = cursor.fetchall()
    
    # 打印表和视图
    print("\n数据库对象:")
    for name, type in objects:
        print(f"- {name} ({type})")
    
    # 打印每个表/视图的记录数
    print("\n记录数:")
    for name, type in objects:
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {name}")
            count = cursor.fetchone()[0]
            print(f"- {name}: {count}行")
        except sqlite3.OperationalError as e:
            print(f"- {name}: 无法获取记录数 ({e})")
    
    # 检查日期时间格式
    print("\n日期时间列示例:")
    for name, type in objects:
        if type == 'table':
            # 获取表的列信息
            cursor.execute(f"PRAGMA table_info({name})")
            columns = cursor.fetchall()
            
            # 查找日期时间列
            datetime_columns = [col[1] for col in columns if 'time' in col[1].lower() or 'date' in col[1].lower()]
            
            if datetime_columns:
                print(f"\n表 {name} 的日期时间列:")
                for col in datetime_columns:
                    try:
                        cursor.execute(f"SELECT {col} FROM {name} LIMIT 1")
                        value = cursor.fetchone()[0]
                        print(f"- {col}: {value}")
                    except:
                        print(f"- {col}: 无法获取值")
    
    conn.close()

if __name__ == "__main__":
    main() 