#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库初始化脚本
用于创建和初始化数据库文件及保护表结构
"""

import os
import sys
import sqlite3
import logging
from pathlib import Path
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), '../logs/db_init.log'), encoding='utf-8')
    ]
)
logger = logging.getLogger('db_init')

def init_database():
    """初始化数据库"""
    # 获取项目根目录
    project_root = Path(__file__).parent.parent.absolute()
    
    # 数据库路径
    db_path = os.path.join(project_root, "db/forum_data.db")
    # SQL文件路径
    sql_path = os.path.join(project_root, "sql/init_protected_tables.sql")
    
    # 确保数据库目录和日志目录存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    os.makedirs(os.path.join(project_root, "logs"), exist_ok=True)
    
    # 检查SQL文件是否存在
    if not os.path.exists(sql_path):
        logger.error(f"SQL文件不存在: {sql_path}")
        return False

    try:
        # 连接到数据库（如果不存在则创建）
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 读取SQL文件内容
        with open(sql_path, 'r', encoding='utf-8') as f:
            sql_script = f.read()
        
        # 执行SQL脚本
        cursor.executescript(sql_script)
        
        # 提交事务
        conn.commit()
        
        # 获取已创建的表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        # 记录初始化状态到维护记录表
        if 'db_maintenance_log' in table_names:
            insert_sql = """
            INSERT INTO db_maintenance_log 
            (operation_type, start_time, end_time, status, details) 
            VALUES (?, ?, ?, ?, ?)
            """
            cursor.execute(
                insert_sql, 
                ('初始化数据库', time.strftime('%Y-%m-%d %H:%M:%S'), 
                 time.strftime('%Y-%m-%d %H:%M:%S'), '完成', 
                 f'已创建表: {", ".join(table_names)}')
            )
            conn.commit()
        
        # 关闭连接
        conn.close()
        
        logger.info(f"数据库初始化成功: {db_path}")
        logger.info(f"已执行SQL文件: {sql_path}")
        logger.info(f"已创建表: {', '.join(table_names)}")
        return True
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        return False

def check_database_structure():
    """检查数据库结构"""
    project_root = Path(__file__).parent.parent.absolute()
    db_path = os.path.join(project_root, "db/forum_data.db")
    
    if not os.path.exists(db_path):
        logger.warning(f"数据库文件不存在: {db_path}")
        return False
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        logger.info(f"数据库包含以下表: {', '.join(table_names)}")
        
        # 检查保护表是否存在
        protected_tables = ['wordcloud_cache', 'user_data', 'db_maintenance_log']
        missing_tables = [table for table in protected_tables if table not in table_names]
        
        if missing_tables:
            logger.warning(f"数据库中缺少以下保护表: {', '.join(missing_tables)}")
            return False
        
        # 检查各表的列结构
        for table in table_names:
            cursor.execute(f"PRAGMA table_info({table})")
            columns = cursor.fetchall()
            column_info = [f"{col[1]}({col[2]})" for col in columns]
            logger.info(f"表 {table} 结构: {', '.join(column_info)}")
        
        conn.close()
        logger.info("数据库结构检查完成")
        return True
    except Exception as e:
        logger.error(f"检查数据库结构时出错: {str(e)}")
        return False

if __name__ == "__main__":
    # 如果数据库文件不存在，则初始化
    project_root = Path(__file__).parent.parent.absolute()
    db_path = os.path.join(project_root, "db/forum_data.db")
    
    if not os.path.exists(db_path):
        logger.info("数据库文件不存在，开始初始化...")
        init_result = init_database()
        if init_result:
            logger.info("数据库初始化成功")
        else:
            logger.error("数据库初始化失败")
            sys.exit(1)
    else:
        logger.info(f"数据库文件已存在: {db_path}")
        # 检查数据库结构
        if not check_database_structure():
            logger.warning("数据库结构不完整，尝试重新初始化保护表...")
            init_result = init_database()
            if init_result:
                logger.info("数据库保护表初始化成功")
            else:
                logger.error("数据库保护表初始化失败")
    
    # 检查最终数据库结构
    check_database_structure() 