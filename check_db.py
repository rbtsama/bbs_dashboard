import sqlite3
import pandas as pd
import os
from datetime import datetime
import traceback

def safe_cast(val, to_type, default=None):
    try:
        if pd.isna(val) or val == '':
            return default
        return to_type(val)
    except:
        return default

class DatabaseChecker:
    def __init__(self, db_path):
        self.db_path = os.path.abspath(db_path)
        self.conn = None
        self.cursor = None
    
    def connect(self):
        if not os.path.exists(self.db_path):
            raise FileNotFoundError(f'数据库文件不存在: {self.db_path}')
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()
    
    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()
    
    def check_table_info(self, table):
        try:
            # 获取记录数
            self.cursor.execute(f'SELECT COUNT(*) FROM {table}')
            count = self.cursor.fetchone()[0]
            
            # 获取表结构
            self.cursor.execute(f'PRAGMA table_info({table})')
            columns = self.cursor.fetchall()
            
            # 获取索引
            self.cursor.execute(f"SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='{table}'")
            indexes = self.cursor.fetchall()
            
            return {
                'count': count,
                'columns': columns,
                'indexes': indexes
            }
        except sqlite3.OperationalError as e:
            return {'error': str(e)}
    
    def check_post_ranking(self):
        try:
            self.cursor.execute('SELECT * FROM post_ranking')
            rows = self.cursor.fetchall()
            columns = [description[0] for description in self.cursor.description]
            df = pd.DataFrame(rows, columns=columns)
            
            # 转换数值字段
            numeric_fields = ['repost_count', 'reply_count', 'delete_reply_count', 'daysold', 'last_active']
            for field in numeric_fields:
                if field in df.columns:
                    df[field] = df[field].apply(lambda x: safe_cast(x, int, 0))
            
            stats = {
                'total_records': len(df),
                'unique_authors': df['author'].nunique(),
                'numeric_stats': {}
            }
            
            for field in numeric_fields:
                if field in df.columns:
                    stats['numeric_stats'][field] = {
                        'mean': df[field].mean(),
                        'max': df[field].max(),
                        'min': df[field].min(),
                        'null_count': df[field].isna().sum()
                    }
            
            # Top 5重发帖子
            stats['top_reposts'] = df.nlargest(5, 'repost_count')[['title', 'author', 'repost_count', 'reply_count']].to_dict('records')
            
            return stats
        except Exception as e:
            return {'error': str(e)}
    
    def check_author_ranking(self):
        try:
            self.cursor.execute('SELECT * FROM author_ranking')
            rows = self.cursor.fetchall()
            columns = [description[0] for description in self.cursor.description]
            df = pd.DataFrame(rows, columns=columns)
            
            # 转换数值字段
            numeric_fields = ['post_count', 'repost_count', 'reply_count', 'delete_reply_count', 'last_active', 'active_posts']
            for field in numeric_fields:
                if field in df.columns:
                    df[field] = df[field].apply(lambda x: safe_cast(x, int, 0))
            
            stats = {
                'total_authors': len(df),
                'numeric_stats': {}
            }
            
            for field in numeric_fields:
                if field in df.columns:
                    stats['numeric_stats'][field] = {
                        'mean': df[field].mean(),
                        'max': df[field].max(),
                        'min': df[field].min(),
                        'null_count': df[field].isna().sum()
                    }
            
            # Top 5活跃作者
            stats['top_authors'] = df.nlargest(5, 'active_posts')[['author', 'post_count', 'active_posts', 'reply_count']].to_dict('records')
            
            return stats
        except Exception as e:
            return {'error': str(e)}
    
    def check_time_ranges(self):
        try:
            time_ranges = {}
            
            # posts表时间范围
            self.cursor.execute('SELECT MIN(post_time), MAX(post_time), MIN(scraping_time), MAX(scraping_time) FROM posts')
            earliest_post, latest_post, earliest_scrape, latest_scrape = self.cursor.fetchone()
            time_ranges['posts'] = {
                'post_time': {'earliest': earliest_post, 'latest': latest_post},
                'scraping_time': {'earliest': earliest_scrape, 'latest': latest_scrape}
            }
            
            # list表时间范围
            self.cursor.execute('SELECT MIN(list_time), MAX(list_time), MIN(scraping_time), MAX(scraping_time) FROM list')
            earliest_list, latest_list, earliest_scrape, latest_scrape = self.cursor.fetchone()
            time_ranges['list'] = {
                'list_time': {'earliest': earliest_list, 'latest': latest_list},
                'scraping_time': {'earliest': earliest_scrape, 'latest': latest_scrape}
            }
            
            return time_ranges
        except Exception as e:
            return {'error': str(e)}

def format_time(t):
    try:
        if pd.isna(t) or t == '':
            return 'N/A'
        dt = pd.to_datetime(t)
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return str(t)

def print_table_info(table, info):
    if 'error' in info:
        print(f'\n{table} 表: 检查出错 - {info["error"]}')
        return
    
    print(f'\n{table} 表:')
    print(f'记录数: {info["count"]:,d}')
    
    print('字段列表:')
    for col in info['columns']:
        name, type_, notnull, dflt_value, pk = col[1:6]
        constraints = []
        if pk: constraints.append('PRIMARY KEY')
        if notnull: constraints.append('NOT NULL')
        if dflt_value is not None: constraints.append(f'DEFAULT {dflt_value}')
        print(f'  - {name:<20} {type_:<10} {" ".join(constraints)}')
    
    if info['indexes']:
        print('索引:')
        for name, sql in info['indexes']:
            print(f'  - {name}')
            if sql:
                print(f'    {sql}')

def print_post_ranking_stats(stats):
    if 'error' in stats:
        print('\npost_ranking表: 检查出错 -', stats['error'])
        return
    
    print('\npost_ranking表数据统计：')
    print('-' * 50)
    print(f'总记录数: {stats["total_records"]:,d}')
    print(f'不同作者数: {stats["unique_authors"]:,d}')
    
    print('\n数值字段统计：')
    for field, field_stats in stats['numeric_stats'].items():
        print(f'{field}:')
        print(f'  - 平均值: {field_stats["mean"]:.1f}')
        print(f'  - 最大值: {field_stats["max"]:,d}')
        print(f'  - 最小值: {field_stats["min"]:,d}')
        print(f'  - 空值数: {field_stats["null_count"]:,d}')
    
    print('\nTop 5重发帖子：')
    for post in stats['top_reposts']:
        print(f'- {post["title"][:30]}... ({post["author"]}) - 重发: {post["repost_count"]}, 回复: {post["reply_count"]}')

def print_author_ranking_stats(stats):
    if 'error' in stats:
        print('\nauthor_ranking表: 检查出错 -', stats['error'])
        return
    
    print('\nauthor_ranking表数据统计：')
    print('-' * 50)
    print(f'总作者数: {stats["total_authors"]:,d}')
    
    print('\n数值字段统计：')
    for field, field_stats in stats['numeric_stats'].items():
        print(f'{field}:')
        print(f'  - 平均值: {field_stats["mean"]:.1f}')
        print(f'  - 最大值: {field_stats["max"]:,d}')
        print(f'  - 最小值: {field_stats["min"]:,d}')
        print(f'  - 空值数: {field_stats["null_count"]:,d}')
    
    print('\nTop 5活跃作者：')
    for author in stats['top_authors']:
        print(f'- {author["author"]} - 发帖: {author["post_count"]}, 活跃: {author["active_posts"]}, 回复: {author["reply_count"]}')

def print_time_ranges(ranges):
    if 'error' in ranges:
        print('\n时间范围检查: 出错 -', ranges['error'])
        return
    
    print('\n时间范围检查：')
    print('-' * 50)
    
    for table, times in ranges.items():
        print(f'\n{table}表时间范围:')
        for time_type, range_info in times.items():
            print(f'- {time_type}: {format_time(range_info["earliest"])} 至 {format_time(range_info["latest"])}')

def check_db():
    db_path = os.path.join(os.path.dirname(__file__), '..', 'backend', 'db', 'forum_data.db')
    checker = None
    
    try:
        checker = DatabaseChecker(db_path)
        checker.connect()
        print(f'数据库路径: {checker.db_path}')
        
        # 获取所有表名
        checker.cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in checker.cursor.fetchall()]
        
        # 检查主要表的记录数和结构
        main_tables = ['posts', 'list', 'detail', 'car_info', 'post_history', 'import', 'author_ranking', 'post_ranking']
        print('\n主要表记录数和结构：')
        print('-' * 50)
        
        for table in main_tables:
            if table not in tables:
                print(f'{table:<15}: 表不存在')
                continue
            
            info = checker.check_table_info(table)
            print_table_info(table, info)
        
        # 检查post_ranking表数据
        stats = checker.check_post_ranking()
        print_post_ranking_stats(stats)
        
        # 检查author_ranking表数据
        stats = checker.check_author_ranking()
        print_author_ranking_stats(stats)
        
        # 检查时间范围
        ranges = checker.check_time_ranges()
        print_time_ranges(ranges)
    
    except Exception as e:
        print(f'检查数据库时出错:')
        print(traceback.format_exc())
    
    finally:
        if checker:
            checker.close()

if __name__ == '__main__':
    check_db() 