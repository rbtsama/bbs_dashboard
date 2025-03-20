import sqlite3
import json
from datetime import datetime, timedelta
import jieba
from collections import Counter
import sys
import os
import random

# 词云缓存版本常量
WORDCLOUD_VERSION = 1

def get_db_connection():
    """获取数据库连接"""
    db_path = 'db/forum_data.db'
    if not os.path.exists(db_path):
        print(f"数据库文件不存在: {db_path}")
        sys.exit(1)
    return sqlite3.connect(db_path)

def init_wordcloud_cache():
    """初始化词云缓存表"""
    print(f"[{datetime.now()}] 初始化词云缓存表...")
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wordcloud_cache'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            # 创建词云缓存表
            print(f"[{datetime.now()}] 创建词云缓存表...")
            cursor.execute('''
            CREATE TABLE wordcloud_cache (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT,
                created_date TEXT,
                version INTEGER DEFAULT 1,
                expire_date TEXT
            )
            ''')
            conn.commit()
            print(f"[{datetime.now()}] 创建词云缓存表成功")
        else:
            # 检查表结构是否符合预期
            print(f"[{datetime.now()}] 检查词云缓存表结构...")
            cursor.execute("PRAGMA table_info(wordcloud_cache)")
            columns = {column[1]: column[2] for column in cursor.fetchall()}
            
            # 检查是否是我们预期的结构
            expected_columns = {
                'id': 'INTEGER',
                'data': 'TEXT',
                'created_date': 'TEXT',
                'version': 'INTEGER',
                'expire_date': 'TEXT'
            }
            
            # 如果表结构完全不同，则重建表
            if 'thread_id' in columns and 'title' in columns and 'image_path' in columns:
                print(f"[{datetime.now()}] 检测到旧版词云表结构，重建表...")
                # 备份旧表数据
                try:
                    cursor.execute("ALTER TABLE wordcloud_cache RENAME TO wordcloud_cache_old")
                    conn.commit()
                    print(f"[{datetime.now()}] 旧表已重命名为wordcloud_cache_old")
                    
                    # 创建新表
                    cursor.execute('''
                    CREATE TABLE wordcloud_cache (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        data TEXT,
                        created_date TEXT,
                        version INTEGER DEFAULT 1,
                        expire_date TEXT
                    )
                    ''')
                    conn.commit()
                    print(f"[{datetime.now()}] 创建新词云缓存表成功")
                except Exception as e:
                    print(f"[{datetime.now()}] 重建词云表出错: {str(e)}")
                    conn.rollback()
            else:
                # 检查各个列是否存在，不存在则添加
                missing_columns = {col: dtype for col, dtype in expected_columns.items() if col not in columns}
                for col, dtype in missing_columns.items():
                    try:
                        print(f"[{datetime.now()}] 添加缺失的列: {col}")
                        cursor.execute(f"ALTER TABLE wordcloud_cache ADD COLUMN {col} {dtype}")
                        conn.commit()
                    except Exception as e:
                        print(f"[{datetime.now()}] 添加列 {col} 出错: {str(e)}")
    except Exception as e:
        print(f"[{datetime.now()}] 初始化词云缓存表出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

def generate_wordcloud():
    """生成词云数据并缓存到数据库"""
    print(f"[{datetime.now()}] 开始生成词云数据...")
    conn = get_db_connection()
    try:
        # 从list表获取所有标题
        cursor = conn.cursor()
        
        # 先尝试从list表获取标题
        try:
            print(f"[{datetime.now()}] 尝试从list表获取标题...")
            cursor.execute("SELECT COUNT(*) FROM list WHERE title IS NOT NULL AND title != ''")
            count = cursor.fetchone()[0]
            print(f"[{datetime.now()}] list表中有 {count} 个有效标题")
            
            if count > 0:
                query = "SELECT title FROM list WHERE title IS NOT NULL AND title != ''"
                titles = cursor.execute(query).fetchall()
                print(f"[{datetime.now()}] 成功从list表获取到 {len(titles)} 个标题")
            else:
                # 如果list表没有数据，尝试从post表获取
                print(f"[{datetime.now()}] list表中没有有效标题，尝试从post表获取...")
                query = "SELECT title FROM post WHERE title IS NOT NULL AND title != ''"
                titles = cursor.execute(query).fetchall()
                print(f"[{datetime.now()}] 从post表获取到 {len(titles)} 个标题")
        except Exception as e:
            # 如果list表不存在或发生错误，尝试从post表获取
            print(f"[{datetime.now()}] 从list表获取标题时出错: {str(e)}，尝试从post表获取...")
            query = "SELECT title FROM post WHERE title IS NOT NULL AND title != ''"
            titles = cursor.execute(query).fetchall()
            print(f"[{datetime.now()}] 从post表获取到 {len(titles)} 个标题")
        
        if not titles or len(titles) == 0:
            print(f"[{datetime.now()}] 没有找到有效的标题数据")
            return None
            
        print(f"[{datetime.now()}] 总共获取到 {len(titles)} 个标题")
        
        # 对所有标题进行分词
        words = []
        for title in titles:
            # 使用jieba进行中文分词
            if title[0]:  # 确保标题不为None
                try:
                    # 尝试解码标题（如果是bytes类型）
                    title_text = title[0]
                    if isinstance(title_text, bytes):
                        title_text = title_text.decode('utf-8')
                    words.extend(jieba.cut(title_text))
                except Exception as e:
                    print(f"[{datetime.now()}] 分词出错: {str(e)}, 标题: {title[0]}")
                    continue
        
        print(f"[{datetime.now()}] 分词完成，共 {len(words)} 个词")
        
        # 统计词频
        word_count = Counter(words)
        
        # 过滤掉停用词和单字词
        stop_words = {'的', '了', '和', '是', '就', '都', '而', '及', '与', '着',
                     '或', '一个', '没有', '我们', '你们', '他们', '它们', '这个',
                     '那个', '这些', '那些', '自己', '什么', '这样', '那样',
                     '怎样', '如此', '只是', '但是', '不过', '然后', '可以', '这', '那', '了',
                     '啊', '哦', '呢', '吗', '嗯', '哈', '把', '让', '在', '中', '有',
                     '为', '以', '到', '从', '被', '对', '能', '会', '要'}
        
        filtered_words = {word: count for word, count in word_count.items()
                         if len(word) > 1 and word not in stop_words}
        
        print(f"[{datetime.now()}] 过滤后剩余 {len(filtered_words)} 个词")
        
        if not filtered_words:
            print(f"[{datetime.now()}] 没有找到有效的词语")
            return None
        
        # 计算词云数据
        max_count = max(filtered_words.values())
        min_count = min(filtered_words.values())
        
        # 生成词云数据
        word_cloud_data = []
        
        # 按词频排序并限制数量（增加显示词汇数量）
        sorted_words = sorted(filtered_words.items(), key=lambda x: x[1], reverse=True)[:300]  # 增加到300个词
        
        print(f"[{datetime.now()}] 选取前 {len(sorted_words)} 个高频词")
        
        # 将词语按大小分组（调整比例，增加数量）
        large_words = sorted_words[:20]    # 大词增加到20个
        medium_words = sorted_words[20:75] # 中词调整为55个
        small_words = sorted_words[75:300] # 小词保持225个
        
        # 生成大词
        for word, count in large_words:
            word_cloud_data.append({
                'text': word,
                'count': count,
                'size': max(60, 90 - (90 - 60) * (max_count - count) / (max_count - min_count)),
                'color': random.choice(['#1890ff', '#52c41a', '#722ed1', '#fa8c16', '#eb2f96']),
                'group': 'large'
            })
        
        # 生成中词
        for word, count in medium_words:
            word_cloud_data.append({
                'text': word,
                'count': count,
                'size': max(40, 60 - (60 - 40) * (max_count - count) / (max_count - min_count)),
                'color': random.choice(['#13c2c2', '#faad14', '#2f54eb', '#f5222d', '#a0d911']),
                'group': 'medium'
            })
        
        # 生成小词
        for word, count in small_words:
            word_cloud_data.append({
                'text': word,
                'count': count,
                'size': max(20, 40 - (40 - 20) * (max_count - count) / (max_count - min_count)),
                'color': random.choice(['#1890ff', '#52c41a', '#722ed1', '#fa8c16', '#eb2f96']),
                'group': 'small'
            })
        
        print(f"[{datetime.now()}] 生成了 {len(word_cloud_data)} 个词云数据")
        
        # 保存到数据库
        try:
            # 获取当前日期
            today = datetime.now().strftime('%Y-%m-%d')
            expire_date = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
            
            # 转换为JSON字符串
            data_json = json.dumps(word_cloud_data, ensure_ascii=False)
            
            # 删除旧版本的缓存
            cursor.execute("DELETE FROM wordcloud_cache WHERE created_date = ? AND version = ?", (today, WORDCLOUD_VERSION))
            
            # 插入新数据
            cursor.execute(
                "INSERT INTO wordcloud_cache (data, created_date, version, expire_date) VALUES (?, ?, ?, ?)",
                (data_json, today, WORDCLOUD_VERSION, expire_date)
            )
            
            # 提交事务
            conn.commit()
            
            print(f"[{datetime.now()}] 词云数据缓存成功")
            return word_cloud_data
        except Exception as e:
            print(f"[{datetime.now()}] 保存词云数据失败: {str(e)}")
            conn.rollback()
            return None
    except Exception as e:
        print(f"[{datetime.now()}] 生成词云数据出错: {str(e)}")
        return None
    finally:
        conn.close()

def check_wordcloud_data():
    """检查词云数据"""
    print(f"[{datetime.now()}] 检查词云数据...")
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        
        # 查询词云缓存数量
        cursor.execute("SELECT COUNT(*) FROM wordcloud_cache")
        count = cursor.fetchone()[0]
        print(f"[{datetime.now()}] 词云缓存表中有 {count} 条记录")
        
        if count > 0:
            # 查询最新的词云缓存
            cursor.execute("SELECT id, created_date, version, expire_date FROM wordcloud_cache ORDER BY id DESC LIMIT 1")
            latest = cursor.fetchone()
            if latest:
                print(f"[{datetime.now()}] 最新的词云缓存:")
                print(f"  ID: {latest[0]}")
                print(f"  创建日期: {latest[1]}")
                print(f"  版本: {latest[2]}")
                print(f"  过期日期: {latest[3]}")
                
                # 查询数据内容
                cursor.execute("SELECT data FROM wordcloud_cache WHERE id = ?", (latest[0],))
                data_json = cursor.fetchone()[0]
                
                if data_json:
                    data = json.loads(data_json)
                    print(f"[{datetime.now()}] 词云数据包含 {len(data)} 个词")
                    if len(data) > 0:
                        print(f"[{datetime.now()}] 前5个词:")
                        for i, word in enumerate(data[:5]):
                            print(f"  {i+1}. {word['text']} (大小: {word['size']}, 频率: {word['count']})")
                else:
                    print(f"[{datetime.now()}] 词云数据为空")
    except Exception as e:
        print(f"[{datetime.now()}] 检查词云数据出错: {str(e)}")
    finally:
        conn.close()

if __name__ == "__main__":
    print(f"[{datetime.now()}] 开始手动生成词云数据...")
    
    # 初始化词云缓存表
    init_wordcloud_cache()
    
    # 生成词云数据
    generate_wordcloud()
    
    # 检查词云数据
    check_wordcloud_data()
    
    print(f"[{datetime.now()}] 词云数据生成完成") 