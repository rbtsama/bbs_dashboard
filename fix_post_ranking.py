import sqlite3
import logging
from datetime import datetime

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def fix_post_ranking_table():
    """修复post_ranking表的数据类型问题"""
    try:
        # 连接数据库
        conn = sqlite3.connect('backend/db/forum_data.db')
        cursor = conn.cursor()
        
        # 1. 备份原表
        logger.info("开始备份原表...")
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS post_ranking_backup AS 
        SELECT * FROM post_ranking
        """)
        
        # 2. 删除原表
        logger.info("删除原表...")
        cursor.execute("DROP TABLE post_ranking")
        
        # 3. 创建新表，使用正确的数据类型
        logger.info("创建新表结构...")
        cursor.execute("""
        CREATE TABLE post_ranking (
            thread_id TEXT,
            url TEXT,
            title TEXT,
            author TEXT,
            author_link TEXT,
            repost_count INTEGER DEFAULT 0,
            reply_count INTEGER DEFAULT 0,
            delete_reply_count INTEGER DEFAULT 0,
            daysold INTEGER DEFAULT 0,
            last_active INTEGER DEFAULT 0,
            created_at TEXT,
            updated_at TEXT
        )
        """)
        
        # 4. 从备份表转换并插入数据
        logger.info("开始转换并插入数据...")
        cursor.execute("SELECT * FROM post_ranking_backup")
        rows = cursor.fetchall()
        
        # 获取列名
        cursor.execute("PRAGMA table_info(post_ranking_backup)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # 准备插入语句
        insert_sql = f"""
        INSERT INTO post_ranking ({','.join(columns)})
        VALUES ({','.join(['?' for _ in columns])})
        """
        
        # 转换并插入数据
        converted_count = 0
        for row in rows:
            # 转换数据类型
            converted_row = list(row)
            # 转换repost_count (index 5)
            converted_row[5] = int(row[5]) if row[5] and row[5].isdigit() else 0
            # 转换reply_count (index 6)
            converted_row[6] = int(row[6]) if row[6] and row[6].isdigit() else 0
            # 转换delete_reply_count (index 7)
            converted_row[7] = int(row[7]) if row[7] and row[7].isdigit() else 0
            # 转换daysold (index 8)
            converted_row[8] = int(row[8]) if row[8] and row[8].isdigit() else 0
            # 转换last_active (index 9)
            converted_row[9] = int(row[9]) if row[9] and row[9].isdigit() else 0
            
            cursor.execute(insert_sql, converted_row)
            converted_count += 1
            
        # 5. 创建索引
        logger.info("创建索引...")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_post_ranking_repost_count ON post_ranking(repost_count)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_post_ranking_reply_count ON post_ranking(reply_count)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_post_ranking_last_active ON post_ranking(last_active)")
        
        # 6. 提交更改
        conn.commit()
        logger.info(f"成功转换 {converted_count} 条记录")
        
        # 7. 验证数据
        logger.info("验证数据...")
        cursor.execute("SELECT COUNT(*) FROM post_ranking")
        new_count = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM post_ranking_backup")
        old_count = cursor.fetchone()[0]
        
        if new_count == old_count:
            logger.info(f"数据验证成功: 新表和备份表都有 {new_count} 条记录")
        else:
            logger.warning(f"数据数量不匹配: 新表 {new_count} 条，备份表 {old_count} 条")
        
        # 8. 检查数据类型转换是否成功
        cursor.execute("""
        SELECT thread_id, repost_count, reply_count, delete_reply_count, daysold, last_active 
        FROM post_ranking 
        LIMIT 5
        """)
        sample_data = cursor.fetchall()
        logger.info("数据样本:")
        for row in sample_data:
            logger.info(f"thread_id: {row[0]}, repost: {row[1]}, reply: {row[2]}, delete: {row[3]}, days: {row[4]}, active: {row[5]}")
        
    except Exception as e:
        logger.error(f"修复过程出错: {str(e)}")
        if conn:
            conn.rollback()
        raise
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    try:
        logger.info("开始修复post_ranking表...")
        fix_post_ranking_table()
        logger.info("修复完成")
    except Exception as e:
        logger.error(f"修复失败: {str(e)}") 