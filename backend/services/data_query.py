import sqlite3
from datetime import datetime, timedelta

def get_db_connection(db_path):
    """获取数据库连接"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_new_posts_yesterday(db_path):
    """获取昨日新帖"""
    conn = get_db_connection(db_path)
    yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    
    posts = conn.execute('''
    SELECT * FROM posts 
    WHERE post_time LIKE ? || '%' 
    ORDER BY post_time DESC
    ''', (yesterday,)).fetchall()
    
    conn.close()
    
    return [dict(post) for post in posts]

def get_post_trend(db_path, time_type='daily'):
    """获取帖子趋势数据"""
    conn = get_db_connection(db_path)
    
    if time_type == 'hourly':
        # 小时粒度
        limit = 120
        date_format = '%Y-%m-%d %H:00:00'
    elif time_type == 'daily':
        # 日粒度
        limit = 60
        date_format = '%Y-%m-%d'
    elif time_type == 'weekly':
        # 周粒度
        limit = 20
        date_format = '%Y-%W'
    else:
        # 月粒度
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
    
    return [dict(row) for row in result]

def get_update_trend(db_path, time_type='daily'):
    """获取更新数据趋势"""
    conn = get_db_connection(db_path)
    
    if time_type == 'hourly':
        date_format = '%Y-%m-%d %H:00:00'
        limit = 120
    elif time_type == 'daily':
        date_format = '%Y-%m-%d'
        limit = 60
    elif time_type == 'weekly':
        date_format = '%Y-%W'
        limit = 20
    else:
        date_format = '%Y-%m'
        limit = 20
    
    # 根据更新原因聚合数据
    query = f'''
    SELECT 
        strftime('{date_format}', scraping_time) as datetime,
        update_reason as updateType,
        COUNT(*) as count
    FROM thread_history
    GROUP BY datetime, updateType
    ORDER BY datetime DESC
    LIMIT {limit * 3}
    '''
    
    result = conn.execute(query).fetchall()
    conn.close()
    
    return [dict(row) for row in result]

def get_view_trend(db_path, time_type='daily'):
    """获取浏览数据趋势"""
    conn = get_db_connection(db_path)
    
    if time_type == 'hourly':
        date_format = '%Y-%m-%d %H:00:00'
    elif time_type == 'daily':
        date_format = '%Y-%m-%d'
    elif time_type == 'weekly':
        date_format = '%Y-%W'
    else:
        date_format = '%Y-%m'
    
    # 查询浏览数据趋势
    query = f'''
    SELECT 
        strftime('{date_format}', scraping_time) as datetime,
        SUM(view_count) as views
    FROM thread_history
    GROUP BY datetime
    ORDER BY datetime DESC
    '''
    
    result = conn.execute(query).fetchall()
    conn.close()
    
    return [dict(row) for row in result]

def get_thread_ranking(db_path, limit=100):
    """获取帖子排行榜"""
    conn = get_db_connection(db_path)
    
    # 查询重发次数最多的帖子
    query = f'''
    SELECT 
        p.thread_id,
        p.title,
        p.author,
        p.author_url as authorUrl,
        p.forum,
        p.views as viewCount,
        p.page_num as pageNum,
        p.num,
        COUNT(DISTINCT th.scraping_time) as repostCount,
        MAX(th.scraping_time) as lastUpdateTime,
        'thread_' || p.thread_id as id
    FROM posts p
    JOIN thread_history th ON p.thread_id = th.thread_id
    GROUP BY p.thread_id
    ORDER BY repostCount DESC
    LIMIT {limit}
    '''
    
    result = conn.execute(query).fetchall()
    
    # 添加排名
    ranked_results = []
    for i, row in enumerate(result):
        row_dict = dict(row)
        row_dict['rank'] = i + 1
        row_dict['threadUrl'] = f"https://example.com/thread/{row_dict['thread_id']}"
        ranked_results.append(row_dict)
    
    conn.close()
    
    return ranked_results

def get_user_ranking(db_path, limit=100):
    """获取用户排行榜"""
    conn = get_db_connection(db_path)
    
    # 查询发帖最多的用户
    query = f'''
    SELECT 
        author as username,
        author_url as userUrl,
        COUNT(DISTINCT thread_id) as totalPosts,
        COUNT(DISTINCT th.id) as repostCount,
        MAX(th.scraping_time) as lastActiveTime,
        'user_' || REPLACE(author, ' ', '_') as id,
        '' as avatar
    FROM posts p
    JOIN thread_history th ON p.thread_id = th.thread_id
    GROUP BY author
    ORDER BY repostCount DESC
    LIMIT {limit}
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
    
    return ranked_results

def get_thread_history(db_path, thread_id):
    """获取帖子历史"""
    conn = get_db_connection(db_path)
    
    history = conn.execute('''
    SELECT * FROM thread_history
    WHERE thread_id = ?
    ORDER BY scraping_time DESC
    ''', (thread_id,)).fetchall()
    
    conn.close()
    
    return [dict(record) for record in history] 