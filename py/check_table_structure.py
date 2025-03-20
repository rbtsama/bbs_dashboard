import sqlite3
import os
import sys

def check_table_structure(db_path, table_name):
    """检查表结构并打印列名"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table_name,))
        if not cursor.fetchone():
            print(f"表 {table_name} 不存在")
            return
        
        # 获取表结构
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = cursor.fetchall()
        
        print(f"表 {table_name} 的列:")
        for col in columns:
            col_id, col_name, col_type, not_null, default_val, pk = col
            print(f"  {col_name} ({col_type}){' PRIMARY KEY' if pk else ''}{' NOT NULL' if not_null else ''}")
        
        # 获取表的索引
        try:
            cursor.execute(f"PRAGMA index_list({table_name})")
            indexes = cursor.fetchall()
            
            if indexes:
                print(f"\n表 {table_name} 的索引:")
                for idx in indexes:
                    # SQLite版本不同，返回的列数可能不同
                    idx_name = idx[1]  # 索引名称通常是第二列
                    print(f"  {idx_name}")
                    
                    # 获取索引的列
                    try:
                        cursor.execute(f"PRAGMA index_info({idx_name})")
                        idx_cols = cursor.fetchall()
                        for idx_col in idx_cols:
                            # 索引列信息也可能因SQLite版本不同而有所不同
                            col_name = idx_col[-1]  # 列名通常是最后一列
                            print(f"    - {col_name}")
                    except Exception as e:
                        print(f"    无法获取索引列: {e}")
            else:
                print(f"\n表 {table_name} 没有索引")
        except Exception as e:
            print(f"\n获取索引时出错: {e}")
        
        conn.close()
    except Exception as e:
        print(f"错误: {e}")

if __name__ == "__main__":
    db_path = os.path.join("backend", "db", "forum_data.db")
    
    if len(sys.argv) > 1:
        table_name = sys.argv[1]
        check_table_structure(db_path, table_name)
    else:
        print("请提供表名作为参数") 