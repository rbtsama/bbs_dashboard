import sqlite3
import os
import sys
import json

def check_db_structure(db_path):
    """检查数据库结构"""
    try:
        if not os.path.exists(db_path):
            print(f"数据库文件不存在: {db_path}")
            return False
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        if not tables:
            print("数据库中没有表")
            return False
        
        print(f"数据库文件: {db_path}")
        print(f"共有 {len(tables)} 个表:")
        
        for table in tables:
            table_name = table[0]
            print(f"\n表名: {table_name}")
            
            # 获取表结构
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            if columns:
                print("  列信息:")
                for col in columns:
                    col_id, col_name, col_type, col_notnull, col_default, col_pk = col
                    print(f"    {col_name} ({col_type}){' PRIMARY KEY' if col_pk else ''}{' NOT NULL' if col_notnull else ''}{f' DEFAULT {col_default}' if col_default is not None else ''}")
                
                # 获取表的索引
                try:
                    cursor.execute(f"PRAGMA index_list({table_name})")
                    indexes = cursor.fetchall()
                    
                    if indexes:
                        print("  索引:")
                        for idx in indexes:
                            idx_name = idx[1]
                            is_unique = "唯一索引" if idx[2] else "普通索引"
                            
                            try:
                                # 获取索引的列
                                cursor.execute(f"PRAGMA index_info({idx_name})")
                                index_columns = cursor.fetchall()
                                
                                if index_columns:
                                    col_names = []
                                    for idx_col in index_columns:
                                        try:
                                            col_pos = idx_col[2]
                                            col_names.append(f"列{col_pos}")
                                        except:
                                            col_names.append("未知列")
                                    
                                    print(f"    {idx_name}: {is_unique} - 列: {', '.join(col_names)}")
                            except Exception as e:
                                print(f"    {idx_name}: {is_unique} - 无法获取列信息: {e}")
                    else:
                        print("  没有索引")
                except Exception as e:
                    print(f"  无法获取索引信息: {e}")
            else:
                print("  表没有列")
        
        # 获取行数信息
        print("\n表行数统计:")
        for table in tables:
            table_name = table[0]
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                row_count = cursor.fetchone()[0]
                print(f"  {table_name}: {row_count} 行")
            except Exception as e:
                print(f"  {table_name}: 无法获取行数 - {e}")
        
        conn.close()
        return True
    except Exception as e:
        print(f"检查数据库结构时出错: {e}")
        return False

def main():
    # 默认数据库路径
    default_db_path = os.path.join("..", "backend", "db", "forum_data.db")
    
    # 从命令行参数获取数据库路径
    db_path = sys.argv[1] if len(sys.argv) > 1 else default_db_path
    
    # 检查数据库结构
    check_db_structure(db_path)

if __name__ == "__main__":
    main() 