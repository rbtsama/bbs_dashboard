import sqlite3
import os
import shutil
from datetime import datetime

# 数据库路径
SOURCE_DB_PATH = os.path.join(os.path.dirname(__file__), 'instance', 'database.db')
TARGET_DB_PATH = os.path.join(os.path.dirname(__file__), 'db', 'forum_data.db')

def get_db_connection(db_path):
    """获取数据库连接"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_tables(conn):
    """获取数据库中的所有表"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cursor.fetchall()]
    return tables

def backup_database(db_path):
    """备份数据库"""
    backup_path = f"{db_path}.bak_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    shutil.copy2(db_path, backup_path)
    print(f"数据库已备份到: {backup_path}")
    return backup_path

def merge_databases():
    """合并数据库"""
    # 确保两个数据库都存在
    if not os.path.exists(SOURCE_DB_PATH):
        print(f"源数据库不存在: {SOURCE_DB_PATH}")
        return False
        
    if not os.path.exists(TARGET_DB_PATH):
        print(f"目标数据库不存在: {TARGET_DB_PATH}")
        return False
    
    # 备份两个数据库
    backup_database(SOURCE_DB_PATH)
    backup_database(TARGET_DB_PATH)
    
    # 连接数据库
    source_conn = get_db_connection(SOURCE_DB_PATH)
    target_conn = get_db_connection(TARGET_DB_PATH)
    
    # 获取源数据库的表
    source_tables = get_tables(source_conn)
    print(f"源数据库 ({SOURCE_DB_PATH}) 包含以下表: {source_tables}")
    
    # 获取目标数据库的表
    target_tables = get_tables(target_conn)
    print(f"目标数据库 ({TARGET_DB_PATH}) 包含以下表: {target_tables}")
    
    # 为每个源表创建临时内存数据库来导出数据
    temp_conn = sqlite3.connect(':memory:')
    
    # 遍历源数据库中的每个表
    for table in source_tables:
        if table == 'sqlite_sequence':
            continue  # 跳过sqlite内部表
            
        print(f"\n处理表: {table}")
        
        # 获取表结构
        source_cursor = source_conn.cursor()
        source_cursor.execute(f"PRAGMA table_info({table})")
        columns = source_cursor.fetchall()
        
        # 打印表结构
        print(f"表 '{table}' 的结构:")
        for col in columns:
            print(f"- {col[1]} ({col[2]})")
            
        # 获取表中的记录数
        source_cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = source_cursor.fetchone()[0]
        print(f"表 '{table}' 中共有 {count} 条记录")
        
        if count == 0:
            print(f"表 '{table}' 没有数据，跳过导入")
            continue
            
        # 检查目标数据库中是否存在该表
        if table in target_tables:
            print(f"目标数据库中已存在表 '{table}'")
            
            # 检查表结构是否相同
            target_cursor = target_conn.cursor()
            target_cursor.execute(f"PRAGMA table_info({table})")
            target_columns = target_cursor.fetchall()
            
            # 比较列名
            source_column_names = [col[1] for col in columns]
            target_column_names = [col[1] for col in target_columns]
            
            if set(source_column_names) != set(target_column_names):
                print(f"警告: 表 '{table}' 在源数据库和目标数据库中结构不同")
                print(f"源数据库列: {source_column_names}")
                print(f"目标数据库列: {target_column_names}")
                continue
                
            # 获取目标表中的记录数
            target_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            target_count = target_cursor.fetchone()[0]
            print(f"目标数据库中表 '{table}' 有 {target_count} 条记录")
            
            # 询问是否要合并数据
            if target_count > 0:
                print(f"目标表已有数据，将保留现有数据")
                continue
        else:
            # 在目标数据库中创建表
            create_statement = source_conn.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'").fetchone()[0]
            print(f"在目标数据库中创建表: \n{create_statement}")
            target_conn.execute(create_statement)
        
        # 使用临时数据库复制数据
        source_conn.backup(temp_conn)
        
        # 将数据从临时表导入到目标表
        column_list = ", ".join([col[1] for col in columns])
        placeholders = ", ".join(["?" for _ in columns])
        
        # 从源数据库读取数据
        temp_cursor = temp_conn.cursor()
        temp_cursor.execute(f"SELECT {column_list} FROM {table}")
        rows = temp_cursor.fetchall()
        
        # 插入到目标数据库
        target_conn.executemany(f"INSERT INTO {table} ({column_list}) VALUES ({placeholders})", rows)
        print(f"从源表 '{table}' 导入了 {len(rows)} 条记录到目标表")
    
    # 提交更改
    target_conn.commit()
    
    # 关闭连接
    source_conn.close()
    target_conn.close()
    temp_conn.close()
    
    print("\n数据库合并完成")
    return True

def update_config_file():
    """更新配置文件中的数据库路径"""
    config_path = os.path.join(os.path.dirname(__file__), 'config.py')
    if os.path.exists(config_path):
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'DATABASE_PATH' in content:
            new_path = 'os.path.join(os.path.dirname(__file__), "db", "forum_data.db")'
            updated_content = content.replace('os.path.join(os.path.dirname(__file__), "instance", "database.db")', new_path)
            
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(updated_content)
                
            print(f"已更新配置文件中的数据库路径: {config_path}")
        else:
            print(f"配置文件中未找到DATABASE_PATH: {config_path}")
    else:
        print(f"配置文件不存在: {config_path}")

if __name__ == "__main__":
    print("开始合并数据库...")
    if merge_databases():
        # 更新配置文件
        update_config_file()
        print("数据库合并和配置更新成功完成")
    else:
        print("数据库合并失败") 