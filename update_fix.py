import os
import sys
import sqlite3
from datetime import datetime
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("update_fix.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("update_fix")

def fix_protected_tables_config():
    """修复update_db.py中的protected_tables配置"""
    try:
        update_db_path = os.path.join('py', 'update_db.py')
        
        if not os.path.exists(update_db_path):
            logger.error(f"找不到更新脚本文件: {update_db_path}")
            return False
        
        # 读取文件内容
        with open(update_db_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 检查是否已包含thread_follow
        if "self.protected_tables = ['wordcloud_cache', 'user_data', 'thread_follow']" in content:
            logger.info("protected_tables配置已包含thread_follow，无需修复")
            return True
        
        # 替换protected_tables的定义
        if "self.protected_tables = ['wordcloud_cache', 'user_data']" in content:
            new_content = content.replace(
                "self.protected_tables = ['wordcloud_cache', 'user_data']",
                "self.protected_tables = ['wordcloud_cache', 'user_data', 'thread_follow']"
            )
            
            # 备份原文件
            backup_path = f"{update_db_path}.bak_{datetime.now().strftime('%Y%m%d%H%M%S')}"
            with open(backup_path, 'w', encoding='utf-8') as f:
                f.write(content)
            logger.info(f"已备份原文件到: {backup_path}")
            
            # 写入修改后的内容
            with open(update_db_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            logger.info(f"已更新protected_tables配置，添加了thread_follow")
            
            return True
        else:
            logger.warning("未找到匹配的protected_tables定义，请手动修改")
            return False
            
    except Exception as e:
        logger.error(f"修复protected_tables配置时出错: {e}")
        return False

def ensure_thread_follow_table():
    """确保thread_follow表存在且结构正确"""
    try:
        # 数据库路径
        db_path = os.path.join('backend', 'db', 'forum_data.db')
        
        if not os.path.exists(db_path):
            logger.error(f"找不到数据库文件: {db_path}")
            return False
        
        # 连接数据库
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 检查thread_follow表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='thread_follow'")
        result = cursor.fetchall()
        
        if not result:
            logger.warning("thread_follow表不存在，将创建该表")
            
            try:
                # 创建thread_follow表
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS thread_follow (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    thread_id TEXT NOT NULL,
                    url TEXT NOT NULL,
                    title TEXT,
                    author TEXT,
                    author_link TEXT,
                    days_old INTEGER DEFAULT 0,
                    last_active INTEGER DEFAULT 0,
                    read_count INTEGER DEFAULT 0,
                    reply_count INTEGER DEFAULT 0,
                    follow_status TEXT CHECK(follow_status IN ('followed', 'my_thread', 'not_followed')) DEFAULT 'not_followed',
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
                """)
                
                # 创建索引
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_thread_follow_thread_id ON thread_follow(thread_id)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_thread_follow_url ON thread_follow(url)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_thread_follow_status ON thread_follow(follow_status)")
                
                conn.commit()
                logger.info("thread_follow表创建成功")
                
            except Exception as e:
                logger.error(f"创建thread_follow表时出错: {e}")
                conn.rollback()
                conn.close()
                return False
        else:
            logger.info("thread_follow表已存在，检查列结构")
            
            # 检查表结构是否完整
            cursor.execute("PRAGMA table_info(thread_follow)")
            columns = [col[1] for col in cursor.fetchall()]
            required_columns = ['thread_id', 'url', 'title', 'author', 'author_link', 'days_old', 'last_active', 'follow_status', 'created_at', 'updated_at']
            
            missing_columns = [col for col in required_columns if col not in columns]
            if missing_columns:
                logger.warning(f"表中缺少以下列: {missing_columns}")
                
                # 添加缺失的列
                for col in missing_columns:
                    if col == 'days_old':
                        cursor.execute("ALTER TABLE thread_follow ADD COLUMN days_old INTEGER DEFAULT 0")
                    elif col == 'last_active':
                        cursor.execute("ALTER TABLE thread_follow ADD COLUMN last_active INTEGER DEFAULT 0")
                    elif col == 'follow_status':
                        cursor.execute("ALTER TABLE thread_follow ADD COLUMN follow_status TEXT CHECK(follow_status IN ('followed', 'my_thread', 'not_followed')) DEFAULT 'not_followed'")
                    elif col == 'created_at':
                        cursor.execute("ALTER TABLE thread_follow ADD COLUMN created_at TEXT DEFAULT CURRENT_TIMESTAMP")
                    elif col == 'updated_at':
                        cursor.execute("ALTER TABLE thread_follow ADD COLUMN updated_at TEXT DEFAULT CURRENT_TIMESTAMP")
                    else:
                        cursor.execute(f"ALTER TABLE thread_follow ADD COLUMN {col} TEXT")
                
                conn.commit()
                logger.info("成功添加了缺失的列")
            else:
                logger.info("表结构完整")
            
            # 检查是否有索引
            cursor.execute("SELECT name FROM sqlite_master WHERE type='index' AND tbl_name='thread_follow'")
            indexes = [idx[0] for idx in cursor.fetchall()]
            required_indexes = ['idx_thread_follow_thread_id', 'idx_thread_follow_url', 'idx_thread_follow_status']
            
            missing_indexes = [idx for idx in required_indexes if idx not in indexes]
            if missing_indexes:
                logger.warning(f"表中缺少以下索引: {missing_indexes}")
                
                # 添加缺失的索引
                for idx in missing_indexes:
                    if idx == 'idx_thread_follow_thread_id':
                        cursor.execute("CREATE INDEX idx_thread_follow_thread_id ON thread_follow(thread_id)")
                    elif idx == 'idx_thread_follow_url':
                        cursor.execute("CREATE INDEX idx_thread_follow_url ON thread_follow(url)")
                    elif idx == 'idx_thread_follow_status':
                        cursor.execute("CREATE INDEX idx_thread_follow_status ON thread_follow(follow_status)")
                
                conn.commit()
                logger.info("成功添加了缺失的索引")
            else:
                logger.info("索引完整")
        
        # 查看记录数
        cursor.execute("SELECT COUNT(*) FROM thread_follow")
        count = cursor.fetchone()[0]
        logger.info(f"表中共有 {count} 条记录")
        
        # 关闭连接
        conn.close()
        return True
        
    except Exception as e:
        logger.error(f"确保thread_follow表存在时出错: {e}")
        return False

def create_follow_restoration_script():
    """创建一个自动修复脚本，将其添加到backend目录下"""
    try:
        script_path = os.path.join('backend', 'create_missing_tables.py')
        
        # 检查文件是否已存在
        if os.path.exists(script_path):
            logger.info(f"修复脚本已存在: {script_path}")
            return True
            
        script_content = """import sqlite3
import os
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), 'db', 'forum_data.db')

def create_thread_follow_table():
    \"\"\"创建并初始化thread_follow表\"\"\"
    try:
        # 连接数据库
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 检查表是否已存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='thread_follow'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            logging.info("创建thread_follow表...")
            
            # 创建thread_follow表
            cursor.execute('''
            CREATE TABLE IF NOT EXISTS thread_follow (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                thread_id TEXT NOT NULL,
                url TEXT,
                title TEXT,
                author TEXT,
                author_link TEXT,
                days_old INTEGER,
                last_active INTEGER,
                read_count INTEGER,
                reply_count INTEGER,
                follow_status TEXT CHECK(follow_status IN ('not_followed', 'followed', 'my_thread')) DEFAULT 'not_followed',
                created_at TEXT,
                updated_at TEXT
            )
            ''')
            
            # 创建索引
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_thread_follow_thread_id ON thread_follow(thread_id)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_thread_follow_follow_status ON thread_follow(follow_status)")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_thread_follow_created_at ON thread_follow(created_at)")
            
            logging.info("thread_follow表创建成功！")
        else:
            # 检查follow_status字段是否存在
            cursor.execute("PRAGMA table_info(thread_follow)")
            columns = [col[1] for col in cursor.fetchall()]
            
            if 'follow_status' not in columns:
                logging.info("thread_follow表已存在，但缺少follow_status字段，正在添加...")
                cursor.execute('''
                ALTER TABLE thread_follow 
                ADD COLUMN follow_status TEXT CHECK(follow_status IN ('not_followed', 'followed', 'my_thread')) DEFAULT 'not_followed'
                ''')
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_thread_follow_follow_status ON thread_follow(follow_status)")
                logging.info("follow_status字段添加成功！")
            else:
                logging.info("thread_follow表及follow_status字段已存在")
        
        # 提交事务并关闭连接
        conn.commit()
        conn.close()
        logging.info("数据库操作完成")
        
    except Exception as e:
        logging.error(f"创建thread_follow表时出错: {str(e)}")
        if 'conn' in locals():
            conn.rollback()
            conn.close()

# 添加其他可能需要修复的表
# ...

if __name__ == "__main__":
    create_thread_follow_table()
    logging.info("所有修复操作完成")
"""
        
        # 写入脚本文件
        with open(script_path, 'w', encoding='utf-8') as f:
            f.write(script_content)
        
        logger.info(f"已创建修复脚本: {script_path}")
        return True
        
    except Exception as e:
        logger.error(f"创建修复脚本时出错: {e}")
        return False

def update_app_py():
    """更新app.py文件，确保在启动时自动检查并创建thread_follow表"""
    try:
        app_path = os.path.join('backend', 'app.py')
        
        if not os.path.exists(app_path):
            logger.error(f"找不到app.py文件: {app_path}")
            return False
        
        # 读取文件内容
        with open(app_path, 'r', encoding='utf-8') as f:
            content = f.readlines()
        
        # 检查是否已包含create_missing_tables导入
        import_exists = False
        init_exists = False
        
        for line in content:
            if "from create_missing_tables import create_thread_follow_table" in line:
                import_exists = True
            if "create_thread_follow_table()" in line:
                init_exists = True
        
        if import_exists and init_exists:
            logger.info("app.py已包含必要的修复代码，无需修改")
            return True
        
        # 备份原文件
        backup_path = f"{app_path}.bak_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.writelines(content)
        logger.info(f"已备份app.py到: {backup_path}")
        
        # 查找合适的导入位置和初始化位置
        import_index = None
        init_index = None
        
        for i, line in enumerate(content):
            if line.startswith('import') or line.startswith('from'):
                import_index = i
            
            if "if __name__ == '__main__':" in line:
                init_index = i
        
        if import_index is not None:
            # 添加导入语句
            if not import_exists:
                content.insert(import_index + 1, "from create_missing_tables import create_thread_follow_table\n")
                logger.info("已添加导入语句")
        
        if init_index is not None:
            # 添加初始化代码
            if not init_exists:
                content.insert(init_index + 1, "    # 确保thread_follow表存在\n    create_thread_follow_table()\n")
                logger.info("已添加初始化代码")
        
        # 写入修改后的内容
        with open(app_path, 'w', encoding='utf-8') as f:
            f.writelines(content)
        
        logger.info("已更新app.py文件")
        return True
        
    except Exception as e:
        logger.error(f"更新app.py文件时出错: {e}")
        return False

def main():
    """执行所有修复操作"""
    logger.info("开始修复关注表问题...")
    
    # 1. 修复protected_tables配置
    success = fix_protected_tables_config()
    if success:
        logger.info("✅ 成功修复protected_tables配置")
    else:
        logger.warning("❌ 修复protected_tables配置失败")
    
    # 2. 确保thread_follow表存在
    success = ensure_thread_follow_table()
    if success:
        logger.info("✅ 成功确保thread_follow表存在")
    else:
        logger.warning("❌ 确保thread_follow表存在失败")
    
    # 3. 创建自动修复脚本
    success = create_follow_restoration_script()
    if success:
        logger.info("✅ 成功创建自动修复脚本")
    else:
        logger.warning("❌ 创建自动修复脚本失败")
    
    # 4. 更新app.py文件
    success = update_app_py()
    if success:
        logger.info("✅ 成功更新app.py文件")
    else:
        logger.warning("❌ 更新app.py文件失败")
    
    logger.info("修复操作完成")

if __name__ == "__main__":
    main() 