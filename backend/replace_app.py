"""
替换原始app.py的脚本
"""

import os
import shutil
import datetime
import logging

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("replace_app")

def replace_app():
    """
    备份原始app.py并用新的app_new.py替换
    """
    try:
        # 检查app_new.py是否存在
        if not os.path.exists('app_new.py'):
            logger.error("app_new.py文件不存在，无法替换")
            return False
        
        # 检查app.py是否存在
        if not os.path.exists('app.py'):
            logger.warning("原始app.py文件不存在，将直接创建")
            shutil.copy2('app_new.py', 'app.py')
            logger.info("已成功创建app.py")
            return True
        
        # 创建备份目录
        backup_dir = 'backups'
        os.makedirs(backup_dir, exist_ok=True)
        
        # 备份原始app.py
        timestamp = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        backup_path = os.path.join(backup_dir, f'app.py.bak_{timestamp}')
        shutil.copy2('app.py', backup_path)
        logger.info(f"已备份原始app.py到: {backup_path}")
        
        # 替换app.py
        shutil.copy2('app_new.py', 'app.py')
        logger.info("已成功替换app.py")
        
        return True
    except Exception as e:
        logger.error(f"替换app.py时出错: {str(e)}")
        return False

if __name__ == "__main__":
    logger.info("开始替换app.py...")
    success = replace_app()
    if success:
        logger.info("替换完成")
    else:
        logger.error("替换失败") 