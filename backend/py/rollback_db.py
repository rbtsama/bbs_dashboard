#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库回滚脚本
用于在数据库更新失败时恢复到最近一次可用状态
"""

import os
import sys
import logging
import argparse
from pathlib import Path
from db_manager import DBManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), '../logs/db_rollback.log'), encoding='utf-8')
    ]
)
logger = logging.getLogger('db_rollback')

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='数据库回滚工具')
    parser.add_argument('--specific-backup', type=str, help='使用指定的备份文件进行恢复')
    parser.add_argument('--check-only', action='store_true', help='仅检查数据库完整性，不执行回滚')
    parser.add_argument('--force', action='store_true', help='强制回滚，即使数据库完整性检查通过')
    return parser.parse_args()

def main():
    """主函数"""
    args = parse_args()
    
    try:
        # 创建数据库管理器
        db_manager = DBManager()
        
        # 记录开始
        logger.info("启动数据库回滚过程")
        
        # 检查数据库完整性
        integrity_result = db_manager.verify_database_integrity()
        
        if args.check_only:
            # 仅检查模式，不执行回滚
            logger.info(f"数据库完整性检查结果: {integrity_result}")
            if integrity_result.get('integrity_ok', False):
                logger.info("数据库完整性检查通过")
                return 0
            else:
                logger.warning("数据库完整性检查失败，建议执行回滚")
                return 1
        
        # 决定是否需要回滚
        need_rollback = args.force or not integrity_result.get('integrity_ok', False) or integrity_result.get('missing_protected_tables')
        
        if not need_rollback:
            logger.info("数据库状态良好，无需回滚")
            return 0
        
        # 执行回滚
        logger.info("开始执行数据库回滚")
        
        # 如果指定了特定备份，使用指定备份
        backup_path = args.specific_backup
        
        # 执行恢复
        restore_result = db_manager.restore_database(backup_path)
        
        if restore_result:
            logger.info("数据库回滚成功")
            
            # 再次验证数据库完整性
            new_integrity = db_manager.verify_database_integrity()
            if new_integrity.get('integrity_ok', False):
                logger.info("回滚后数据库完整性检查通过")
            else:
                logger.warning("回滚后数据库完整性检查失败，可能需要手动干预")
            
            return 0
        else:
            logger.error("数据库回滚失败")
            return 1
        
    except Exception as e:
        logger.error(f"数据库回滚过程中出现错误: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 