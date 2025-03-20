#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
初始化数据库脚本
用于创建数据库结构和初始化保护表
"""

import os
import sys
import sqlite3
import logging
from pathlib import Path

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), "logs", "init_db.log"), encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("init_db")

# 确保日志目录存在
os.makedirs(os.path.join(os.path.dirname(__file__), "logs"), exist_ok=True)

def init_database():
    """初始化数据库"""
    # 获取项目根目录
    project_root = Path(__file__).parent.parent.absolute()
    
    # 数据库路径
    db_path = os.path.join(project_root, "backend/db/forum_data.db")
    # SQL文件路径
    sql_path = os.path.join(project_root, "backend/sql/init_protected_tables.sql")
    
    # 确保数据库目录存在
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
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
        
        # 关闭连接
        conn.close()
        
        logger.info(f"数据库初始化成功: {db_path}")
        logger.info(f"已执行SQL文件: {sql_path}")
        return True
    except Exception as e:
        logger.error(f"数据库初始化失败: {str(e)}")
        return False

def main():
    """主函数"""
    logger.info("开始初始化数据库...")
    if init_database():
        logger.info("数据库初始化完成")
        return 0
    else:
        logger.error("数据库初始化失败")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 