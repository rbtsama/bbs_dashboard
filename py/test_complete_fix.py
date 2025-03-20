#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试所有修复的组件
"""

import os
import sys
import logging
import time
from datetime import datetime
import importlib.util
import subprocess

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_complete_fix")

# 获取项目根目录
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# 将项目根目录添加到模块搜索路径
sys.path.append(project_root)

def check_module_importable(module_name):
    """检查模块是否可导入"""
    try:
        importlib.import_module(module_name)
        logger.info(f"成功导入模块 {module_name}")
        return True
    except ImportError as e:
        logger.error(f"导入模块 {module_name} 失败: {str(e)}")
        return False

def test_analyze_data_function():
    """测试analyze_data函数是否可以正常使用"""
    try:
        # 导入函数
        from analysis import analyze_data
        
        logger.info("成功导入analyze_data函数")
        
        # 执行函数，设置debug=True以获取更多日志信息
        result = analyze_data(debug=True)
        
        if result:
            logger.info("analyze_data函数执行成功")
            return True
        else:
            logger.error("analyze_data函数执行失败")
            return False
    except ImportError as e:
        logger.error(f"导入analyze_data函数失败: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"测试过程中发生其他错误: {str(e)}")
        return False

def test_import_car_info_data():
    """测试car_info导入功能"""
    try:
        # 导入DatabaseUpdater
        from update_db import DatabaseUpdater
        
        # 创建临时测试数据库
        test_db_path = os.path.join(project_root, "test_data", "test_complete_fix.db")
        temp_db_path = os.path.join(project_root, "test_data", "temp_complete_fix.db")
        
        # 清理之前的测试文件
        for path in [test_db_path, temp_db_path]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                    logger.info(f"已删除已存在的测试文件: {path}")
                except Exception as e:
                    logger.error(f"删除测试文件时出错: {path}: {str(e)}")
        
        # 确保测试数据存在
        test_data_dir = os.path.join(project_root, "test_data")
        os.makedirs(test_data_dir, exist_ok=True)
        
        data_processed_dir = os.path.join(project_root, "data", "processed")
        os.makedirs(data_processed_dir, exist_ok=True)
        
        test_car_info_path = os.path.join(data_processed_dir, "car_info.csv")
        if not os.path.exists(test_car_info_path):
            with open(test_car_info_path, 'w', encoding='utf-8') as f:
                f.write("url,title,year,make,model,miles,price,trade_type,location\n")
                f.write("https://test.com/t_456.html,测试车辆,2022,测试品牌,测试型号,10000,20000,出售,测试地点\n")
                logger.info(f"创建测试用的car_info.csv文件: {test_car_info_path}")
        
        # 创建更新器实例
        updater = DatabaseUpdater(test_db_path)
        updater.temp_db_path = temp_db_path
        
        # 创建临时数据库
        if not updater.create_temp_database():
            logger.error("创建临时数据库失败，测试终止")
            return False
        
        # 测试导入车辆信息
        logger.info("开始测试导入车辆信息功能")
        result = updater.import_car_info_data()
        
        if result:
            logger.info("car_info导入功能测试通过")
            return True
        else:
            logger.error("car_info导入功能测试失败")
            return False
    except Exception as e:
        logger.error(f"测试car_info导入功能时出错: {str(e)}")
        return False

def test_backup_protected_tables():
    """测试备份保护表功能"""
    try:
        # 导入DatabaseUpdater
        from update_db import DatabaseUpdater
        import sqlite3
        
        # 测试数据库路径
        test_db_path = os.path.join(project_root, "test_data", "test_backup_fix.db")
        temp_db_path = os.path.join(project_root, "test_data", "temp_backup_fix.db")
        
        # 清理之前的测试文件
        for path in [test_db_path, temp_db_path]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                    logger.info(f"已删除已存在的测试文件: {path}")
                except Exception as e:
                    logger.error(f"删除测试文件时出错: {path}: {str(e)}")
        
        # 创建测试数据库
        logger.info("创建测试数据库")
        os.makedirs(os.path.dirname(test_db_path), exist_ok=True)
        
        # 创建新数据库
        with sqlite3.connect(test_db_path) as conn:
            cursor = conn.cursor()
            
            # 创建wordcloud_cache表（保护表）
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS wordcloud_cache (
                id INTEGER PRIMARY KEY,
                type TEXT,
                data TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                version INTEGER DEFAULT 1
            )
            ''')
            
            # 插入一些测试数据
            cursor.execute('''
            INSERT INTO wordcloud_cache (type, data, version)
            VALUES (?, ?, ?)
            ''', ('test', '{"word":"test","value":10}', 1))
            
            conn.commit()
            
        logger.info(f"已创建测试数据库: {test_db_path}")
        
        # 创建更新器实例
        updater = DatabaseUpdater(test_db_path)
        updater.temp_db_path = temp_db_path
        
        # 创建临时数据库
        if not updater.create_temp_database():
            logger.error("创建临时数据库失败，测试终止")
            return False
        
        # 测试备份保护表
        protected_tables = ['wordcloud_cache']
        logger.info(f"测试备份保护表: {', '.join(protected_tables)}")
        
        result = updater.backup_protected_tables(protected_tables)
        
        if result:
            logger.info("备份保护表功能测试通过")
            return True
        else:
            logger.error("备份保护表功能测试失败")
            return False
    except Exception as e:
        logger.error(f"测试备份保护表功能时出错: {str(e)}")
        return False

def test_database_replace():
    """测试数据库替换功能"""
    try:
        # 导入DatabaseUpdater
        from update_db import DatabaseUpdater
        import sqlite3
        
        # 测试数据库路径
        test_db_path = os.path.join(project_root, "test_data", "test_replace_fix.db")
        temp_db_path = os.path.join(project_root, "test_data", "temp_replace_fix.db")
        
        # 清理之前的测试文件
        for path in [test_db_path, temp_db_path]:
            if os.path.exists(path):
                try:
                    os.remove(path)
                    logger.info(f"已删除已存在的测试文件: {path}")
                except Exception as e:
                    logger.error(f"删除测试文件时出错: {path}: {str(e)}")
        
        # 创建测试数据库
        with sqlite3.connect(test_db_path) as conn:
            cursor = conn.cursor()
            # 创建测试表
            cursor.execute('''
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value INTEGER
            )
            ''')
            # 插入测试数据
            cursor.execute('''
            INSERT INTO test_table (name, value)
            VALUES (?, ?)
            ''', ('test_name', 123))
            conn.commit()
            
        logger.info(f"已创建源测试数据库: {test_db_path}")
        
        # 创建临时数据库
        with sqlite3.connect(temp_db_path) as conn:
            cursor = conn.cursor()
            # 创建测试表
            cursor.execute('''
            CREATE TABLE test_table (
                id INTEGER PRIMARY KEY,
                name TEXT,
                value INTEGER
            )
            ''')
            # 插入测试数据
            cursor.execute('''
            INSERT INTO test_table (name, value)
            VALUES (?, ?)
            ''', ('temp_name', 456))
            conn.commit()
            
        logger.info(f"已创建临时测试数据库: {temp_db_path}")
        
        # 创建更新器实例
        updater = DatabaseUpdater(test_db_path)
        updater.temp_db_path = temp_db_path
        
        # 测试替换数据库
        logger.info("测试替换数据库功能")
        result = updater.replace_database()
        
        if result:
            # 验证替换后的数据库内容
            with sqlite3.connect(test_db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT name, value FROM test_table")
                row = cursor.fetchone()
                
                if row and row[0] == 'temp_name' and row[1] == 456:
                    logger.info("替换数据库功能测试通过")
                    return True
                else:
                    logger.error("替换后的数据库内容不正确")
                    return False
        else:
            logger.error("替换数据库功能测试失败")
            return False
    except Exception as e:
        logger.error(f"测试替换数据库功能时出错: {str(e)}")
        return False

def run_tests():
    """运行所有测试"""
    # 确保测试数据目录存在
    test_data_dir = os.path.join(project_root, "test_data")
    os.makedirs(test_data_dir, exist_ok=True)
    
    # 测试项
    tests = [
        ("分析函数导入和执行", test_analyze_data_function),
        ("车辆信息导入功能", test_import_car_info_data),
        ("备份保护表功能", test_backup_protected_tables),
        ("数据库替换功能", test_database_replace)
    ]
    
    # 保存测试结果
    results = {}
    
    # 执行测试
    for test_name, test_func in tests:
        logger.info(f"\n======= 开始测试: {test_name} =======")
        start_time = time.time()
        
        try:
            result = test_func()
            end_time = time.time()
            duration = end_time - start_time
            
            results[test_name] = result
            
            if result:
                logger.info(f"测试通过: {test_name} (耗时: {duration:.2f}秒)")
            else:
                logger.error(f"测试失败: {test_name} (耗时: {duration:.2f}秒)")
        except Exception as e:
            logger.error(f"测试执行出错: {test_name}: {str(e)}")
            results[test_name] = False
    
    # 显示测试结果摘要
    logger.info("\n\n========== 测试结果摘要 ==========")
    all_passed = True
    for test_name, result in results.items():
        status = "通过" if result else "失败"
        logger.info(f"  {test_name}: {status}")
        
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