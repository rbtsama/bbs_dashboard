import pandas as pd
import os
import sqlite3
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
import numpy as np
import time
from colorama import init, Fore, Style

# 初始化colorama以支持彩色输出
init()

# 设置数据路径
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
RAW_DIR = DATA_DIR / 'raw'
PROCESSED_DIR = DATA_DIR / 'processed'
OUTPUT_FILE = PROCESSED_DIR / 'action.csv'
DB_PATH = BASE_DIR / 'backend' / 'db' / 'forum_data.db'

# 进度条和提示信息
def show_progress(message, delay=0.1):
    """显示加载动画"""
    print(f"{Fore.CYAN}{message}{Style.RESET_ALL}", end="", flush=True)
    for _ in range(3):
        time.sleep(delay)
        print(".", end="", flush=True)
    print(" 完成！")

def extract_thread_id_from_url(url):
    """从URL中提取thread_id"""
    try:
        # 从URL中提取，格式通常是 page_viewtopic/t_123456.html
        return url.split('t_')[-1].replace('.html', '')
    except:
        return None

def get_thread_info_from_db(conn, url):
    """从数据库获取URL对应的thread信息"""
    cursor = conn.cursor()
    try:
        # 尝试从postranking表中获取信息
        cursor.execute("SELECT url, title, author, author_link FROM postranking WHERE url = ?", (url,))
        result = cursor.fetchone()
        if result:
            return {
                'url': result[0],
                'title': result[1],
                'author': result[2],
                'author_link': result[3]
            }
        
        # 尝试从其他表获取信息
        for table in ['thread_history', 'thread_follows', 'follow_history']:
            try:
                cursor.execute(f"SELECT url, title, author FROM {table} WHERE url = ?", (url,))
                result = cursor.fetchone()
                if result:
                    return {
                        'url': result[0],
                        'title': result[1],
                        'author': result[2]
                    }
            except sqlite3.OperationalError:
                # 表可能不存在或结构不同
                continue
                
        return None
    except Exception as e:
        print(f"{Fore.YELLOW}获取thread信息出错: {e}{Style.RESET_ALL}")
        return None

def process_actions():
    """处理帖子异动数据并导出到CSV"""
    print(f"{Fore.GREEN}开始处理帖子异动数据...{Style.RESET_ALL}")
    
    # 加载数据
    show_progress("正在加载Excel数据")
    list_df = pd.read_excel(PROCESSED_DIR / 'list.xlsx')
    post_df = pd.read_excel(PROCESSED_DIR / 'post.xlsx')
    
    # 连接数据库获取额外信息
    show_progress("正在连接数据库")
    conn = None
    try:
        conn = sqlite3.connect(str(DB_PATH))
        print(f"{Fore.GREEN}数据库连接成功{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}数据库连接失败: {e}{Style.RESET_ALL}")
    
    # 获取所有不重复的URL
    unique_urls = list_df['url'].unique()
    url_count = len(unique_urls)
    print(f"{Fore.GREEN}找到 {url_count} 个不重复的URL{Style.RESET_ALL}")
    
    # 创建结果列表
    results = []
    
    # 遍历URL
    print(f"{Fore.GREEN}开始处理URL数据...{Style.RESET_ALL}")
    for i, url in enumerate(tqdm(unique_urls, desc="处理URL进度", 
                                 bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.BLUE, Style.RESET_ALL))):
        # 从URL中提取thread_id
        thread_id = extract_thread_id_from_url(url)
        
        # 尝试从数据库获取额外信息
        db_info = None
        if conn:
            db_info = get_thread_info_from_db(conn, url)
        
        # 添加发帖记录 - 从post.xlsx获取发帖时间
        post_records = post_df[post_df['url'] == url]
        if not post_records.empty:
            # 找到最早的发帖时间
            post_time = post_records['post_time'].min()
            title = post_records.iloc[0]['title']
            author = post_records.iloc[0]['author']
            
            results.append({
                'thread_id': thread_id,
                'url': url,
                'title': title,
                'author': author,
                'action_time': post_time,
                'action': '新发布',
                'source': 'post.xlsx'
            })
        
        # 查找所有列表记录并按抓取时间排序
        list_records = list_df[list_df['url'] == url].sort_values('scraping_time')
        
        # 如果post.xlsx中没有记录，从list.xlsx或数据库中获取标题和作者信息
        if post_records.empty:
            if not list_records.empty:
                title = list_records.iloc[0]['title']
                author = list_records.iloc[0]['author']
            elif db_info:
                title = db_info.get('title')
                author = db_info.get('author')
            else:
                title = None
                author = None
        
        # 添加更新记录
        for idx, row in list_records.iterrows():
            if pd.notna(row['update_reason']):
                results.append({
                    'thread_id': thread_id,
                    'url': url,
                    'title': title,
                    'author': author,
                    'action_time': row['scraping_time'],
                    'action': row['update_reason'],
                    'source': 'list.xlsx'
                })
        
        # 每处理100个URL显示一次进度
        if (i + 1) % 100 == 0 or i == url_count - 1:
            print(f"{Fore.GREEN}已处理 {i+1}/{url_count} 个URL ({((i+1)/url_count*100):.2f}%){Style.RESET_ALL}")
    
    # 关闭数据库连接
    if conn:
        conn.close()
        print(f"{Fore.GREEN}数据库连接已关闭{Style.RESET_ALL}")
    
    # 创建DataFrame
    if results:
        show_progress("正在整理数据")
        result_df = pd.DataFrame(results)
        
        # 确保action_time是datetime类型
        result_df['action_time'] = pd.to_datetime(result_df['action_time'])
        
        # 按照thread_id和action_time排序
        show_progress("正在排序数据")
        result_df.sort_values(['thread_id', 'action_time'], inplace=True)
        
        # 确保所有列都是字符串格式，避免任何潜在的格式问题
        for col in result_df.columns:
            if col == 'action_time':
                # 格式化日期时间
                result_df[col] = result_df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
            else:
                # 其他列转为字符串
                result_df[col] = result_df[col].astype(str)
        
        # 导出到CSV，确保正确处理中文 - 尝试处理文件可能被占用的问题
        show_progress("正在导出数据到CSV")
        try:
            # 先尝试检查文件是否可以访问
            if os.path.exists(OUTPUT_FILE):
                # 尝试重命名文件测试是否被占用
                temp_file = str(OUTPUT_FILE) + '.temp'
                try:
                    os.rename(OUTPUT_FILE, temp_file)
                    os.rename(temp_file, OUTPUT_FILE)
                except PermissionError:
                    # 文件被占用，使用一个临时文件名
                    print(f"{Fore.YELLOW}原CSV文件可能被占用，将使用一个新文件名{Style.RESET_ALL}")
                    OUTPUT_FILE = PROCESSED_DIR / f'action_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            
            # 导出到CSV
            result_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
            print(f"{Fore.GREEN}已将 {len(result_df)} 条帖子异动数据导出到 {OUTPUT_FILE}{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}导出CSV时出错: {e}{Style.RESET_ALL}")
            # 尝试使用不同的文件名
            alt_file = PROCESSED_DIR / f'action_alt_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
            try:
                result_df.to_csv(alt_file, index=False, encoding='utf-8-sig')
                print(f"{Fore.GREEN}已将数据导出到备用文件: {alt_file}{Style.RESET_ALL}")
                OUTPUT_FILE = alt_file
            except Exception as e2:
                print(f"{Fore.RED}导出备用CSV也失败: {e2}{Style.RESET_ALL}")
        
        # 显示操作类型的统计
        print(f"\n{Fore.GREEN}异动类型统计:{Style.RESET_ALL}")
        action_counts = result_df['action'].value_counts().head(10)  # 只显示前10种最常见的异动类型
        for action, count in action_counts.items():
            print(f"{Fore.CYAN}{action}: {count}{Style.RESET_ALL}")
        
        if len(result_df['action'].unique()) > 10:
            print(f"{Fore.CYAN}... 以及其他 {len(result_df['action'].unique()) - 10} 种异动类型{Style.RESET_ALL}")
        
        # 验证生成的CSV文件
        print(f"\n{Fore.GREEN}验证生成的CSV文件...{Style.RESET_ALL}")
        try:
            check_df = pd.read_csv(OUTPUT_FILE)
            print(f"{Fore.CYAN}CSV文件记录数: {len(check_df)}{Style.RESET_ALL}")
            print(f"{Fore.CYAN}CSV文件编码: utf-8-sig (支持中文){Style.RESET_ALL}")
            
            # 输出一个表格格式的样例
            print(f"\n{Fore.GREEN}CSV文件前3行样例:{Style.RESET_ALL}")
            sample_df = check_df.head(3)[['thread_id', 'title', 'author', 'action_time', 'action']]
            
            # 使用更清晰的表格格式输出
            headers = sample_df.columns.tolist()
            widths = [15, 30, 15, 20, 25]  # 各列的宽度
            
            # 打印表头
            header_line = " | ".join([f"{h:<{w}}" for h, w in zip(headers, widths)])
            sep_line = "-+-".join(["-" * w for w in widths])
            print(header_line)
            print(sep_line)
            
            # 打印数据行
            for _, row in sample_df.iterrows():
                row_values = [str(v) for v in row.values]
                # 截断过长的字符串
                row_values = [v[:w-3] + "..." if len(v) > w else v for v, w in zip(row_values, widths)]
                row_line = " | ".join([f"{v:<{w}}" for v, w in zip(row_values, widths)])
                print(row_line)
            
            print(f"\n{Fore.GREEN}CSV文件生成成功！{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.RED}验证CSV文件时出错: {e}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}没有找到帖子异动数据{Style.RESET_ALL}")

if __name__ == "__main__":
    process_actions()