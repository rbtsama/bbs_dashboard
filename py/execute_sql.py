import sqlite3
import os
import sys
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("execute_sql")

def execute_sql_file(db_path, sql_file_path):
    """执行SQL文件"""
    try:
        # 检查文件是否存在
        if not os.path.exists(sql_file_path):
            logger.error(f"SQL文件不存在: {sql_file_path}")
            return False
        
        # 检查数据库目录是否存在
        db_dir = os.path.dirname(db_path)
        os.makedirs(db_dir, exist_ok=True)
        
        # 读取SQL文件内容
        with open(sql_file_path, 'r', encoding='utf-8') as f:
            sql_content = f.read()
        
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 拆分SQL语句并执行
        statements = sql_content.split(';')
        
        for statement in statements:
            statement = statement.strip()
            if statement:
                print(f"执行: {statement}")
                cursor.execute(statement)
        
        conn.commit()
        conn.close()
        
        print("\nSQL文件执行成功！")
        return True
    except Exception as e:
        print(f"\n执行出错: {e}")
        return False

def main():
    # 检查命令行参数
    if len(sys.argv) < 2:
        print("用法: python execute_sql.py <sql_file_path> [db_path]")
        return
    
    # 获取SQL文件路径
    sql_file_path = sys.argv[1]
    
    # 获取数据库路径，如果未提供则使用默认路径
    db_path = sys.argv[2] if len(sys.argv) > 2 else os.path.join("backend", "db", "forum_data.db")
    
    print(f"执行SQL文件: {os.path.abspath(sql_file_path)}")
    print(f"数据库文件: {os.path.abspath(db_path)}")
    
    # 执行SQL文件
    success = execute_sql_file(db_path, sql_file_path)
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main() 