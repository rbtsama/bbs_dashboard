import sqlite3
import pandas as pd
import os
from datetime import datetime
import sys

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), 'db', 'forum_data.db')

def get_db_connection():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def import_car_info():
    """导入车辆信息"""
    try:
        conn = get_db_connection()
        
        # 读取CSV文件
        csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'processed', 'car_info.csv')
        print(f"读取CSV文件: {csv_path}")
        
        if not os.path.exists(csv_path):
            print(f"错误: CSV文件不存在: {csv_path}")
            return 0
            
        try:
            # 尝试读取文件的前几行
            with open(csv_path, 'r', encoding='utf-8') as f:
                print("CSV文件前5行:")
                for i, line in enumerate(f):
                    if i < 5:
                        print(f"  {i+1}: {line.strip()}")
                    else:
                        break
        except Exception as e:
            print(f"读取文件前几行时出错: {e}")
        
        try:
            df = pd.read_csv(csv_path, encoding='utf-8')
            print(f"CSV文件读取成功，共 {len(df)} 条记录")
        except Exception as e:
            print(f"读取CSV失败: {e}")
            raise
        
        # 获取list表信息，用于关联
        list_df = pd.read_sql("""
            SELECT 
                url, 
                author, 
                list_time AS post_time,
                julianday('now') - julianday(list_time) AS daysold,
                julianday('now') - julianday(scraping_time) AS last_active,
                title
            FROM list
        """, conn)
        
        print(f"从list表获取了 {len(list_df)} 条记录")
        
        # 创建URL到list数据的映射
        list_dict = {}
        for _, row in list_df.iterrows():
            list_dict[row['url']] = {
                'author': row['author'],
                'post_time': row['post_time'],
                'daysold': row['daysold'],
                'last_active': row['last_active'],
                'title': row['title']
            }
        
        # 计算导入时间
        now = datetime.now()
        
        # 准备批量插入
        records = []
        skipped = 0
        for _, row in df.iterrows():
            # 跳过trade_type为"不知道"的记录
            if pd.isna(row['trade_type']) or row['trade_type'] == '不知道':
                skipped += 1
                continue
                
            url = row['url']
            thread_id = url.split('/')[-1].split('.')[0].replace('t_', '')
            
            # 从list表获取作者和发帖时间
            author = None
            post_time = None
            last_active = None
            daysold = None
            
            if url in list_dict:
                author = list_dict[url]['author'].split(' | ')[0] if ' | ' in list_dict[url]['author'] else list_dict[url]['author']
                post_time = list_dict[url]['post_time']
                daysold = int(list_dict[url]['daysold']) if list_dict[url]['daysold'] else None
                last_active = int(list_dict[url]['last_active']) if list_dict[url]['last_active'] else None
            
            # 准备记录
            year_value = None
            try:
                if not pd.isna(row['year']):
                    # 处理特殊情况的年份
                    year_str = str(row['year']).strip()
                    # 如果年份是纯数字，直接转换
                    if year_str.isdigit():
                        year_value = int(year_str)
                    # 对于"2017以后"等格式，提取数字部分
                    elif '以后' in year_str and year_str.split('以后')[0].isdigit():
                        year_value = int(year_str.split('以后')[0])
                    # 对于"20, 23"等多个年份的情况，使用第一个数字
                    elif ',' in year_str:
                        parts = year_str.split(',')
                        for part in parts:
                            part = part.strip()
                            if part.isdigit():
                                year_value = int(part)
                                break
                    # 其他情况保持为None
            except Exception as e:
                # 仅在调试模式下显示错误
                # print(f"年份转换出错 {row['year']}: {e}")
                pass
                
            record = (
                url,
                year_value,
                row['make'] if not pd.isna(row['make']) else None,
                row['model'] if not pd.isna(row['model']) else None,
                row['miles'] if not pd.isna(row['miles']) else None,
                row['price'] if not pd.isna(row['price']) else None,
                row['trade_type'] if not pd.isna(row['trade_type']) else None,
                row['location'] if not pd.isna(row['location']) else None,
                thread_id,
                author,
                post_time,
                daysold,
                last_active
            )
            records.append(record)
        
        print(f"准备插入 {len(records)} 条记录，跳过 {skipped} 条记录")
        
        # 先清空表
        conn.execute("DELETE FROM car_info")
        
        # 批量插入
        conn.executemany("""
            INSERT INTO car_info (url, year, make, model, miles, price, trade_type, location, thread_id, author, post_time, daysold, last_active)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, records)
        
        conn.commit()
        conn.close()
        
        print(f"成功导入 {len(records)} 条车辆信息记录")
        return len(records)
    except Exception as e:
        print(f"导入失败: {str(e)}")
        return 0

if __name__ == "__main__":
    count = import_car_info()
    print(f"导入完成，共导入 {count} 条记录")
    sys.exit(0 if count > 0 else 1) 