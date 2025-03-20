#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
容错机制测试脚本
用于测试数据库管理增强的容错机制
"""

import os
import sys
import logging
import sqlite3
import time
import argparse
from pathlib import Path
from db_manager import DBManager

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), '../logs/test_resilience.log'), encoding='utf-8')
    ]
)
logger = logging.getLogger('test_resilience')

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='容错机制测试工具')
    parser.add_argument('--test-case', type=str, default='all', 
                      choices=['all', 'backup', 'restore', 'migrate', 'replace', 'integrity'],
                      help='要执行的测试用例')
    parser.add_argument('--setup-only', action='store_true', help='仅设置测试环境，不执行测试')
    return parser.parse_args()

def setup_test_environment():
    """设置测试环境"""
    project_root = Path(__file__).parent.parent.absolute()
    
    # 测试数据库路径
    test_db_path = os.path.join(project_root, "db/test_forum_data.db")
    test_temp_db_path = os.path.join(project_root, "db/test_temp_forum_data.db")
    test_backup_dir = os.path.join(project_root, "db/test_backups")
    
    # 确保目录存在
    os.makedirs(os.path.dirname(test_db_path), exist_ok=True)
    os.makedirs(test_backup_dir, exist_ok=True)
    
    # 创建测试数据库
    conn = sqlite3.connect(test_db_path)
    cursor = conn.cursor()
    
    # 创建测试表
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS test_data (
        id INTEGER PRIMARY KEY,
        name TEXT,
        value TEXT
    );
    
    CREATE TABLE IF NOT EXISTS wordcloud_cache (
        id INTEGER PRIMARY KEY,
        cache_key TEXT,
        word_data TEXT,
        created_at TEXT,
        updated_at TEXT
    );
    
    CREATE TABLE IF NOT EXISTS user_data (
        id INTEGER PRIMARY KEY,
        user_id TEXT,
        preferences TEXT,
        created_at TEXT,
        updated_at TEXT
    );
    
    CREATE TABLE IF NOT EXISTS db_maintenance_log (
        id INTEGER PRIMARY KEY,
        operation_type TEXT,
        start_time TEXT,
        end_time TEXT,
        status TEXT,
        details TEXT,
        error_message TEXT
    );
    """)
    
    # 插入一些测试数据
    cursor.executescript("""
    INSERT INTO test_data (name, value) VALUES ('test1', 'value1');
    INSERT INTO test_data (name, value) VALUES ('test2', 'value2');
    
    INSERT INTO wordcloud_cache (cache_key, word_data, created_at, updated_at) 
    VALUES ('test', '{"word":"count"}', '2023-01-01', '2023-01-01');
    
    INSERT INTO user_data (user_id, preferences, created_at, updated_at)
    VALUES ('user1', '{"theme":"dark"}', '2023-01-01', '2023-01-01');
    """)
    
    conn.commit()
    conn.close()
    
    # 创建临时数据库
    conn = sqlite3.connect(test_temp_db_path)
    cursor = conn.cursor()
    
    # 创建测试表，但有不同的数据
    cursor.executescript("""
    CREATE TABLE IF NOT EXISTS test_data (
        id INTEGER PRIMARY KEY,
        name TEXT,
        value TEXT
    );
    
    INSERT INTO test_data (name, value) VALUES ('test3', 'value3');
    INSERT INTO test_data (name, value) VALUES ('test4', 'value4');
    """)
    
    conn.commit()
    conn.close()
    
    logger.info(f"测试环境设置完成：\n主数据库: {test_db_path}\n临时数据库: {test_temp_db_path}\n备份目录: {test_backup_dir}")
    
    return {
        'test_db_path': test_db_path,
        'test_temp_db_path': test_temp_db_path,
        'test_backup_dir': test_backup_dir
    }

def test_backup(db_manager):
    """测试数据库备份功能"""
    logger.info("开始测试备份功能")
    
    try:
        # 执行备份
        backup_path = db_manager.backup_database()
        
        if not backup_path or not os.path.exists(backup_path):
            logger.error("备份失败：未能创建备份文件")
            return False
        
        # 验证备份文件
        conn = sqlite3.connect(backup_path)
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        table_names = [table[0] for table in tables]
        
        # 验证所有表都已备份
        required_tables = ['test_data', 'wordcloud_cache', 'user_data', 'db_maintenance_log']
        missing_tables = [table for table in required_tables if table not in table_names]
        
        if missing_tables:
            logger.error(f"备份验证失败：缺少表 {', '.join(missing_tables)}")
            conn.close()
            return False
        
        # 验证数据
        cursor.execute("SELECT COUNT(*) FROM test_data")
        count = cursor.fetchone()[0]
        
        if count != 2:
            logger.error(f"备份数据验证失败：test_data表应有2条记录，实际有{count}条")
            conn.close()
            return False
        
        conn.close()
        logger.info(f"备份测试成功：{backup_path}")
        return True
    except Exception as e:
        logger.error(f"备份测试时出错：{str(e)}")
        return False

def test_restore(db_manager):
    """测试数据库恢复功能"""
    logger.info("开始测试恢复功能")
    
    try:
        # 先备份当前数据库
        original_backup = db_manager.backup_database()
        
        if not original_backup:
            logger.error("恢复测试准备失败：无法创建原始备份")
            return False
        
        # 修改当前数据库
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        # 删除一些数据
        cursor.execute("DELETE FROM test_data")
        cursor.execute("INSERT INTO test_data (name, value) VALUES ('modified', 'data')")
        conn.commit()
        conn.close()
        
        # 从备份恢复
        restore_result = db_manager.restore_database(original_backup)
        
        if not restore_result:
            logger.error("恢复测试失败：恢复操作返回失败")
            return False
        
        # 验证恢复后的数据
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM test_data")
        count = cursor.fetchone()[0]
        
        if count != 2:
            logger.error(f"恢复数据验证失败：test_data表应有2条记录，实际有{count}条")
            conn.close()
            return False
        
        cursor.execute("SELECT name FROM test_data")
        names = [row[0] for row in cursor.fetchall()]
        
        if 'modified' in names:
            logger.error("恢复数据验证失败：发现应被恢复掉的修改数据")
            conn.close()
            return False
        
        conn.close()
        logger.info("恢复测试成功")
        return True
    except Exception as e:
        logger.error(f"恢复测试时出错：{str(e)}")
        return False

def test_migrate_protected_tables(db_manager):
    """测试保护表迁移功能"""
    logger.info("开始测试保护表迁移功能")
    
    try:
        # 确保临时数据库存在
        if not os.path.exists(db_manager.temp_db_path):
            logger.error(f"迁移测试失败：临时数据库不存在 {db_manager.temp_db_path}")
            return False
        
        # 向主数据库的保护表添加一些数据
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        # 添加一些词云缓存数据
        cursor.execute("DELETE FROM wordcloud_cache")
        cursor.execute("""
        INSERT INTO wordcloud_cache (cache_key, word_data, created_at, updated_at) 
        VALUES ('migration_test', '{"word":"test"}', '2023-01-01', '2023-01-01')
        """)
        
        conn.commit()
        conn.close()
        
        # 执行迁移
        migration_result = db_manager.migrate_protected_tables(db_manager.db_path, db_manager.temp_db_path)
        
        if not migration_result:
            logger.error("迁移测试失败：迁移操作返回失败")
            return False
        
        # 验证迁移后的临时数据库
        conn = sqlite3.connect(db_manager.temp_db_path)
        cursor = conn.cursor()
        
        # 检查保护表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wordcloud_cache'")
        if not cursor.fetchone():
            logger.error("迁移验证失败：目标数据库中不存在迁移的保护表")
            conn.close()
            return False
        
        # 验证迁移的数据
        cursor.execute("SELECT cache_key FROM wordcloud_cache WHERE cache_key='migration_test'")
        if not cursor.fetchone():
            logger.error("迁移验证失败：未找到迁移的数据")
            conn.close()
            return False
        
        conn.close()
        logger.info("保护表迁移测试成功")
        return True
    except Exception as e:
        logger.error(f"保护表迁移测试时出错：{str(e)}")
        return False

def test_replace_database(db_manager):
    """测试数据库替换功能"""
    logger.info("开始测试数据库替换功能")
    
    try:
        # 确保临时数据库存在并有预期的数据
        conn = sqlite3.connect(db_manager.temp_db_path)
        cursor = conn.cursor()
        
        # 重置临时数据库
        cursor.execute("DROP TABLE IF EXISTS test_data")
        cursor.execute("""
        CREATE TABLE test_data (
            id INTEGER PRIMARY KEY,
            name TEXT,
            value TEXT
        )
        """)
        
        # 添加一些不同的测试数据
        cursor.execute("INSERT INTO test_data (name, value) VALUES ('replaced1', 'new1')")
        cursor.execute("INSERT INTO test_data (name, value) VALUES ('replaced2', 'new2')")
        
        conn.commit()
        conn.close()
        
        # 执行保护表迁移和数据库替换
        replace_result = db_manager.replace_database()
        
        if not replace_result:
            logger.error("数据库替换测试失败：替换操作返回失败")
            return False
        
        # 验证替换后的数据库
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        # 检查常规表数据是否已替换
        cursor.execute("SELECT name FROM test_data")
        names = [row[0] for row in cursor.fetchall()]
        
        if 'test1' in names or 'test2' in names:
            logger.error("替换验证失败：仍存在原始数据")
            conn.close()
            return False
        
        if 'replaced1' not in names or 'replaced2' not in names:
            logger.error("替换验证失败：未找到新数据")
            conn.close()
            return False
        
        # 检查保护表是否保留
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wordcloud_cache'")
        if not cursor.fetchone():
            logger.error("替换验证失败：保护表丢失")
            conn.close()
            return False
        
        # 验证保护表数据
        cursor.execute("SELECT cache_key FROM wordcloud_cache WHERE cache_key='migration_test'")
        if not cursor.fetchone():
            logger.error("替换验证失败：保护表数据丢失")
            conn.close()
            return False
        
        conn.close()
        logger.info("数据库替换测试成功")
        return True
    except Exception as e:
        logger.error(f"数据库替换测试时出错：{str(e)}")
        return False

def test_database_integrity(db_manager):
    """测试数据库完整性检查功能"""
    logger.info("开始测试数据库完整性检查功能")
    
    try:
        # 执行完整性检查
        integrity_result = db_manager.verify_database_integrity()
        
        if not integrity_result:
            logger.error("完整性检查测试失败：检查操作返回失败")
            return False
        
        if not integrity_result.get('integrity_ok', False):
            logger.error(f"完整性检查测试失败：数据库完整性检查未通过 {integrity_result}")
            return False
        
        # 故意破坏数据库完整性进行测试
        conn = sqlite3.connect(db_manager.db_path)
        cursor = conn.cursor()
        
        # 删除一个保护表
        cursor.execute("DROP TABLE IF EXISTS db_maintenance_log")
        conn.commit()
        conn.close()
        
        # 再次执行完整性检查
        integrity_result = db_manager.verify_database_integrity()
        
        if integrity_result.get('integrity_ok', False) and not integrity_result.get('missing_protected_tables'):
            logger.error("完整性检查测试失败：未能检测到缺失的保护表")
            return False
        
        logger.info("数据库完整性检查测试成功")
        return True
    except Exception as e:
        logger.error(f"数据库完整性检查测试时出错：{str(e)}")
        return False

def run_all_tests():
    """运行所有测试"""
    # 设置测试环境
    test_env = setup_test_environment()
    
    # 创建测试专用的数据库管理器
    db_manager = DBManager(
        db_path=test_env['test_db_path'],
        backup_dir=test_env['test_backup_dir']
    )
    db_manager.temp_db_path = test_env['test_temp_db_path']
    
    # 运行各测试用例
    results = {}
    
    logger.info("===== 开始运行全部测试 =====")
    
    results['backup'] = test_backup(db_manager)
    results['restore'] = test_restore(db_manager)
    results['migrate'] = test_migrate_protected_tables(db_manager)
    results['replace'] = test_replace_database(db_manager)
    results['integrity'] = test_database_integrity(db_manager)
    
    # 汇总结果
    success_count = sum(1 for result in results.values() if result)
    total_count = len(results)
    
    logger.info(f"===== 测试完成 =====")
    logger.info(f"总测试用例: {total_count}")
    logger.info(f"通过用例: {success_count}")
    logger.info(f"失败用例: {total_count - success_count}")
    
    for test_name, result in results.items():
        logger.info(f"{test_name}: {'通过' if result else '失败'}")
    
    return success_count == total_count

def main():
    """主函数"""
    args = parse_args()
    
    # 设置测试环境
    test_env = setup_test_environment()
    
    if args.setup_only:
        logger.info("仅设置测试环境，测试结束")
        return 0
    
    # 创建测试专用的数据库管理器
    db_manager = DBManager(
        db_path=test_env['test_db_path'],
        backup_dir=test_env['test_backup_dir']
    )
    db_manager.temp_db_path = test_env['test_temp_db_path']
    
    success = False
    
    # 根据指定的测试用例执行
    if args.test_case == 'all':
        success = run_all_tests()
    elif args.test_case == 'backup':
        success = test_backup(db_manager)
    elif args.test_case == 'restore':
        success = test_restore(db_manager)
    elif args.test_case == 'migrate':
        success = test_migrate_protected_tables(db_manager)
    elif args.test_case == 'replace':
        success = test_replace_database(db_manager)
    elif args.test_case == 'integrity':
        success = test_database_integrity(db_manager)
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main()) 