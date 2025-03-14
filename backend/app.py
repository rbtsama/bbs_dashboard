from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import pandas as pd
import os
from datetime import datetime, timedelta, date
import json
from config import DATABASE_PATH, API_PREFIX, DEBUG, HOST, PORT, LIST_FILE, POST_FILE
import jieba
from collections import Counter
import math
import random
import colorsys
import threading
import time
import schedule

app = Flask(__name__)
CORS(app)  # 启用CORS以允许前端访问

# 缓存
_word_cloud_cache = {'data': None, 'date': None, 'version': 1}

# 词云缓存版本号 - 当算法或数据结构变化时递增此值
WORDCLOUD_VERSION = 1

# 词云缓存保留天数
WORDCLOUD_CACHE_DAYS = 7

# 定时任务线程
scheduler_thread = None
scheduler_running = False

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# 初始化数据库
def init_db():
    """初始化数据库"""
    conn = get_db_connection()
    
    # 创建帖子表
    conn.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        url TEXT PRIMARY KEY,
        title TEXT,
        author TEXT,
        post_time TEXT,
        scraping_time TEXT
    )
    ''')
    
    # 创建更新历史表
    conn.execute('''
    CREATE TABLE IF NOT EXISTS thread_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        title TEXT,
        author TEXT,
        scraping_time TEXT,
        read_count INTEGER,
        reply_count INTEGER,
        last_reply_time TEXT,
        update_reason TEXT
    )
    ''')
    
    # 创建车辆信息表
    conn.execute('''
    CREATE TABLE IF NOT EXISTS car_info (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT UNIQUE,
        year INTEGER,
        make TEXT,
        model TEXT,
        miles TEXT,
        price TEXT,
        trade_type TEXT,
        location TEXT,
        thread_id TEXT,
        author TEXT,
        post_time TEXT,
        daysold INTEGER,
        last_active TEXT,
        FOREIGN KEY (url) REFERENCES posts(url)
    )
    ''')
    
    # 检查thread_follows表是否存在，如果不存在则创建
    table_exists = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='thread_follows'").fetchone()
    if not table_exists:
        # 创建新的关注表，使用 url 作为唯一标识
        conn.execute('''
        CREATE TABLE IF NOT EXISTS thread_follows (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            follow_type TEXT NOT NULL CHECK(follow_type IN ('my_follow', 'my_thread')),
            title TEXT,
            author TEXT,
            author_link TEXT,
            read_count INTEGER DEFAULT 0,
            reply_count INTEGER DEFAULT 0,
            repost_count INTEGER DEFAULT 0,
            delete_count INTEGER DEFAULT 0,
            days_old INTEGER DEFAULT 0,
            last_active INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(url, follow_type)
        )
        ''')
    
    # 检查follow_history表是否存在，如果不存在则创建
    table_exists = conn.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='follow_history'").fetchone()
    if not table_exists:
        # 创建关注帖子的异动记录表
        conn.execute('''
        CREATE TABLE IF NOT EXISTS follow_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT,
            author TEXT,
            scraping_time TEXT,
            read_count INTEGER,
            reply_count INTEGER,
            last_reply_time TEXT,
            update_reason TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (url) REFERENCES thread_follows(url) ON DELETE CASCADE
        )
        ''')
    
    conn.commit()
    conn.close()

# 数据导入API
@app.route('/api/import-data', methods=['POST'])
def import_data():
    try:
        if 'list_file' not in request.files or 'post_file' not in request.files:
            return jsonify({'error': '缺少文件'}), 400
        
        list_file = request.files['list_file']
        post_file = request.files['post_file']
        
        # 读取Excel文件
        list_df = pd.read_excel(list_file)
        post_df = pd.read_excel(post_file)
        
        conn = get_db_connection()
        
        # 导入posts表数据
        for _, row in list_df.iterrows():
            conn.execute('''
            INSERT OR IGNORE INTO posts 
            (thread_id, title, author, author_url, post_time, forum, views, page_num, num) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                row.get('thread_id', ''),
                row.get('title', ''),
                row.get('author', ''),
                row.get('author_url', ''),
                row.get('post_time', ''),
                row.get('forum', ''),
                row.get('views', 0),
                row.get('page_num', 0),
                row.get('num', 0)
            ))
        
        # 导入thread_history表数据
        for _, row in post_df.iterrows():
            conn.execute('''
            INSERT OR IGNORE INTO thread_history 
            (thread_id, scraping_time, update_reason, view_count, page_num, num) 
            VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                row.get('thread_id', ''),
                row.get('scraping_time', ''),
                row.get('update_reason', ''),
                row.get('view_count', 0),
                row.get('page_num', 0),
                row.get('num', 0)
            ))
        
        conn.commit()
        conn.close()
        
        return jsonify({'success': True, 'message': '数据导入成功'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# 获取昨日新帖
@app.route('/api/new-posts-yesterday', methods=['GET'])
def new_posts_yesterday():
    """获取昨日新帖"""
    conn = get_db_connection()
    
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    offset = (page - 1) * limit
    
    try:
        # 获取最新的post_time日期
        latest_date_query = """
        SELECT DATE(post_time) as latest_date 
        FROM post 
        ORDER BY post_time DESC 
        LIMIT 1
        """
        latest_date = conn.execute(latest_date_query).fetchone()
        
        if not latest_date:
            return jsonify([])
            
        latest_date = latest_date[0]
        
        # 查询该日期的所有帖子
        query = """
        SELECT 
            url,
            title,
            author,
            author_link,
            post_time
        FROM post 
        WHERE DATE(post_time) = ?
        ORDER BY post_time ASC
        LIMIT ? OFFSET ?
        """
        
        result = conn.execute(query, (latest_date, limit, offset)).fetchall()
        
        # 转换结果为字典列表
        posts = []
        for row in result:
            post_dict = {}
            for idx, col in enumerate(row.keys()):
                post_dict[col] = row[idx]
            posts.append(post_dict)
            
        return jsonify(posts)
            
    except Exception as e:
        print(f"获取昨日新帖出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify([])
    finally:
        conn.close()

def generate_mock_posts(count=10):
    """生成模拟的帖子数据"""
    from datetime import datetime, timedelta
    import random
    
    # 模拟数据
    titles = [
        "2025年春节活动讨论", "新版本更新内容汇总", "游戏平衡性分析",
        "攻略：如何快速升级", "社区活动：截图大赛", "官方公告：服务器维护",
        "求助：游戏无法登录", "分享：我的游戏心得", "讨论：未来版本展望",
        "投票：最喜欢的角色", "建议：游戏优化方向", "bug反馈：任务无法完成",
        "新手指南：入门必看", "资源分享：高清壁纸", "组队：周末副本"
    ]
    
    authors = ["玩家1", "游戏达人", "资深玩家", "新手小白", "社区管理员", "游戏爱好者"]
    
    # 生成模拟数据
    mock_posts = []
    yesterday = datetime.now() - timedelta(days=1)
    
    for i in range(count):
        post_time = yesterday.replace(
            hour=random.randint(0, 23),
            minute=random.randint(0, 59),
            second=random.randint(0, 59)
        )
        
        mock_post = {
            "id": i + 1,
            "title": random.choice(titles),
            "author": random.choice(authors),
            "author_link": f"https://example.com/user/{i+1}",
            "post_time": post_time.strftime("%Y-%m-%d %H:%M:%S"),
            "url": f"https://example.com/post/{i+1}",
            "views": random.randint(100, 10000)
        }
        
        mock_posts.append(mock_post)
    
    # 按时间排序
    mock_posts.sort(key=lambda x: x["post_time"], reverse=True)
    
    return mock_posts

# 获取帖子趋势数据
@app.route('/api/post-trend', methods=['GET'])
def post_trend():
    time_type = request.args.get('type', 'daily')
    conn = get_db_connection()
    
    if time_type == 'hourly':
        # 小时粒度 - 最新的90个小时
        limit = 90
        date_format = '%Y-%m-%d %H:00:00'
    elif time_type == 'daily':
        # 日粒度 - 最新的30天
        limit = 30
        date_format = '%Y-%m-%d'
    elif time_type == 'weekly':
        # 周粒度 - 最新的20周
        limit = 20
        date_format = '%Y-%W'
    else:
        # 月粒度 - 最新的20个月
        limit = 20
        date_format = '%Y-%m'
    
    # 根据时间粒度聚合数据
    query = f'''
    SELECT 
        strftime('{date_format}', post_time) as datetime,
        COUNT(*) as count,
        'post' as type
    FROM posts
    GROUP BY datetime
    ORDER BY datetime DESC
    LIMIT {limit}
    '''
    
    result = conn.execute(query).fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in result])

# 获取更新数据趋势
@app.route('/api/update-trend', methods=['GET'])
def update_trend():
    time_type = request.args.get('type', 'daily')
    conn = get_db_connection()
    
    if time_type == 'hourly':
        # 小时粒度 - 最新的90个小时
        limit = 90
        date_format = '%Y-%m-%d %H:00:00'
    elif time_type == 'daily':
        # 日粒度 - 最新的30天
        limit = 30
        date_format = '%Y-%m-%d'
    elif time_type == 'weekly':
        # 周粒度 - 最新的20周
        limit = 20
        date_format = '%Y-%W'
    else:
        # 月粒度 - 最新的20个月
        limit = 20
        date_format = '%Y-%m'
    
    try:
        # 首先获取最近的时间点列表
        time_query = f'''
        SELECT DISTINCT strftime('{date_format}', scraping_time) as datetime
        FROM thread_history
        ORDER BY datetime DESC
        LIMIT {limit}
        '''
        
        time_points = [row['datetime'] for row in conn.execute(time_query).fetchall()]
        
        if not time_points:
            return jsonify([])
        
        # 构建IN子句
        time_placeholders = ','.join(['?'] * len(time_points))
        
        # 根据更新原因聚合数据，只查询最近的时间点
        query = f'''
        SELECT 
            strftime('{date_format}', scraping_time) as datetime,
            update_reason as updateType,
            COUNT(*) as count
        FROM thread_history
        WHERE strftime('{date_format}', scraping_time) IN ({time_placeholders})
        GROUP BY datetime, updateType
        ORDER BY datetime DESC
        '''
        
        result = conn.execute(query, time_points).fetchall()
        
        # 确保所有时间点都有数据，即使某些时间点没有特定类型的更新
        update_types = ['重发', '回帖', '删回帖']
        complete_data = []
        
        for time_point in time_points:
            for update_type in update_types:
                # 查找当前时间点和更新类型的记录
                found = False
                for row in result:
                    if row['datetime'] == time_point and row['updateType'] == update_type:
                        complete_data.append(dict(row))
                        found = True
                        break
                
                # 如果没有找到，添加一个计数为0的记录
                if not found:
                    complete_data.append({
                        'datetime': time_point,
                        'updateType': update_type,
                        'count': 0
                    })
        
        return jsonify(complete_data)
    except Exception as e:
        print(f"获取更新趋势数据出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify([])
    finally:
        conn.close()

# 获取浏览数据趋势
@app.route('/api/view-trend', methods=['GET'])
def view_trend():
    time_type = request.args.get('type', 'daily')
    conn = get_db_connection()
    
    if time_type == 'hourly':
        # 小时粒度 - 最新的90个小时
        limit = 90
        date_format = '%Y-%m-%d %H:00:00'
    elif time_type == 'daily':
        # 日粒度 - 最新的30天
        limit = 30
        date_format = '%Y-%m-%d'
    elif time_type == 'weekly':
        # 周粒度 - 最新的20周
        limit = 20
        date_format = '%Y-%W'
    else:
        # 月粒度 - 最新的20个月
        limit = 20
        date_format = '%Y-%m'
    
    # 查询浏览数据趋势，并限制返回数量
    query = f'''
    SELECT 
        strftime('{date_format}', scraping_time) as datetime,
        SUM(view_count) as views
    FROM thread_history
    WHERE scraping_time >= '2025-02-12'
    GROUP BY datetime
    ORDER BY datetime DESC
    LIMIT {limit}
    '''
    
    result = conn.execute(query).fetchall()
    conn.close()
    
    return jsonify([dict(row) for row in result])

# 获取帖子排行榜
@app.route('/api/thread-ranking', methods=['GET'])
def thread_ranking():
    conn = get_db_connection()
    
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    offset = (page - 1) * limit
    
    # 获取排序参数
    sort_field = request.args.get('sort_field', 'repost_count')
    sort_order = request.args.get('sort_order', 'desc')
    
    # 验证排序字段，防止SQL注入
    valid_sort_fields = {
        'repost_count': 'p.repost_count',
        'reply_count': 'p.reply_count',
        'delete_count': 'p.delete_count',
        'days_old': 'p.Days_Old',
        'last_active': 'p.last_active',
        'read_count': 'lr.read_count'
    }
    
    # 默认按重发次数排序
    db_sort_field = valid_sort_fields.get(sort_field, 'p.repost_count')
    
    # 验证排序顺序
    if sort_order.lower() not in ['asc', 'desc']:
        sort_order = 'DESC'
    else:
        sort_order = sort_order.upper()
    
    try:
        # 查询帖子排行榜，包含所有帖子（包括repost_count=0的）
        # 同时从list表获取最新的read_count
        query = f'''
        WITH latest_reads AS (
            SELECT url, read_count, scraping_time,
                   ROW_NUMBER() OVER (PARTITION BY url ORDER BY scraping_time DESC) as rn
            FROM list
            WHERE read_count IS NOT NULL
        )
        SELECT 
            p.*,
            p.url as thread_id,  -- 使用 url 作为 thread_id
            COALESCE(lr.read_count, 0) as read_count
        FROM postranking p
        LEFT JOIN latest_reads lr ON p.url = lr.url AND lr.rn = 1
        ORDER BY {db_sort_field} {sort_order}, p.repost_count DESC
        LIMIT ? OFFSET ?
        '''
        
        result = conn.execute(query, (limit, offset)).fetchall()
        
        # 获取总记录数
        count_query = 'SELECT COUNT(*) as total FROM postranking'
        total_count = conn.execute(count_query).fetchone()['total']
        
        # 打印一些调试信息
        print(f"查询到 {len(result)} 条记录")
        if result:
            first_record = dict(result[0])
            print(f"第一条记录示例: {first_record}")
        
        return jsonify({
            'data': [dict(row) for row in result],
            'total': total_count,
            'page': page,
            'limit': limit,
            'sort_field': sort_field,
            'sort_order': sort_order.lower()
        })
    except Exception as e:
        print(f"查询帖子排行榜出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# 获取用户排行榜
@app.route('/api/user-ranking', methods=['GET'])
def user_ranking():
    conn = get_db_connection()
    
    # 获取分页参数
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 10, type=int)
    offset = (page - 1) * limit
    
    # 获取排序参数
    sort_field = request.args.get('sort_field', 'repost_count')
    sort_order = request.args.get('sort_order', 'desc')
    
    # 验证排序字段，防止SQL注入
    valid_sort_fields = {
        'repost_count': 'a.repost_count',
        'reply_count': 'a.reply_count',
        'delete_count': 'a.delete_count',
        'last_active': 'a.last_active',
        'post_count': 'post_count'
    }
    
    # 默认按重发次数排序
    db_sort_field = valid_sort_fields.get(sort_field, 'a.repost_count')
    
    # 验证排序顺序
    if sort_order.lower() not in ['asc', 'desc']:
        sort_order = 'DESC'
    else:
        sort_order = sort_order.upper()
    
    try:
        # 查询用户排行榜，包含所有用户，并计算每个用户的帖子数
        query = f'''
        WITH user_posts AS (
            SELECT author, COUNT(DISTINCT url) as post_count
            FROM list
            GROUP BY author
        )
        SELECT a.*, COALESCE(up.post_count, 0) as post_count
        FROM authorranking a
        LEFT JOIN user_posts up ON a.author = up.author
        ORDER BY {db_sort_field} {sort_order}, a.repost_count DESC
        LIMIT ? OFFSET ?
        '''
        
        result = conn.execute(query, (limit, offset)).fetchall()
        
        # 获取总记录数
        count_query = 'SELECT COUNT(*) as total FROM authorranking'
        total_count = conn.execute(count_query).fetchone()['total']
        
        return jsonify({
            'data': [dict(row) for row in result],
            'total': total_count,
            'page': page,
            'limit': limit,
            'sort_field': sort_field,
            'sort_order': sort_order.lower()
        })
    except Exception as e:
        print(f"查询用户排行榜出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500
    finally:
        conn.close()

# 创建异动日志缓存表
def init_thread_history_cache():
    """初始化异动日志缓存表"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # 创建异动日志缓存表
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS thread_history_cache (
            url TEXT PRIMARY KEY,
            history_data TEXT,
            last_update TEXT,
            update_count INTEGER DEFAULT 0,
            repost_count INTEGER DEFAULT 0,
            reply_count INTEGER DEFAULT 0,
            delete_count INTEGER DEFAULT 0
        )
        ''')
        conn.commit()
    finally:
        conn.close()

# 计算所有帖子的异动日志
def calculate_all_thread_history():
    """计算并缓存所有帖子的异动日志"""
    print(f"[{datetime.now()}] 开始计算所有帖子的异动日志...")
    conn = get_db_connection()
    try:
        # 获取所有不同的帖子URL
        urls = conn.execute('''
        SELECT DISTINCT url 
        FROM thread_history
        ''').fetchall()
        
        total_urls = len(urls)
        print(f"找到 {total_urls} 个帖子需要处理")
        
        for index, row in enumerate(urls, 1):
            url = row['url']
            try:
                # 获取该帖子的所有异动记录
                history_records = conn.execute('''
                SELECT 
                    id,
                    url,
                    title,
                    author,
                    scraping_time,
                    read_count,
                    reply_count,
                    last_reply_time,
                    update_reason
                FROM thread_history 
                WHERE url = ?
                ORDER BY scraping_time DESC
                ''', (url,)).fetchall()
                
                if not history_records:
                    continue
                
                # 计算各类型更新的次数
                update_count = len(history_records)
                repost_count = sum(1 for r in history_records if r['update_reason'] == '重发')
                reply_count = sum(1 for r in history_records if r['update_reason'] == '回帖')
                delete_count = sum(1 for r in history_records if r['update_reason'] == '删回帖')
                
                # 格式化历史记录
                formatted_history = []
                for record in history_records:
                    history_item = dict(record)
                    # 格式化时间
                    if history_item['scraping_time']:
                        try:
                            dt = datetime.strptime(history_item['scraping_time'], '%Y-%m-%d %H:%M:%S')
                            history_item['scraping_time'] = dt.strftime('%Y/%m/%d %H:%M:%S')
                        except Exception:
                            history_item['scraping_time'] = "未知"
                    
                    if history_item['last_reply_time']:
                        try:
                            dt = datetime.strptime(history_item['last_reply_time'], '%Y-%m-%d %H:%M:%S')
                            history_item['last_reply_time'] = dt.strftime('%Y/%m/%d %H:%M:%S')
                        except Exception:
                            history_item['last_reply_time'] = "未知"
                    
                    formatted_history.append(history_item)
                
                # 更新缓存
                conn.execute('''
                INSERT OR REPLACE INTO thread_history_cache 
                (url, history_data, last_update, update_count, repost_count, reply_count, delete_count)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    url,
                    json.dumps(formatted_history),
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    update_count,
                    repost_count,
                    reply_count,
                    delete_count
                ))
                
                if index % 100 == 0:  # 每处理100个帖子提交一次事务
                    conn.commit()
                    print(f"已处理 {index}/{total_urls} 个帖子")
            
            except Exception as e:
                print(f"处理帖子 {url} 时出错: {str(e)}")
                continue
        
        conn.commit()
        print(f"[{datetime.now()}] 异动日志计算完成，共处理 {total_urls} 个帖子")
    
    except Exception as e:
        print(f"[{datetime.now()}] 计算异动日志时出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

# 修改获取帖子历史的函数，优先使用缓存
@app.route('/api/thread-history', methods=['GET'])
@app.route('/api/thread-history/<path:thread_id>', methods=['GET'])
def get_thread_history(thread_id=None):
    """获取帖子的异动日志"""
    conn = None
    try:
        # 从查询参数或路径参数获取thread_id
        if not thread_id:
            thread_id = request.args.get('thread_id')
        if not thread_id:
            return jsonify({"error": "缺少thread_id参数"}), 400
            
        conn = get_db_connection()
        print(f"正在查询帖子异动日志，thread_id: {thread_id}")
        
        # 先从缓存中查询
        cache_result = conn.execute('''
        SELECT history_data, last_update 
        FROM thread_history_cache 
        WHERE url = ?
        ''', (thread_id,)).fetchone()
        
        if cache_result and cache_result['history_data']:
            history = json.loads(cache_result['history_data'])
            print(f"从缓存中获取到 {len(history)} 条异动记录")
            return jsonify(history)
        
        # 如果缓存中没有，则从原始表中查询
        query = '''
        SELECT 
            id,
            url,
            title,
            author,
            scraping_time,
            read_count,
            reply_count,
            last_reply_time,
            update_reason
        FROM thread_history 
        WHERE url = ?
        ORDER BY scraping_time DESC
        '''
        
        result = conn.execute(query, (thread_id,)).fetchall()
        print(f"从原始表中查询到 {len(result)} 条异动记录")
        
        # 转换结果为列表
        history = []
        for row in result:
            history_item = dict(row)
            # 格式化时间
            if history_item['scraping_time']:
                try:
                    dt = datetime.strptime(history_item['scraping_time'], '%Y-%m-%d %H:%M:%S')
                    history_item['scraping_time'] = dt.strftime('%Y/%m/%d %H:%M:%S')
                except Exception as e:
                    print(f"时间格式化错误 (scraping_time): {str(e)}")
                    history_item['scraping_time'] = "未知"
            
            if history_item['last_reply_time']:
                try:
                    dt = datetime.strptime(history_item['last_reply_time'], '%Y-%m-%d %H:%M:%S')
                    history_item['last_reply_time'] = dt.strftime('%Y/%m/%d %H:%M:%S')
                except Exception as e:
                    print(f"时间格式化错误 (last_reply_time): {str(e)}")
                    history_item['last_reply_time'] = "未知"
            
            history.append(history_item)
        
        if not history:
            print("未找到异动记录")
            return jsonify([])
        
        # 将查询结果存入缓存
        conn.execute('''
        INSERT OR REPLACE INTO thread_history_cache 
        (url, history_data, last_update, update_count, repost_count, reply_count, delete_count)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            thread_id,
            json.dumps(history),
            datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            len(history),
            sum(1 for h in history if h['update_reason'] == '重发'),
            sum(1 for h in history if h['update_reason'] == '回帖'),
            sum(1 for h in history if h['update_reason'] == '删回帖')
        ))
        conn.commit()
        
        return jsonify(history)
        
    except Exception as e:
        print(f"获取帖子异动日志出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": f"获取帖子异动日志失败: {str(e)}"}), 500
    finally:
        if conn:
            conn.close()

# 获取数据趋势
@app.route('/api/data-trends', methods=['GET'])
def data_trends():
    conn = get_db_connection()
    
    # 获取查询参数
    data_type = request.args.get('type', 'post')  # 数据类型：post, update, view
    time_type = request.args.get('time_type', 'daily')  # 时间粒度：hourly, daily, weekly, monthly
    
    # 根据数据类型选择表名
    if data_type == 'post':
        table_name = 'poststatistics'
    elif data_type == 'update':
        table_name = 'updatestatistics'
    elif data_type == 'view':
        table_name = 'viewstatistics'
    else:
        return jsonify({"error": "无效的数据类型"}), 400
    
    # 根据时间粒度设置数据量限制
    if time_type == 'hourly':
        # 小时粒度 - 最新的90个小时
        limit = 90
    elif time_type == 'daily':
        # 日粒度 - 最新的30天
        limit = 30
    elif time_type == 'weekly':
        # 周粒度 - 最新的20周
        limit = 20
    elif time_type == 'monthly':
        # 月粒度 - 最新的20个月
        limit = 20
    else:
        return jsonify({"error": "无效的时间粒度"}), 400
    
    # 查询数据
    try:
        if data_type == 'update':
            # 对于更新趋势，需要先获取时间点列表，然后确保每个时间点都有所有更新类型的数据
            if time_type == 'daily':
                # 获取最近的时间点
                time_query = f'''
                SELECT DISTINCT strftime('%Y-%m-%d', datetime) as date_group
                FROM {table_name}
                ORDER BY date_group DESC
                LIMIT {limit}
                '''
                time_points = [row['date_group'] for row in conn.execute(time_query).fetchall()]
                
                if not time_points:
                    return jsonify([])
                
                # 构建IN子句
                time_placeholders = ','.join(['?'] * len(time_points))
                
                # 查询这些时间点的数据
                query = f'''
                SELECT strftime('%Y-%m-%d', datetime) as date_group, SUM(count) as count, type
                FROM {table_name}
                WHERE strftime('%Y-%m-%d', datetime) IN ({time_placeholders})
                GROUP BY date_group, type
                ORDER BY date_group DESC
                '''
                
                result = conn.execute(query, time_points).fetchall()
                
                # 确保所有时间点都有所有更新类型的数据
                update_types = ['重发', '回帖', '删回帖']
                complete_data = []
                
                for time_point in time_points:
                    for update_type in update_types:
                        found = False
                        for row in result:
                            if row['date_group'] == time_point and row['type'] == update_type:
                                complete_data.append(dict(row))
                                found = True
                                break
                        
                        if not found:
                            complete_data.append({
                                'date_group': time_point,
                                'type': update_type,
                                'count': 0
                            })
                
                return jsonify(complete_data)
                
            elif time_type == 'weekly':
                # 获取最近的时间点
                time_query = f'''
                SELECT DISTINCT strftime('%Y-%W', datetime) as week_group
                FROM {table_name}
                ORDER BY week_group DESC
                LIMIT {limit}
                '''
                time_points = [row['week_group'] for row in conn.execute(time_query).fetchall()]
                
                if not time_points:
                    return jsonify([])
                
                # 构建IN子句
                time_placeholders = ','.join(['?'] * len(time_points))
                
                # 查询这些时间点的数据
                query = f'''
                SELECT strftime('%Y-%W', datetime) as week_group, SUM(count) as count, type
                FROM {table_name}
                WHERE strftime('%Y-%W', datetime) IN ({time_placeholders})
                GROUP BY week_group, type
                ORDER BY week_group DESC
                '''
                
                result = conn.execute(query, time_points).fetchall()
                
                # 确保所有时间点都有所有更新类型的数据
                update_types = ['重发', '回帖', '删回帖']
                complete_data = []
                
                for time_point in time_points:
                    for update_type in update_types:
                        found = False
                        for row in result:
                            if row['week_group'] == time_point and row['type'] == update_type:
                                complete_data.append(dict(row))
                                found = True
                                break
                        
                        if not found:
                            complete_data.append({
                                'week_group': time_point,
                                'type': update_type,
                                'count': 0
                            })
                
                return jsonify(complete_data)
                
            elif time_type == 'monthly':
                # 获取最近的时间点
                time_query = f'''
                SELECT DISTINCT strftime('%Y-%m', datetime) as month_group
                FROM {table_name}
                ORDER BY month_group DESC
                LIMIT {limit}
                '''
                time_points = [row['month_group'] for row in conn.execute(time_query).fetchall()]
                
                if not time_points:
                    return jsonify([])
                
                # 构建IN子句
                time_placeholders = ','.join(['?'] * len(time_points))
                
                # 查询这些时间点的数据
                query = f'''
                SELECT strftime('%Y-%m', datetime) as month_group, SUM(count) as count, type
                FROM {table_name}
                WHERE strftime('%Y-%m', datetime) IN ({time_placeholders})
                GROUP BY month_group, type
                ORDER BY month_group DESC
                '''
                
                result = conn.execute(query, time_points).fetchall()
                
                # 确保所有时间点都有所有更新类型的数据
                update_types = ['重发', '回帖', '删回帖']
                complete_data = []
                
                for time_point in time_points:
                    for update_type in update_types:
                        found = False
                        for row in result:
                            if row['month_group'] == time_point and row['type'] == update_type:
                                complete_data.append(dict(row))
                                found = True
                                break
                        
                        if not found:
                            complete_data.append({
                                'month_group': time_point,
                                'type': update_type,
                                'count': 0
                            })
                
                return jsonify(complete_data)
                
            else:  # hourly
                # 获取最近的时间点
                time_query = f'''
                SELECT DISTINCT datetime
                FROM {table_name}
                ORDER BY datetime DESC
                LIMIT {limit}
                '''
                time_points = [row['datetime'] for row in conn.execute(time_query).fetchall()]
                
                if not time_points:
                    return jsonify([])
                
                # 构建IN子句
                time_placeholders = ','.join(['?'] * len(time_points))
                
                # 查询这些时间点的数据
                query = f'''
                SELECT datetime, SUM(count) as count, type
                FROM {table_name}
                WHERE datetime IN ({time_placeholders})
                GROUP BY datetime, type
                ORDER BY datetime DESC
                '''
                
                result = conn.execute(query, time_points).fetchall()
                
                # 确保所有时间点都有所有更新类型的数据
                update_types = ['重发', '回帖', '删回帖']
                complete_data = []
                
                for time_point in time_points:
                    for update_type in update_types:
                        found = False
                        for row in result:
                            if row['datetime'] == time_point and row['type'] == update_type:
                                complete_data.append(dict(row))
                                found = True
                                break
                        
                        if not found:
                            complete_data.append({
                                'datetime': time_point,
                                'type': update_type,
                                'count': 0
                            })
                
                return jsonify(complete_data)
        
        elif data_type == 'view':
            # 对于阅读趋势，需要包含view_gap字段
            if time_type == 'daily':
                # 按日期分组
                query = f'''
                SELECT strftime('%Y-%m-%d', datetime) as date_group, SUM(count) as count, type, SUM(view_gap) as view_gap
                FROM {table_name}
                GROUP BY date_group, type
                ORDER BY date_group DESC
                LIMIT {limit}
                '''
            elif time_type == 'weekly':
                # 按周分组
                query = f'''
                SELECT strftime('%Y-%W', datetime) as week_group, SUM(count) as count, type, SUM(view_gap) as view_gap
                FROM {table_name}
                GROUP BY week_group, type
                ORDER BY week_group DESC
                LIMIT {limit}
                '''
            elif time_type == 'monthly':
                # 按月分组
                query = f'''
                SELECT strftime('%Y-%m', datetime) as month_group, SUM(count) as count, type, SUM(view_gap) as view_gap
                FROM {table_name}
                GROUP BY month_group, type
                ORDER BY month_group DESC
                LIMIT {limit}
                '''
            else:
                # 按小时分组
                query = f'''
                SELECT datetime, SUM(count) as count, type, SUM(view_gap) as view_gap
                FROM {table_name}
                GROUP BY datetime, type
                ORDER BY datetime DESC
                LIMIT {limit}
                '''
        else:
            # 对于发帖趋势，使用原来的查询
            if time_type == 'daily':
                # 按日期分组
                query = f'''
                SELECT strftime('%Y-%m-%d', datetime) as date_group, SUM(count) as count, type
                FROM {table_name}
                GROUP BY date_group, type
                ORDER BY date_group DESC
                LIMIT {limit}
                '''
            elif time_type == 'weekly':
                # 按周分组
                query = f'''
                SELECT strftime('%Y-%W', datetime) as week_group, SUM(count) as count, type
                FROM {table_name}
                GROUP BY week_group, type
                ORDER BY week_group DESC
                LIMIT {limit}
                '''
            elif time_type == 'monthly':
                # 按月分组
                query = f'''
                SELECT strftime('%Y-%m', datetime) as month_group, SUM(count) as count, type
                FROM {table_name}
                GROUP BY month_group, type
                ORDER BY month_group DESC
                LIMIT {limit}
                '''
            else:
                # 按小时分组
                query = f'''
                SELECT datetime, SUM(count) as count, type
                FROM {table_name}
                GROUP BY datetime, type
                ORDER BY datetime DESC
                LIMIT {limit}
                '''
        
        if data_type != 'update':  # 对于非更新趋势，直接返回查询结果
            result = conn.execute(query).fetchall()
            return jsonify([dict(row) for row in result])
            
    except Exception as e:
        print(f"获取数据趋势出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# 获取更新类型分布
@app.route('/api/update-distribution', methods=['GET'])
def update_distribution():
    conn = get_db_connection()
    
    # 获取查询参数
    time_type = request.args.get('time_type', 'daily')  # 时间粒度：hourly, daily, weekly, monthly
    
    # 根据时间粒度设置数据量限制
    if time_type == 'hourly':
        # 小时粒度 - 最新的90个小时
        limit = 90
    elif time_type == 'daily':
        # 日粒度 - 最新的30天
        limit = 30
    elif time_type == 'weekly':
        # 周粒度 - 最新的20周
        limit = 20
    elif time_type == 'monthly':
        # 月粒度 - 最新的20个月
        limit = 20
    else:
        return jsonify({"error": "无效的时间粒度"}), 400
    
    # 查询数据
    try:
        if time_type == 'hourly':
            # 直接查询最近90个小时的数据，按时间顺序排列
            query = '''
            WITH time_points AS (
                SELECT DISTINCT datetime
                FROM updatestatistics
                WHERE type LIKE 'list_%'
                ORDER BY datetime DESC
                LIMIT ?
            ),
            update_data AS (
                SELECT u.datetime, 
                       SUBSTR(u.type, 6) as updateType, 
                       SUM(u.count) as count
                FROM updatestatistics u
                JOIN time_points t ON u.datetime = t.datetime
                WHERE u.type LIKE 'list_%'
                GROUP BY u.datetime, u.type
            )
            SELECT * FROM update_data
            ORDER BY datetime ASC
            '''
            
            result = conn.execute(query, (limit,)).fetchall()
            
            # 转换为JSON格式
            data = []
            for row in result:
                data.append({
                    'datetime': row['datetime'],
                    'updateType': row['updateType'],
                    'count': row['count']
                })
            
            # 打印调试信息
            print(f"更新分布查询结果 (hourly): {len(data)}条记录")
            if data:
                print(f"时间范围: {data[0]['datetime']} 到 {data[-1]['datetime']}")
                
                # 检查是否有重复的时间点
                time_points = [item['datetime'] for item in data]
                unique_time_points = set(time_points)
                if len(time_points) != len(unique_time_points):
                    print(f"警告: 有重复的时间点! 总数: {len(time_points)}, 唯一数: {len(unique_time_points)}")
                
                # 检查是否有缺失的更新类型
                for i, item in enumerate(data):
                    if i > 0 and data[i-1]['datetime'] == item['datetime'] and data[i-2]['datetime'] == item['datetime']:
                        print(f"  时间点 {item['datetime']} 有多个更新类型")
            
            return jsonify(data)
            
        elif time_type == 'daily':
            # 直接查询最近30天的数据，按时间顺序排列
            query = '''
            WITH time_points AS (
                SELECT DISTINCT strftime('%Y-%m-%d', datetime) as date_group
                FROM updatestatistics
                WHERE type LIKE 'list_%'
                ORDER BY date_group DESC
                LIMIT ?
            ),
            update_data AS (
                SELECT strftime('%Y-%m-%d', u.datetime) as date_group, 
                       SUBSTR(u.type, 6) as updateType, 
                       SUM(u.count) as count
                FROM updatestatistics u
                JOIN time_points t ON strftime('%Y-%m-%d', u.datetime) = t.date_group
                WHERE u.type LIKE 'list_%'
                GROUP BY date_group, u.type
            )
            SELECT * FROM update_data
            ORDER BY date_group ASC
            '''
            
            result = conn.execute(query, (limit,)).fetchall()
            
            # 转换为JSON格式
            data = []
            for row in result:
                data.append({
                    'date_group': row['date_group'],
                    'updateType': row['updateType'],
                    'count': row['count']
                })
            
            return jsonify(data)
            
        elif time_type == 'weekly':
            # 直接查询最近20周的数据，按时间顺序排列
            query = '''
            WITH time_points AS (
                SELECT DISTINCT strftime('%Y-%W', datetime) as week_group
                FROM updatestatistics
                WHERE type LIKE 'list_%'
                ORDER BY week_group DESC
                LIMIT ?
            ),
            update_data AS (
                SELECT strftime('%Y-%W', u.datetime) as week_group, 
                       SUBSTR(u.type, 6) as updateType, 
                       SUM(u.count) as count
                FROM updatestatistics u
                JOIN time_points t ON strftime('%Y-%W', u.datetime) = t.week_group
                WHERE u.type LIKE 'list_%'
                GROUP BY week_group, u.type
            )
            SELECT * FROM update_data
            ORDER BY week_group ASC
            '''
            
            result = conn.execute(query, (limit,)).fetchall()
            
            # 转换为JSON格式
            data = []
            for row in result:
                data.append({
                    'week_group': row['week_group'],
                    'updateType': row['updateType'],
                    'count': row['count']
                })
            
            return jsonify(data)
            
        else:  # monthly
            # 直接查询最近20个月的数据，按时间顺序排列
            query = '''
            WITH time_points AS (
                SELECT DISTINCT strftime('%Y-%m', datetime) as month_group
                FROM updatestatistics
                WHERE type LIKE 'list_%'
                ORDER BY month_group DESC
                LIMIT ?
            ),
            update_data AS (
                SELECT strftime('%Y-%m', u.datetime) as month_group, 
                       SUBSTR(u.type, 6) as updateType, 
                       SUM(u.count) as count
                FROM updatestatistics u
                JOIN time_points t ON strftime('%Y-%m', u.datetime) = t.month_group
                WHERE u.type LIKE 'list_%'
                GROUP BY month_group, u.type
            )
            SELECT * FROM update_data
            ORDER BY month_group ASC
            '''
            
            result = conn.execute(query, (limit,)).fetchall()
            
            # 转换为JSON格式
            data = []
            for row in result:
                data.append({
                    'month_group': row['month_group'],
                    'updateType': row['updateType'],
                    'count': row['count']
                })
            
            return jsonify(data)
        
    except Exception as e:
        print(f"更新分布查询错误: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# 获取用户活跃度排行
@app.route('/api/user-activity', methods=['GET'])
def user_activity():
    conn = get_db_connection()
    
    # 查询数据
    query = '''
    SELECT 
        author as username,
        author_link as userUrl,
        SUM(count) as totalPosts,
        SUM(repost_count) as repostCount,
        MAX(last_active) as lastActiveTime,
        'user_' || REPLACE(author, ' ', '_') as id
    FROM data_trends
    WHERE author != ''
    GROUP BY author
    ORDER BY totalPosts DESC
    LIMIT 100
    '''
    
    result = conn.execute(query).fetchall()
    
    # 添加排名和用户等级
    ranked_results = []
    for i, row in enumerate(result):
        row_dict = dict(row)
        row_dict['rank'] = i + 1
        row_dict['userLevel'] = min(10, 1 + (row_dict['totalPosts'] // 50))  # 简单的用户等级计算
        row_dict['avatar'] = f"https://randomuser.me/api/portraits/men/{i+1}.jpg"  # 模拟头像
        ranked_results.append(row_dict)
    
    conn.close()
    
    return jsonify(ranked_results)

@app.route('/api/test-update-hourly', methods=['GET'])
def test_update_hourly():
    """测试API，检查updatestatistics表中是否有小时粒度的数据"""
    conn = get_db_connection()
    try:
        # 查询所有不同的datetime值
        query = '''
        SELECT DISTINCT datetime
        FROM updatestatistics
        ORDER BY datetime DESC
        LIMIT 20
        '''
        datetime_results = conn.execute(query).fetchall()
        
        # 查询所有不同的update_reason值
        query = '''
        SELECT DISTINCT update_reason
        FROM updatestatistics
        WHERE update_reason != ''
        '''
        reason_results = conn.execute(query).fetchall()
        
        # 查询一些示例数据
        query = '''
        SELECT datetime, update_reason, count
        FROM updatestatistics
        WHERE update_reason != ''
        ORDER BY datetime DESC
        LIMIT 20
        '''
        sample_results = conn.execute(query).fetchall()
        
        # 查询表的总记录数
        query = '''
        SELECT COUNT(*) as total
        FROM updatestatistics
        '''
        count_result = conn.execute(query).fetchone()
        
        result = {
            'datetime_values': [dict(row) for row in datetime_results],
            'reason_values': [dict(row) for row in reason_results],
            'sample_data': [dict(row) for row in sample_results],
            'total_records': dict(count_result)['total']
        }
        
        conn.close()
        return jsonify(result)
    except Exception as e:
        conn.close()
        return jsonify({"error": str(e)}), 500

@app.route('/api/test-posts', methods=['GET'])
def test_posts():
    """测试API，检查数据库中的帖子数据"""
    conn = get_db_connection()
    result = {"tables": [], "data": {}}
    
    try:
        # 获取所有表
        tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        result["tables"] = [table[0] for table in tables]
        
        # 检查可能包含帖子数据的表
        possible_tables = ['list', 'post', 'posts']
        
        for table in possible_tables:
            if table in result["tables"]:
                # 检查表结构
                columns = [column[1] for column in conn.execute(f"PRAGMA table_info({table})").fetchall()]
                result["data"][table] = {"columns": columns}
                
                # 获取记录数
                count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                result["data"][table]["count"] = count
                
                # 获取最新的10条记录
                if count > 0:
                    records = conn.execute(f"SELECT * FROM {table} ORDER BY rowid DESC LIMIT 10").fetchall()
                    result["data"][table]["records"] = [dict(record) for record in records]
                    
                    # 如果有post_time列，检查日期格式
                    if 'post_time' in columns:
                        date_samples = [record['post_time'] for record in records if record['post_time']]
                        result["data"][table]["date_samples"] = date_samples
        
        conn.close()
        return jsonify(result)
    except Exception as e:
        import traceback
        traceback.print_exc()
        conn.close()
        return jsonify({"error": str(e)}), 500

# 初始化词云缓存表
def init_wordcloud_cache():
    """初始化词云缓存表"""
    conn = get_db_connection()
    try:
        cursor = conn.cursor()
        # 检查表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='wordcloud_cache'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            # 创建词云缓存表
            cursor.execute('''
            CREATE TABLE wordcloud_cache (
                id INTEGER PRIMARY KEY,
                data TEXT,
                created_date TEXT,
                version INTEGER,
                expire_date TEXT
            )
            ''')
            conn.commit()
        else:
            # 检查是否需要更新表结构
            cursor.execute("PRAGMA table_info(wordcloud_cache)")
            columns = [column[1] for column in cursor.fetchall()]
            
            # 如果缺少version列，添加它
            if 'version' not in columns:
                cursor.execute("ALTER TABLE wordcloud_cache ADD COLUMN version INTEGER DEFAULT 1")
            
            # 如果缺少expire_date列，添加它
            if 'expire_date' not in columns:
                cursor.execute("ALTER TABLE wordcloud_cache ADD COLUMN expire_date TEXT")
            
            conn.commit()
    finally:
        conn.close()

# 生成词云数据
def generate_wordcloud():
    """生成词云数据并缓存到数据库"""
    print(f"[{datetime.now()}] 开始生成词云数据...")
    conn = get_db_connection()
    try:
        # 从list表获取所有标题
        query = "SELECT title FROM list WHERE title IS NOT NULL AND title != ''"
        titles = conn.execute(query).fetchall()
        
        # 对所有标题进行分词
        words = []
        for title in titles:
            # 使用jieba进行中文分词
            words.extend(jieba.cut(title[0]))
        
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
        
        if not filtered_words:
            print("没有找到有效的词语")
            return None
        
        # 计算词云数据
        max_count = max(filtered_words.values())
        min_count = min(filtered_words.values())
        
        # 生成词云数据
        word_cloud_data = []
        
        # 按词频排序并限制数量（增加显示词汇数量）
        sorted_words = sorted(filtered_words.items(), key=lambda x: x[1], reverse=True)[:300]  # 增加到300个词
        
        # 将词语按大小分组（调整比例，增加数量）
        large_words = sorted_words[:20]    # 大词增加到20个
        medium_words = sorted_words[20:75] # 中词调整为55个
        small_words = sorted_words[75:300] # 小词保持225个
        
        def check_collision(x, y, width, height, used_boxes, overlap_ratio=0.01):
            """检查给定位置是否与已有词语碰撞，几乎不允许重叠"""
            box = (x - width/2, y - height/2, x + width/2, y + height/2)
            box_area = (box[2] - box[0]) * (box[3] - box[1])
            
            for used_box in used_boxes:
                # 计算重叠区域
                x_overlap = max(0, min(box[2], used_box[2]) - max(box[0], used_box[0]))
                y_overlap = max(0, min(box[3], used_box[3]) - max(box[1], used_box[1]))
                overlap_area = x_overlap * y_overlap
                
                # 如果重叠面积超过允许的比例，则认为发生碰撞
                if overlap_area > box_area * overlap_ratio:
                    return True
            return False
        
        # 定义不同区域的布局参数
        layouts = [
            # 中心区域（大词）
            {
                'words': large_words,
                'x_range': (-450, 450),  # 缩小范围，使大词更集中
                'y_range': (-120, 120),  # 缩小范围，使大词更集中
                'size_range': (90, 130),  # 增大字体大小
                'overlap_ratio': 0.01  # 几乎不允许重叠
            },
            # 中间区域（中词）
            {
                'words': medium_words,
                'x_range': (-750, 750),  # 调整范围
                'y_range': (-160, 160),  # 调整范围
                'size_range': (40, 65),  # 调整字体大小
                'overlap_ratio': 0.01  # 几乎不允许重叠
            },
            # 外围区域（小词）
            {
                'words': small_words,
                'x_range': (-1100, 1100),  # 调整范围，避免过于分散
                'y_range': (-180, 180),  # 保持y范围
                'size_range': (18, 30),  # 调整字体大小
                'overlap_ratio': 0.01  # 几乎不允许重叠
            }
        ]
        
        # 记录已使用的边界框
        used_boxes = []
        
        # 预定义的颜色列表
        predefined_colors = [
            '#a61b29', '#c04851', '#7a7374', '#2d0c13', '#8b2671',
            '#525288', '#22202e', '#2376b7', '#4e7ca1', '#474b4c',
            '#22a2c3', '#248067', '#12aa9c', '#8a988e', '#2b312c',
            '#bec936', '#fbda41', '#645822', '#fb8b05', '#e16723',
            '#4b2e2b', '#363433', '#b7d07a', '#1a6840'
        ]
        
        # 为每个区域布局词语
        for layout in layouts:
            for word, count in layout['words']:
                # 计算字体大小
                min_size, max_size = layout['size_range']
                size = min_size + (count - min_count) * (max_size - min_size) / (max_count - min_count)
                
                # 估算词语占用的空间（根据字数和字体大小）
                word_width = len(word) * size * 0.6  # 假设每个字符宽度是字体大小的0.6倍
                word_height = size * 1.2  # 假设高度是字体大小的1.2倍
                
                # 在区域内寻找合适的位置
                found_position = False
                min_x, max_x = layout['x_range']
                min_y, max_y = layout['y_range']
                
                # 从中心向外螺旋搜索
                spiral_step = 0
                max_attempts = 500  # 最大尝试次数
                
                # 对于大词和中词，优先尝试中心位置
                if word in [w for w, _ in large_words[:5]] or word in [w for w, _ in medium_words[:10]]:
                    # 中心区域优先
                    center_attempts = 50
                    center_radius = 100  # 中心区域半径
                    for i in range(center_attempts):
                        # 在中心区域随机选择位置
                        angle = random.random() * 2 * math.pi
                        radius = random.random() * center_radius
                        x = radius * math.cos(angle)
                        y = radius * math.sin(angle)
                        
                        # 确保在布局范围内
                        x = max(min_x + word_width/2, min(max_x - word_width/2, x))
                        y = max(min_y + word_height/2, min(max_y - word_height/2, y))
                        
                        if not check_collision(x, y, word_width, word_height, 
                                            used_boxes, layout['overlap_ratio']):
                            found_position = True
                            # 记录这个词的边界框
                            box = (x - word_width/2,
                                  y - word_height/2,
                                  x + word_width/2,
                                  y + word_height/2)
                            used_boxes.append(box)
                            
                            # 从预定义颜色列表中随机选择一个颜色
                            color = random.choice(predefined_colors)
                            
                            # 所有词语都不旋转
                            rotate = 0
                            
                            word_cloud_data.append({
                                'text': word,
                                'size': size,
                                'count': count,
                                'x': x,
                                'y': y,
                                'rotate': rotate,
                                'color': color
                            })
                            break
                
                # 如果中心位置没找到，或者是小词，则使用螺旋搜索
                while spiral_step < max_attempts and not found_position:
                    # 使用黄金角度来创建更自然的分布
                    golden_angle = math.pi * (3 - math.sqrt(5))
                    angle = spiral_step * golden_angle
                    
                    # 根据词的大小调整螺旋步长
                    if word in [w for w, _ in large_words]:
                        step_scale = 3.0  # 大词步长大一些，分布更开
                    elif word in [w for w, _ in medium_words]:
                        step_scale = 2.5  # 中词步长适中
                    else:
                        step_scale = 2.0  # 小词步长小一些，分布更密集
                    
                    radius = spiral_step * step_scale
                    
                    x = radius * math.cos(angle)
                    y = radius * math.sin(angle)
                    
                    # 确保在布局范围内
                    x = max(min_x + word_width/2, min(max_x - word_width/2, x))
                    y = max(min_y + word_height/2, min(max_y - word_height/2, y))
                    
                    if not check_collision(x, y, word_width, word_height, 
                                        used_boxes, layout['overlap_ratio']):
                        found_position = True
                        # 记录这个词的边界框
                        box = (x - word_width/2,
                              y - word_height/2,
                              x + word_width/2,
                              y + word_height/2)
                        used_boxes.append(box)
                        
                        # 从预定义颜色列表中随机选择一个颜色
                        color = random.choice(predefined_colors)
                        
                        # 所有词语都不旋转
                        rotate = 0
                        
                        word_cloud_data.append({
                            'text': word,
                            'size': size,
                            'count': count,
                            'x': x,
                            'y': y,
                            'rotate': rotate,
                            'color': color
                        })
                        break
                    
                    spiral_step += 1
        
        # 保存到数据库
        today = datetime.now().strftime('%Y-%m-%d')
        expire_date = (datetime.now() + timedelta(days=WORDCLOUD_CACHE_DAYS)).strftime('%Y-%m-%d')
        
        cursor = conn.cursor()
        # 删除当天的旧缓存
        cursor.execute("DELETE FROM wordcloud_cache WHERE created_date = ?", (today,))
        # 插入新缓存
        cursor.execute(
            "INSERT INTO wordcloud_cache (data, created_date, version, expire_date) VALUES (?, ?, ?, ?)", 
            (json.dumps(word_cloud_data), today, WORDCLOUD_VERSION, expire_date)
        )
        # 清理过期缓存
        cursor.execute("DELETE FROM wordcloud_cache WHERE expire_date < ?", (today,))
        conn.commit()
        
        # 更新内存缓存
        _word_cloud_cache['data'] = word_cloud_data
        _word_cloud_cache['date'] = today
        _word_cloud_cache['version'] = WORDCLOUD_VERSION
        
        print(f"[{datetime.now()}] 词云数据生成完成，共{len(word_cloud_data)}个词")
        return word_cloud_data
    except Exception as e:
        print(f"[{datetime.now()}] 生成词云数据出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return None
    finally:
        conn.close()

# 获取标题词云数据
@app.route('/api/title-wordcloud', methods=['GET'])
def title_wordcloud():
    """获取所有标题的词云数据"""
    # 检查是否请求强制刷新
    force_refresh = request.args.get('refresh', '0') == '1'
    
    conn = get_db_connection()
    try:
        # 确保词云缓存表存在
        init_wordcloud_cache()
        
        if not force_refresh:
            # 检查是否有今天的缓存数据
            today = datetime.now().strftime('%Y-%m-%d')
            cursor = conn.cursor()
            cursor.execute(
                "SELECT data FROM wordcloud_cache WHERE created_date = ? AND version = ?", 
                (today, WORDCLOUD_VERSION)
            )
            cached_data = cursor.fetchone()
            
            if cached_data:
                # 如果有缓存数据，直接返回
                return jsonify(json.loads(cached_data[0]))
        
        # 如果没有缓存或强制刷新，生成新的词云数据
        word_cloud_data = generate_wordcloud()
        
        if word_cloud_data is None:
            # 如果生成失败，尝试返回最近的缓存
            cursor = conn.cursor()
            cursor.execute(
                "SELECT data FROM wordcloud_cache WHERE version = ? ORDER BY created_date DESC LIMIT 1", 
                (WORDCLOUD_VERSION,)
            )
            latest_cache = cursor.fetchone()
            
            if latest_cache:
                return jsonify(json.loads(latest_cache[0]))
            else:
                return jsonify([])
        
        return jsonify(word_cloud_data)
        
    except Exception as e:
        print(f"获取词云数据出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify([])
    finally:
        conn.close()

# 手动刷新词云缓存
@app.route('/api/refresh-wordcloud', methods=['POST'])
def refresh_wordcloud():
    """手动刷新词云缓存"""
    try:
        word_cloud_data = generate_wordcloud()
        if word_cloud_data is not None:
            return jsonify({"success": True, "message": "词云数据已刷新", "count": len(word_cloud_data)})
        else:
            return jsonify({"success": False, "message": "刷新词云数据失败，请查看服务器日志"})
    except Exception as e:
        return jsonify({"success": False, "message": f"刷新词云数据出错: {str(e)}"})

# 更新关注帖子的异动记录
def update_follow_history():
    """更新所有关注帖子的异动记录"""
    print(f"[{datetime.now()}] 开始更新关注帖子的异动记录...")
    conn = get_db_connection()
    try:
        # 获取所有关注的帖子
        follows = conn.execute('SELECT DISTINCT url FROM thread_follows').fetchall()
        
        for follow in follows:
            url = follow['url']
            try:
                # 获取最新的异动记录时间
                latest_history = conn.execute('''
                SELECT MAX(scraping_time) as last_time 
                FROM follow_history 
                WHERE url = ?
                ''', (url,)).fetchone()
                
                last_time = latest_history['last_time'] if latest_history else None
                
                # 查询新的异动记录
                query = '''
                SELECT * FROM thread_history 
                WHERE url = ?
                '''
                params = [url]
                
                if last_time:
                    query += ' AND scraping_time > ?'
                    params.append(last_time)
                
                query += ' ORDER BY scraping_time DESC'
                
                new_records = conn.execute(query, params).fetchall()
                
                # 添加新的异动记录
                for record in new_records:
                    conn.execute('''
                    INSERT INTO follow_history 
                    (url, title, author, scraping_time, read_count, reply_count, 
                     last_reply_time, update_reason)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        url,
                        record['title'],
                        record['author'],
                        record['scraping_time'],
                        record['read_count'],
                        record['reply_count'],
                        record['last_reply_time'],
                        record['update_reason']
                    ))
                
                # 更新帖子信息
                if new_records:
                    latest = new_records[0]
                    conn.execute('''
                    UPDATE thread_follows 
                    SET title = ?, author = ?, read_count = ?, reply_count = ?
                    WHERE url = ?
                    ''', (
                        latest['title'],
                        latest['author'],
                        latest['read_count'],
                        latest['reply_count'],
                        url
                    ))
                
                conn.commit()
                print(f"[{datetime.now()}] 已更新帖子 {url} 的异动记录，新增 {len(new_records)} 条记录")
                
            except Exception as e:
                print(f"[{datetime.now()}] 更新帖子 {url} 的异动记录失败: {str(e)}")
                continue
        
    except Exception as e:
        print(f"[{datetime.now()}] 更新关注帖子的异动记录出错: {str(e)}")
        import traceback
        traceback.print_exc()
    finally:
        conn.close()

# 在定时任务函数中添加更新关注帖子的异动记录
def run_scheduler():
    """运行定时任务"""
    global scheduler_running
    
    # 设置每天凌晨2点生成词云数据
    schedule.every().day.at("02:00").do(generate_wordcloud)
    # 每小时更新一次关注帖子的异动记录
    schedule.every(1).hours.do(update_follow_history)
    
    print(f"[{datetime.now()}] 定时任务已启动")
    print("- 每天02:00生成词云数据")
    print("- 每小时更新关注帖子的异动记录")
    
    while scheduler_running:
        schedule.run_pending()
        time.sleep(60)  # 每分钟检查一次

# 启动定时任务
def start_scheduler():
    """启动定时任务线程"""
    global scheduler_thread, scheduler_running
    
    if scheduler_thread is None or not scheduler_thread.is_alive():
        scheduler_running = True
        scheduler_thread = threading.Thread(target=run_scheduler)
        scheduler_thread.daemon = True  # 设为守护线程，主线程结束时自动结束
        scheduler_thread.start()
        print(f"[{datetime.now()}] 词云数据定时生成任务已启动")

# 获取关注列表
@app.route('/api/thread-follows', methods=['GET'])
def get_thread_follows():
    """获取关注列表"""
    conn = None
    try:
        follow_type = request.args.get('type', 'my_follow')
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        offset = (page - 1) * limit
        
        print(f"正在获取关注列表: type={follow_type}, page={page}, limit={limit}")
        
        if follow_type not in ['my_follow', 'my_thread']:
            return jsonify({"error": "无效的关注类型"}), 400
            
        conn = get_db_connection()
        
        # 获取总数
        total = conn.execute(
            'SELECT COUNT(*) FROM thread_follows WHERE follow_type = ?',
            (follow_type,)
        ).fetchone()[0]
        
        print(f"找到 {total} 条关注记录")
        
        # 获取关注列表，包含所有信息
        query = '''
        SELECT 
            tf.*,
            tf.url as thread_id,
            (
                SELECT json_group_array(json_object(
                    'id', fh.id,
                    'url', fh.url,
                    'title', fh.title,
                    'author', fh.author,
                    'scraping_time', fh.scraping_time,
                    'read_count', fh.read_count,
                    'reply_count', fh.reply_count,
                    'last_reply_time', fh.last_reply_time,
                    'update_reason', fh.update_reason
                ))
                FROM follow_history fh
                WHERE fh.url = tf.url
                ORDER BY fh.scraping_time DESC
            ) as history
        FROM thread_follows tf
        WHERE tf.follow_type = ?
        ORDER BY tf.created_at DESC
        LIMIT ? OFFSET ?
        '''
        
        result = conn.execute(query, (follow_type, limit, offset)).fetchall()
        
        # 转换结果为列表
        follows = []
        for row in result:
            follow_dict = dict(row)
            # 确保所有字段都有值，避免 None
            follow_dict['title'] = follow_dict.get('title') or ''
            follow_dict['author'] = follow_dict.get('author') or ''
            follow_dict['author_link'] = follow_dict.get('author_link') or ''
            follow_dict['read_count'] = follow_dict.get('read_count') or 0
            follow_dict['reply_count'] = follow_dict.get('reply_count') or 0
            follow_dict['repost_count'] = follow_dict.get('repost_count') or 0
            follow_dict['delete_count'] = follow_dict.get('delete_count') or 0
            follow_dict['days_old'] = follow_dict.get('days_old') or 0
            follow_dict['last_active'] = follow_dict.get('last_active') or 0
            
            # 解析历史记录的JSON字符串
            try:
                import json
                history_str = follow_dict.get('history')
                follow_dict['history'] = json.loads(history_str) if history_str else []
            except Exception as e:
                print(f"解析历史记录失败: {str(e)}")
                follow_dict['history'] = []
            
            follows.append(follow_dict)
        
        print(f"成功获取 {len(follows)} 条关注记录")
        
        return jsonify({
            "data": follows,
            "total": total,
            "page": page,
            "limit": limit
        })
    except Exception as e:
        print(f"获取关注列表失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "获取关注列表失败，请稍后重试", "details": str(e)}), 500
    finally:
        if conn:
            conn.close()

# 添加关注
@app.route('/api/thread-follows', methods=['POST'])
def add_thread_follow():
    """添加关注"""
    try:
        data = request.get_json()
        thread_id = data.get('thread_id')
        follow_type = data.get('follow_type')
        thread_info = data.get('thread_info', {})
        
        # 获取 url，如果不存在则使用 thread_id
        url = thread_info.get('url') or thread_id
        
        if not url:
            return jsonify({"error": "缺少必要参数 url"}), 400
        if not follow_type:
            return jsonify({"error": "缺少必要参数 follow_type"}), 400
        if follow_type not in ['my_follow', 'my_thread']:
            return jsonify({"error": "无效的关注类型"}), 400
            
        conn = get_db_connection()
        
        try:
            # 开始事务
            conn.execute('BEGIN')
            
            # 检查是否已经关注
            existing = conn.execute(
                'SELECT * FROM thread_follows WHERE url = ? AND follow_type = ?', 
                (url, follow_type)
            ).fetchone()
            
            if not existing:
                print(f"添加新的关注记录: {url}")
                # 如果还没有关注，添加新的关注记录
                conn.execute('''
                INSERT INTO thread_follows 
                (url, follow_type, title, author, author_link, read_count, 
                 reply_count, repost_count, delete_count, days_old, last_active)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    url,
                    follow_type,
                    thread_info.get('title', ''),
                    thread_info.get('author', ''),
                    thread_info.get('author_link', ''),
                    thread_info.get('read_count', 0),
                    thread_info.get('reply_count', 0),
                    thread_info.get('repost_count', 0),
                    thread_info.get('delete_count', 0),
                    thread_info.get('days_old', 0),
                    thread_info.get('last_active', 0)
                ))
                
                # 从 thread_history 表获取所有历史异动记录
                print(f"获取帖子历史记录: {url}")
                history_records = conn.execute('''
                SELECT * FROM thread_history 
                WHERE url = ?
                ORDER BY scraping_time DESC
                ''', (url,)).fetchall()
                
                print(f"找到 {len(history_records)} 条历史记录")
                
                # 将历史记录添加到 follow_history 表
                for record in history_records:
                    conn.execute('''
                    INSERT INTO follow_history 
                    (url, title, author, scraping_time, read_count, reply_count, 
                     last_reply_time, update_reason)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        url,
                        record['title'],
                        record['author'],
                        record['scraping_time'],
                        record['read_count'],
                        record['reply_count'],
                        record['last_reply_time'],
                        record['update_reason']
                    ))
            
            # 提交事务
            conn.commit()
            print(f"成功添加关注和历史记录")
            return jsonify({"success": True})
            
        except Exception as e:
            # 回滚事务
            conn.rollback()
            print(f"添加关注失败: {str(e)}")
            raise e
            
    except Exception as e:
        print(f"添加关注失败: {str(e)}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

# 获取异动日志
@app.route('/api/action-logs', methods=['GET'])
def get_action_logs():
    """获取异动日志"""
    try:
        # 获取查询参数
        thread_id = request.args.get('thread_id')
        url = request.args.get('url')
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        offset = (page - 1) * limit
        
        # 构建查询条件
        conditions = []
        params = []
        
        if thread_id:
            conditions.append("thread_id = ?")
            params.append(thread_id)
        if url:
            conditions.append("url = ?")
            params.append(url)
            
        # 如果没有提供任何条件，返回错误
        if not conditions:
            return jsonify({"error": "必须提供thread_id或url参数"}), 400
            
        conn = get_db_connection()
        
        # 构建查询语句
        where_clause = " OR ".join(conditions)
        
        # 获取总数
        count_query = f"SELECT COUNT(*) FROM action WHERE {where_clause}"
        total = conn.execute(count_query, params).fetchone()[0]
        
        # 获取异动记录，使用正确的字段名
        query = f"""
        SELECT 
            thread_id, 
            url, 
            title, 
            author, 
            action_time, 
            action_type as action, 
            reason as action_reason,
            source
        FROM action 
        WHERE {where_clause}
        ORDER BY action_time DESC
        LIMIT ? OFFSET ?
        """
        
        params.extend([limit, offset])
        result = conn.execute(query, params).fetchall()
        
        # 转换结果为列表
        logs = []
        for row in result:
            log = dict(row)
            # 合并action_type和reason字段
            log['action'] = f"{log['action']}({log['action_reason']})" if log['action_reason'] else log['action']
            del log['action_reason']  # 删除多余的字段
            logs.append(log)
            
        return jsonify({
            "data": logs,
            "total": total,
            "page": page,
            "limit": limit
        })
        
    except Exception as e:
        print(f"获取异动日志失败: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": "获取异动日志失败，请稍后重试"}), 500
    finally:
        if conn:
            conn.close()

# 导入车辆信息
@app.route('/api/import-car-info', methods=['POST'])
def import_car_info():
    try:
        conn = get_db_connection()
        
        # 读取CSV文件
        csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed', 'car_info.csv')
        df = pd.read_csv(csv_path)
        
        # 获取帖子信息，用于关联
        posts_df = pd.read_sql("SELECT url, author, post_time FROM posts", conn)
        posts_dict = dict(zip(posts_df['url'], zip(posts_df['author'], posts_df['post_time'])))
        
        # 计算导入时间
        now = datetime.now()
        
        # 准备批量插入
        records = []
        for _, row in df.iterrows():
            # 跳过trade_type为"不知道"的记录
            if row['trade_type'] == '不知道':
                continue
                
            url = row['url']
            thread_id = url.split('/')[-1].split('.')[0].replace('t_', '')
            
            # 从posts表获取作者和发帖时间
            author = None
            post_time = None
            last_active = None
            daysold = None
            
            if url in posts_dict:
                author, post_time = posts_dict[url]
                
                # 计算daysold
                if post_time:
                    try:
                        post_datetime = datetime.strptime(post_time, '%Y-%m-%d %H:%M:%S')
                        daysold = (now - post_datetime).days
                        # 假设最后活跃时间为当前时间，实际应从thread_history表获取
                        last_active = now.strftime('%Y-%m-%d %H:%M:%S')
                    except:
                        pass
            
            # 准备记录
            record = (
                url,
                int(row['year']) if not pd.isna(row['year']) else None,
                row['make'] if not pd.isna(row['make']) else None,
                row['model'] if not pd.isna(row['model']) else None,
                row['miles'] if not pd.isna(row['miles']) else None,
                row['price'] if not pd.isna(row['price']) else None,
                row['trade_type'] if not pd.isna(row['trade_type']) else None,
                row['location'] if not pd.isna(row['location']) else None,
                thread_id,
                author,
                post_time,
                daysold,
                last_active
            )
            records.append(record)
        
        # 先清空表
        conn.execute("DELETE FROM car_info")
        
        # 批量插入
        conn.executemany("""
            INSERT INTO car_info (url, year, make, model, miles, price, trade_type, location, thread_id, author, post_time, daysold, last_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, records)
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': f'成功导入{len(records)}条车辆信息记录',
            'count': len(records)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'导入失败: {str(e)}'
        }), 500

# 获取车辆信息列表
@app.route('/api/car-info', methods=['GET'])
def get_car_info():
    try:
        # 获取查询参数
        page = int(request.args.get('page', 1))
        page_size = int(request.args.get('pageSize', 20))
        search = request.args.get('search', '')
        
        # 计算偏移量
        offset = (page - 1) * page_size
        
        conn = get_db_connection()
        
        # 构建查询语句
        query = "SELECT * FROM car_info WHERE 1=1"
        params = []
        
        # 添加搜索条件
        if search:
            query += " AND (year LIKE ? OR make LIKE ? OR model LIKE ?)"
            search_param = f"%{search}%"
            params.extend([search_param, search_param, search_param])
        
        # 添加排序 - daysold正序、last_active正序（数值越小表示越活跃）
        query += " ORDER BY daysold ASC, last_active ASC"
        
        # 添加分页
        query += " LIMIT ? OFFSET ?"
        params.extend([page_size, offset])
        
        # 执行查询
        result = conn.execute(query, params).fetchall()
        
        # 获取总记录数
        count_query = "SELECT COUNT(*) as count FROM car_info WHERE 1=1"
        count_params = []
        
        if search:
            count_query += " AND (year LIKE ? OR make LIKE ? OR model LIKE ?)"
            search_param = f"%{search}%"
            count_params.extend([search_param, search_param, search_param])
        
        total = conn.execute(count_query, count_params).fetchone()['count']
        
        # 转换结果为字典列表
        car_list = []
        for row in result:
            car_list.append({
                'id': row['id'],
                'url': row['url'],
                'year': row['year'],
                'make': row['make'],
                'model': row['model'],
                'miles': row['miles'],
                'price': row['price'],
                'trade_type': row['trade_type'],
                'location': row['location'],
                'thread_id': row['thread_id'],
                'author': row['author'],
                'post_time': row['post_time'],
                'daysold': row['daysold'],
                'last_active': row['last_active']
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'data': car_list,
            'total': total,
            'page': page,
            'pageSize': page_size
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'获取车辆信息失败: {str(e)}'
        }), 500

if __name__ == '__main__':
    # 确保数据库目录存在
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    
    # 初始化数据库
    init_db()
    
    # 初始化词云缓存表
    init_wordcloud_cache()
    
    # 初始化异动日志缓存表
    init_thread_history_cache()
    
    # 计算所有帖子的异动日志
    calculate_all_thread_history()
    
    # 启动定时任务
    start_scheduler()
    
    app.run(debug=DEBUG, host=HOST, port=PORT) 