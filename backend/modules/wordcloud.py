"""
词云模块，提供词云生成和获取功能
"""

import jieba
import json
import os
import pandas as pd
import logging
from collections import Counter
from datetime import datetime
from typing import List, Dict, Any, Optional

from .db_utils import execute_query, execute_update, table_exists

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("wordcloud")

# 词云版本号 - 当算法或数据结构变化时递增此值
WORDCLOUD_VERSION = 1

# 词云缓存保留天数
WORDCLOUD_CACHE_DAYS = 7

def ensure_cache_table():
    """确保词云缓存表存在"""
    if not table_exists('wordcloud_cache'):
        # 创建词云缓存表
        query = """
        CREATE TABLE IF NOT EXISTS wordcloud_cache (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            type TEXT,
            data TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            version INTEGER DEFAULT 1
        )
        """
        execute_update(query)
        logger.info("创建词云缓存表")
    else:
        # 检查表结构是否正确，如果不正确则重建表
        try:
            # 先查询表结构
            check_query = "PRAGMA table_info(wordcloud_cache)"
            columns = execute_query(check_query)
            column_names = [col['name'] for col in columns] if columns else []
            
            # 检查是否缺少必要的列
            required_columns = ['id', 'type', 'data', 'created_at', 'version']
            missing_columns = [col for col in required_columns if col not in column_names]
            
            if missing_columns:
                logger.warning(f"词云缓存表缺少列: {missing_columns}，正在重建表")
                
                # 删除旧表
                drop_query = "DROP TABLE IF EXISTS wordcloud_cache"
                execute_update(drop_query)
                
                # 创建新表
                create_query = """
                CREATE TABLE wordcloud_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT,
                    data TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    version INTEGER DEFAULT 1
                )
                """
                execute_update(create_query)
                logger.info("已重建词云缓存表")
        except Exception as e:
            logger.error(f"检查词云缓存表结构出错: {str(e)}")
            # 出错时也尝试重建表
            try:
                drop_query = "DROP TABLE IF EXISTS wordcloud_cache"
                execute_update(drop_query)
                
                create_query = """
                CREATE TABLE wordcloud_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT,
                    data TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    version INTEGER DEFAULT 1
                )
                """
                execute_update(create_query)
                logger.info("因错误已重建词云缓存表")
            except Exception as rebuild_err:
                logger.error(f"重建词云缓存表失败: {str(rebuild_err)}")

def generate_wordcloud_from_titles() -> List[Dict[str, Any]]:
    """
    从标题生成词云数据
    
    Returns:
        List[Dict[str, Any]]: 词云数据，格式为[{"text": "词语", "value": 数值}, ...]
    """
    logger.info("开始生成词云数据...")
    
    # 导入标题数据
    titles = []
    
    # 从数据库中获取标题
    tables_to_check = ['posts', 'list', 'detail']
    for table in tables_to_check:
        if table_exists(table):
            query = f"SELECT title FROM {table} WHERE title IS NOT NULL"
            result = execute_query(query)
            titles.extend([row['title'] for row in result if row['title']])
    
    # 如果数据库中没有足够的标题，尝试从Excel文件中读取
    if len(titles) < 100:
        # 项目根目录的绝对路径
        project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
        
        excel_files = [
            os.path.join(project_root, 'data', 'processed', 'post.xlsx'),
            os.path.join(project_root, 'data', 'processed', 'update.xlsx'),
            os.path.join(project_root, 'data', 'processed', 'detail.xlsx')
        ]
        
        for file_path in excel_files:
            try:
                if os.path.exists(file_path):
                    df = pd.read_excel(file_path)
                    if 'title' in df.columns:
                        valid_titles = df['title'].dropna().tolist()
                        titles.extend(valid_titles)
                        logger.info(f"从 {file_path} 读取到 {len(valid_titles)} 个标题")
            except Exception as e:
                logger.error(f"读取Excel文件 {file_path} 出错: {str(e)}")
    
    # 如果没有足够的标题，返回默认数据
    if not titles or len(titles) < 10:
        logger.warning("没有足够的标题数据，返回默认词云")
        return [
            {"text": "汽车", "value": 100},
            {"text": "二手车", "value": 80},
            {"text": "出售", "value": 70},
            {"text": "求购", "value": 60},
            {"text": "交易", "value": 50}
        ]
    
    logger.info(f"共获取到 {len(titles)} 个标题")
    
    # 对所有标题进行分词
    words = []
    for title in titles:
        if title and isinstance(title, str):
            words.extend(jieba.cut(title))
    
    # 统计词频
    word_count = Counter(words)
    
    # 过滤掉停用词和单字词
    stop_words = {
        '的', '了', '和', '是', '就', '都', '而', '及', '与', '着',
        '或', '一个', '没有', '我们', '你们', '他们', '它们', '这个',
        '那个', '这些', '那些', '自己', '什么', '这样', '那样',
        '怎样', '如此', '只是', '但是', '不过', '然后', '可以', '这', '那', '了',
        '啊', '哦', '呢', '吗', '嗯', '哈', '把', '让', '在', '中', '有',
        '为', '以', '到', '从', '被', '对', '能', '会', '要', '我'
    }
    
    filtered_words = {word: count for word, count in word_count.items()
                     if len(word) > 1 and word not in stop_words}
    
    if not filtered_words:
        logger.warning("过滤后没有词语，返回默认词云")
        return [
            {"text": "汽车", "value": 100},
            {"text": "二手车", "value": 80},
            {"text": "出售", "value": 70},
            {"text": "求购", "value": 60},
            {"text": "交易", "value": 50}
        ]
    
    # 按词频排序并限制数量
    sorted_words = sorted(filtered_words.items(), key=lambda x: x[1], reverse=True)[:300]
    
    # 为react-wordcloud生成标准格式数据
    wordcloud_data = []
    for word, count in sorted_words:
        wordcloud_data.append({
            "text": word,
            "value": count
        })
    
    logger.info(f"成功生成词云数据，共 {len(wordcloud_data)} 个词")
    
    # 保存到缓存表中
    save_to_cache(wordcloud_data)
    
    return wordcloud_data

def save_to_cache(wordcloud_data: List[Dict[str, Any]]) -> bool:
    """
    将词云数据保存到缓存表
    
    Args:
        wordcloud_data: 词云数据
        
    Returns:
        bool: 是否保存成功
    """
    try:
        # 确保缓存表存在
        ensure_cache_table()
        
        # 转换为JSON字符串
        json_data = json.dumps(wordcloud_data, ensure_ascii=False)
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # 保存到缓存表
        query = """
        INSERT INTO wordcloud_cache (type, data, created_at, version) 
        VALUES (?, ?, ?, ?)
        """
        execute_update(query, ('wordcloud', json_data, now, WORDCLOUD_VERSION))
        
        # 清理旧的缓存数据
        clean_old_cache()
        
        return True
    except Exception as e:
        logger.error(f"保存词云数据到缓存出错: {str(e)}")
        return False

def clean_old_cache() -> None:
    """清理旧的缓存数据"""
    try:
        # 保留最新的10条记录，删除更老的记录
        query = """
        DELETE FROM wordcloud_cache 
        WHERE id NOT IN (
            SELECT id FROM wordcloud_cache 
            ORDER BY created_at DESC 
            LIMIT 10
        )
        """
        affected_rows = execute_update(query)
        if affected_rows > 0:
            logger.info(f"清理了 {affected_rows} 条旧的词云缓存记录")
    except Exception as e:
        logger.error(f"清理词云缓存出错: {str(e)}")

def get_cached_wordcloud() -> Optional[List[Dict[str, Any]]]:
    """
    获取缓存的词云数据
    
    Returns:
        Optional[List[Dict[str, Any]]]: 词云数据，如果没有缓存则返回None
    """
    try:
        # 查询缓存中的最新词云数据
        query = """
        SELECT data, created_at 
        FROM wordcloud_cache 
        WHERE type = 'wordcloud'
        ORDER BY created_at DESC LIMIT 1
        """
        result = execute_query(query)
        
        if result and result[0]['data']:
            try:
                wordcloud_data = json.loads(result[0]['data'])
                if isinstance(wordcloud_data, list) and len(wordcloud_data) > 0:
                    logger.info(f"从缓存获取到词云数据，共 {len(wordcloud_data)} 个词")
                    return wordcloud_data
            except Exception as e:
                logger.error(f"解析缓存词云数据出错: {str(e)}")
        
        return None
    except Exception as e:
        logger.error(f"获取缓存词云数据出错: {str(e)}")
        return None

def get_wordcloud() -> List[Dict[str, Any]]:
    """
    获取词云数据，优先从缓存获取，如果没有则生成新数据
    
    Returns:
        List[Dict[str, Any]]: 词云数据
    """
    try:
        # 先尝试从缓存获取
        cached_data = get_cached_wordcloud()
        if cached_data:
            return cached_data
        
        # 如果没有缓存，生成新数据
        return generate_wordcloud_from_titles()
    except Exception as e:
        logger.error(f"获取词云数据出错: {str(e)}")
        # 返回默认数据
        return [
            {"text": "汽车", "value": 100},
            {"text": "二手车", "value": 80},
            {"text": "出售", "value": 70},
            {"text": "求购", "value": 60},
            {"text": "交易", "value": 50}
        ] 