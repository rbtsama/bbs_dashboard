import sqlite3
import pandas as pd
import os
from pathlib import Path
import json
import re

# 设置路径
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / 'backend' / 'db' / 'forum_data.db'
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'
SQL_DIR = BASE_DIR / 'sql'

# 确保数据库目录存在
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def clean_column_name(name):
    """清理列名，使其适合SQLite"""
    # 移除特殊字符，替换空格为下划线
    return re.sub(r'[^\w]', '_', str(name)).lower()

def execute_sql_file(conn, sql_file):
    """执行SQL文件"""
    print(f"\n执行SQL文件: {sql_file}")
    try:
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql_script = f.read()
            
        # 分割SQL语句
        sql_statements = [stmt.strip() for stmt in sql_script.split(';') if stmt.strip()]
        
        # 执行每个语句
        for stmt in sql_statements:
            try:
                conn.execute(stmt)
                print(f"成功执行: {stmt[:100]}...")
            except sqlite3.OperationalError as e:
                print(f"执行语句时出错: {e}\n语句: {stmt}")
        
        conn.commit()
        print("SQL文件执行完成")
    except Exception as e:
        print(f"执行SQL文件时出错: {e}")

def drop_all_tables(conn):
    """删除数据库中的所有表，但保留关注相关表"""
    cursor = conn.cursor()
    
    # 获取所有表名，排除sqlite_sequence和关注相关表
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name != 'sqlite_sequence' AND name != 'thread_follows' AND name != 'follow_history'")
    tables = cursor.fetchall()
    
    # 删除每个表
    for table in tables:
        table_name = table[0]
        try:
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
            print(f"已删除表 {table_name}")
        except sqlite3.OperationalError as e:
            print(f"删除表 {table_name} 时出错: {e}")
    
    conn.commit()

def import_excel_to_db(conn, file_path, table_name):
    """将Excel文件导入到数据库"""
    print(f"\n导入 {file_path} 到表 {table_name}")
    
    try:
        # 读取Excel文件
        df = pd.read_excel(file_path)
        
        # 清理列名
        df.columns = [clean_column_name(col) for col in df.columns]
        
        # 处理日期时间列
        for col in df.columns:
            if 'time' in col.lower() or 'date' in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col])
                except:
                    pass  # 如果无法转换，保持原样
        
        # 写入目标数据库
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f"成功导入 {len(df)} 行到表 {table_name}")
    except Exception as e:
        print(f"导入 {file_path} 时出错: {e}")

def import_csv_to_db(conn, file_path, table_name):
    """将CSV文件导入到数据库"""
    print(f"\n导入 {file_path} 到表 {table_name}")
    
    try:
        # 读取CSV文件
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        
        # 清理列名
        df.columns = [clean_column_name(col) for col in df.columns]
        
        # 处理日期时间列
        for col in df.columns:
            if 'time' in col.lower() or 'date' in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col])
                except:
                    pass  # 如果无法转换，保持原样
        
        # 写入目标数据库
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f"成功导入 {len(df)} 行到表 {table_name}")
    except Exception as e:
        print(f"导入 {file_path} 时出错: {e}")

def process_import_data(conn, df):
    """处理import.csv的数据，将其分配到相应的表中"""
    print("\n处理import.csv数据...")
    
    # 按data_category分组处理数据
    categories = df['data_category'].unique()
    
    for category in categories:
        category_data = df[df['data_category'] == category].copy()
        
        # 删除通用字段
        if 'id' in category_data.columns:
            category_data.drop('id', axis=1, inplace=True)
        if 'data_category' in category_data.columns:
            category_data.drop('data_category', axis=1, inplace=True)
        if 'type' in category_data.columns:
            category_data.drop('type', axis=1, inplace=True)
        
        # 根据不同类别处理数据
        table_name = category
        
        try:
            category_data.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"成功导入 {len(category_data)} 行到表 {table_name}")
        except Exception as e:
            print(f"导入到表 {table_name} 时出错: {e}")

def main():
    """主函数"""
    print(f"连接到数据库: {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    
    # 设置数据库连接以正确处理中文
    conn.execute("PRAGMA encoding = 'UTF-8'")
    
    # 清空数据库
    drop_all_tables(conn)
    
    # 执行create_tables.sql
    if (SQL_DIR / 'create_tables.sql').exists():
        execute_sql_file(conn, SQL_DIR / 'create_tables.sql')
    else:
        print("警告: create_tables.sql文件不存在")
    
    # 导入Excel文件
    if (PROCESSED_DIR / 'post.xlsx').exists():
        import_excel_to_db(conn, PROCESSED_DIR / 'post.xlsx', 'post')
    
    if (PROCESSED_DIR / 'update.xlsx').exists():
        import_excel_to_db(conn, PROCESSED_DIR / 'update.xlsx', 'list')
    
    # 导入car_info.csv文件
    if (PROCESSED_DIR / 'car_info.csv').exists():
        import_csv_to_db(conn, PROCESSED_DIR / 'car_info.csv', 'car_info')
    
    # 导入import.csv文件并处理数据
    if (PROCESSED_DIR / 'import.csv').exists():
        df = pd.read_csv(PROCESSED_DIR / 'import.csv', encoding='utf-8-sig')
        process_import_data(conn, df)
    
    # 创建必要的视图
    print("创建数据视图...")
    
    # 先删除旧视图
    conn.execute("DROP VIEW IF EXISTS data_trends")
    
    # 创建data_trends视图
    view_query = """
    CREATE VIEW data_trends AS
    SELECT * FROM post_statistic
    UNION ALL
    SELECT * FROM update_statistic
    UNION ALL
    SELECT * FROM view_statistic
    """
    conn.execute(view_query)
    print("成功创建data_trends视图")
    
    # 关闭连接
    conn.commit()
    conn.close()
    
    print("数据库重置完成！")

if __name__ == "__main__":
    main() 