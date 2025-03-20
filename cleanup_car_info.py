#!/usr/bin/env python
"""
清理car_info相关的数据表和代码引用(保留原始文件)
"""

import os
import sqlite3
import logging
import shutil
import re
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 工作目录
ROOT_DIR = Path(__file__).absolute().parent
DB_PATH = ROOT_DIR / 'backend' / 'db' / 'forum_data.db'

# 需要修改的SQL文件
SQL_FILES_TO_MODIFY = [
    'sql/process_import_data.sql',
    'sql/incremental_update.sql',
    'sql/create_missing_tables.sql',
]

# 需要注释掉car_info导入的Python文件
PY_FILES_TO_MODIFY = [
    'backend/import_car_info.py',
    'backend/update_car_info.py',
    'backend/alter_car_info.py',
    'update_car_info.py',
]

def delete_car_info_table():
    """删除数据库中的car_info表及相关索引"""
    try:
        if not DB_PATH.exists():
            logger.warning(f"数据库文件不存在: {DB_PATH}")
            return False
            
        logger.info(f"正在连接数据库: {DB_PATH}")
        
        # 连接数据库
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 删除car_info表的所有索引
        logger.info("正在删除car_info表的索引...")
        cursor.execute("""
            SELECT name FROM sqlite_master 
            WHERE type='index' AND sql LIKE '%car_info%'
        """)
        indexes = cursor.fetchall()
        
        for index in indexes:
            try:
                cursor.execute(f"DROP INDEX IF EXISTS {index[0]}")
                logger.info(f"已删除索引: {index[0]}")
            except Exception as e:
                logger.warning(f"删除索引 {index[0]} 时出错: {str(e)}")
        
        # 删除car_info表
        logger.info("正在删除car_info表...")
        cursor.execute("DROP TABLE IF EXISTS car_info")
        
        # 提交更改
        conn.commit()
        logger.info("car_info表及其索引已成功删除")
        
        # 关闭连接
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"删除car_info表时出错: {str(e)}")
        return False

def modify_sql_files():
    """修改SQL文件，注释掉car_info相关的引用"""
    success_count = 0
    fail_count = 0
    
    for file_path in SQL_FILES_TO_MODIFY:
        full_path = ROOT_DIR / file_path
        
        if not full_path.exists():
            logger.info(f"文件不存在,跳过: {file_path}")
            continue
            
        try:
            # 备份原文件
            backup_path = str(full_path) + '.bak_carinfo'
            shutil.copy2(full_path, backup_path)
            
            # 读取文件内容
            with open(full_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # 注释掉car_info相关的引用行
            lines = content.split('\n')
            modified_lines = []
            
            for line in lines:
                if 'car_info' in line and not line.strip().startswith('--'):
                    modified_lines.append(f"-- {line} -- 已由清理脚本注释")
                else:
                    modified_lines.append(line)
            
            modified_content = '\n'.join(modified_lines)
            
            # 写回文件
            with open(full_path, 'w', encoding='utf-8') as file:
                file.write(modified_content)
                
            logger.info(f"已修改: {file_path}")
            logger.info(f"已创建备份: {backup_path}")
            success_count += 1
            
        except Exception as e:
            logger.error(f"修改 {file_path} 时出错: {str(e)}")
            fail_count += 1
    
    return success_count, fail_count

def comment_py_files():
    """注释掉Python文件中的car_info相关代码"""
    success_count = 0
    fail_count = 0
    
    for file_path in PY_FILES_TO_MODIFY:
        full_path = ROOT_DIR / file_path
        
        if not full_path.exists():
            logger.info(f"文件不存在,跳过: {file_path}")
            continue
            
        try:
            # 备份原文件
            backup_path = str(full_path) + '.bak_carinfo'
            shutil.copy2(full_path, backup_path)
            
            # 读取文件内容
            with open(full_path, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # 在文件顶部添加注释
            modified_content = f"""# 此文件中的代码已被禁用（由car_info清理脚本处理）
# 原始功能已被移除，但保留文件以备参考
# 原始备份文件: {os.path.basename(backup_path)}

{content}
"""
            
            # 写回文件
            with open(full_path, 'w', encoding='utf-8') as file:
                file.write(modified_content)
                
            logger.info(f"已修改: {file_path}")
            logger.info(f"已创建备份: {backup_path}")
            success_count += 1
            
        except Exception as e:
            logger.error(f"修改 {file_path} 时出错: {str(e)}")
            fail_count += 1
    
    return success_count, fail_count

if __name__ == "__main__":
    print("开始清理car_info相关的数据表和代码引用...")
    
    # 删除car_info表
    if delete_car_info_table():
        print("✅ 成功删除car_info表及其索引")
    else:
        print("❌ 删除car_info表失败")
    
    # 修改SQL文件
    success_sql, fail_sql = modify_sql_files()
    print(f"✅ 成功修改 {success_sql} 个SQL文件")
    if fail_sql > 0:
        print(f"❌ {fail_sql} 个SQL文件修改失败")
    
    # 修改Python文件
    success_py, fail_py = comment_py_files()
    print(f"✅ 成功修改 {success_py} 个Python文件")
    if fail_py > 0:
        print(f"❌ {fail_py} 个Python文件修改失败")
    
    print("\n清理完成！保留了所有原始文件，并创建了备份。") 