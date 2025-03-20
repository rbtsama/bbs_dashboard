import os
import sys
import logging
import sqlite3

# 添加父目录到模块搜索路径，以便导入update_db模块
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from update_db import DatabaseUpdater

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("test_backup_table")

def main():
    # 创建测试数据库路径
    test_db_path = "../backend/db/test_backup.db"
    temp_db_path = "../backend/db/temp_backup.db"
    
    # 删除已存在的测试文件
    for file_path in [test_db_path, temp_db_path]:
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                logger.info(f"已删除已存在的测试文件: {file_path}")
            except Exception as e:
                logger.error(f"无法删除文件 {file_path}: {str(e)}")
    
    # 创建原始数据库
    try:
        conn = sqlite3.connect(test_db_path)
        cursor = conn.cursor()
        
        # 创建测试表
        cursor.execute("""
        CREATE TABLE wordcloud_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            data TEXT,
            created_at TEXT,
            version INTEGER
        )
        """)
        
        # 插入测试数据
        for i in range(10):
            cursor.execute(
                "INSERT INTO wordcloud_cache (type, data, created_at, version) VALUES (?, ?, ?, ?)",
                (f"test_type_{i}", f"test_data_{i}", "2023-01-01", 1)
            )
        
        conn.commit()
        conn.close()
        logger.info(f"已创建测试数据库: {test_db_path}")
    except Exception as e:
        logger.error(f"创建测试数据库失败: {str(e)}")
        return False
    
    # 初始化数据库更新器
    updater = DatabaseUpdater(test_db_path)
    
    # 测试创建临时数据库
    if not updater.create_temp_database():
        logger.error("创建临时数据库失败")
        return False
    logger.info("临时数据库创建成功")
    
    # 测试备份保护表
    protected_tables = ['wordcloud_cache']
    logger.info(f"测试备份保护表: {', '.join(protected_tables)}")
    
    result = updater.backup_protected_tables(protected_tables)
    if not result:
        logger.error("备份保护表失败")
        return False
    
    # 验证表被成功复制
    try:
        temp_conn = sqlite3.connect(updater.temp_db_path)
        temp_cursor = temp_conn.cursor()
        
        # 检查表是否存在
        temp_cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", ('wordcloud_cache',))
        if not temp_cursor.fetchone():
            logger.error("临时数据库中没有找到保护表")
            return False
        
        # 检查数据是否复制
        temp_cursor.execute("SELECT COUNT(*) FROM wordcloud_cache")
        count = temp_cursor.fetchone()[0]
        if count != 10:
            logger.error(f"保护表数据复制不完整，期望10条，实际{count}条")
            return False
        
        temp_conn.close()
        logger.info("验证成功，保护表已正确备份")
    except Exception as e:
        logger.error(f"验证过程中出错: {str(e)}")
        return False
    
    logger.info("备份保护表功能测试通过")
    return True

if __name__ == "__main__":
    if main():
        logger.info("测试成功！")
        sys.exit(0)
    else:
        logger.error("测试失败！")
        sys.exit(1) 