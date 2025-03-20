#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
数据库回滚脚本

此脚本用于在数据库更新失败时从备份恢复数据库。
它会查找最新的"更新前备份"并用它替换当前数据库。

用法:
    python rollback_db.py [--force]

选项:
    --force  强制执行回滚，即使没有检测到更新失败也执行
"""

import os
import sys
import time
import sqlite3
import shutil
import glob
import json
import argparse
import logging
from datetime import datetime

# 配置日志记录
log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'logs')
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, f"db_rollback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

# 数据库目录和文件
DB_DIR = 'backend/db'
DB_FILE = os.path.join(DB_DIR, 'forum_data.db')
BACKUP_DIR = 'backup/db'

def get_latest_backup(prefix="before_update_"):
    """
    获取最新的数据库备份
    
    Args:
        prefix: 备份文件前缀，默认为"before_update_"，用于筛选更新前的备份
        
    Returns:
        最新备份文件的路径，如果没有找到则返回None
    """
    if not os.path.exists(BACKUP_DIR):
        logging.error(f"备份目录不存在: {BACKUP_DIR}")
        return None
        
    # 查找所有匹配前缀的备份文件
    backup_files = glob.glob(os.path.join(BACKUP_DIR, f"{prefix}*.db"))
    
    if not backup_files:
        logging.error(f"未找到前缀为'{prefix}'的备份文件")
        return None
        
    # 按照文件修改时间排序
    backup_files.sort(key=os.path.getmtime, reverse=True)
    
    # 返回最新的备份文件
    latest_backup = backup_files[0]
    logging.info(f"找到最新备份文件: {latest_backup}")
    return latest_backup

def check_db_integrity(db_path):
    """
    检查数据库文件的完整性
    
    Args:
        db_path: 数据库文件路径
        
    Returns:
        如果数据库完整返回True，否则返回False
    """
    if not os.path.exists(db_path):
        logging.error(f"数据库文件不存在: {db_path}")
        return False
        
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 执行完整性检查
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()[0]
        
        conn.close()
        
        if result == "ok":
            logging.info(f"数据库完整性检查通过: {db_path}")
            return True
        else:
            logging.error(f"数据库完整性检查失败: {db_path}, 结果: {result}")
            return False
    except Exception as e:
        logging.error(f"检查数据库完整性时发生错误: {str(e)}")
        return False

def rollback_database(force=False):
    """
    从最新的备份恢复数据库
    
    Args:
        force: 如果为True，即使没有检测到更新失败也执行回滚
        
    Returns:
        成功返回True，失败返回False
    """
    # 检查是否需要回滚
    if not force:
        # 检查更新状态文件
        status_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'tmp', 'db_update_status.json')
        if os.path.exists(status_file):
            try:
                with open(status_file, 'r', encoding='utf-8') as f:
                    status = json.load(f)
                
                # 如果更新成功或部分成功，不需要回滚
                if status.get('status') in ['success', 'partial_success']:
                    logging.info("最近的更新状态为成功或部分成功，不需要回滚")
                    return False
            except Exception as e:
                logging.warning(f"读取更新状态文件失败: {str(e)}")
    
    # 获取最新的备份
    latest_backup = get_latest_backup()
    if not latest_backup:
        logging.error("未找到可用的备份文件，无法执行回滚")
        return False
    
    # 检查备份的完整性
    if not check_db_integrity(latest_backup):
        logging.error("备份文件完整性检查失败，不执行回滚")
        return False
    
    # 创建当前数据库的备份，以防需要恢复
    if os.path.exists(DB_FILE):
        rollback_backup = os.path.join(BACKUP_DIR, f"before_rollback_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
        try:
            shutil.copy2(DB_FILE, rollback_backup)
            logging.info(f"已创建回滚前的备份: {rollback_backup}")
        except Exception as e:
            logging.warning(f"创建回滚前备份失败: {str(e)}")
    
    # 执行回滚
    try:
        # 如果数据库文件正在使用，可能需要等待
        max_attempts = 3
        attempts = 0
        success = False
        
        while attempts < max_attempts and not success:
            try:
                if os.path.exists(DB_FILE):
                    os.remove(DB_FILE)
                shutil.copy2(latest_backup, DB_FILE)
                success = True
            except Exception as e:
                attempts += 1
                logging.warning(f"回滚尝试 {attempts}/{max_attempts} 失败: {str(e)}")
                time.sleep(2)  # 等待2秒后重试
        
        if success:
            logging.info(f"数据库已成功回滚到: {latest_backup}")
            return True
        else:
            logging.error(f"在 {max_attempts} 次尝试后回滚失败")
            return False
    except Exception as e:
        logging.error(f"执行回滚时发生错误: {str(e)}")
        return False

def main():
    parser = argparse.ArgumentParser(description="数据库回滚工具")
    parser.add_argument('--force', action='store_true', help='强制执行回滚，即使没有检测到更新失败也执行')
    args = parser.parse_args()
    
    logging.info("开始执行数据库回滚")
    
    # 确保备份目录存在
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # 执行回滚
    success = rollback_database(force=args.force)
    
    if success:
        logging.info("数据库回滚成功完成")
        return 0
    else:
        logging.error("数据库回滚失败")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 