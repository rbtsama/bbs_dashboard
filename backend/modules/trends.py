"""
趋势模块，提供各种趋势数据查询功能
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

from .db_utils import execute_query, table_exists

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
)
logger = logging.getLogger("trends")

def get_formatted_date(date_str: str, time_type: str) -> str:
    """
    格式化日期字符串，根据时间类型返回不同格式
    
    Args:
        date_str: 日期字符串
        time_type: 时间类型 ('hourly', 'daily', 'weekly', 'monthly')
        
    Returns:
        str: 格式化后的日期字符串
    """
    try:
        date_value = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        
        if time_type == 'hourly':
            # 小时格式：dd/hh点
            return f"{date_value.day}/{date_value.hour}点"
        elif time_type == 'daily':
            # 日格式：mm/dd
            return f"{date_value.month}/{date_value.day}"
        elif time_type == 'weekly':
            # 周格式：mm/dd
            # 获取本周周一的日期
            day = date_value.weekday()  # 0是周一，6是周日
            week_start = date_value - timedelta(days=day)
            return f"{week_start.month}/{week_start.day}"
        elif time_type == 'monthly':
            # 月格式：yyyy/mm
            return f"{date_value.year}/{date_value.month}"
        else:
            return date_str
    except:
        return date_str

def get_post_trend(time_type: str = 'daily') -> List[Dict[str, Any]]:
    """
    获取发帖趋势数据
    
    Args:
        time_type: 时间类型 ('hourly', 'daily', 'weekly', 'monthly')
        
    Returns:
        List[Dict[str, Any]]: 发帖趋势数据列表
    """
    try:
        # 根据时间类型设置不同的日期格式和限制
        if time_type == 'hourly':
            # 小时粒度 - 最新的90个小时
            group_format = '%Y-%m-%d %H:00:00'
            limit = 90
        elif time_type == 'daily':
            # 日粒度 - 最新的30天
            group_format = '%Y-%m-%d'
            limit = 30
        elif time_type == 'weekly':
            # 周粒度 - 最新的20周
            group_format = '%Y-%W'  # 使用年份和周数
            limit = 20
        else:
            # 月粒度 - 最新的20个月
            group_format = '%Y-%m'
            limit = 20
        
        # 检查import表是否存在
        if not table_exists('import'):
            logger.warning("import表不存在")
            return []
        
        # 查询import表中的发帖趋势数据
        query = f"""
        SELECT 
            strftime('{group_format}', datetime) as datetime,
            SUM(count) as count
        FROM import 
        WHERE data_category = 'post_statistics'
        AND type = 'post'
        GROUP BY strftime('{group_format}', datetime)
        ORDER BY datetime DESC
        LIMIT {limit}
        """
        
        result = execute_query(query)
        
        # 格式化日期
        for item in result:
            item['datetime'] = get_formatted_date(item['datetime'], time_type)
        
        # 按日期升序排序
        result.sort(key=lambda x: x['datetime'])
        
        return result
    except Exception as e:
        logger.error(f"获取发帖趋势数据出错: {str(e)}")
        return []

def get_update_trend(time_type: str = 'daily') -> List[Dict[str, Any]]:
    """
    获取更新趋势数据
    
    Args:
        time_type: 时间类型 ('hourly', 'daily', 'weekly', 'monthly')
        
    Returns:
        List[Dict[str, Any]]: 更新趋势数据列表
    """
    try:
        # 根据时间类型设置不同的日期格式和限制
        if time_type == 'hourly':
            # 小时粒度 - 最新的90个小时
            group_format = '%Y-%m-%d %H:00:00'
            limit = 90
        elif time_type == 'daily':
            # 日粒度 - 最新的30天
            group_format = '%Y-%m-%d'
            limit = 30
        elif time_type == 'weekly':
            # 周粒度 - 最新的20周
            group_format = '%Y-%W'  # 使用年份和周数
            limit = 20
        else:
            # 月粒度 - 最新的20个月
            group_format = '%Y-%m'
            limit = 20
        
        # 检查import表是否存在
        if not table_exists('import'):
            logger.warning("import表不存在")
            return []
        
        # 英文类型到中文类型的映射 - 用于记录日志
        type_mapping = {
            'repost': '重发',
            'reply': '回帖',
            'delete_reply': '删回帖'
        }
        
        # 查询import表中的更新趋势数据
        query = f"""
        SELECT 
            strftime('{group_format}', datetime) as datetime,
            type,
            SUM(count) as count
        FROM import 
        WHERE data_category = 'update_statistics'
        AND type IN ('repost', 'reply', 'delete_reply')
        GROUP BY strftime('{group_format}', datetime), type
        ORDER BY datetime DESC
        LIMIT {limit * 3}  /* 因为每个时间点有三种类型的数据 */
        """
        
        result = execute_query(query)
        
        # 格式化日期，但不转换类型名称为中文（保留英文类型名）
        for item in result:
            # 不再转换类型，只格式化日期
            item['datetime'] = get_formatted_date(item['datetime'], time_type)
            # 记录日志中仍然使用中文类型名
            logger.debug(f"类型 {item['type']} ({type_mapping.get(item['type'], '未知')}) 的数据: {item}")
        
        # 按日期和类型排序
        result.sort(key=lambda x: (x['datetime'], x['type']))
        
        return result
    except Exception as e:
        logger.error(f"获取更新趋势数据出错: {str(e)}")
        return []

def get_view_trend(time_type: str = 'daily') -> List[Dict[str, Any]]:
    """
    获取阅读趋势数据
    
    Args:
        time_type: 时间粒度 ('hourly', 'daily', 'weekly', 'monthly')
        
    Returns:
        List[Dict[str, Any]]: 阅读趋势数据
    """
    try:
        # 根据时间粒度设置查询参数
        if time_type == 'hourly':
            # 小时粒度 - 最新的90小时
            group_format = '%Y-%m-%d %H'
            limit = 90
        elif time_type == 'daily':
            # 日粒度 - 最新的30天
            group_format = '%Y-%m-%d'
            limit = 30
        elif time_type == 'weekly':
            # 周粒度 - 最新的20周
            group_format = '%Y-%W'  # 使用年份和周数
            limit = 20
        else:
            # 月粒度 - 最新的20个月
            group_format = '%Y-%m'
            limit = 20
        
        # 检查import表是否存在
        if not table_exists('import'):
            logger.warning("import表不存在")
            return []
        
        # 查询import表中的阅读趋势数据
        query = f"""
        SELECT 
            strftime('{group_format}', datetime) as datetime,
            SUM(count) as count
        FROM import 
        WHERE data_category = 'view_statistics'
        AND type = 'view'
        GROUP BY strftime('{group_format}', datetime)
        ORDER BY datetime DESC
        LIMIT {limit}
        """
        
        result = execute_query(query)
        
        # 格式化日期
        for item in result:
            item['datetime'] = get_formatted_date(item['datetime'], time_type)
        
        # 按日期升序排序
        result.sort(key=lambda x: x['datetime'])
        
        return result
    except Exception as e:
        logger.error(f"获取阅读趋势数据出错: {str(e)}")
        return []

def get_data_trends(days: int = 30, granularity: str = 'daily') -> Dict[str, List[Dict[str, Any]]]:
    """
    获取多种数据趋势，整合发帖、更新和浏览趋势数据
    
    Args:
        days: 获取多少天的数据，默认30天
        granularity: 时间粒度 ('daily', 'weekly', 'monthly')
        
    Returns:
        Dict[str, List[Dict[str, Any]]]: 包含三种趋势数据的字典
    """
    try:
        # 确保时间粒度参数有效
        if granularity not in ['daily', 'weekly', 'monthly']:
            granularity = 'daily'
        
        # 获取三种趋势数据
        post_data = get_post_trend(granularity)
        update_data = get_update_trend(granularity)
        view_data = get_view_trend(granularity)
        
        # 为每个数据点添加类型标记
        for item in post_data:
            item['type'] = 'post'
        
        for item in update_data:
            item['type'] = 'update'
            
        for item in view_data:
            item['type'] = 'view'
            
        # 合并所有数据点
        combined_data = post_data + update_data + view_data
        
        return {
            'post_trend': post_data,
            'update_trend': update_data,
            'view_trend': view_data,
            'combined': combined_data  # 使用combined替代combined_data
        }
    except Exception as e:
        logger.error(f"获取数据趋势出错: {str(e)}")
        return {
            'post_trend': [],
            'update_trend': [],
            'view_trend': [],
            'combined': []
        }

def get_new_posts(date=None, page=1, limit=10) -> Dict[str, Any]:
    """
    获取新帖列表
    
    Args:
        date: 日期，默认为None表示获取最新日期的数据
        page: 页码
        limit: 每页记录数
        
    Returns:
        Dict[str, Any]: 包含新帖列表的字典
    """
    try:
        # 计算偏移量
        offset = (page - 1) * limit
        
        # 准备返回的空数据结构
        empty_response = {
            'data': [],
            'total': 0,
            'page': page,
            'limit': limit,
            'date': None
        }
        
        # 检查posts表是否存在
        if not table_exists('posts'):
            logger.warning("posts表不存在")
            return empty_response
        
        # 如果没有提供日期，获取最新日期
        if date is None:
            date_query = "SELECT DATE(post_time) AS date FROM posts ORDER BY post_time DESC LIMIT 1"
            date_result = execute_query(date_query)
            if not date_result:
                return empty_response
            
            date = date_result[0]['date']
        
        # 查询指定日期的帖子
        query = """
        SELECT *
        FROM posts
        WHERE DATE(post_time) = ?
        ORDER BY post_time DESC
        LIMIT ? OFFSET ?
        """
        result = execute_query(query, (date, limit, offset))
        
        # 获取总记录数
        count_query = "SELECT COUNT(*) as total FROM posts WHERE DATE(post_time) = ?"
        count_result = execute_query(count_query, (date,))
        total_count = count_result[0]['total'] if count_result else 0
        
        return {
            'data': result,
            'total': total_count,
            'page': page,
            'limit': limit,
            'date': date
        }
    except Exception as e:
        logger.error(f"获取新帖列表出错: {str(e)}")
        return {
            'data': [],
            'total': 0,
            'page': page,
            'limit': limit,
            'date': date,
            'error': str(e)
        } 