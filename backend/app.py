"""
主应用模块，提供REST API服务
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
from datetime import datetime, timedelta
import time
import random
import sqlite3

# 导入模块
from modules.db_utils import get_db_connection, dict_factory
from modules.wordcloud import get_wordcloud
from modules.rankings import get_post_ranking, get_author_ranking, get_thread_history, get_author_history
from modules.trends import get_post_trend, get_update_trend, get_view_trend, get_data_trends, get_new_posts
from create_missing_tables import create_thread_follow_table

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("app")

# 数据库路径
DB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db')
DB_PATH = os.path.join(DB_DIR, 'forum_data.db')

# 创建应用
app = Flask(__name__, static_folder='../frontend/build', static_url_path='/')
CORS(app)  # 启用CORS以允许前端访问

# API前缀
API_PREFIX = '/api'

# 健康检查接口
@app.route(f'{API_PREFIX}/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    try:
        # 检查数据库连接
        conn = get_db_connection()
        conn.execute("SELECT 1").fetchone()
        conn.close()
        
        return jsonify({
            'status': 'ok',
            'message': '服务运行正常',
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"健康检查失败: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': f'服务异常: {str(e)}',
            'timestamp': datetime.now().isoformat()
        }), 500

# 词云API
@app.route(f'{API_PREFIX}/title-wordcloud', methods=['GET'])
def title_wordcloud():
    """获取标题词云数据"""
    try:
        wordcloud_data = get_wordcloud()
        
        # 确保数据格式正确
        if isinstance(wordcloud_data, list):
            # 转换为前端期望的数据结构
            for item in wordcloud_data:
                # 确保每项都有text和value
                if 'text' not in item or 'value' not in item:
                    logger.warning(f"词云数据格式不正确: {item}")
            
            # 直接返回数组，因为前端期望词云API返回数组
            return jsonify(wordcloud_data)
        else:
            logger.warning(f"词云数据非列表类型: {type(wordcloud_data)}")
            return jsonify([{"text": "数据", "value": 100}])
    except Exception as e:
        logger.error(f"获取词云数据失败: {str(e)}")
        # 返回默认数据，确保前端不会因为错误而崩溃
        return jsonify([
            {"text": "汽车", "value": 100},
            {"text": "二手车", "value": 80},
            {"text": "出售", "value": 70},
            {"text": "求购", "value": 60},
            {"text": "交易", "value": 50}
        ])

# 帖子排行API
@app.route(f'{API_PREFIX}/post-rank', methods=['GET'])
def post_rank():
    """获取帖子排行数据"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        sort_field = request.args.get('sort_field', 'repost_count')
        sort_order = request.args.get('sort_order', 'desc')
        
        # 记录请求参数
        logger.info(f"接收到帖子排行请求: page={page}, limit={limit}, sort_field={sort_field}, sort_order={sort_order}")
        
        # 检查参数有效性
        if page < 1:
            page = 1
            logger.warning(f"页码参数无效，已重置为1")
        if limit < 1 or limit > 100:
            limit = 20
            logger.warning(f"每页数量参数无效，已重置为20")
        
        # 调用排行榜模块获取数据
        ranking_data = get_post_ranking(page, limit, sort_field, sort_order)
        
        # 记录返回数据的信息
        if isinstance(ranking_data, dict) and 'data' in ranking_data:
            data_count = len(ranking_data['data']) if ranking_data['data'] else 0
            total_count = ranking_data.get('total', 0)
            logger.info(f"返回帖子排行数据: {data_count}条记录, 总计{total_count}条")
        else:
            logger.warning(f"排行榜返回格式不正确: {type(ranking_data)}")
            
        # 确保返回的数据格式是完整的
        if not isinstance(ranking_data, dict) or 'data' not in ranking_data:
            ranking_data = {
                'data': ranking_data if isinstance(ranking_data, list) else [],
                'total': len(ranking_data) if isinstance(ranking_data, list) else 0,
                'page': page,
                'limit': limit
            }
            
        return jsonify(ranking_data)
    except Exception as e:
        logger.error(f"获取帖子排行数据失败: {str(e)}")
        return jsonify({"data": [], "total": 0, "page": 1, "limit": 20, "error": str(e)}), 500

# 作者排行API
@app.route(f'{API_PREFIX}/author-rank', methods=['GET'])
def author_rank():
    """获取作者排行数据"""
    try:
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 20, type=int)
        sort_field = request.args.get('sort_field', 'repost_count')
        sort_order = request.args.get('sort_order', 'desc')
        
        # 记录请求参数
        logger.info(f"接收到作者排行请求: page={page}, limit={limit}, sort_field={sort_field}, sort_order={sort_order}")
        
        # 检查参数有效性
        if page < 1:
            page = 1
            logger.warning(f"页码参数无效，已重置为1")
        if limit < 1 or limit > 100:
            limit = 20
            logger.warning(f"每页数量参数无效，已重置为20")
            
        # 调用排行榜模块获取数据
        ranking_data = get_author_ranking(page, limit, sort_field, sort_order)
        
        # 记录返回数据的信息
        if isinstance(ranking_data, dict) and 'data' in ranking_data:
            data_count = len(ranking_data['data']) if ranking_data['data'] else 0
            total_count = ranking_data.get('total', 0)
            logger.info(f"返回作者排行数据: {data_count}条记录, 总计{total_count}条")
        else:
            logger.warning(f"排行榜返回格式不正确: {type(ranking_data)}")
            
        # 确保返回的数据格式是完整的
        if not isinstance(ranking_data, dict) or 'data' not in ranking_data:
            ranking_data = {
                'data': ranking_data if isinstance(ranking_data, list) else [],
                'total': len(ranking_data) if isinstance(ranking_data, list) else 0,
                'page': page,
                'limit': limit
            }
            
        return jsonify(ranking_data)
    except Exception as e:
        logger.error(f"获取作者排行数据失败: {str(e)}")
        return jsonify({"data": [], "total": 0, "page": 1, "limit": 20, "error": str(e)}), 500

# 帖子历史API
@app.route(f'{API_PREFIX}/thread-history/<thread_id>', methods=['GET'])
def thread_history(thread_id):
    """获取帖子历史"""
    try:
        result = get_thread_history(thread_id)
        return jsonify({'data': result})
    except Exception as e:
        logger.error(f"获取帖子历史出错: {str(e)}")
        return jsonify({'data': [], 'error': str(e)})

# 作者历史API
@app.route(f'{API_PREFIX}/author-history/<author>', methods=['GET'])
def author_history(author):
    """获取作者历史"""
    try:
        result = get_author_history(author)
        return jsonify({'data': result})
    except Exception as e:
        logger.error(f"获取作者历史出错: {str(e)}")
        return jsonify({'data': [], 'error': str(e)})

# 发帖趋势API
@app.route(f'{API_PREFIX}/post-trend', methods=['GET'])
def post_trend_api():
    """
    获取发帖趋势数据
    """
    try:
        # 获取granularity参数，可从type或granularity获取，默认为daily
        granularity = request.args.get('type', request.args.get('granularity', 'daily'))
        
        # 获取真实数据
        trend_data = get_post_trend(granularity)
        
        # 仅在没有数据时才输出警告，但不使用模拟数据
        if not trend_data:
            logging.warning(f"未找到发帖趋势数据(data_category='post_statistics')，当前granularity={granularity}")
        
        return jsonify({'data': trend_data})
    except Exception as e:
        logging.error(f"获取发帖趋势数据出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 更新趋势API
@app.route(f'{API_PREFIX}/update-trend', methods=['GET'])
def update_trend_api():
    """
    获取更新趋势数据
    """
    try:
        # 获取granularity参数，可从type或granularity获取，默认为daily
        granularity = request.args.get('type', request.args.get('granularity', 'daily'))
        
        # 获取真实数据
        trend_data = get_update_trend(granularity)
        
        # 仅在没有数据时才输出警告，但不使用模拟数据
        if not trend_data:
            logging.warning(f"未找到更新趋势数据(data_category='update_statistics')，当前granularity={granularity}")
        
        return jsonify({'data': trend_data})
    except Exception as e:
        logging.error(f"获取更新趋势数据出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 阅读趋势API
@app.route(f'{API_PREFIX}/view-trend', methods=['GET'])
def view_trend_api():
    """
    获取阅读趋势数据
    """
    try:
        # 获取granularity参数，可从type或granularity获取，默认为daily
        granularity = request.args.get('type', request.args.get('granularity', 'daily'))
        
        # 获取真实数据
        trend_data = get_view_trend(granularity)
        
        # 仅在没有数据时才输出警告，但不使用模拟数据
        if not trend_data:
            logging.warning(f"未找到阅读趋势数据(data_category='view_statistics')，当前granularity={granularity}")
        
        return jsonify({'data': trend_data})
    except Exception as e:
        logging.error(f"获取阅读趋势数据出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 数据趋势API
@app.route(f'{API_PREFIX}/data-trends', methods=['GET'])
def data_trends_api():
    """
    获取综合数据趋势
    """
    try:
        days = request.args.get('days', 30, type=int)
        granularity = request.args.get('type', request.args.get('granularity', 'daily'))
        
        # 获取真实数据趋势
        trends_data = get_data_trends(days, granularity)
        
        # 如果没有combined字段，尝试使用combined_data字段
        if 'combined' not in trends_data and 'combined_data' in trends_data:
            trends_data['combined'] = trends_data['combined_data']
        
        # 如果仍然没有combined字段，根据已有数据创建一个
        if 'combined' not in trends_data:
            # 合并所有趋势数据
            combined_data = []
            
            # 添加发帖趋势
            for item in trends_data.get('post_trend', []):
                if item.get('datetime') and item.get('count') is not None:
                    combined_data.append({
                        'datetime': item['datetime'],
                        'count': item['count'],
                        'type': 'post'
                    })
            
            # 添加更新趋势
            for item in trends_data.get('update_trend', []):
                if item.get('datetime') and item.get('count') is not None:
                    data_item = {
                        'datetime': item['datetime'],
                        'count': item['count'],
                        'type': 'update'
                    }
                    if 'type' in item:
                        data_item['subtype'] = item['type']
                    combined_data.append(data_item)
            
            # 添加阅读趋势
            for item in trends_data.get('view_trend', []):
                if item.get('datetime') and item.get('count') is not None:
                    combined_data.append({
                        'datetime': item['datetime'],
                        'count': item['count'],
                        'type': 'view'
                    })
            
            trends_data['combined'] = combined_data
        
        # 仅在找不到数据时输出警告，不使用模拟数据
        if not trends_data.get('post_trend') and not trends_data.get('update_trend') and not trends_data.get('view_trend'):
            logging.warning(f"未找到趋势数据，当前granularity={granularity}, days={days}")
        
        return jsonify({'data': trends_data})
    except Exception as e:
        logging.error(f"获取数据趋势出错: {str(e)}")
        return jsonify({'error': str(e)}), 500

# 新帖列表API
@app.route(f'{API_PREFIX}/new-posts-yesterday', methods=['GET'])
def new_posts_yesterday():
    """获取昨日新帖"""
    try:
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        # 获取日期参数
        date = request.args.get('date')
        
        result = get_new_posts(date, page, limit)
        return jsonify(result)
    except Exception as e:
        logger.error(f"获取昨日新帖出错: {str(e)}")
        return jsonify({
            'data': [],
            'total': 0,
            'page': request.args.get('page', 1, type=int),
            'limit': request.args.get('limit', 10, type=int),
            'date': None,
            'error': str(e)
        })

# 以下是为了兼容前端API调用而添加的路由

@app.route(f'{API_PREFIX}/thread-ranking', methods=['GET'])
def thread_ranking():
    """线程排行（兼容旧API）"""
    return post_rank()

@app.route(f'{API_PREFIX}/user-ranking', methods=['GET'])
def user_ranking():
    """用户排行（兼容旧API）"""
    return author_rank()

@app.route(f'{API_PREFIX}/update-distribution', methods=['GET'])
def update_distribution():
    """更新分布（兼容旧API）"""
    try:
        # 返回空数据
        return jsonify({"data": []})
    except Exception as e:
        logger.error(f"获取更新分布数据失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route(f'{API_PREFIX}/user-activity', methods=['GET'])
def user_activity():
    """用户活动（兼容旧API）"""
    try:
        # 返回空数据
        return jsonify({"data": []})
    except Exception as e:
        logger.error(f"获取用户活动数据失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route(f'{API_PREFIX}/post-date-range', methods=['GET'])
def post_date_range():
    """帖子日期范围（兼容旧API）"""
    try:
        # 尝试从数据库中获取真实的日期范围
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 首先检查posts表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='posts'")
        if not cursor.fetchone():
            logger.warning("posts表不存在，返回空日期范围")
            return jsonify({
                "start_date": None,
                "end_date": None,
                "min_date": None,
                "max_date": None
            })
        
        # 获取最早和最晚的帖子日期
        cursor.execute("""
            SELECT MIN(post_time) as start_date, MAX(post_time) as end_date 
            FROM posts 
            WHERE post_time IS NOT NULL
        """)
        
        date_range = cursor.fetchone()
        conn.close()
        
        if date_range and date_range['start_date'] and date_range['end_date']:
            return jsonify({
                "start_date": date_range['start_date'],
                "end_date": date_range['end_date'],
                "min_date": date_range['start_date'],  # 添加前端需要的字段
                "max_date": date_range['end_date']     # 添加前端需要的字段
            })
        else:
            # 如果没有数据，返回空日期
            return jsonify({
                "start_date": None,
                "end_date": None,
                "min_date": None,  # 添加前端需要的字段
                "max_date": None   # 添加前端需要的字段
            })
    except Exception as e:
        logger.error(f"获取帖子日期范围失败: {str(e)}")
        return jsonify({"error": str(e), "start_date": None, "end_date": None, "min_date": None, "max_date": None}), 500

@app.route(f'{API_PREFIX}/author-post-logs', methods=['GET'])
def author_post_logs():
    """作者发帖日志（兼容旧API）"""
    try:
        # 返回空数据
        return jsonify({"data": []})
    except Exception as e:
        logger.error(f"获取作者发帖日志失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route(f'{API_PREFIX}/thread-follows', methods=['GET', 'POST', 'DELETE'])
def thread_follows():
    """获取、添加或删除关注"""
    try:
        if request.method == 'GET':
            follow_type = request.args.get('type', 'my_follow')
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 根据类型查询不同状态的数据
            status = 'followed' if follow_type == 'my_follow' else 'my_thread'
            
            # 修改查询语句，关联post_ranking表获取完整数据
            query = """
                SELECT 
                    tf.id,
                    tf.thread_id, 
                    tf.url, 
                    tf.title, 
                    tf.author, 
                    tf.author_link,
                    COALESCE(pr.repost_count, 0) as repost_count,
                    COALESCE(pr.reply_count, 0) as reply_count,
                    COALESCE(pr.delete_reply_count, 0) as delete_reply_count,
                    COALESCE(pr.daysold, 0) as days_old,
                    COALESCE(pr.last_active, 0) as last_active,
                    tf.follow_status, 
                    tf.created_at, 
                    tf.updated_at
                FROM thread_follow tf
                LEFT JOIN post_ranking pr ON tf.thread_id = pr.thread_id OR tf.url = pr.url
                WHERE tf.follow_status = ?
                ORDER BY tf.created_at DESC
            """
            
            cursor.execute(query, (status,))
            rows = cursor.fetchall()
            
            conn.close()
            
            return jsonify({
                "data": rows,
                "total": len(rows)
            })
        
        elif request.method == 'POST':
            data = request.get_json()
            if not data or 'thread_id' not in data or 'type' not in data:
                return jsonify({"error": "缺少必要参数"}), 400
                
            thread_id = data['thread_id']
            follow_type = data['type']
            
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 更新关注状态
            status = 'followed' if follow_type == 'my_follow' else 'my_thread'
            now = datetime.now().isoformat()
            
            # 检查是否已存在
            cursor.execute("""
                SELECT id FROM thread_follow 
                WHERE thread_id = ?
            """, (thread_id,))
            
            existing = cursor.fetchone()
            
            if existing:
                # 更新状态
                cursor.execute("""
                    UPDATE thread_follow 
                    SET follow_status = ?, updated_at = ?
                    WHERE thread_id = ?
                """, (status, now, thread_id))
            else:
                # 从post_ranking获取帖子信息
                cursor.execute("""
                    SELECT url, title, author, author_link
                    FROM post_ranking
                    WHERE thread_id = ?
                """, (thread_id,))
                
                post_info = cursor.fetchone()
                
                if post_info:
                    # 插入新记录
                    cursor.execute("""
                        INSERT INTO thread_follow (
                            thread_id, url, title, author, author_link,
                            follow_status, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (
                        thread_id,
                        post_info['url'],  # 使用键名而不是索引
                        post_info['title'],
                        post_info['author'],
                        post_info['author_link'],
                        status,
                        now,
                        now
                    ))
                else:
                    # 如果在post_ranking中找不到，使用基本信息创建
                    cursor.execute("""
                        INSERT INTO thread_follow (
                            thread_id, follow_status, created_at, updated_at
                        ) VALUES (?, ?, ?, ?)
                    """, (thread_id, status, now, now))
            
            conn.commit()
            conn.close()
            
            return jsonify({
                "message": "关注成功",
                "status": status
            })
            
        elif request.method == 'DELETE':
            data = request.get_json()
            if not data:
                return jsonify({"error": "缺少请求数据"}), 400
                
            thread_id = data.get('thread_id')
            title = data.get('title')
            url = data.get('url')
            follow_type = data.get('type', 'my_follow')
            
            # 至少需要提供一个标识符
            if not thread_id and not title and not url:
                return jsonify({"error": "缺少必要参数，请提供thread_id, title或url"}), 400
                
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # 根据类型确定状态
            status = 'followed' if follow_type == 'my_follow' else 'my_thread'
            
            # 构建查询条件
            where_clause = "follow_status = ?"
            params = [status]
            
            if thread_id:
                # 同时匹配数字形式和字符串形式的thread_id
                where_clause += " AND (thread_id = ? OR thread_id LIKE ?)" 
                params.extend([thread_id, f"%{thread_id}%"])
            
            if title:
                where_clause += " AND title LIKE ?"
                params.append(f"%{title}%")
                
            if url:
                where_clause += " AND url LIKE ?"
                params.append(f"%{url}%")
            
            # 获取要删除的记录ID
            query = f"SELECT id FROM thread_follow WHERE {where_clause}"
            logger.info(f"查询语句: {query}, 参数: {params}")
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            if rows:
                ids = [row['id'] for row in rows]
                placeholders = ', '.join(['?' for _ in ids])
                # 删除符合条件的记录
                cursor.execute(f"DELETE FROM thread_follow WHERE id IN ({placeholders})", ids)
                conn.commit()
                affected_rows = conn.total_changes
                logger.info(f"已删除{affected_rows}条关注记录")
                
                conn.close()
                return jsonify({
                    "message": f"成功取消关注，共删除{affected_rows}条记录",
                    "affected_rows": affected_rows
                })
            else:
                conn.close()
                logger.warning(f"未找到符合条件的关注记录: thread_id={thread_id}, title={title}, url={url}, status={status}")
                return jsonify({
                    "message": "未找到符合条件的关注记录",
                    "affected_rows": 0
                }), 404
            
    except Exception as e:
        logger.error(f"处理关注请求失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route(f'{API_PREFIX}/action-logs', methods=['GET'])
def action_logs():
    """操作日志（兼容旧API）"""
    try:
        # 获取请求参数
        thread_id = request.args.get('thread_id')
        url = request.args.get('url')
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        # 至少需要提供thread_id或url参数之一
        if not thread_id and not url:
            return jsonify({"error": "请提供thread_id或url参数"}), 400
        
        # 调试日志
        logger.info(f"接收到action_logs请求: thread_id={thread_id}, url={url}, page={page}, limit={limit}")
        
        # 优先使用thread_id，如果有的话
        conn = get_db_connection()
        # 使用dict_factory确保输出为字典
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        
        try:
            # 先检查post_history表是否存在
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='post_history'")
            if not cursor.fetchone():
                logger.warning("post_history表不存在")
                return jsonify({"data": [], "total": 0, "page": page, "limit": limit})
            
            # 构建查询条件 - 优先使用thread_id
            params = []
            if thread_id:
                # 使用字符串匹配，因为数据库中thread_id是TEXT类型
                where_str = "thread_id = ?"
                params.append(str(thread_id))
                
                # 检查是否有匹配的记录
                cursor.execute(f"SELECT COUNT(*) as count FROM post_history WHERE {where_str}", params)
                result = cursor.fetchone()
                count = result['count'] if result else 0
                
                # 如果没有记录，尝试模糊匹配URL
                if count == 0 and url:
                    params = []
                    where_str = "url LIKE ?"
                    params.append(f"%{url}%")
                    
                    # 再次检查是否有匹配记录
                    cursor.execute(f"SELECT COUNT(*) as count FROM post_history WHERE {where_str}", params)
                    result = cursor.fetchone()
                    count = result['count'] if result else 0
                    
                    if count == 0:
                        # 如果仍然没有找到记录，返回空结果
                        logger.warning(f"未找到thread_id={thread_id}或url包含{url}的记录")
                        return jsonify({"data": [], "total": 0, "page": page, "limit": limit})
            else:
                # URL可能是完整URL或部分URL
                where_str = "url LIKE ?"
                params.append(f"%{url}%")
            
            # 查询总记录数
            count_sql = f"SELECT COUNT(*) as count FROM post_history WHERE {where_str}"
            cursor.execute(count_sql, params)
            result = cursor.fetchone()
            total = result['count'] if result else 0
            
            logger.info(f"找到 {total} 条与条件匹配的记录")
            
            # 计算分页
            offset = (page - 1) * limit
            
            # 查询数据
            data_sql = f"""
            SELECT * FROM post_history 
            WHERE {where_str}
            ORDER BY action_time DESC
            LIMIT ? OFFSET ?
            """
            
            # 使用列表拼接参数
            all_params = params + [limit, offset]
            logger.info(f"执行查询: {data_sql}, 参数: {all_params}")
            
            cursor.execute(data_sql, all_params)
            rows = cursor.fetchall()
            
            # 处理结果
            result = []
            for row in rows:
                # row是字典，直接添加
                item = dict(row)
                
                # 将'action'映射为'event_type'以兼容前端
                if 'action' in item:
                    item['event_type'] = item['action']
                if 'action_time' in item:
                    item['event_time'] = item['action_time']
                
                result.append(item)
            
            # 调试日志
            logger.info(f"查询到 {len(result)} 条帖子历史记录, 总计 {total} 条")
            
            # 关闭连接
            conn.close()
            
            # 返回标准格式数据
            return jsonify({
                "data": result,
                "total": total,
                "page": page,
                "limit": limit
            })
            
        except Exception as e:
            logger.error(f"查询action_logs出错: {str(e)}")
            if conn:
                conn.close()
            
            # 返回空数据而不是500错误，保证前端能正常显示
            return jsonify({
                "data": [],
                "total": 0,
                "page": page,
                "limit": limit,
                "error": f"数据库查询错误: {str(e)}"
            })
            
    except Exception as e:
        logger.error(f"获取操作日志失败: {str(e)}")
        # 返回空数据而不是500错误
        return jsonify({
            "data": [],
            "total": 0, 
            "page": page if 'page' in locals() else 1,
            "limit": limit if 'limit' in locals() else 10,
            "error": f"服务器错误: {str(e)}"
        })

@app.route(f'{API_PREFIX}/author-post-history', methods=['GET'])
def author_post_history():
    """获取作者的发帖历史"""
    try:
        author = request.args.get('author')
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        if not author:
            return jsonify({"error": "请提供作者参数"}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            # 1. 获取所有帖子 (从posts表中作者的所有帖子)
            cursor.execute("""
                SELECT url, title, post_time 
                FROM posts 
                WHERE author = ? 
                GROUP BY url
            """, (author,))
            all_posts = cursor.fetchall()
            
            # 将所有帖子转换为字典
            all_posts_dict = {}
            for post in all_posts:
                url = post['url']
                all_posts_dict[url] = {
                    'url': url,
                    'title': post['title'] or '无标题',
                    'post_time': post['post_time'],
                    'is_active': False  # 初始设置为非活跃
                }
            
            # 2. 获取活跃帖子 (在list表最新抓取日期中存在的帖子)
            # 首先获取最新的scraping_time_R
            cursor.execute("SELECT MAX(scraping_time_R) as latest_time FROM list")
            latest_time_result = cursor.fetchone()
            latest_time = latest_time_result['latest_time'] if latest_time_result else None
            print(f"最新抓取时间(scraping_time_R): {latest_time}")
            
            cursor.execute("""
                SELECT DISTINCT url FROM list 
                WHERE author = ? AND scraping_time_R = (
                    SELECT MAX(scraping_time_R) FROM list
                )
            """, (author,))
            active_posts = cursor.fetchall()
            
            # 记录调试信息
            print(f"作者 {author} 的活跃帖子数量: {len(active_posts)}")
            if active_posts:
                print(f"活跃帖子URL示例: {active_posts[0]['url'] if len(active_posts) > 0 else 'None'}")
            
            # 标记活跃帖子
            for post in active_posts:
                if post['url'] in all_posts_dict:
                    all_posts_dict[post['url']]['is_active'] = True
            
            # 将字典转换回列表并按post_time倒序排序
            result_posts = list(all_posts_dict.values())
            result_posts.sort(key=lambda x: x['post_time'] if x['post_time'] else '', reverse=True)
            
            # 计算总数量
            total_count = len(result_posts)
            
            # 分页处理
            start_idx = (page - 1) * limit
            end_idx = start_idx + limit
            paged_posts = result_posts[start_idx:end_idx] if start_idx < total_count else []
            
            # 格式化返回数据
            response_data = {
                "data": paged_posts,
                "total": total_count,
                "page": page,
                "limit": limit
            }
            
            # 添加调试信息
            # 统计不活跃帖子数量
            inactive_posts = sum(1 for post in result_posts if not post['is_active'])
            response_data["debug"] = {
                "total_posts": total_count,
                "active_posts": total_count - inactive_posts,
                "inactive_posts": inactive_posts
            }
            
            return jsonify(response_data)
        
        except Exception as e:
            logger.error(f"查询作者发帖历史出错: {str(e)}")
            return jsonify({
                "data": [],
                "total": 0,
                "page": page,
                "limit": limit,
                "error": f"数据库查询错误: {str(e)}"
            })
        finally:
            if conn:
                conn.close()
    
    except Exception as e:
        logger.error(f"获取作者发帖历史失败: {str(e)}")
        return jsonify({
            "data": [],
            "total": 0,
            "page": 1,
            "limit": 10,
            "error": f"服务器错误: {str(e)}"
        })

@app.route(f'{API_PREFIX}/post-rank/batch', methods=['POST'])
def post_rank_batch():
    """批量获取帖子排行数据"""
    try:
        data = request.get_json()
        if not data or 'thread_ids' not in data:
            return jsonify({"error": "请提供thread_ids参数"}), 400
            
        thread_ids = data['thread_ids']
        if not thread_ids:
            return jsonify({"data": [], "total": 0})
            
        # 构建查询条件
        placeholders = ','.join(['?' for _ in thread_ids])
        query = f"""
            SELECT thread_id, url, title, author, author_link, 
                   repost_count, reply_count, delete_reply_count,
                   daysold, last_active
            FROM post_ranking 
            WHERE thread_id IN ({placeholders})
            OR url IN ({placeholders})
        """
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # 执行查询，参数需要传递两次因为有两个IN条件
        cursor.execute(query, thread_ids + thread_ids)
        rows = cursor.fetchall()
        
        # 获取列名
        columns = [description[0] for description in cursor.description]
        
        # 转换为字典列表
        result = []
        for row in rows:
            item = {}
            for i, column in enumerate(columns):
                item[column] = row[i]
            result.append(item)
            
        conn.close()
        
        return jsonify({
            "data": result,
            "total": len(result)
        })
        
    except Exception as e:
        logger.error(f"批量获取帖子排行数据失败: {str(e)}")
        return jsonify({"error": str(e)}), 500

# 汽车信息API
@app.route(f'{API_PREFIX}/cars', methods=['GET'])
def get_cars():
    """获取汽车信息列表"""
    try:
        # 获取请求参数
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 5000, type=int)  # 默认值改为5000
        offset = (page - 1) * limit
        
        # 搜索参数
        make = request.args.get('make', '')
        model = request.args.get('model', '')
        year_min = request.args.get('year_min', '')
        year_max = request.args.get('year_max', '')
        price_min = request.args.get('price_min', '')
        price_max = request.args.get('price_max', '')
        sort_field = request.args.get('sort_field', 'id')
        sort_order = request.args.get('sort_order', 'desc')
        
        # 连接数据库
        conn = get_db_connection()
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        
        # 构建SQL条件
        conditions = []
        params = []
        
        if make:
            conditions.append("make LIKE ?")
            params.append(f"%{make}%")
        
        if model:
            conditions.append("model LIKE ?")
            params.append(f"%{model}%")
        
        if year_min:
            conditions.append("year >= ?")
            params.append(year_min)
        
        if year_max:
            conditions.append("year <= ?")
            params.append(year_max)
        
        if price_min:
            conditions.append("price >= ?")
            params.append(price_min)
        
        if price_max:
            conditions.append("price <= ?")
            params.append(price_max)
        
        # 构建WHERE子句
        where_clause = " AND ".join(conditions) if conditions else "1=1"
        
        # 获取总记录数
        cursor.execute(f"SELECT COUNT(*) as total FROM car_info WHERE {where_clause}", params)
        total = cursor.fetchone()['total']
        
        # 获取分页数据
        query = f"""
        SELECT * FROM car_info 
        WHERE {where_clause} 
        ORDER BY {sort_field} {sort_order} 
        LIMIT ? OFFSET ?
        """
        cursor.execute(query, params + [limit, offset])
        cars = cursor.fetchall()
        
        # 获取所有可用品牌和型号（用于过滤）
        cursor.execute("SELECT DISTINCT make FROM car_info WHERE make IS NOT NULL AND make != '-' ORDER BY make")
        makes = [row['make'] for row in cursor.fetchall()]
        
        cursor.execute("SELECT DISTINCT model FROM car_info WHERE model IS NOT NULL AND model != '-' ORDER BY model")
        models = [row['model'] for row in cursor.fetchall()]
        
        conn.close()
        
        # 组装返回数据
        response = {
            'data': cars,
            'meta': {
                'total': total,
                'page': page,
                'limit': limit,
                'pages': (total + limit - 1) // limit,
                'makes': makes,
                'models': models
            }
        }
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"获取汽车信息失败: {str(e)}")
        return jsonify({
            'error': f'获取汽车信息失败: {str(e)}',
            'data': [],
            'meta': {
                'total': 0,
                'page': 1,
                'limit': 20,
                'pages': 0
            }
        }), 500

# 汽车信息详情API
@app.route(f'{API_PREFIX}/cars/<car_id>', methods=['GET'])
def get_car_detail(car_id):
    """获取汽车信息详情"""
    try:
        # 连接数据库
        conn = get_db_connection()
        conn.row_factory = dict_factory
        cursor = conn.cursor()
        
        # 查询汽车信息
        cursor.execute("SELECT * FROM car_info WHERE id = ?", (car_id,))
        car = cursor.fetchone()
        
        if not car:
            return jsonify({'error': f'找不到ID为{car_id}的汽车信息'}), 404
        
        # 查询相关帖子
        cursor.execute("""
        SELECT p.*, a.name as author_name 
        FROM posts p
        LEFT JOIN authors a ON p.author_id = a.id
        WHERE p.url = ?
        """, (car['url'],))
        post = cursor.fetchone()
        
        conn.close()
        
        # 组装返回数据
        response = {
            'car': car,
            'post': post
        }
        
        return jsonify(response)
    except Exception as e:
        logger.error(f"获取汽车详情失败: {str(e)}")
        return jsonify({'error': f'获取汽车详情失败: {str(e)}'}), 500

# 启动服务
    # 确保thread_follow表存在
    create_thread_follow_table()
if __name__ == '__main__':
    # 从环境变量获取主机和端口
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    
    logger.info(f"启动服务，监听: {host}:{port}, 调试模式: {debug}")
    app.run(host=host, port=port, debug=debug) 