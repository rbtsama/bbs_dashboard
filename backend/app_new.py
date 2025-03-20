"""
主应用模块，提供REST API服务
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import logging
import os
from datetime import datetime

# 导入模块
from modules.db_utils import get_db_connection
from modules.wordcloud import get_wordcloud
from modules.rankings import get_post_ranking, get_author_ranking, get_thread_history, get_author_history
from modules.trends import get_post_trend, get_update_trend, get_view_trend, get_new_posts

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("app")

# 创建应用
app = Flask(__name__)
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
        data = get_wordcloud()
        return jsonify(data)
    except Exception as e:
        logger.error(f"获取词云数据出错: {str(e)}")
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
    """获取帖子排行榜"""
    try:
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        # 获取排序参数
        sort_field = request.args.get('sort_field', 'repost_count')
        sort_order = request.args.get('sort_order', 'desc')
        
        result = get_post_ranking(page, limit, sort_field, sort_order)
        return jsonify(result)
    except Exception as e:
        logger.error(f"获取帖子排行榜出错: {str(e)}")
        return jsonify({
            'data': [],
            'total': 0,
            'page': request.args.get('page', 1, type=int),
            'limit': request.args.get('limit', 10, type=int),
            'error': str(e)
        })

# 作者排行API
@app.route(f'{API_PREFIX}/author-rank', methods=['GET'])
def author_rank():
    """获取作者排行榜"""
    try:
        # 获取分页参数
        page = request.args.get('page', 1, type=int)
        limit = request.args.get('limit', 10, type=int)
        
        # 获取排序参数
        sort_field = request.args.get('sort_field', 'repost_count')
        sort_order = request.args.get('sort_order', 'desc')
        
        result = get_author_ranking(page, limit, sort_field, sort_order)
        return jsonify(result)
    except Exception as e:
        logger.error(f"获取作者排行榜出错: {str(e)}")
        return jsonify({
            'data': [],
            'total': 0,
            'page': request.args.get('page', 1, type=int),
            'limit': request.args.get('limit', 10, type=int),
            'error': str(e)
        })

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
def post_trend():
    """获取发帖趋势"""
    try:
        time_type = request.args.get('type', 'daily')
        result = get_post_trend(time_type)
        return jsonify(result)
    except Exception as e:
        logger.error(f"获取发帖趋势出错: {str(e)}")
        return jsonify([])

# 更新趋势API
@app.route(f'{API_PREFIX}/update-trend', methods=['GET'])
def update_trend():
    """获取更新趋势"""
    try:
        time_type = request.args.get('type', 'daily')
        result = get_update_trend(time_type)
        return jsonify(result)
    except Exception as e:
        logger.error(f"获取更新趋势出错: {str(e)}")
        return jsonify([])

# 阅读趋势API
@app.route(f'{API_PREFIX}/view-trend', methods=['GET'])
def view_trend():
    """获取阅读趋势"""
    try:
        time_type = request.args.get('type', 'daily')
        result = get_view_trend(time_type)
        return jsonify(result)
    except Exception as e:
        logger.error(f"获取阅读趋势出错: {str(e)}")
        return jsonify([])

# 整合趋势API
@app.route(f'{API_PREFIX}/data-trends', methods=['GET'])
def data_trends():
    """获取整合趋势数据"""
    try:
        data_type = request.args.get('type', 'post')
        time_type = request.args.get('time_type', 'daily')
        
        # 根据数据类型调用相应的处理函数
        if data_type == 'post':
            return jsonify(get_post_trend(time_type))
        elif data_type == 'update':
            return jsonify(get_update_trend(time_type))
        elif data_type == 'view':
            return jsonify(get_view_trend(time_type))
        else:
            return jsonify({"error": "不支持的数据类型"}), 400
    except Exception as e:
        logger.error(f"获取整合趋势数据出错: {str(e)}")
        return jsonify([])

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

# 启动服务
if __name__ == '__main__':
    # 从环境变量获取主机和端口
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    
    logger.info(f"启动服务，监听: {host}:{port}, 调试模式: {debug}")
    app.run(host=host, port=port, debug=debug) 