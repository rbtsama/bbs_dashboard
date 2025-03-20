#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试数据分析功能
"""

import os
import sys
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_analysis")

# 获取项目根目录
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
# 将项目根目录添加到模块搜索路径
sys.path.append(project_root)

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

def test_direct_execution():
    """测试直接执行analysis.py脚本"""
    try:
        # 构建脚本路径
        script_path = os.path.join(project_root, "py", "analysis.py")
        
        # 检查脚本是否存在
        if not os.path.exists(script_path):
            logger.error(f"分析脚本不存在: {script_path}")
            return False
        
        logger.info(f"正在执行分析脚本: {script_path}")
        
        # 执行脚本
        result = os.system(f"python {script_path}")
        
        if result == 0:
            logger.info("分析脚本执行成功")
            return True
        else:
            logger.error(f"分析脚本执行失败，返回码: {result}")
            return False
    except Exception as e:
        logger.error(f"测试过程中发生错误: {str(e)}")
        return False

def run_tests():
    """运行所有测试"""
    # 运行测试
    tests = [
        ("测试analyze_data函数", test_analyze_data_function),
        ("测试直接执行analysis.py", test_direct_execution)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        logger.info(f"开始测试: {test_name}")
        
        try:
            result = test_func()
            results[test_name] = result
            
            if result:
                logger.info(f"测试通过: {test_name}")
            else:
                logger.error(f"测试失败: {test_name}")
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