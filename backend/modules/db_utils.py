"""
数据库工具模块，提供统一的数据库连接和查询功能
"""

import sqlite3
import os
import logging
from typing import List, Dict, Any, Optional, Tuple, Union
import time
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("db_utils")

# 数据库默认配置
DEFAULT_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'db', 'forum_data.db')

# 最大重试次数
MAX_RETRIES = 3

def dict_factory(cursor, row):
    """
    将SQLite查询结果转换为字典
    
    Args:
        cursor: SQLite游标对象
        row: 查询结果行
        
    Returns:
        dict: 字典形式的查询结果行
    """
    result = {}
    for idx, col in enumerate(cursor.description):
        result[col[0]] = row[idx]
    return result

def get_db_connection(db_path: str = None) -> sqlite3.Connection:
    """
    获取数据库连接
    
    Args:
        db_path: 数据库文件路径，默认使用DEFAULT_DB_PATH
        
    Returns:
        sqlite3.Connection: 数据库连接对象
    """
    # 如果未提供路径，使用默认路径
    if db_path is None:
        db_path = os.environ.get('DATABASE_PATH', DEFAULT_DB_PATH)
    
    # 确保目录存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    # 连接数据库
    conn = sqlite3.connect(db_path)
    
    # 设置行工厂，返回字典类型结果
    conn.row_factory = dict_factory
    
    # 开启外键约束
    conn.execute("PRAGMA foreign_keys = ON")
    
    return conn

def execute_query(query: str, params: tuple = None, db_path: str = None) -> List[Dict[str, Any]]:
    """
    执行查询并返回结果
    
    Args:
        query: SQL查询语句
        params: 查询参数
        db_path: 数据库文件路径
        
    Returns:
        List[Dict[str, Any]]: 查询结果列表
    """
    result = []
    retries = 0
    
    while retries < MAX_RETRIES:
        try:
            conn = get_db_connection(db_path)
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            result = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return result
        except sqlite3.Error as e:
            logger.error(f"数据库查询出错 (尝试 {retries+1}/{MAX_RETRIES}): {str(e)}")
            retries += 1
            if retries < MAX_RETRIES:
                time.sleep(1)  # 重试前等待
            else:
                logger.error(f"查询失败，已达到最大重试次数: {query}")
                raise
        finally:
            if 'conn' in locals() and conn:
                conn.close()
    
    return result

def execute_update(query: str, params: tuple = None, db_path: str = None) -> int:
    """
    执行更新操作并返回受影响的行数
    
    Args:
        query: SQL更新语句
        params: 查询参数
        db_path: 数据库文件路径
        
    Returns:
        int: 受影响的行数
    """
    affected_rows = 0
    retries = 0
    
    while retries < MAX_RETRIES:
        try:
            conn = get_db_connection(db_path)
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
                
            affected_rows = cursor.rowcount
            conn.commit()
            conn.close()
            return affected_rows
        except sqlite3.Error as e:
            logger.error(f"数据库更新出错 (尝试 {retries+1}/{MAX_RETRIES}): {str(e)}")
            retries += 1
            if retries < MAX_RETRIES:
                time.sleep(1)  # 重试前等待
            else:
                logger.error(f"更新失败，已达到最大重试次数: {query}")
                raise
        finally:
            if 'conn' in locals() and conn:
                conn.close()
    
    return affected_rows

def get_table_info(table_name: str, db_path: str = None) -> List[Dict[str, Any]]:
    """
    获取表结构信息
    
    Args:
        table_name: 表名
        db_path: 数据库文件路径
        
    Returns:
        List[Dict[str, Any]]: 表结构信息
    """
    query = f"PRAGMA table_info({table_name})"
    return execute_query(query, db_path=db_path)

def table_exists(table_name: str, db_path: str = None) -> bool:
    """
    检查表是否存在
    
    Args:
        table_name: 表名
        db_path: 数据库文件路径
        
    Returns:
        bool: 表是否存在
    """
    query = """
    SELECT name FROM sqlite_master 
    WHERE type='table' AND name=?
    """
    result = execute_query(query, (table_name,), db_path)
    return len(result) > 0

def get_all_tables(db_path: str = None) -> List[str]:
    """
    获取所有表名
    
    Args:
        db_path: 数据库文件路径
        
    Returns:
        List[str]: 表名列表
    """
    query = """
    SELECT name FROM sqlite_master 
    WHERE type='table' 
    ORDER BY name
    """
    result = execute_query(query, db_path=db_path)
    return [row['name'] for row in result]

def init_db():
    """初始化数据库表"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()

        # 创建thread_follow表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS thread_follow (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            thread_id TEXT NOT NULL,
            url TEXT NOT NULL,
            title TEXT,
            author TEXT,
            author_link TEXT,
            days_old INTEGER DEFAULT 0,
            last_active INTEGER DEFAULT 0,
            read_count INTEGER DEFAULT 0,
            reply_count INTEGER DEFAULT 0,
            follow_status TEXT CHECK(follow_status IN ('followed', 'my_thread', 'not_followed')) DEFAULT 'not_followed',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """)

        # 创建索引
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_thread_follow_thread_id ON thread_follow(thread_id)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_thread_follow_url ON thread_follow(url)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_thread_follow_status ON thread_follow(follow_status)")

        conn.commit()
        conn.close()
        logger.info("数据库表初始化成功")
    except Exception as e:
        logger.error(f"数据库表初始化失败: {str(e)}")
        raise

def insert_test_data():
    """此功能已禁用，不再生成测试数据"""
    print("系统已禁用测试数据生成功能")
    return True

# 在模块导入时初始化数据库
init_db()
insert_test_data() 