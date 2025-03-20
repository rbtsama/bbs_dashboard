"""
删除car_info表的脚本
"""

import sqlite3
import os
import logging
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def drop_car_info_table():
    """
    删除car_info表及其相关索引
    """
    try:
        # 获取数据库路径
        db_path = Path(__file__).parent / 'db' / 'forum_data.db'
        
        # 检查数据库文件是否存在
        if not db_path.exists():
            raise FileNotFoundError(f"数据库文件不存在: {db_path}")
            
        logger.info(f"正在连接数据库: {db_path}")
        
        # 连接数据库
        conn = sqlite3.connect(db_path)
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
        
    except Exception as e:
        logger.error(f"删除car_info表时出错: {str(e)}")
        raise

if __name__ == "__main__":
    try:
        drop_car_info_table()
        print("✅ car_info表及其相关索引已成功删除")
    except Exception as e:
        print(f"❌ 删除car_info表时出错: {str(e)}") 