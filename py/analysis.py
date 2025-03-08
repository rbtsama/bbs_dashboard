import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import warnings
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
        complete_reason_stats['type'] = f'list_{reason}'
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
            'view_gap': item['view_gap'],
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
        complete_view_stats['view_gap'] = 0
        complete_view_stats['duplicate_posts'] = 0
    
    # 填充空值为0
    complete_view_stats['view_gap'] = complete_view_stats['view_gap'].fillna(0).astype(int)
    complete_view_stats['duplicate_posts'] = complete_view_stats['duplicate_posts'].fillna(0).astype(int)
    complete_view_stats['type'] = 'view'
    
    return complete_view_stats[['type', 'datetime', 'view_gap', 'duplicate_posts']]

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
    list_df = pd.read_excel(PROCESSED_DIR / 'list.xlsx')
    
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

def analyze_post_ranking(list_df, post_df, create_datetime):
    """分析帖子排行榜"""
    # 统计每个帖子的更新次数
    post_stats = list_df.groupby('url').agg({
        'update_reason': lambda x: x.value_counts().to_dict(),
        'scraping_time': 'max'  # 获取每个URL的最新scraping_time
    }).reset_index()
    
    # 直接从list_df中获取所有URL的title和author信息
    print("从list_df中获取所有URL的title和author信息")
    
    # 检查list_df中是否包含author字段
    if 'author' in list_df.columns:
        # 按URL分组，取最新的记录
        list_info = list_df.sort_values('scraping_time', ascending=False)
        list_info = list_info[['url', 'title', 'author', 'author_link']].drop_duplicates(subset=['url'], keep='first')
        
        # 合并信息
        post_ranking = post_stats.merge(list_info, on='url', how='left')
    else:
        # 如果list_df中没有author字段，只获取title
        print("警告: list_df中不包含author字段，只能获取title信息")
        list_info = list_df.sort_values('scraping_time', ascending=False)
        list_info = list_info[['url', 'title']].drop_duplicates(subset=['url'], keep='first')
        
        # 合并信息
        post_ranking = post_stats.merge(list_info, on='url', how='left')
        post_ranking['author'] = '未知作者'
        post_ranking['author_link'] = ''
    
    # 检查合并后缺失的title
    missing_title = post_ranking[post_ranking['title'].isna()].shape[0]
    if missing_title > 0:
        print(f"警告: 合并后仍有{missing_title}个URL没有title信息")
        # 填充缺失的title
        post_ranking['title'] = post_ranking['title'].fillna('未知标题')
    
    # 计算帖子年龄 - 使用post_df中的post_time计算，但不保留在结果中
    post_df_with_time = post_df[['url', 'post_time']].drop_duplicates()
    post_df_with_time['post_time'] = pd.to_datetime(post_df_with_time['post_time'])
    post_ranking = post_ranking.merge(post_df_with_time, on='url', how='left')
    
    # 处理空值
    post_ranking['Days_Old'] = post_ranking['post_time'].apply(
        lambda x: ((create_datetime - x).total_seconds() / (24*3600) if pd.notna(x) else 0)
    ).astype(int)
    
    # 计算last_active - URL最新的list time距离今天的天数，不足1天为0
    post_ranking['scraping_time'] = pd.to_datetime(post_ranking['scraping_time'])
    post_ranking['last_active'] = post_ranking['scraping_time'].apply(
        lambda x: max(0, int((create_datetime - x).total_seconds() / (24*3600))) if pd.notna(x) else 0
    )
    
    # 移除post_time和scraping_time字段，不再需要
    post_ranking.drop(['post_time', 'scraping_time'], axis=1, inplace=True)
    
    # 确保title和author字段不为空
    post_ranking['title'] = post_ranking['title'].fillna('未知标题')
    post_ranking['author'] = post_ranking['author'].fillna('未知作者')
    post_ranking['author_link'] = post_ranking['author_link'].fillna('')
    
    # 展开更新原因统计（使用英文字段名）
    post_ranking['repost_count'] = post_ranking['update_reason'].apply(lambda x: x.get('重发', 0))
    post_ranking['reply_count'] = post_ranking['update_reason'].apply(lambda x: x.get('回帖', 0))
    post_ranking['delete_count'] = post_ranking['update_reason'].apply(lambda x: x.get('删回帖', 0))
    
    # 按重发次数降序排序
    post_ranking.sort_values('repost_count', ascending=False, inplace=True)
    
    # 添加type字段
    post_ranking['type'] = 'post_rank'
    
    return post_ranking[['type', 'url', 'title', 'Days_Old', 'author', 'author_link', 'repost_count', 'reply_count', 'delete_count', 'last_active']]

def analyze_author_ranking(list_df, create_datetime):
    """分析用户排行榜"""
    # 获取用户对应的author_link
    author_links = list_df[['author', 'author_link']].drop_duplicates()
    # 如果一个author有多个author_link，取第一个
    author_links = author_links.drop_duplicates(subset=['author'], keep='first')
    
    # 统计每个作者的更新次数
    author_stats = list_df.groupby('author').agg({
        'update_reason': lambda x: x.value_counts().to_dict(),
        'scraping_time': 'max'
    }).reset_index()
    
    # 合并author_link信息
    author_stats = author_stats.merge(author_links, on='author', how='left')
    
    # 对于没有author_link的行，设置为空字符串
    author_stats['author_link'] = author_stats['author_link'].fillna('')
    
    # 计算最后活跃时间
    author_stats['scraping_time'] = pd.to_datetime(author_stats['scraping_time'])
    author_stats['last_active'] = ((create_datetime - author_stats['scraping_time']).dt.total_seconds() / (24*3600)).astype(int)
    
    # 展开更新原因统计（使用英文字段名）
    author_stats['repost_count'] = author_stats['update_reason'].apply(lambda x: x.get('重发', 0))
    author_stats['reply_count'] = author_stats['update_reason'].apply(lambda x: x.get('回帖', 0))
    author_stats['delete_count'] = author_stats['update_reason'].apply(lambda x: x.get('删回帖', 0))
    
    # 按重发次数降序排序
    author_stats.sort_values('repost_count', ascending=False, inplace=True)
    
    # 添加type字段
    author_stats['type'] = 'author_rank'
    
    return author_stats[['type', 'author', 'author_link', 'repost_count', 'reply_count', 'delete_count', 'last_active']]

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
    # 添加唯一ID和数据类型标识
    post_stats['id'] = [f"post_stat_{i}" for i in range(len(post_stats))]
    post_stats['data_category'] = 'post_statistics'
    results.append(post_stats)
    
    # 2. 帖子更新数据统计
    list_stats = analyze_list_statistics(list_df, complete_time_series)
    # 添加唯一ID和数据类型标识
    list_stats['id'] = [f"list_stat_{i}" for i in range(len(list_stats))]
    list_stats['data_category'] = 'update_statistics'
    results.append(list_stats)
    
    # 3. 阅读量数据统计
    view_stats = analyze_view_statistics(list_df, complete_time_series)
    # 添加唯一ID和数据类型标识
    view_stats['id'] = [f"view_stat_{i}" for i in range(len(view_stats))]
    view_stats['data_category'] = 'view_statistics'
    results.append(view_stats)
    
    # 4. 帖子排行榜
    post_ranking = analyze_post_ranking(list_df, post_df, create_datetime)
    # 添加唯一ID和数据类型标识
    post_ranking['id'] = [f"post_rank_{i}" for i in range(len(post_ranking))]
    post_ranking['data_category'] = 'post_ranking'
    results.append(post_ranking)
    
    # 5. 用户排行榜
    author_ranking = analyze_author_ranking(list_df, create_datetime)
    # 添加唯一ID和数据类型标识
    author_ranking['id'] = [f"author_rank_{i}" for i in range(len(author_ranking))]
    author_ranking['data_category'] = 'author_ranking'
    results.append(author_ranking)
    
    # 合并所有结果
    final_df = pd.concat(results, ignore_index=True)
    
    # 处理日期时间格式
    if 'datetime' in final_df.columns:
        # 使用ISO标准格式输出日期时间
        final_df['datetime'] = final_df['datetime'].apply(
            lambda x: x.isoformat() if pd.notnull(x) else None
        )
    
    # 确保数值类型正确
    numeric_columns = ['count', 'view_gap', 'duplicate_posts', 'repost_count', 'reply_count', 'delete_count', 'Days_Old', 'last_active']
    for col in numeric_columns:
        if col in final_df.columns:
            final_df[col] = pd.to_numeric(final_df[col], errors='coerce').fillna(0).astype(int)
    
    # 保存结果到CSV文件
    output_file = PROCESSED_DIR / 'import.csv'
    
    # 保存到CSV文件，不使用索引，使用UTF-8编码
    final_df.to_csv(output_file, index=False, encoding='utf-8-sig')
    print(f"分析完成，结果已保存到：{output_file}")
    
    # 同时保存一个JSON格式的文件，更适合导入数据库
    json_output_file = PROCESSED_DIR / 'import.json'
    final_df.to_json(json_output_file, orient='records', date_format='iso')
    print(f"同时保存了JSON格式文件：{json_output_file}")
    
    # 保存一个SQLite数据库文件，直接可用于数据库操作
    import sqlite3
    db_output_file = PROCESSED_DIR / 'import.db'
    conn = sqlite3.connect(str(db_output_file))
    
    # 按数据类别分表保存
    for category in final_df['data_category'].unique():
        category_df = final_df[final_df['data_category'] == category].copy()
        # 移除data_category列，避免冗余
        category_df.drop('data_category', axis=1, inplace=True)
        # 将表名中的下划线替换为更清晰的名称
        table_name = category.replace('_', '')
        category_df.to_sql(table_name, conn, if_exists='replace', index=False)
    
    conn.close()
    print(f"同时保存了SQLite数据库文件：{db_output_file}")

if __name__ == "__main__":
    main() 