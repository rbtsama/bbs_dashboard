#!/usr/bin/env python
"""
数据库检查工具 - 专门用于分析数据库结构和数据
"""

import os
import sys
import logging
from pprint import pprint

# 添加当前目录到path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.db_utils import get_db_connection, execute_query

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("db_inspector")

def inspect_database():
    """检查数据库结构"""
    try:
        # 获取所有表
        query = "SELECT name FROM sqlite_master WHERE type='table'"
        tables = execute_query(query)
        
        logger.info(f"数据库中的表: {[t['name'] for t in tables]}")
        
        # 检查import表结构
        query = "PRAGMA table_info(import)"
        columns = execute_query(query)
        logger.info(f"import表的列: {[col['name'] for col in columns]}")
        
        return True
    except Exception as e:
        logger.error(f"检查数据库结构失败: {str(e)}")
        return False

def analyze_import_table():
    """分析import表中的数据"""
    try:
        # 检查data_category字段的所有可能值
        query = """
        SELECT DISTINCT data_category 
        FROM import 
        ORDER BY data_category
        """
        categories = execute_query(query)
        logger.info(f"import表中data_category的不同值: {[cat['data_category'] for cat in categories]}")
        
        # 对每种data_category统计记录数
        for cat in categories:
            category = cat['data_category']
            count_query = f"""
            SELECT COUNT(*) as count 
            FROM import 
            WHERE data_category = '{category}'
            """
            count_result = execute_query(count_query)
            logger.info(f"data_category='{category}'的记录数: {count_result[0]['count']}")
            
            # 获取该类别的示例记录
            sample_query = f"""
            SELECT * 
            FROM import 
            WHERE data_category = '{category}' 
            LIMIT 1
            """
            sample = execute_query(sample_query)
            if sample:
                logger.info(f"data_category='{category}'的示例记录: {sample[0]}")
        
        # 检查发帖统计相关数据
        post_stats_queries = [
            "SELECT COUNT(*) as count FROM import WHERE data_category = 'post_statistics'",
            "SELECT COUNT(*) as count FROM import WHERE data_category = 'post_trend'",
            "SELECT COUNT(*) as count FROM import WHERE type = 'post'"
        ]
        
        for query in post_stats_queries:
            result = execute_query(query)
            logger.info(f"查询 '{query}' 的结果: {result[0]['count']}")
        
        # 检查更新统计相关数据
        update_stats_queries = [
            "SELECT COUNT(*) as count FROM import WHERE data_category = 'update_statistics'",
            "SELECT COUNT(*) as count FROM import WHERE data_category LIKE '%update%'",
            "SELECT COUNT(*) as count FROM import WHERE type IN ('repost', 'reply', 'delete_reply')"
        ]
        
        for query in update_stats_queries:
            result = execute_query(query)
            logger.info(f"查询 '{query}' 的结果: {result[0]['count']}")
        
        # 检查浏览统计相关数据
        view_stats_queries = [
            "SELECT COUNT(*) as count FROM import WHERE data_category = 'view_statistics'",
            "SELECT COUNT(*) as count FROM import WHERE data_category = 'view_trend'",
            "SELECT COUNT(*) as count FROM import WHERE data_category LIKE '%view%'"
        ]
        
        for query in view_stats_queries:
            result = execute_query(query)
            logger.info(f"查询 '{query}' 的结果: {result[0]['count']}")
            
        # 检查type字段的所有可能值
        query = """
        SELECT DISTINCT type 
        FROM import 
        ORDER BY type
        """
        types = execute_query(query)
        logger.info(f"import表中type的不同值: {[t['type'] for t in types]}")
        
        return True
    except Exception as e:
        logger.error(f"分析import表失败: {str(e)}")
        return False

def find_trend_data():
    """尝试找出趋势数据的正确查询方式"""
    try:
        # 查找可能包含趋势数据的记录
        possible_trend_queries = [
            "SELECT * FROM import WHERE data_category LIKE '%trend%' LIMIT 2",
            "SELECT * FROM import WHERE data_category LIKE '%statistics%' LIMIT 2",
            "SELECT * FROM import WHERE type = 'post' LIMIT 2",
            "SELECT * FROM import WHERE type IN ('repost', 'reply', 'delete_reply') LIMIT 2"
        ]
        
        for i, query in enumerate(possible_trend_queries):
            result = execute_query(query)
            logger.info(f"可能的趋势数据查询 {i+1}: {query}")
            for record in result:
                logger.info(f"示例记录: {record}")
            logger.info("-" * 50)
        
        return True
    except Exception as e:
        logger.error(f"查找趋势数据失败: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("======= 开始检查数据库 =======")
    
    # 检查数据库结构
    if not inspect_database():
        logger.error("检查数据库结构失败，退出")
        sys.exit(1)
    
    # 分析import表
    if not analyze_import_table():
        logger.error("分析import表失败，退出")
        sys.exit(1)
    
    # 尝试找出趋势数据
    if not find_trend_data():
        logger.error("查找趋势数据失败，退出")
        sys.exit(1)
    
    logger.info("======= 数据库检查完成 =======") 