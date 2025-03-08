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

# 确保数据库目录存在
DB_PATH.parent.mkdir(parents=True, exist_ok=True)

def clean_column_name(name):
    """清理列名，使其适合SQLite"""
    # 移除特殊字符，替换空格为下划线
    return re.sub(r'[^\w]', '_', str(name)).lower()

def drop_all_tables(conn):
    """删除数据库中的所有表"""
    cursor = conn.cursor()
    
    # 获取所有表名
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    
    # 删除每个表
    for table in tables:
        table_name = table[0]
        if table_name != 'sqlite_sequence':  # 跳过sqlite内部表
            print(f"删除表: {table_name}")
            cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
    
    conn.commit()
    print("所有表已删除")

def import_excel_to_db(conn, file_path, table_name):
    """将Excel文件导入到数据库表中"""
    print(f"导入 {file_path} 到表 {table_name}")
    
    # 读取Excel文件
    df = pd.read_excel(file_path)
    
    # 清理列名
    df.columns = [clean_column_name(col) for col in df.columns]
    
    # 确保日期时间列使用正确的格式
    for col in df.columns:
        if 'time' in col.lower() or 'date' in col.lower():
            try:
                df[col] = pd.to_datetime(df[col])
            except:
                pass  # 如果无法转换，保持原样
    
    # 将DataFrame写入SQLite
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    print(f"成功导入 {len(df)} 行到表 {table_name}")

def import_csv_to_db(conn, file_path):
    """将CSV文件导入到数据库，按数据类型分表"""
    print(f"导入 {file_path} 到数据库")
    
    # 读取CSV文件
    df = pd.read_csv(file_path, encoding='utf-8-sig')
    
    # 检查是否有data_category列
    if 'data_category' in df.columns:
        # 按data_category分组导入
        for category, group_df in df.groupby('data_category'):
            # 清理表名
            table_name = clean_column_name(category)
            
            # 清理列名
            group_df.columns = [clean_column_name(col) for col in group_df.columns]
            
            # 处理日期时间列
            for col in group_df.columns:
                if 'time' in col.lower() or 'date' in col.lower():
                    try:
                        # 尝试转换为日期时间格式
                        group_df[col] = pd.to_datetime(group_df[col])
                    except:
                        pass  # 如果无法转换，保持原样
            
            # 将数据写入表
            group_df.to_sql(table_name, conn, if_exists='replace', index=False)
            print(f"成功导入 {len(group_df)} 行到表 {table_name}")
    else:
        # 没有分类，直接导入到一个表
        table_name = 'import_data'
        
        # 清理列名
        df.columns = [clean_column_name(col) for col in df.columns]
        
        # 处理日期时间列
        for col in df.columns:
            if 'time' in col.lower() or 'date' in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col])
                except:
                    pass  # 如果无法转换，保持原样
        
        # 将数据写入表
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f"成功导入 {len(df)} 行到表 {table_name}")

def import_db_to_db(conn, db_path):
    """从另一个SQLite数据库导入数据"""
    print(f"从 {db_path} 导入数据")
    
    # 连接源数据库
    src_conn = sqlite3.connect(str(db_path))
    src_cursor = src_conn.cursor()
    
    # 获取所有表
    src_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = src_cursor.fetchall()
    
    # 导入每个表
    for table in tables:
        table_name = table[0]
        if table_name != 'sqlite_sequence':  # 跳过sqlite内部表
            print(f"导入表: {table_name}")
            
            # 读取源表数据
            df = pd.read_sql(f"SELECT * FROM {table_name}", src_conn)
            
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
    
    src_conn.close()

def main():
    """主函数"""
    print(f"连接到数据库: {DB_PATH}")
    conn = sqlite3.connect(str(DB_PATH))
    
    # 设置数据库连接以正确处理中文
    conn.execute("PRAGMA encoding = 'UTF-8'")
    
    # 清空数据库
    drop_all_tables(conn)
    
    # 导入Excel文件
    if (PROCESSED_DIR / 'post.xlsx').exists():
        import_excel_to_db(conn, PROCESSED_DIR / 'post.xlsx', 'post')
    
    if (PROCESSED_DIR / 'list.xlsx').exists():
        import_excel_to_db(conn, PROCESSED_DIR / 'list.xlsx', 'list')
    
    # 导入CSV或DB文件（优先使用DB）
    if (PROCESSED_DIR / 'import.db').exists():
        import_db_to_db(conn, PROCESSED_DIR / 'import.db')
    elif (PROCESSED_DIR / 'import.csv').exists():
        import_csv_to_db(conn, PROCESSED_DIR / 'import.csv')
    
    # 创建必要的视图
    print("创建数据视图...")
    
    # 先删除旧视图
    conn.execute("DROP VIEW IF EXISTS data_trends")
    
    # 检查表是否存在
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [table[0] for table in cursor.fetchall()]
    
    # 创建data_trends视图，使用存在的表
    view_parts = []
    if 'poststatistics' in tables:
        view_parts.append("SELECT * FROM poststatistics")
    if 'updatestatistics' in tables:
        view_parts.append("SELECT * FROM updatestatistics")
    if 'viewstatistics' in tables:
        view_parts.append("SELECT * FROM viewstatistics")
    
    if view_parts:
        view_query = " UNION ALL ".join(view_parts)
        conn.execute(f"CREATE VIEW data_trends AS {view_query}")
        print("成功创建data_trends视图")
    else:
        print("警告: 未找到统计数据表，无法创建data_trends视图")
    
    # 关闭连接
    conn.commit()
    conn.close()
    
    print("数据库重置完成！")

if __name__ == "__main__":
    main() 