import os
import jieba
import sqlite3
import pandas as pd
from collections import Counter
import logging
import json
from datetime import datetime
import random
import colorsys
import math

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("logs/wordcloud.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("wordcloud")

def ensure_table_structure():
    """确保数据库表结构正确"""
    try:
        conn = sqlite3.connect(os.path.join("backend", "db", "forum_data.db"))
        cursor = conn.cursor()
        
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wordcloud_cache'")
        table_exists = cursor.fetchone() is not None
        
        if table_exists:
            # 检查表结构
            cursor.execute("PRAGMA table_info(wordcloud_cache)")
            columns = [row[1] for row in cursor.fetchall()]
            
            # 检查是否包含必要的列
            required_columns = {'type', 'data', 'created_at', 'version'}
            missing_columns = required_columns - set(columns)
            
            if missing_columns:
                # 表结构不完整，需要重建
                cursor.execute("DROP TABLE IF EXISTS wordcloud_cache")
                table_exists = False
        
        if not table_exists:
            # 创建新表
            cursor.execute("""
                CREATE TABLE wordcloud_cache (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    type TEXT,
                    data TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    version INTEGER DEFAULT 1
                )
            """)
        
        conn.commit()
        conn.close()
        logger.info("数据库表结构已更新")
        return True
    except Exception as e:
        logger.error(f"更新数据库表结构时出错: {e}")
        return False

def update_word_frequencies():
    """从update.xlsx统计词频并更新到数据库"""
    try:
        # 确保表结构正确
        if not ensure_table_structure():
            return False
            
        # 读取update.xlsx文件
        update_file = os.path.join("data", "processed", "update.xlsx")
        if not os.path.exists(update_file):
            logger.error(f"文件不存在: {update_file}")
            return False
            
        # 读取数据
        df = pd.read_excel(update_file)
        if 'title' not in df.columns:
            logger.error("文件中没有title列")
            return False
            
        # 合并所有标题
        text = " ".join(df['title'].dropna().astype(str))
        
        # 分词
        words = jieba.cut(text)
        
        # 过滤停用词和单字词
        stop_words = {'的', '了', '和', '是', '就', '都', '而', '及', '与', '着',
                     '或', '一个', '没有', '我们', '你们', '他们', '它们', '这个',
                     '那个', '这些', '那些', '自己', '什么', '哪些', '怎么', '多少'}
        word_list = [word for word in words if len(word) > 1 and word not in stop_words]
        
        # 统计词频
        word_counts = Counter(word_list)
        
        # 获取前100个高频词
        top_words = word_counts.most_common(100)
        
        # 计算最大和最小词频
        max_count = max(count for _, count in top_words)
        min_count = min(count for _, count in top_words)
        
        # 生成词云数据
        wordcloud_data = []
        for word, count in top_words:
            # 计算字体大小 (对数缩放)
            size = 14 + int(46 * (math.log(count + 1) - math.log(min_count + 1)) / 
                          (math.log(max_count + 1) - math.log(min_count + 1)))
            
            # 生成随机颜色
            h = random.random()  # 随机色调
            s = 0.5 + random.random() * 0.3  # 中等到高饱和度
            v = 0.8 + random.random() * 0.2  # 高亮度
            rgb = colorsys.hsv_to_rgb(h, s, v)
            color = f"rgb({int(rgb[0]*255)}, {int(rgb[1]*255)}, {int(rgb[2]*255)})"
            
            wordcloud_data.append({
                'text': word,
                'value': count,
                'size': size,
                'color': color
            })
        
        # 连接数据库
        conn = sqlite3.connect(os.path.join("backend", "db", "forum_data.db"))
        cursor = conn.cursor()
        
        # 更新wordcloud_cache表
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        data = json.dumps(wordcloud_data, ensure_ascii=False)
        
        cursor.execute("""
            INSERT INTO wordcloud_cache 
            (type, data, created_at, version)
            VALUES (?, ?, ?, ?)
        """, ('wordcloud', data, current_time, 1))
        
        conn.commit()
        conn.close()
        
        logger.info("词云数据已更新到数据库")
        return True
        
    except Exception as e:
        logger.error(f"更新词云数据时出错: {e}")
        return False

if __name__ == "__main__":
    update_word_frequencies() 