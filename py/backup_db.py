import os
import shutil
import datetime
import sqlite3
import logging
import argparse

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/backup.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("backup_db")

def create_backup(before_update=False):
    """创建数据库备份
    
    Args:
        before_update (bool): 是否是更新前的备份
    """
    # 设置路径
    db_path = os.path.join("backend", "db", "forum_data.db")
    backup_dir = os.path.join("backup", "db")
    
    # 确保备份目录存在
    os.makedirs(backup_dir, exist_ok=True)
    os.makedirs("logs", exist_ok=True)
    
    # 生成备份文件名
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    prefix = "before_update_" if before_update else ""
    backup_file = os.path.join(backup_dir, f"{prefix}forum_data_{timestamp}.db")
    
    try:
        # 检查数据库是否存在
        if not os.path.exists(db_path):
            logger.error(f"数据库文件不存在: {db_path}")
            return False
            
        # 检查数据库是否正常
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        if result[0] != "ok":
            logger.error(f"数据库完整性检查失败: {result[0]}")
            conn.close()
            return False
        
        # 获取数据库大小
        conn.close()
        db_size = os.path.getsize(db_path) / (1024 * 1024)  # 转换为MB
        
        # 复制文件
        shutil.copy2(db_path, backup_file)
        
        if before_update:
            logger.info(f"更新前备份成功: {backup_file} ({db_size:.2f} MB)")
        else:
            logger.info(f"数据库备份成功: {backup_file} ({db_size:.2f} MB)")
        
        # 清理旧备份 (保留最近30个普通备份)
        regular_backups = sorted([f for f in os.listdir(backup_dir) 
                                if f.startswith("forum_data_") and not f.startswith("before_update_")])
        if len(regular_backups) > 30:
            for old_backup in regular_backups[:-30]:
                os.remove(os.path.join(backup_dir, old_backup))
                logger.info(f"删除旧备份: {old_backup}")
        
        # 清理旧的更新前备份 (保留最近5个)
        if before_update:
            update_backups = sorted([f for f in os.listdir(backup_dir) if f.startswith("before_update_")])
            if len(update_backups) > 5:
                for old_backup in update_backups[:-5]:
                    os.remove(os.path.join(backup_dir, old_backup))
                    logger.info(f"删除旧的更新前备份: {old_backup}")
        
        return True
    except Exception as e:
        logger.error(f"备份数据库时出错: {e}")
        return False

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='数据库备份工具')
    parser.add_argument('--before-update', action='store_true', help='创建更新前的备份')
    args = parser.parse_args()
    
    create_backup(before_update=args.before_update) 