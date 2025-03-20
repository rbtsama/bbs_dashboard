import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import warnings
import os
import traceback
warnings.filterwarnings('ignore')

# 设置数据路径
DATA_DIR = Path(__file__).parent.parent / 'data'
PROCESSED_DIR = DATA_DIR / 'processed'
ANALYSIS_DIR = DATA_DIR / 'analysis'

def generate_complete_time_series(start_time, end_time):
    """生成完整的时间序列"""
    # 确保时间是整点
    start_time = start_time.replace(minute=0, second=0, microsecond=0)
    end_time = end_time.replace(minute=0, second=0, microsecond=0)
    
    # 生成所有小时的时间序列
    hours = pd.date_range(start=start_time, end=end_time, freq='H')
    
    # 创建基础数据框
    time_series = pd.DataFrame({
        'datetime': hours
    })
    
    # 添加其他时间组件
    components = time_series['datetime'].apply(format_date_components).apply(pd.Series)
    time_series['month'] = components['month']
    time_series['week'] = components['week']
    time_series['date'] = components['date']
    time_series['hour'] = components['hour']
    
    return time_series

def format_datetime(dt):
    """格式化日期时间，将分钟和秒设为00"""
    if pd.isna(dt):
        return None
    dt = pd.to_datetime(dt)
    return dt.replace(minute=0, second=0, microsecond=0)

def format_date_components(dt):
    """格式化日期组件（年月日等）"""
    if pd.isna(dt):
        return {
            'month': None,
            'week': None,
            'date': None,
            'hour': None
        }
    
    dt = pd.to_datetime(dt)
    
    # 获取当前周的周一
    monday = dt - timedelta(days=dt.weekday())
    
    # 使用字符串格式化确保格式正确
    return {
        'month': f"{dt.year % 100}{dt.month:02d}",          # 年月格式，如2503表示25年3月
        'week': f"{dt.month:02d}{dt.day:02d}",              # 月日格式，如0325表示3月25日
        'date': f"{dt.day:02d}",                            # 日期格式，如25表示25日
        'hour': dt.hour
    }

def process_time_components(df, time_col, prefix=''):
    """处理时间组件"""
    df[f'{prefix}datetime'] = df[time_col].apply(format_datetime)
    
    # 获取所有时间组件
    time_components = df[time_col].apply(format_date_components).apply(pd.Series)
    
    # 添加时间组件列
    df[f'{prefix}month'] = time_components['month']
    df[f'{prefix}week'] = time_components['week']
    df[f'{prefix}date'] = time_components['date']
    df[f'{prefix}hour'] = time_components['hour']
    
    return df

def analyze_post_statistics(post_df, complete_time_series):
    """分析发帖数据统计"""
    # 按小时统计发帖数量
    hourly_stats = post_df.groupby('post_datetime').agg({
        'url': 'count'
    }).reset_index()
    
    # 合并完整时间序列
    complete_stats = complete_time_series.merge(
        hourly_stats,
        left_on='datetime',
        right_on='post_datetime',
        how='left'
    )
    
    # 填充空值为0
    complete_stats['count'] = complete_stats['url'].fillna(0).astype(int)
    complete_stats['type'] = 'post'
    
    return complete_stats[['type', 'datetime', 'count']]

def analyze_list_statistics(list_df, complete_time_series):
    """分析帖子更新数据统计"""
    # 按小时和更新原因统计
    hourly_stats = list_df.groupby(['datetime', 'update_reason']).agg({
        'url': 'count'
    }).reset_index()
    
    # 为每种更新原因创建完整时间序列
    results = []
    
    # 定义更新原因和type的映射关系
    reason_to_type = {
        '重发': 'repost',
        '回帖': 'reply',
        '删回帖': 'delete_reply'
    }
    
    for reason in ['重发', '回帖', '删回帖']:
        reason_stats = hourly_stats[hourly_stats['update_reason'] == reason].copy()
        
        # 合并完整时间序列
        complete_reason_stats = complete_time_series.merge(
            reason_stats,
            on='datetime',
            how='left'
        )
        
        # 填充空值为0
        complete_reason_stats['count'] = complete_reason_stats['url'].fillna(0).astype(int)
        complete_reason_stats['type'] = reason_to_type[reason]  # 使用映射转换type值
        complete_reason_stats['update_reason'] = reason
        
        results.append(complete_reason_stats[['type', 'datetime', 'count', 'update_reason']])
    
    return pd.concat(results, ignore_index=True)

def analyze_view_statistics(list_df, complete_time_series):
    """分析阅读量数据统计（严格模式）"""
    print("\n=== 阅读量数据统计（严格模式）===")
    
    # 检查数据时间范围
    target_date = pd.Timestamp('2025-02-27')
    
    # 分析原始数据的时间分布
    print("\n=== 原始数据时间分布分析 ===")
    # 按小时统计数据点数量
    hour_counts = list_df.groupby(list_df['scraping_time_R'].dt.hour)['url'].count()
    print("每小时数据点数量:")
    for hour, count in hour_counts.items():
        print(f"  {hour}点: {count}条记录")
    
    # 按分钟统计数据点数量
    minute_counts = list_df.groupby(list_df['scraping_time_R'].dt.minute)['url'].count()
    print("\n每分钟数据点数量:")
    for minute, count in sorted(minute_counts.items()):
        print(f"  {minute}分: {count}条记录")
    
    # 分析单双小时的数据分布
    single_hours = list_df[list_df['scraping_time_R'].dt.hour % 2 == 1]
    double_hours = list_df[list_df['scraping_time_R'].dt.hour % 2 == 0]
    
    print(f"\n单数小时数据点: {len(single_hours)}条")
    print(f"双数小时数据点: {len(double_hours)}条")
    
    # 分析单双小时的阅读量分布
    print("\n单数小时阅读量统计:")
    print(f"  平均值: {single_hours['read_count'].mean():.2f}")
    print(f"  中位数: {single_hours['read_count'].median():.2f}")
    print(f"  最小值: {single_hours['read_count'].min()}")
    print(f"  最大值: {single_hours['read_count'].max()}")
    
    print("\n双数小时阅读量统计:")
    print(f"  平均值: {double_hours['read_count'].mean():.2f}")
    print(f"  中位数: {double_hours['read_count'].median():.2f}")
    print(f"  最小值: {double_hours['read_count'].min()}")
    print(f"  最大值: {double_hours['read_count'].max()}")
    
    # 将数据转换为字典格式，以便于计算
    # 格式: {hour_timestamp: {url: read_count, ...}, ...}
    data_dict = {}
    
    # 只处理15分钟的数据点
    list_15min_df = list_df[list_df['scraping_time_R'].dt.minute == 15]
    
    # 按小时分组
    for hour, group in list_15min_df.groupby(list_15min_df['scraping_time_R'].dt.floor('H')):
        hour_timestamp = int(hour.timestamp())
        url_read_counts = {}
        
        for _, row in group.iterrows():
            url_read_counts[row['url']] = row['read_count']
        
        data_dict[hour_timestamp] = url_read_counts
    
    # 计算每小时阅读量增长
    view_gaps = calculate_hourly_view_gap(data_dict)
    
    # 转换为DataFrame以便于后续处理
    view_stats = []
    for item in view_gaps:
        # 从时间戳提取datetime
        curr_hour_ts = int(item['window'].split('→')[1])
        curr_hour = pd.Timestamp(curr_hour_ts, unit='s')
        
        view_stats.append({
            'hour_datetime': curr_hour,
            'count': item['view_gap'],  # 将view_gap填入count字段
            'duplicate_posts': item['common_urls_count'],
            'new_posts': item.get('new_urls_count', 0),
            'disappeared_posts': item.get('disappeared_urls_count', 0)
        })
    
    # 打印2025年2月27日的数据
    print("\n2025年2月27日阅读量增长:")
    for item in view_gaps:
        curr_hour_ts = int(item['window'].split('→')[1])
        curr_hour = pd.Timestamp(curr_hour_ts, unit='s')
        
        if curr_hour.date() == target_date.date():
            prev_hour_ts = int(item['window'].split('→')[0])
            prev_hour = pd.Timestamp(prev_hour_ts, unit='s')
            
            print(f"时间窗口: {prev_hour} → {curr_hour}")
            print(f"重叠URL数量: {item['common_urls_count']}")
            print(f"阅读量增长: {item['view_gap']:,}")
            
            # 如果有数据，显示详细信息
            if item['common_urls_count'] > 0:
                # 获取前一个时间点和当前时间点的数据
                prev_data = data_dict.get(prev_hour_ts, {})
                curr_data = data_dict.get(curr_hour_ts, {})
                
                # 找出共同的URL
                common_urls = set(prev_data.keys()) & set(curr_data.keys())
                
                # 计算每个URL的增长并排序
                url_gaps = []
                for url in common_urls:
                    if curr_data[url] >= prev_data[url]:  # 只考虑增长的情况
                        url_gaps.append((url, prev_data[url], curr_data[url], curr_data[url] - prev_data[url]))
                
                # 按增长量排序
                url_gaps.sort(key=lambda x: x[3], reverse=True)
                
                # 显示前5个URL的增长情况
                print("\n增长最多的URL示例（前5个）:")
                for url, prev, curr, gap in url_gaps[:5]:
                    print(f"URL: {url}")
                    print(f"  前一个时间点: {prev:,}")
                    print(f"  当前时间点: {curr:,}")
                    print(f"  增长量: {gap:,}")
                
                # 计算增长量的统计信息
                if url_gaps:
                    gaps = [g[3] for g in url_gaps]
                    print(f"\n增长量统计信息:")
                    print(f"最小值: {min(gaps):,}")
                    print(f"最大值: {max(gaps):,}")
                    print(f"平均值: {sum(gaps)/len(gaps):.2f}")
                    print(f"中位数: {sorted(gaps)[len(gaps)//2]:,}")
                    
                    # 统计增长量分布
                    gap_ranges = [(0,5), (6,10), (11,15), (16,20), (21,float('inf'))]
                    gap_dist = {f"{r[0]}-{r[1]}": len([g for g in gaps if r[0] <= g <= r[1]]) for r in gap_ranges}
                    print(f"\n增长量分布:")
                    for range_str, count in gap_dist.items():
                        print(f"{range_str}: {count:,} URLs")
            
            print("\n" + "-"*50)
    
    # 转换为DataFrame
    view_stats_df = pd.DataFrame(view_stats)
    
    # 合并完整时间序列
    if not view_stats_df.empty:
        complete_view_stats = complete_time_series.merge(
            view_stats_df,
            left_on='datetime',
            right_on='hour_datetime',
            how='left'
        )
    else:
        # 如果没有数据，创建空列
        complete_view_stats = complete_time_series.copy()
        complete_view_stats['count'] = 0
        complete_view_stats['duplicate_posts'] = 0
    
    # 填充空值为0
    complete_view_stats['count'] = complete_view_stats['count'].fillna(0).astype(int)
    complete_view_stats['duplicate_posts'] = complete_view_stats['duplicate_posts'].fillna(0).astype(int)
    complete_view_stats['type'] = 'view'
    
    return complete_view_stats[['type', 'datetime', 'count', 'duplicate_posts']]

def calculate_hourly_view_gap(data_dict):
    """
    分小时阅读量增量计算器（严格模式）
    
    设计原则：
    1. 仅比较相邻完整小时窗口
    2. 仅统计共同存在的URL阅读量增长
    3. 自动处理缺失时间窗口
    4. 异常数据自动过滤
    """
    # 按时间戳升序排列（确保正确的时间窗口顺序）
    sorted_hours = sorted(data_dict.keys())
    
    # 添加调试信息：时间窗口序列
    print("\n=== 时间窗口序列分析 ===")
    print(f"总窗口数: {len(sorted_hours)}")
    print("前5个时间窗口:")
    for h in sorted_hours[:5]:
        print(f"  {datetime.fromtimestamp(h).strftime('%Y-%m-%d %H:%M:%S')} ({h})")
    
    print("\n时间窗口间隔分析:")
    intervals = [sorted_hours[i] - sorted_hours[i-1] for i in range(1, len(sorted_hours))]
    interval_counts = {}
    for interval in intervals:
        interval_counts[interval] = interval_counts.get(interval, 0) + 1
    
    for interval, count in sorted(interval_counts.items()):
        print(f"  间隔 {interval} 秒 ({interval/3600:.1f} 小时): {count} 次")
    
    # 分析单双小时的数据特征
    print("\n=== 单双小时数据特征分析 ===")
    single_hours = [h for h in sorted_hours if (datetime.fromtimestamp(h).hour % 2) == 1]
    double_hours = [h for h in sorted_hours if (datetime.fromtimestamp(h).hour % 2) == 0]
    
    print(f"单数小时窗口数: {len(single_hours)}")
    print(f"双数小时窗口数: {len(double_hours)}")
    
    # 分析URL数量
    single_hour_urls = [len(data_dict[h]) for h in single_hours]
    double_hour_urls = [len(data_dict[h]) for h in double_hours]
    
    if single_hour_urls:
        print(f"单数小时平均URL数: {sum(single_hour_urls)/len(single_hour_urls):.1f}")
        print(f"单数小时URL数范围: {min(single_hour_urls)} - {max(single_hour_urls)}")
    
    if double_hour_urls:
        print(f"双数小时平均URL数: {sum(double_hour_urls)/len(double_hour_urls):.1f}")
        print(f"双数小时URL数范围: {min(double_hour_urls)} - {max(double_hour_urls)}")
    
    # 计算每相邻时间点的阅读量差值
    results = []
    
    # 分析单双小时的增长差异
    single_hour_gaps = []
    double_hour_gaps = []
    
    for i in range(1, len(sorted_hours)):
        curr_hour = sorted_hours[i]
        prev_hour = sorted_hours[i-1]
        
        # 校验时间窗口连续性（必须间隔3600秒）
        if curr_hour - prev_hour != 3600:
            print(f"警告：时间窗口不连续 {prev_hour}→{curr_hour}，跳过计算")
            continue
            
        prev_data = data_dict.get(prev_hour, {})
        curr_data = data_dict.get(curr_hour, {})
        
        # 分析URL的生命周期
        prev_urls = set(prev_data.keys())
        curr_urls = set(curr_data.keys())
        common_urls = prev_urls & curr_urls
        new_urls = curr_urls - prev_urls
        disappeared_urls = prev_urls - curr_urls
        
        # 核心计算逻辑（仅处理共同存在的URL）
        valid_gap = 0
        url_gaps = []
        
        for url in common_urls:
            curr_views = curr_data[url]
            prev_views = prev_data[url]
            gap = curr_views - prev_views
            if gap >= 0:  # 过滤异常减少
                valid_gap += gap
                url_gaps.append(gap)
        
        # 记录单双小时的增长情况
        curr_hour_dt = datetime.fromtimestamp(curr_hour)
        if curr_hour_dt.hour % 2 == 1:  # 单数小时
            single_hour_gaps.append(valid_gap)
        else:  # 双数小时
            double_hour_gaps.append(valid_gap)
        
        # 详细分析特定时间窗口
        target_date = datetime(2025, 2, 27).date()
        if curr_hour_dt.date() == target_date:
            print(f"\n时间窗口详细分析: {datetime.fromtimestamp(prev_hour)} → {curr_hour_dt}")
            print(f"  前一时间点URL数: {len(prev_urls)}")
            print(f"  当前时间点URL数: {len(curr_urls)}")
            print(f"  共同URL数: {len(common_urls)}")
            print(f"  新增URL数: {len(new_urls)}")
            print(f"  消失URL数: {len(disappeared_urls)}")
            print(f"  有效增长量: {valid_gap}")
            
            if url_gaps:
                print(f"  平均每URL增长: {valid_gap/len(common_urls):.2f}")
                print(f"  增长分布: 最小={min(url_gaps)}, 最大={max(url_gaps)}, 中位数={sorted(url_gaps)[len(url_gaps)//2]}")
            
            # 分析增长最多的URL
            if common_urls:
                top_gaps = []
                for url in common_urls:
                    gap = curr_data[url] - prev_data[url]
                    if gap > 0:
                        top_gaps.append((url, prev_data[url], curr_data[url], gap))
                
                top_gaps.sort(key=lambda x: x[3], reverse=True)
                print("\n  增长最多的5个URL:")
                for url, prev, curr, gap in top_gaps[:5]:
                    print(f"    {url}: {prev} → {curr} (+{gap})")
        
        results.append({
            "window": f"{prev_hour}→{curr_hour}",
            "view_gap": valid_gap,
            "common_urls_count": len(common_urls),
            "new_urls_count": len(new_urls),
            "disappeared_urls_count": len(disappeared_urls)
        })
    
    # 分析单双小时的增长差异
    print("\n=== 单双小时增长差异分析 ===")
    if single_hour_gaps:
        print(f"单数小时平均增长: {sum(single_hour_gaps)/len(single_hour_gaps):.2f}")
        print(f"单数小时增长范围: {min(single_hour_gaps)} - {max(single_hour_gaps)}")
    
    if double_hour_gaps:
        print(f"双数小时平均增长: {sum(double_hour_gaps)/len(double_hour_gaps):.2f}")
        print(f"双数小时增长范围: {min(double_hour_gaps)} - {max(double_hour_gaps)}")
    
    if single_hour_gaps and double_hour_gaps:
        ratio = sum(single_hour_gaps)/len(single_hour_gaps) / (sum(double_hour_gaps)/len(double_hour_gaps))
        print(f"单/双小时增长比例: {ratio:.2f}")
    
    return results

def load_and_preprocess_data():
    """加载并预处理数据"""
    # 读取数据
    post_df = pd.read_excel(PROCESSED_DIR / 'post.xlsx')
    list_df = pd.read_excel(PROCESSED_DIR / 'update.xlsx')
    
    # 设置当前运行时间
    create_datetime = datetime.now()
    
    # 处理时间字段
    post_df = process_time_components(post_df, 'post_time', 'post_')
    post_df = process_time_components(post_df, 'scraping_time')
    list_df = process_time_components(list_df, 'scraping_time')
    
    # 获取数据的时间范围
    min_time = min(
        post_df['post_datetime'].min(),
        post_df['datetime'].min(),
        list_df['datetime'].min()
    )
    max_time = max(
        post_df['post_datetime'].max(),
        post_df['datetime'].max(),
        list_df['datetime'].max()
    )
    
    print("\n数据时间范围:")
    print(f"最早时间: {min_time}")
    print(f"最晚时间: {max_time}")
    print("\nlist_df的时间范围:")
    print(f"最早抓取时间: {list_df['scraping_time'].min()}")
    print(f"最晚抓取时间: {list_df['scraping_time'].max()}")
    print(f"总记录数: {len(list_df)}")
    print(f"15分钟记录数: {len(list_df[pd.to_datetime(list_df['scraping_time']).dt.minute == 15])}")
    
    # 生成完整时间序列
    complete_time_series = generate_complete_time_series(min_time, max_time)
    
    return post_df, list_df, create_datetime, complete_time_series

def extract_author_id(author_link):
    """从author_link中提取作者ID"""
    if pd.isna(author_link) or not author_link:
        return None
    return author_link.split('/')[-1]

def analyze_post_ranking(post_df, update_df, create_datetime):
    """分析帖子排行榜数据，输出到post_ranking.csv"""
    print("\n分析帖子排行榜数据...")
    
    # 检查update_df是否有数据
    if update_df.empty:
        print("警告：update.xlsx为空，无法生成帖子排行榜")
        # 创建空的排行榜
        post_ranking = pd.DataFrame(columns=[
            'thread_id', 'url', 'title', 'author', 'author_link', 
            'repost_count', 'reply_count', 'delete_reply_count', 
            'daysold', 'last_active'
        ])
        return post_ranking
    
    # 从update.xlsx获取基础信息（不使用post_time）
    # 按URL分组，取最新的记录作为基础信息
    base_info = update_df.sort_values('scraping_time', ascending=False)
    
    # 检查update_df中是否包含所需的列
    required_columns = ['url', 'title', 'author', 'author_link']
    available_columns = [col for col in required_columns if col in update_df.columns]
    
    # 如果缺少thread_id列，从URL中提取
    if 'thread_id' not in update_df.columns:
        print("警告：update.xlsx中缺少thread_id列，尝试从URL中提取")
        # 从URL中提取thread_id
        base_info['thread_id'] = base_info['url'].apply(
            lambda url: url.split('t_')[-1].replace('.html', '') if pd.notna(url) and 't_' in str(url) else ''
        )
        available_columns.append('thread_id')
    else:
        available_columns.append('thread_id')
    
    # 只选择可用的列
    base_info = base_info[available_columns].drop_duplicates(subset=['url'], keep='first')
    
    # 尝试从action.csv读取帖子的操作数据
    action_file = PROCESSED_DIR / 'action.csv'
    if action_file.exists():
        try:
            print(f"读取操作数据: {action_file}")
            action_df = pd.read_csv(action_file)
            
            # 检查必要的列是否存在
            if all(col in action_df.columns for col in ['url', 'action']):
                print(f"成功读取action.csv，包含{len(action_df)}条记录")
                
                # 计算每个URL的重发、回帖和删回帖次数
                action_counts = action_df.groupby(['url', 'action']).size().unstack(fill_value=0).reset_index()
                
                # 确保所有需要的action类型都有对应的列
                for action_type in ['重发', '回帖', '删回帖']:
                    if action_type not in action_counts.columns:
                        action_counts[action_type] = 0
                
                # 重命名列以匹配输出格式
                action_counts = action_counts.rename(columns={
                    '重发': 'repost_count',
                    '回帖': 'reply_count',
                    '删回帖': 'delete_reply_count'
                })
                
                print(f"从action.csv中获取了{len(action_counts)}个帖子的操作统计")
                
                # 合并到post_ranking
                post_ranking = pd.merge(base_info, action_counts[['url', 'repost_count', 'reply_count', 'delete_reply_count']], 
                                        on='url', how='left')
            else:
                print(f"警告：action.csv中缺少必要的列(url/action)，使用旧方法计算操作数")
                # 使用旧方法计算
                post_ranking = calculate_post_actions_old_method(update_df, base_info)
        except Exception as e:
            print(f"读取action.csv时出错: {str(e)}，使用旧方法计算操作数")
            # 使用旧方法计算
            post_ranking = calculate_post_actions_old_method(update_df, base_info)
    else:
        print(f"警告：找不到action.csv文件，使用旧方法计算操作数")
        # 使用旧方法计算
        post_ranking = calculate_post_actions_old_method(update_df, base_info)
    
    # 计算last_active (最后活动与当前时间的差值，天数)
    last_activity = update_df.groupby('url')['scraping_time'].max().reset_index()
    last_activity['scraping_time'] = pd.to_datetime(last_activity['scraping_time'])
    last_activity['last_active'] = (create_datetime - last_activity['scraping_time']).dt.total_seconds() / (24*3600)
    last_activity['last_active'] = last_activity['last_active'].fillna(0).astype(int)
    
    # 计算帖龄 (daysold)
    first_appearance = update_df.groupby('url')['scraping_time'].min().reset_index()
    first_appearance['scraping_time'] = pd.to_datetime(first_appearance['scraping_time'])
    first_appearance['daysold'] = (create_datetime - first_appearance['scraping_time']).dt.total_seconds() / (24*3600)
    first_appearance['daysold'] = first_appearance['daysold'].fillna(0).astype(int)
    
    # 合并last_active和daysold数据
    post_ranking = post_ranking.merge(last_activity[['url', 'last_active']], on='url', how='left')
    post_ranking = post_ranking.merge(first_appearance[['url', 'daysold']], on='url', how='left')
    
    # 填充缺失值为0
    post_ranking['repost_count'] = post_ranking['repost_count'].fillna(0).astype(int)
    post_ranking['reply_count'] = post_ranking['reply_count'].fillna(0).astype(int)
    post_ranking['delete_reply_count'] = post_ranking['delete_reply_count'].fillna(0).astype(int)
    post_ranking['last_active'] = post_ranking['last_active'].fillna(0).astype(int)
    post_ranking['daysold'] = post_ranking['daysold'].fillna(0).astype(int)
    
    # 按重发次数降序排列
    post_ranking = post_ranking.sort_values('repost_count', ascending=False)
    
    # 选择并重排列
    post_ranking = post_ranking[[
        'thread_id', 'url', 'title', 'author', 'author_link', 
        'repost_count', 'reply_count', 'delete_reply_count', 
        'daysold', 'last_active'
    ]]
    
    # 导出结果
    output_file = os.path.join(str(PROCESSED_DIR), 'post_ranking.csv')
    post_ranking.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"帖子排行榜数据已保存至: {output_file}")
    
    return post_ranking

def calculate_post_actions_old_method(update_df, base_info):
    """旧方法：基于update_df计算帖子的各类操作数量"""
    # 从update_df统计每个URL的重发、回帖、删回帖次数
    if 'update_reason' in update_df.columns:
        # 重发计数
        repost_counts = update_df[update_df['update_reason'] == '重发'].groupby('url').size()
        repost_counts = pd.DataFrame(repost_counts).reset_index()
        repost_counts.columns = ['url', 'repost_count']
        
        # 回帖计数
        reply_counts = update_df[update_df['update_reason'] == '回帖'].groupby('url').size()
        reply_counts = pd.DataFrame(reply_counts).reset_index()
        reply_counts.columns = ['url', 'reply_count']
        
        # 删回帖计数
        delete_counts = update_df[update_df['update_reason'] == '删回帖'].groupby('url').size()
        delete_counts = pd.DataFrame(delete_counts).reset_index()
        delete_counts.columns = ['url', 'delete_reply_count']
        
        # 合并所有统计数据
        post_ranking = base_info.merge(repost_counts, on='url', how='left')
        post_ranking = post_ranking.merge(reply_counts, on='url', how='left')
        post_ranking = post_ranking.merge(delete_counts, on='url', how='left')
    else:
        # 如果没有update_reason列，创建空列
        post_ranking = base_info.copy()
        post_ranking['repost_count'] = 0
        post_ranking['reply_count'] = 0
        post_ranking['delete_reply_count'] = 0
    
    return post_ranking

def analyze_author_ranking(post_df, update_df, create_datetime):
    """
    分析用户排行榜数据
    """
    print("分析用户排行榜数据...")
    
    # 从action.csv中获取所有作者信息
    action_file = PROCESSED_DIR / 'action.csv'
    if action_file.exists():
        try:
            print(f"读取操作数据: {action_file}")
            action_df = pd.read_csv(action_file)
            
            # 检查必要的列是否存在
            if all(col in action_df.columns for col in ['author', 'action']):
                print(f"成功读取action.csv，包含{len(action_df)}条记录")
                
                # 计算每个作者的重发、回帖和删回帖次数
                action_counts = action_df.groupby(['author', 'action']).size().unstack(fill_value=0).reset_index()
                
                # 确保所有需要的action类型都有对应的列
                for action_type in ['重发', '回帖', '删回帖']:
                    if action_type not in action_counts.columns:
                        action_counts[action_type] = 0
                
                # 重命名列以匹配输出格式
                action_counts = action_counts.rename(columns={
                    '重发': 'repost_count',
                    '回帖': 'reply_count',
                    '删回帖': 'delete_reply_count'
                })
                
                print(f"从action.csv中获取了{len(action_counts)}个作者的操作统计")
                
                # 使用action.csv中的作者作为基础
                author_action_list = action_df['author'].unique()
                print(f"在action.csv中找到{len(author_action_list)}个唯一作者")
            else:
                print(f"警告：action.csv中缺少必要的列(author/action)，使用post.xlsx中的作者列表")
                # 使用post.xlsx中的作者
                if 'author' in post_df.columns:
                    author_action_list = post_df['author'].unique()
                    print(f"在post.xlsx中找到{len(author_action_list)}个唯一作者")
                else:
                    print("错误：post.xlsx中缺少author列，无法生成用户排行榜")
                    return pd.DataFrame(columns=['author', 'author_link', 'post_count', 'reply_count', 'repost_count', 'delete_reply_count', 'active_posts'])
                
                # 使用旧方法计算
                action_counts = calculate_author_actions_old_method(post_df, update_df, None)
        except Exception as e:
            print(f"读取action.csv时出错: {str(e)}，使用post.xlsx中的作者列表")
            # 使用post.xlsx中的作者
            if 'author' in post_df.columns:
                author_action_list = post_df['author'].unique()
                print(f"在post.xlsx中找到{len(author_action_list)}个唯一作者")
            else:
                print("错误：post.xlsx中缺少author列，无法生成用户排行榜")
                return pd.DataFrame(columns=['author', 'author_link', 'post_count', 'reply_count', 'repost_count', 'delete_reply_count', 'active_posts'])
            
            # 使用旧方法计算
            action_counts = calculate_author_actions_old_method(post_df, update_df, None)
    else:
        print(f"警告：找不到action.csv文件，使用post.xlsx中的作者列表")
        # 使用post.xlsx中的作者
        if 'author' in post_df.columns:
            author_action_list = post_df['author'].unique()
            print(f"在post.xlsx中找到{len(author_action_list)}个唯一作者")
        else:
            print("错误：post.xlsx中缺少author列，无法生成用户排行榜")
            return pd.DataFrame(columns=['author', 'author_link', 'post_count', 'reply_count', 'repost_count', 'delete_reply_count', 'active_posts'])
        
        # 使用旧方法计算
        action_counts = calculate_author_actions_old_method(post_df, update_df, None)
    
    # 创建基础用户数据框架
    # 现在包含所有在action.csv中出现的作者，不仅仅是post.xlsx中的作者
    author_base = pd.DataFrame({'author': author_action_list})
    
    # 收集作者链接信息 - 从所有可用的数据源
    author_links_dict = {}
    
    # 1. 从post.xlsx中获取作者链接
    if 'author' in post_df.columns and 'author_link' in post_df.columns:
        print("从post.xlsx中收集作者链接...")
        post_links = post_df[['author', 'author_link']].dropna(subset=['author', 'author_link'])
        for _, row in post_links.iterrows():
            if pd.notna(row['author_link']) and row['author_link'] != '':
                author_links_dict[row['author']] = row['author_link']
        print(f"从post.xlsx中收集到{len(author_links_dict)}个作者链接")
    
    # 2. 从update.xlsx中获取作者链接
    if 'author' in update_df.columns and 'author_link' in update_df.columns:
        print("从update.xlsx中收集作者链接...")
        update_links = update_df[['author', 'author_link']].dropna(subset=['author', 'author_link'])
        # 获取最新的记录（按scraping_time排序）
        if 'scraping_time' in update_df.columns:
            update_df['scraping_time'] = pd.to_datetime(update_df['scraping_time'], errors='coerce')
            update_links = update_df.sort_values('scraping_time', ascending=False)
            update_links = update_links[['author', 'author_link']].dropna(subset=['author', 'author_link'])
        
        # 添加或更新链接
        before_count = len(author_links_dict)
        for _, row in update_links.iterrows():
            if pd.notna(row['author_link']) and row['author_link'] != '':
                author_links_dict[row['author']] = row['author_link']
        after_count = len(author_links_dict)
        print(f"从update.xlsx中收集到{after_count - before_count}个新作者链接")
    
    # 3. 尝试从action.csv中提取作者链接（如果存在）
    if action_file.exists() and 'author_link' in action_df.columns:
        print("从action.csv中收集作者链接...")
        action_links = action_df[['author', 'author_link']].dropna(subset=['author', 'author_link'])
        # 添加或更新链接
        before_count = len(author_links_dict)
        for _, row in action_links.iterrows():
            if pd.notna(row['author_link']) and row['author_link'] != '':
                author_links_dict[row['author']] = row['author_link']
        after_count = len(author_links_dict)
        print(f"从action.csv中收集到{after_count - before_count}个新作者链接")
    
    # 4. 创建作者链接DataFrame
    author_links = pd.DataFrame({
        'author': list(author_links_dict.keys()),
        'author_link': list(author_links_dict.values())
    })
    
    # 5. 合并到author_base
    author_base = pd.merge(author_base, author_links, on='author', how='left')
    
    # 6. 填充缺失的author_link为空字符串
    author_base['author_link'] = author_base['author_link'].fillna('')
    
    # 计算每个作者的历史帖数（post.xlsx中按作者去重的url数量）
    if 'author' in post_df.columns and 'url' in post_df.columns:
        # 确保去重后计算每个作者的总贴数
        author_post_counts = post_df.drop_duplicates(subset=['author', 'url']).groupby(['author'])['url'].count().reset_index()
        author_post_counts.columns = ['author', 'post_count']
        
        # 合并到author_base
        author_base = pd.merge(author_base, author_post_counts, on='author', how='left')
        author_base['post_count'] = author_base['post_count'].fillna(0).astype(int)
        print(f"计算了 {len(author_post_counts)} 个作者的历史贴数")
    else:
        # 如果post.xlsx中没有作者信息，创建空列
        author_base['post_count'] = 0
    
    # 计算每个作者的活跃帖数（update.xlsx中最新一天的去重URL数量）
    active_posts_counts = pd.DataFrame(columns=['author', 'active_posts'])

    if all(col in update_df.columns for col in ['scraping_time_R', 'url', 'author']):
        try:
            # 确保scraping_time_R列是datetime类型
            update_df['scraping_time_R'] = pd.to_datetime(update_df['scraping_time_R'], errors='coerce')
            
            # 获取最新的日期
            latest_date = update_df['scraping_time_R'].max().date()
            print(f"最新数据日期: {latest_date}")
            
            # 筛选最新一天的数据 (即整个最新日期的所有数据)
            latest_data = update_df[update_df['scraping_time_R'].dt.date == latest_date]
            
            # 对于每个作者, 计算其发过帖子(在post_df中)且仍在最新抓取日期活跃(在latest_data中)的url数量
            active_posts = {}
            
            for author in author_base['author']:
                # 获取该作者在post_df中的所有URL (历史帖子)
                if 'author' in post_df.columns and 'url' in post_df.columns:
                    author_posts = set(post_df[post_df['author'] == author]['url'].unique())
                else:
                    author_posts = set()
                
                # 获取该作者在最新日期数据中的所有URL (活跃帖子)
                author_latest = set(latest_data[latest_data['author'] == author]['url'].unique())
                
                # 计算交集 (历史帖子中仍然活跃的)
                active_count = len(author_posts.intersection(author_latest))
                
                # 确保活跃帖数不超过历史贴数
                post_count = author_base.loc[author_base['author'] == author, 'post_count'].values[0] if len(author_base[author_base['author'] == author]) > 0 else 0
                active_count = min(active_count, post_count)
                
                active_posts[author] = active_count
            
            # 创建DataFrame
            active_posts_counts = pd.DataFrame({
                'author': list(active_posts.keys()),
                'active_posts': list(active_posts.values())
            })
            
            print(f"计算了 {len(active_posts_counts)} 个作者的活跃帖子数")
        except Exception as e:
            print(f"计算活跃帖数时出错: {str(e)}")
            traceback.print_exc()
            # 如果出错，将所有作者的活跃帖数设为0
            active_posts_counts = pd.DataFrame({'author': author_base['author'], 'active_posts': 0})
    else:
        print("警告：update.xlsx中缺少必要的列(scraping_time_R/url/author)，无法计算活跃帖数")
        # 将所有作者的活跃帖数设为0
        active_posts_counts = pd.DataFrame({'author': author_base['author'], 'active_posts': 0})
    
    # 将action_counts合并到author_base
    author_ranking = pd.merge(author_base, action_counts[['author', 'repost_count', 'reply_count', 'delete_reply_count']], 
                              on='author', how='left')
    
    # 计算每个作者帖子的最小last_active值
    last_active_values = {}
    
    # 如果update_df中有scraping_time_R列，可以计算last_active
    if 'scraping_time_R' in update_df.columns:
        # 将scraping_time_R转换为datetime类型
        update_df['scraping_time_R'] = pd.to_datetime(update_df['scraping_time_R'], errors='coerce')
        
        # 对于每个作者，找出其最后一次活动时间
        for author in author_base['author']:
            # 获取该作者的所有记录
            author_updates = update_df[update_df['author'] == author]
            
            if not author_updates.empty:
                # 获取最新的活动时间
                latest_time = author_updates['scraping_time_R'].max()
                # 计算last_active（天数）
                days_diff = (create_datetime - latest_time).total_seconds() / (24 * 3600)
                last_active_values[author] = max(0, int(days_diff))
            else:
                last_active_values[author] = 0
    
    # 添加last_active到author_ranking
    if last_active_values:
        last_active_df = pd.DataFrame({'author': list(last_active_values.keys()), 'last_active': list(last_active_values.values())})
        author_ranking = pd.merge(author_ranking, last_active_df, on='author', how='left')
    else:
        author_ranking['last_active'] = 0
    
    # 合并活跃帖数
    author_ranking = pd.merge(author_ranking, active_posts_counts, on='author', how='left')
    
    # 填充缺失值为0
    numerical_columns = ['post_count', 'repost_count', 'reply_count', 'delete_reply_count', 'active_posts', 'last_active']
    for col in numerical_columns:
        if col in author_ranking.columns:
            author_ranking[col] = author_ranking[col].fillna(0).astype(int)
    
    # 打印链接覆盖率统计
    authors_with_link = sum(author_ranking['author_link'] != '')
    total_authors = len(author_ranking)
    coverage_percent = authors_with_link / total_authors * 100 if total_authors > 0 else 0
    print(f"作者链接覆盖率: {authors_with_link}/{total_authors} ({coverage_percent:.2f}%)")
    
    # 按repost_count排序
    author_ranking = author_ranking.sort_values('repost_count', ascending=False)
    
    # 保存用户排行榜数据
    output_path = os.path.join(PROCESSED_DIR, 'author_ranking.csv')
    author_ranking.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"用户排行榜数据已保存至: {output_path}")
    
    return author_ranking

def calculate_author_actions_old_method(post_df, update_df, author_post_counts):
    """旧方法：基于post_df和update_df计算作者的各类操作数量"""
    # 创建作者-URL映射
    author_urls = {}
    for _, row in post_df.iterrows():
        author = row['author']
        url = row['url']
        if author not in author_urls:
            author_urls[author] = set()
        author_urls[author].add(url)
    
    # 计算每个作者的重发、回帖、删回帖次数
    repost_counts = {}
    reply_counts = {}
    delete_reply_counts = {}
    
    for author in author_urls:
        # 获取该作者的所有URL
        author_url_set = author_urls[author]
        
        # 筛选出该作者的所有URL相关的记录
        author_updates = update_df[update_df['url'].isin(author_url_set)]
        
        # 计算重发、回帖、删回帖次数
        repost_count = len(author_updates[author_updates['update_reason'] == '重发'])
        reply_count = len(author_updates[author_updates['update_reason'] == '回帖'])
        delete_reply_count = len(author_updates[author_updates['update_reason'] == '删回帖'])
        
        repost_counts[author] = repost_count
        reply_counts[author] = reply_count
        delete_reply_counts[author] = delete_reply_count
    
    # 创建DataFrame
    repost_df = pd.DataFrame({'author': list(repost_counts.keys()), 'repost_count': list(repost_counts.values())})
    reply_df = pd.DataFrame({'author': list(reply_counts.keys()), 'reply_count': list(reply_counts.values())})
    delete_reply_df = pd.DataFrame({'author': list(delete_reply_counts.keys()), 'delete_reply_count': list(delete_reply_counts.values())})
    
    # 合并到author_ranking
    author_ranking = pd.merge(author_post_counts, repost_df, on='author', how='left')
    author_ranking = pd.merge(author_ranking, reply_df, on='author', how='left')
    author_ranking = pd.merge(author_ranking, delete_reply_df, on='author', how='left')
    
    return author_ranking

def analyze_post_history(list_df):
    """
    分析帖子历史数据
    """
    print("分析帖子历史数据...")
    
    # 检查list_df中是否包含所需的列
    required_columns = ['scraping_time']
    available_columns = ['scraping_time']
    
    if 'update_reason' in list_df.columns:
        available_columns.append('update_reason')
    else:
        # 如果没有update_reason列，添加一个默认值
        list_df['update_reason'] = '未知'
        available_columns.append('update_reason')
    
    # 如果没有thread_id列，尝试从URL中提取
    if 'thread_id' not in list_df.columns:
        print("警告：list_df中缺少thread_id列，尝试从URL中提取")
        if 'url' in list_df.columns:
            list_df['thread_id'] = list_df['url'].apply(
                lambda url: url.split('t_')[-1].replace('.html', '') if pd.notna(url) and 't_' in str(url) else ''
            )
            available_columns.append('thread_id')
        else:
            # 如果没有URL列，使用索引作为thread_id
            print("警告：list_df中也缺少url列，使用索引作为thread_id")
            list_df['thread_id'] = list_df.index.astype(str)
            available_columns.append('thread_id')
    else:
        available_columns.append('thread_id')
    
    # 使用可用的列创建post_history
    post_history = list_df[available_columns].copy()
    
    # 保存帖子历史数据
    output_path = os.path.join(PROCESSED_DIR, 'post_history.csv')
    post_history.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"帖子历史数据已保存至: {output_path}")
    
    # 直接返回可用的列，不尝试访问可能不存在的列
    return post_history

def analyze_author_history(list_df):
    """
    分析作者历史数据
    """
    print("分析作者历史数据...")
    
    # 检查list_df中是否包含所需的列
    required_columns = ['scraping_time']
    available_columns = ['scraping_time']
    
    # 检查并处理可选列
    optional_columns = ['thread_id', 'url', 'title', 'update_reason', 'author']
    for col in optional_columns:
        if col in list_df.columns:
            available_columns.append(col)
        elif col == 'thread_id' and 'url' in list_df.columns:
            # 如果没有thread_id列但有url列，尝试从URL中提取
            if 'thread_id' not in list_df.columns and 'url' in list_df.columns:
                print(f"警告：list_df中缺少{col}列，尝试从URL中提取")
                list_df['thread_id'] = list_df['url'].apply(
                    lambda url: url.split('t_')[-1].replace('.html', '') if pd.notna(url) and 't_' in str(url) else ''
                )
                available_columns.append('thread_id')
        else:
            print(f"警告：list_df中缺少{col}列")
    
    # 如果没有author_id列，但有author列，使用author作为author_id
    if 'author' in list_df.columns and 'author_id' not in list_df.columns:
        print("警告：list_df中缺少author_id列，使用author作为替代")
        list_df['author_id'] = list_df['author']
        available_columns.append('author_id')
    
    # 使用可用的列创建author_history
    author_history = list_df[available_columns].copy()
    
    # 保存作者历史数据
    output_path = os.path.join(PROCESSED_DIR, 'author_history.csv')
    author_history.to_csv(output_path, index=False, encoding='utf-8-sig')
    print(f"作者历史数据已保存至: {output_path}")
    
    # 直接返回可用的列，不尝试访问可能不存在的列
    return author_history

def analyze_car_detail(list_df, post_df, create_datetime):
    """
    分析车辆详情数据
    """
    print("分析车辆详情数据...")
    
    # 检查list_df和post_df中是否包含所需的列
    list_required = ['url', 'title', 'author', 'author_link', 'scraping_time']
    post_required = ['url', 'title', 'post_time', 'author', 'author_link']
    
    list_missing = [col for col in list_required if col not in list_df.columns]
    post_missing = [col for col in post_required if col not in post_df.columns]
    
    if list_missing:
        print(f"警告：list.xlsx中缺少以下列：{list_missing}")
    
    if post_missing:
        print(f"警告：post.xlsx中缺少以下列：{post_missing}")
    
    # 提取有车辆信息的帖子
    car_posts = post_df[
        post_df['title'].str.contains('车|桑塔纳|宝马|奔驰|奥迪|大众|丰田|本田|日产|三菱|现代|起亚|雪佛兰|别克|福特|玛莎拉蒂|法拉利|保时捷|路虎|捷豹|沃尔沃|凯迪拉克', na=False)
    ].copy()
    
    print(f"找到 {len(car_posts)} 个可能包含车辆信息的帖子")
    
    if len(car_posts) == 0:
        # 创建空的DataFrame
        return pd.DataFrame(columns=[
            'thread_id', 'url', 'title', 'author', 'author_link', 
            'days_old', 'post_time', 'last_active', 'price', 'miles', 
            'year', 'model', 'type'
        ])
    
    # 提取最新的帖子状态信息
    latest_posts = list_df.sort_values('scraping_time', ascending=False)
    latest_posts = latest_posts.drop_duplicates('url')
    
    # 合并帖子信息和状态信息
    car_detail = car_posts.merge(latest_posts[['url', 'scraping_time']], on='url', how='left')
    
    # 提取thread_id（从url中）
    car_detail['thread_id'] = car_detail['url'].apply(
        lambda x: x.split('/')[-1].split('.')[0] if pd.notna(x) else None
    )
    
    # 计算帖子年龄（daysold）
    car_detail['post_time'] = pd.to_datetime(car_detail['post_time'])
    car_detail['daysold'] = car_detail['post_time'].apply(
        lambda x: max(0, int((create_datetime - x).total_seconds() / (24*3600))) if pd.notna(x) else 0
    )
    
    # 计算最后活跃时间
    car_detail['post_last_active'] = latest_posts['scraping_time'].apply(
        lambda x: max(0, int((create_datetime - pd.to_datetime(x)).total_seconds() / (24*3600))) if pd.notna(x) else 0
    )
    
    # 添加type字段
    car_detail['type'] = 'car_detail'
    
    # 选择需要的列
    car_detail = car_detail[[
        'thread_id', 'url', 'title', 'author', 'author_link', 
        'daysold', 'post_time', 'post_last_active', 'type'
    ]]
    
    # 重命名列
    car_detail = car_detail.rename(columns={
        'post_time': 'create_time',
        'post_last_active': 'last_active'
    })
    
    # 添加占位符列
    car_detail['price'] = 0
    car_detail['miles'] = 0
    car_detail['year'] = 0
    car_detail['model'] = ''
    
    # 输出csv文件
    output_file = os.path.join(str(PROCESSED_DIR), 'car_detail.csv')
    car_detail.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"车辆详情数据已保存至: {output_file}")
    
    return car_detail

def main():
    """主函数"""
    # 创建输出目录
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    
    # 加载数据
    post_df, list_df, create_datetime, complete_time_series = load_and_preprocess_data()
    
    # 生成所有统计数据
    results = []
    
    # 1. 发帖数据统计
    post_stats = analyze_post_statistics(post_df, complete_time_series)
    post_stats['id'] = [f"post_stat_{i}" for i in range(len(post_stats))]
    post_stats['data_category'] = 'post_statistics'
    results.append(post_stats)
    
    # 2. 帖子更新数据统计
    list_stats = analyze_list_statistics(list_df, complete_time_series)
    list_stats['id'] = [f"list_stat_{i}" for i in range(len(list_stats))]
    list_stats['data_category'] = 'update_statistics'
    results.append(list_stats)
    
    # 3. 阅读量数据统计
    view_stats = analyze_view_statistics(list_df, complete_time_series)
    view_stats['id'] = [f"view_stat_{i}" for i in range(len(view_stats))]
    view_stats['data_category'] = 'view_statistics'
    results.append(view_stats)
    
    # 4. 添加排行榜数据到结果集 - 使用list_df替代update_df
    post_ranking = analyze_post_ranking(post_df, list_df, create_datetime)
    post_ranking['id'] = [f"post_rank_{i}" for i in range(len(post_ranking))]
    post_ranking['data_category'] = 'post_ranking'
    results.append(post_ranking)
    
    # 5. 用户排行榜 - 使用list_df替代update_df
    author_ranking = analyze_author_ranking(post_df, list_df, create_datetime)
    author_ranking['id'] = [f"author_rank_{i}" for i in range(len(author_ranking))]
    author_ranking['data_category'] = 'author_ranking'
    results.append(author_ranking)
    
    # 合并所有结果
    final_df = pd.concat(results, ignore_index=True)
    
    # 处理日期时间格式
    if 'datetime' in final_df.columns:
        final_df['datetime'] = final_df['datetime'].apply(
            lambda x: x.isoformat() if pd.notnull(x) else None
        )
    
    # 去除指定的字段
    columns_to_remove = ['total_count', 'rank', 'scraping_time', 'author_id', 'create_time', 'price', 'miles', 'year', 'model']
    for col in columns_to_remove:
        if col in final_df.columns:
            final_df = final_df.drop(columns=[col])
    
    # 确保数值类型正确
    numeric_columns = ['count', 'duplicate_posts', 'repost_count', 'reply_count', 
                      'delete_reply_count', 'daysold', 'last_active', 'active_posts']
    for col in numeric_columns:
        if col in final_df.columns:
            final_df[col] = pd.to_numeric(final_df[col], errors='coerce').fillna(0).astype(int)
    
    # 保存结果到CSV文件
    output_file = PROCESSED_DIR / 'import.csv'
    final_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"\n分析完成，结果已保存到：{output_file}")
    print(f"数据导入文件：{output_file}")
    
    return final_df

def analyze_data(debug=False):
    """外部调用的入口点函数"""
    try:
        print("开始执行数据分析...")
        if debug:
            print("调试模式：打印更多日志信息")
        
        result_df = main()
        
        print(f"数据分析完成，生成了 {len(result_df)} 条分析记录")
        return True
    except Exception as e:
        print(f"数据分析执行出错: {str(e)}")
        if debug:
            import traceback
            traceback.print_exc()
        return False

if __name__ == "__main__":
    main() 