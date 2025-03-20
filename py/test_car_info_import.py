#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试car_info数据导入功能
"""

import os
import sys
import logging
from update_db import DatabaseUpdater

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("test_car_info_import")

def test_car_info_import():
    """测试car_info数据导入功能"""
    try:
        # 获取项目根目录
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        
        # 数据库路径
        db_path = os.path.join(project_root, "backend/db/forum_data.db")
        
        # 初始化数据库更新器
        updater = DatabaseUpdater(db_path)
        
        # 打印数据库路径
        logger.info(f"数据库路径: {db_path}")
        
        # 创建临时数据库
        if not updater.create_temp_database():
            logger.error("创建临时数据库失败")
            return False
        
        # 导入car_info数据
        if not updater.import_car_info_data():
            logger.error("导入car_info数据失败")
            return False
        
        # 替换数据库
        if not updater.replace_database():
            logger.error("替换数据库失败")
            return False
        
        logger.info("car_info数据导入测试完成")
        return True
    
    except Exception as e:
        logger.error(f"测试过程中出错: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_car_info_import()
    if success:
        logger.info("测试成功")
        sys.exit(0)
    else:
        logger.error("测试失败")
        sys.exit(1) 