#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试数据库更新功能
"""

import os
import sys
import logging
import time
from datetime import datetime
import shutil
import sqlite3

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_update_db")

# 获取项目根目录
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# 将项目根目录添加到模块搜索路径
sys.path.append(project_root)

# 导入需要测试的模块
from update_db import DatabaseUpdater

def create_test_db(db_path):
    """创建测试数据库"""
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        
        # 如果已存在，先删除
        if os.path.exists(db_path):
            os.remove(db_path)
        
        # 创建新数据库
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # 创建一些测试表
            # 创建post_history表
            cursor.execute('''
            CREATE TABLE post_history (
                id INTEGER PRIMARY KEY,
                thread_id TEXT,
                url TEXT,
                title TEXT,
                author TEXT,
                action TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            ''')
            
            # 创建wordcloud_cache表（保护表）
            cursor.execute('''
            CREATE TABLE wordcloud_cache (
                id INTEGER PRIMARY KEY,
                type TEXT,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                version INTEGER DEFAULT 1
            )
            ''')
            
            # 插入一些测试数据
            # post_history表
            cursor.execute('''
            INSERT INTO post_history (thread_id, url, title, author, action)
            VALUES (?, ?, ?, ?, ?)
            ''', ('123', 'https://test.com/t_123.html', '测试帖子', '测试作者', '新发布'))
            
            # wordcloud_cache表
            cursor.execute('''
            INSERT INTO wordcloud_cache (type, data, version)
            VALUES (?, ?, ?)
            ''', ('test', '{"word":"test","value":10}', 1))
            
            conn.commit()
            
        logger.info(f"已创建测试数据库: {db_path}")
        return True
    except Exception as e:
        logger.error(f"创建测试数据库时出错: {str(e)}")
        return False

def test_backup_protected_tables():
    """测试备份保护表功能"""
    # 测试数据库路径
    test_db_path = os.path.join(project_root, "test_data", "test_db.db")
    temp_db_path = os.path.join(project_root, "test_data", "temp_db.db")
    
    # 清理之前的测试文件
    for path in [test_db_path, temp_db_path]:
        if os.path.exists(path):
            try:
                os.remove(path)
                logger.info(f"已删除已存在的测试文件: {path}")
            except Exception as e:
                logger.error(f"删除测试文件时出错: {path}: {str(e)}")
    
    # 创建测试数据库
    if not create_test_db(test_db_path):
        logger.error("创建测试数据库失败，测试终止")
        return False
    
    # 创建更新器实例
    updater = DatabaseUpdater(test_db_path)
    updater.temp_db_path = temp_db_path
    
    # 创建临时数据库
    if not updater.create_temp_database():
        logger.error("创建临时数据库失败，测试终止")
        return False
    
    # 测试备份保护表
    protected_tables = ['wordcloud_cache']
    if not updater.backup_protected_tables(protected_tables):
        logger.error("备份保护表失败")
        return False
    
    # 验证保护表是否已复制到临时数据库
    try:
        with sqlite3.connect(temp_db_path) as conn:
            cursor = conn.cursor()
            
            # 检查表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", ('wordcloud_cache',))
            if not cursor.fetchone():
                logger.error("保护表未被成功复制到临时数据库")
                return False
            
            # 检查数据是否已复制
            cursor.execute("SELECT * FROM wordcloud_cache")
            rows = cursor.fetchall()
            if not rows:
                logger.error("保护表数据未被复制")
                return False
            
            logger.info(f"保护表已成功复制，发现 {len(rows)} 条记录")
            
            # 测试替换数据库
            if not updater.replace_database():
                logger.error("替换数据库失败")
                return False
            
            logger.info("数据库替换成功")
            
            return True
    except Exception as e:
        logger.error(f"验证保护表复制时出错: {str(e)}")
        return False

def test_car_info_import():
    """测试车辆信息导入功能"""
    # 测试数据库路径
    test_db_path = os.path.join(project_root, "test_data", "test_db_car.db")
    temp_db_path = os.path.join(project_root, "test_data", "temp_db_car.db")
    
    # 清理之前的测试文件
    for path in [test_db_path, temp_db_path]:
        if os.path.exists(path):
            try:
                os.remove(path)
                logger.info(f"已删除已存在的测试文件: {path}")
            except Exception as e:
                logger.error(f"删除测试文件时出错: {path}: {str(e)}")
    
    # 创建更新器实例
    updater = DatabaseUpdater(test_db_path)
    updater.temp_db_path = temp_db_path
    
    # 创建临时数据库
    if not updater.create_temp_database():
        logger.error("创建临时数据库失败，测试终止")
        return False
    
    # 测试导入车辆信息
    if not updater.import_car_info_data():
        logger.error("导入车辆信息失败")
        return False
    
    # 验证车辆信息是否已导入
    try:
        # 注意：数据被导入到临时数据库中
        with sqlite3.connect(updater.temp_db_path) as conn:
            cursor = conn.cursor()
            
            # 检查表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", ('car_info',))
            if not cursor.fetchone():
                logger.error("car_info表未被创建")
                return False
            
            # 检查数据是否已导入
            cursor.execute("SELECT * FROM car_info")
            rows = cursor.fetchall()
            if not rows:
                logger.error("car_info表数据未被导入")
                return False
            
            logger.info(f"车辆信息已成功导入，发现 {len(rows)} 条记录")
            
            # 检查thread_id字段是否存在
            cursor.execute("PRAGMA table_info(car_info)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'thread_id' not in columns:
                logger.error("car_info表中不存在thread_id字段")
                return False
            
            logger.info("car_info表中存在thread_id字段")
            
            return True
    except Exception as e:
        logger.error(f"验证车辆信息导入时出错: {str(e)}")
        return False

def run_tests():
    """运行所有测试"""
    # 创建测试数据目录
    test_data_dir = os.path.join(project_root, "test_data")
    os.makedirs(test_data_dir, exist_ok=True)
    
    # 创建测试数据目录结构
    test_data_subdirs = [
        os.path.join(test_data_dir, "processed"),
        os.path.join(test_data_dir, "raw"),
        os.path.join(test_data_dir, "backup")
    ]
    
    for subdir in test_data_subdirs:
        os.makedirs(subdir, exist_ok=True)
        logger.info(f"已创建测试数据子目录: {subdir}")
    
    # 确保data/processed目录存在，用于测试
    data_processed_dir = os.path.join(project_root, "data", "processed")
    os.makedirs(data_processed_dir, exist_ok=True)
    
    # 创建测试用的car_info.csv文件
    test_car_info_path = os.path.join(data_processed_dir, "car_info.csv")
    with open(test_car_info_path, 'w', encoding='utf-8') as f:
        f.write("url,title,year,make,model,miles,price,trade_type,location\n")
        f.write("https://test.com/t_456.html,测试车辆,2022,测试品牌,测试型号,10000,20000,出售,测试地点\n")
    
    logger.info(f"已创建测试用的car_info.csv文件: {test_car_info_path}")
    
    tests = [
        ("备份保护表测试", test_backup_protected_tables),
        ("车辆信息导入测试", test_car_info_import),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"开始测试: {test_name}")
        start_time = time.time()
        
        try:
            result = test_func()
            results[test_name] = result
            end_time = time.time()
            duration = end_time - start_time
            
            if result:
                logger.info(f"测试通过: {test_name} (耗时: {duration:.2f}秒)")
            else:
                logger.error(f"测试失败: {test_name} (耗时: {duration:.2f}秒)")
        except Exception as e:
            logger.error(f"测试执行出错: {test_name}: {str(e)}")
            results[test_name] = False
    
    # 显示测试结果摘要
    logger.info("\n测试结果摘要:")
    all_passed = True
    for test_name, result in results.items():
        status = "通过" if result else "失败"
        logger.info(f"  - {test_name}: {status}")
        
        if not result:
            all_passed = False
    
    if all_passed:
        logger.info("\n所有测试通过!")
        return 0
    else:
        logger.error("\n部分测试失败，请检查日志")
        return 1

if __name__ == "__main__":
    sys.exit(run_tests()) 