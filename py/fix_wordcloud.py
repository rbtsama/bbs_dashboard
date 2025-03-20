import os
import sqlite3
import logging
import json
from pathlib import Path

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("fix_wordcloud")

# 设置数据路径
BASE_DIR = Path(__file__).parent.parent
DB_PATH = BASE_DIR / 'backend' / 'db' / 'forum_data.db'

def fix_wordcloud_table():
    """修复词云表结构问题"""
    print("开始修复词云表结构...")
    
    # 连接到数据库
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    try:
        # 检查是否存在wordcloud_cache表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wordcloud_cache'")
        if cursor.fetchone():
            print("找到已存在的wordcloud_cache表，检查结构...")
            
            # 检查表结构
            cursor.execute("PRAGMA table_info(wordcloud_cache)")
            columns = cursor.fetchall()
            column_names = [col[1] for col in columns]
            
            print(f"当前表结构: {', '.join(column_names)}")
            
            # 检查是否有data列和type列
            has_data = 'data' in column_names
            has_type = 'type' in column_names
            
            if has_data:
                print("词云表包含'data'列")
            else:
                print("警告: 词云表缺少'data'列")
                
            if has_type:
                print("词云表包含'type'列")
            else:
                print("警告: 词云表缺少'type'列")
                
            # 如果缺少关键列，重建表
            if not has_data or not has_type:
                print("词云表结构不完整，需要重建表")
                rebuild_wordcloud_table(cursor)
            else:
                print("词云表结构正常，不需要修复")
        else:
            print("未找到wordcloud_cache表，创建新表...")
            create_wordcloud_table(cursor)
            
        # 提交更改
        conn.commit()
        print("词云表结构修复完成")
        
        # 检查表内容
        cursor.execute("SELECT COUNT(*) FROM wordcloud_cache")
        count = cursor.fetchone()[0]
        print(f"词云表中有 {count} 条记录")
        
        return True
    except Exception as e:
        print(f"修复过程中出错: {str(e)}")
        conn.rollback()
        return False
    finally:
        conn.close()

def create_wordcloud_table(cursor):
    """创建词云表"""
    cursor.execute("""
    CREATE TABLE wordcloud_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        data TEXT,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        version INTEGER DEFAULT 1
    )
    """)
    print("创建了新的wordcloud_cache表")

def rebuild_wordcloud_table(cursor):
    """重建词云表"""
    # 保存原表数据
    cursor.execute("SELECT * FROM wordcloud_cache")
    old_data = cursor.fetchall()
    
    # 获取原表列名
    cursor.execute("PRAGMA table_info(wordcloud_cache)")
    columns = cursor.fetchall()
    column_names = [col[1] for col in columns]
    
    print(f"备份了 {len(old_data)} 条旧数据")
    
    # 重命名旧表
    cursor.execute("ALTER TABLE wordcloud_cache RENAME TO wordcloud_cache_backup")
    print("已将旧表重命名为wordcloud_cache_backup")
    
    # 创建新表
    create_wordcloud_table(cursor)
    
    # 尝试恢复数据
    recovered = 0
    try:
        for row in old_data:
            # 构建数据字典
            row_dict = dict(zip(column_names, row))
            
            # 如果有data字段，尝试导入
            if 'data' in row_dict and row_dict['data']:
                # 确定type
                wordcloud_type = row_dict.get('type', 'wordcloud')
                
                # 准备版本和时间戳
                version = row_dict.get('version', 1)
                created_at = row_dict.get('created_at', row_dict.get('generated_at', None))
                
                # 插入到新表
                cursor.execute("""
                INSERT INTO wordcloud_cache (type, data, created_at, version)
                VALUES (?, ?, ?, ?)
                """, (wordcloud_type, row_dict['data'], created_at, version))
                recovered += 1
    except Exception as e:
        print(f"恢复数据时出错: {str(e)}")
    
    print(f"从旧表恢复了 {recovered} 条数据到新表")

if __name__ == "__main__":
    if fix_wordcloud_table():
        print("词云修复完成！")
    else:
        print("词云修复失败，请检查错误信息") 