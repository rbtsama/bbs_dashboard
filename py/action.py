import pandas as pd
import os
import sqlite3
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
import numpy as np
import time
from colorama import init, Fore, Style
import sys

# 设置控制台输出编码
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

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
        # 只从thread_history表获取信息
        cursor.execute("""
            SELECT url, title, author 
            FROM thread_history 
            WHERE url = ? 
            ORDER BY scraping_time DESC 
            LIMIT 1
        """, (url,))
        result = cursor.fetchone()
        if result:
            return {
                'url': result[0],
                'title': result[1],
                'author': result[2]
            }
        return None
    except Exception as e:
        print(f"{Fore.YELLOW}获取thread信息出错: {str(e)}{Style.RESET_ALL}")
        return None

def process_actions():
    """处理帖子异动数据并导出到CSV"""
    print(f"{Fore.GREEN}开始处理帖子异动数据...{Style.RESET_ALL}")
    
    # 加载数据
    show_progress("正在加载Excel数据")
    try:
        # 读取Excel文件时指定dtype以确保正确的编码
        update_df = pd.read_excel(
            PROCESSED_DIR / 'update.xlsx',
            dtype={
                'url': str,
                'title': str,
                'author': str,
                'update_reason': str
            }
        )
        post_df = pd.read_excel(
            PROCESSED_DIR / 'post.xlsx',
            dtype={
                'url': str,
                'title': str,
                'author': str
            }
        )
    except Exception as e:
        print(f"{Fore.RED}加载Excel数据失败: {str(e)}{Style.RESET_ALL}")
        return
    
    # 连接数据库获取额外信息
    show_progress("正在连接数据库")
    conn = None
    try:
        conn = sqlite3.connect(str(DB_PATH))
        # 设置数据库连接的编码
        conn.text_factory = str
        print(f"{Fore.GREEN}数据库连接成功{Style.RESET_ALL}")
    except Exception as e:
        print(f"{Fore.RED}数据库连接失败: {str(e)}{Style.RESET_ALL}")
        return
    
    # 获取所有不重复的URL
    unique_urls = pd.concat([post_df['url'], update_df['url']]).unique()
    url_count = len(unique_urls)
    print(f"{Fore.GREEN}找到 {url_count} 个不重复的URL{Style.RESET_ALL}")
    
    # 创建结果列表
    results = []
    
    # 预处理post_df，创建url索引以提高查询性能
    post_df_dict = {}
    for _, row in post_df.iterrows():
        if pd.notna(row['url']):
            post_df_dict[row['url']] = {
                'post_time': row['post_time'],
                'title': str(row['title']),
                'author': str(row['author'])
            }
    
    # 预处理update_df，创建url索引以提高查询性能
    update_df_dict = {}
    for _, row in update_df.iterrows():
        if pd.notna(row['url']):
            if row['url'] not in update_df_dict:
                update_df_dict[row['url']] = []
            update_df_dict[row['url']].append({
                'scraping_time': row['scraping_time'],
                'update_reason': str(row['update_reason']) if pd.notna(row.get('update_reason')) else None,
                'title': str(row['title']),
                'author': str(row['author'])
            })
    
    # 遍历URL
    print(f"{Fore.GREEN}开始处理URL数据...{Style.RESET_ALL}")
    for url in tqdm(unique_urls, desc="处理URL进度", 
                   bar_format="{l_bar}%s{bar}%s{r_bar}" % (Fore.BLUE, Style.RESET_ALL)):
        try:
            # 从URL中提取thread_id
            thread_id = extract_thread_id_from_url(url)
            
            # 获取发帖记录
            post_info = post_df_dict.get(url)
            if post_info:
                results.append({
                    'thread_id': thread_id,
                    'url': url,
                    'title': post_info['title'],
                    'author': post_info['author'],
                    'action_time': post_info['post_time'],
                    'action': '新发布',
                    'source': 'post.xlsx'
                })
            
            # 获取更新记录
            update_records = update_df_dict.get(url, [])
            if update_records:
                # 按时间排序
                update_records.sort(key=lambda x: x['scraping_time'])
                
                # 如果没有发帖记录，使用第一条记录的信息
                if not post_info:
                    title = update_records[0]['title']
                    author = update_records[0]['author']
                else:
                    title = post_info['title']
                    author = post_info['author']
                
                # 记录上一次的更新原因，用于去重
                last_action = None
                last_time = None
                
                # 添加更新记录
                for record in update_records:
                    update_reason = record.get('update_reason')
                    current_time = record['scraping_time']
                    
                    # 只处理有更新原因的记录
                    if pd.notna(update_reason):
                        # 如果与上一次动作相同且时间间隔小于1小时，则跳过
                        if (last_action == update_reason and 
                            last_time is not None and 
                            (current_time - last_time).total_seconds() < 3600):
                            continue
                            
                        # 添加动作记录
                        results.append({
                            'thread_id': thread_id,
                            'url': url,
                            'title': title,
                            'author': author,
                            'action_time': current_time,
                            'action': update_reason,
                            'source': 'update.xlsx'
                        })
                        
                        # 更新上一次动作信息
                        last_action = update_reason
                        last_time = current_time
                        
        except Exception as e:
            print(f"{Fore.RED}处理URL {url} 时出错: {str(e)}{Style.RESET_ALL}")
            continue
    
    # 关闭数据库连接
    if conn:
        conn.close()
    
    # 转换为DataFrame并保存
    if results:
        show_progress("正在保存结果")
        result_df = pd.DataFrame(results)
        
        # 确保时间格式正确
        result_df['action_time'] = pd.to_datetime(result_df['action_time'])
        result_df['action_time'] = result_df['action_time'].dt.strftime('%Y-%m-%d %H:%M:%S')
        
        # 按时间排序
        result_df = result_df.sort_values('action_time')
        
        # 使用utf-8-sig编码保存CSV，以支持Excel正确显示中文
        result_df.to_csv(OUTPUT_FILE, index=False, encoding='utf-8-sig')
        
        # 统计各类动作的数量
        action_counts = result_df['action'].value_counts()
        print(f"\n{Fore.GREEN}处理完成！动作统计：{Style.RESET_ALL}")
        for action, count in action_counts.items():
            print(f"  {action}: {count}条记录")
        
        # 显示前几行数据作为预览
        print("\n数据预览（前3行）:")
        preview = result_df.head(3)
        for _, row in preview.iterrows():
            print(f"标题: {row['title']}")
            print(f"作者: {row['author']}")
            print(f"动作: {row['action']}")
            print(f"时间: {row['action_time']}")
            print("-" * 50)
    else:
        print(f"{Fore.RED}没有找到任何记录{Style.RESET_ALL}")

if __name__ == "__main__":
    process_actions()