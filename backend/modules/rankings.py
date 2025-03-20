"""
排行榜模块，提供帖子排行和作者排行功能
"""

import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime

from .db_utils import execute_query, table_exists

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("rankings")

# 排序字段映射 - 帖子排行
POST_SORT_FIELDS = {
    'repost_count': ('repost_count', True),       # 重发次数
    'reply_count': ('reply_count', True),         # 回复数
    'delete_reply_count': ('delete_reply_count', True), # 删除数
    'author': ('author', False),                   # 作者
    'title': ('title', False),                     # 标题
    'last_active': ('last_active', True),         # 最后活跃
    'daysold': ('daysold', True),                 # 帖子天数
    'thread_id': ('thread_id', False),             # 帖子ID
    'url': ('url', False)                          # 帖子URL
}

# 排序字段映射 - 作者排行
AUTHOR_SORT_FIELDS = {
    'repost_count': ('repost_count', True),       # 重发次数
    'post_count': ('post_count', True),           # 发帖数
    'active_posts': ('active_posts', True),       # 活跃帖数
    'author': ('author', False),                   # 作者名
    'reply_count': ('reply_count', True),         # 回复数
    'delete_reply_count': ('delete_reply_count', True), # 删除数
    'last_active': ('last_active', True),         # 最后活跃时间
    'author_link': ('author_link', False)          # 作者链接
}

def get_post_ranking(
    page: int = 1, 
    limit: int = 10, 
    sort_field: str = 'repost_count', 
    sort_order: str = 'desc'
) -> Dict[str, Any]:
    """
    获取帖子排行榜数据
    
    Args:
        page: 页码
        limit: 每页记录数
        sort_field: 排序字段
        sort_order: 排序顺序 ('asc'或'desc')
        
    Returns:
        Dict[str, Any]: 包含帖子排行榜数据的字典
    """
    try:
        # 输出请求的参数进行调试
        logger.info(f"请求参数: page={page}, limit={limit}, sort_field={sort_field}, sort_order={sort_order}")
        
        # 计算偏移量
        offset = (page - 1) * limit
        
        # 验证排序参数
        sort_info = POST_SORT_FIELDS.get(sort_field, ('repost_count', True))
        db_sort_field, is_numeric = sort_info
        logger.info(f"映射后的排序字段: {db_sort_field}, 是否为数值: {is_numeric}")
        
        # 验证排序顺序
        if sort_order.upper() not in ['ASC', 'DESC']:
            sort_order = 'DESC'
        else:
            sort_order = sort_order.upper()
        
        # 准备返回的空数据结构
        empty_response = {
            'data': [],
            'total': 0,
            'page': page,
            'limit': limit
        }
        
        # 检查post_ranking表是否存在
        if not table_exists('post_ranking'):
            logger.warning("post_ranking表不存在")
            return empty_response
        
        # 获取总记录数
        count_query = "SELECT COUNT(*) as total FROM post_ranking"
        count_result = execute_query(count_query)
        total_count = count_result[0]['total'] if count_result else 0
        logger.info(f"post_ranking表总数: {total_count}")
        
        # 如果没有数据，返回空结果
        if total_count == 0:
            return empty_response
            
        # 构建排序表达式
        sort_expr = db_sort_field
        if is_numeric:
            sort_expr = f"CAST(CASE WHEN {db_sort_field} = '' OR {db_sort_field} IS NULL THEN '0' ELSE {db_sort_field} END AS INTEGER)"
        
        # 从post_ranking表查询数据
        query = f"""
        SELECT 
            thread_id,
            url,
            title,
            author,
            author_link,
            CAST(CASE WHEN repost_count = '' OR repost_count IS NULL THEN '0' ELSE repost_count END AS INTEGER) as repost_count,
            CAST(CASE WHEN reply_count = '' OR reply_count IS NULL THEN '0' ELSE reply_count END AS INTEGER) as reply_count,
            CAST(CASE WHEN delete_reply_count = '' OR delete_reply_count IS NULL THEN '0' ELSE delete_reply_count END AS INTEGER) as delete_reply_count,
            CAST(CASE WHEN daysold = '' OR daysold IS NULL THEN '0' ELSE daysold END AS INTEGER) as daysold,
            CAST(CASE WHEN last_active = '' OR last_active IS NULL THEN '0' ELSE last_active END AS INTEGER) as last_active
        FROM post_ranking
        ORDER BY {sort_expr} {sort_order}
        LIMIT ? OFFSET ?
        """
        
        logger.info(f"执行查询: {query}")
        result = execute_query(query, (limit, offset))
        logger.info(f"从post_ranking表查询到{len(result)}条记录")
        
        # 验证返回的记录数
        if not result:
            logger.warning(f"查询参数 limit={limit}, offset={offset}, sort={sort_expr} {sort_order}，但没有返回数据")
            return empty_response
        
        return {
            'data': result,
            'total': total_count,
            'page': page,
            'limit': limit
        }
    except Exception as e:
        logger.error(f"获取帖子排行榜数据出错: {str(e)}")
        return {
            'data': [],
            'total': 0,
            'page': page,
            'limit': limit,
            'error': str(e)
        }

def get_author_ranking(
    page: int = 1, 
    limit: int = 10, 
    sort_field: str = 'repost_count', 
    sort_order: str = 'desc'
) -> Dict[str, Any]:
    """
    获取作者排行榜数据
    
    Args:
        page: 页码
        limit: 每页记录数
        sort_field: 排序字段
        sort_order: 排序顺序 ('asc'或'desc')
        
    Returns:
        Dict[str, Any]: 包含作者排行榜数据的字典
    """
    try:
        # 输出请求的参数进行调试
        logger.info(f"请求作者排行参数: page={page}, limit={limit}, sort_field={sort_field}, sort_order={sort_order}")
        
        # 计算偏移量
        offset = (page - 1) * limit
        
        # 验证排序参数
        sort_info = AUTHOR_SORT_FIELDS.get(sort_field, ('repost_count', True))
        db_sort_field, is_numeric = sort_info
        logger.info(f"映射后的排序字段: {db_sort_field}, 是否为数值: {is_numeric}")
        
        # 验证排序顺序
        if sort_order.upper() not in ['ASC', 'DESC']:
            sort_order = 'DESC'
        else:
            sort_order = sort_order.upper()
        
        # 准备返回的空数据结构
        empty_response = {
            'data': [],
            'total': 0,
            'page': page,
            'limit': limit
        }
        
        # 检查author_ranking表是否存在
        if not table_exists('author_ranking'):
            logger.warning("author_ranking表不存在")
            return empty_response
            
        # 获取总记录数
        count_query = "SELECT COUNT(*) as total FROM author_ranking"
        count_result = execute_query(count_query)
        total_count = count_result[0]['total'] if count_result else 0
        logger.info(f"author_ranking表总数: {total_count}")
        
        # 如果没有数据，返回空结果
        if total_count == 0:
            return empty_response
            
        # 构建排序表达式
        sort_expr = db_sort_field
        if is_numeric:
            sort_expr = f"CAST(CASE WHEN {db_sort_field} = '' OR {db_sort_field} IS NULL THEN '0' ELSE {db_sort_field} END AS INTEGER)"
        
        # 从author_ranking表查询数据
        query = f"""
        SELECT 
            author,
            author_link,
            CAST(CASE WHEN post_count = '' OR post_count IS NULL THEN '0' ELSE post_count END AS INTEGER) as post_count,
            CAST(CASE WHEN repost_count = '' OR repost_count IS NULL THEN '0' ELSE repost_count END AS INTEGER) as repost_count,
            CAST(CASE WHEN reply_count = '' OR reply_count IS NULL THEN '0' ELSE reply_count END AS INTEGER) as reply_count,
            CAST(CASE WHEN delete_reply_count = '' OR delete_reply_count IS NULL THEN '0' ELSE delete_reply_count END AS INTEGER) as delete_reply_count,
            CAST(CASE WHEN last_active = '' OR last_active IS NULL THEN '0' ELSE last_active END AS INTEGER) as last_active,
            CAST(CASE WHEN active_posts = '' OR active_posts IS NULL THEN '0' ELSE active_posts END AS INTEGER) as active_posts
        FROM author_ranking
        ORDER BY {sort_expr} {sort_order}
        LIMIT ? OFFSET ?
        """
        
        logger.info(f"执行查询: {query}")
        result = execute_query(query, (limit, offset))
        logger.info(f"从author_ranking表查询到{len(result)}条记录")
        
        # 验证返回的记录数
        if not result:
            logger.warning(f"查询参数 limit={limit}, offset={offset}, sort={sort_expr} {sort_order}，但没有返回数据")
            return empty_response
        
        return {
            'data': result,
            'total': total_count,
            'page': page,
            'limit': limit
        }
    except Exception as e:
        logger.error(f"获取作者排行榜数据出错: {str(e)}")
        return {
            'data': [],
            'total': 0,
            'page': page,
            'limit': limit,
            'error': str(e)
        }

def get_thread_history(thread_id: str) -> List[Dict[str, Any]]:
    """
    获取帖子历史数据
    
    Args:
        thread_id: 帖子ID
        
    Returns:
        List[Dict[str, Any]]: 帖子历史数据列表
    """
    try:
        # 检查post_history表是否存在
        if not table_exists('post_history'):
            logger.warning("post_history表不存在")
            
            # 检查import表是否存在并包含帖子历史数据
            if table_exists('import'):
                # 从import表查询帖子历史数据
                query = """
                SELECT *
                FROM import
                WHERE data_category = 'post_history'
                AND thread_id = ?
                ORDER BY action_time DESC
                """
                return execute_query(query, (thread_id,))
            
            # 如果都不存在，返回空列表
            return []
        
        # 从post_history表查询数据
        query = """
        SELECT *
        FROM post_history
        WHERE thread_id = ?
        ORDER BY action_time DESC
        """
        return execute_query(query, (thread_id,))
    except Exception as e:
        logger.error(f"获取帖子历史数据出错: {str(e)}")
        return []

def get_author_history(author: str) -> List[Dict[str, Any]]:
    """
    获取作者历史数据
    
    Args:
        author: 作者名
        
    Returns:
        List[Dict[str, Any]]: 作者历史数据列表
    """
    try:
        # 从post_history表查询数据
        query = """
        SELECT *
        FROM post_history
        WHERE author = ?
        ORDER BY action_time DESC
        LIMIT 100
        """
        return execute_query(query, (author,))
    except Exception as e:
        logger.error(f"获取作者历史数据出错: {str(e)}")
        return [] 