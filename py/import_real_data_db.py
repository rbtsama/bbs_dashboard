import sqlite3
import os
import pandas as pd
from datetime import datetime, timedelta
import csv
from pathlib import Path

# 获取当前脚本路径
SCRIPT_DIR = Path(__file__).parent.absolute()
PROJECT_DIR = SCRIPT_DIR.parent

# 数据库路径
DB_PATH = os.path.join(PROJECT_DIR, 'backend', 'db', 'forum_data.db')
# CSV文件路径
CSV_PATH = os.path.join(PROJECT_DIR, 'data', 'processed', 'import.csv')

def get_db_connection():
    """获取数据库连接"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        print(f"连接数据库时出错: {str(e)}")
        return None

def check_csv_data():
    """检查CSV文件中的数据"""
    if not os.path.exists(CSV_PATH):
        print(f"CSV文件不存在: {CSV_PATH}")
        return False
    
    try:
        # 读取CSV文件
        df = pd.read_csv(CSV_PATH)
        print(f"CSV文件包含 {len(df)} 行数据")
        
        # 检查必要的列
        required_columns = ['data_category', 'type', 'datetime', 'count']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            print(f"CSV文件缺少必要的列: {missing_columns}")
            return False
        
        # 检查数据类别
        categories = df['data_category'].unique()
        print(f"数据类别: {categories}")
        
        # 检查数据量
        for category in categories:
            category_count = len(df[df['data_category'] == category])
            print(f"  {category}: {category_count} 条记录")
        
        return True
    except Exception as e:
        print(f"检查CSV数据时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def import_csv_to_db():
    """将CSV文件导入到数据库"""
    conn = get_db_connection()
    if not conn:
        return False
    
    try:
        # 检查CSV文件是否存在
        if not os.path.exists(CSV_PATH):
            print(f"CSV文件不存在: {CSV_PATH}")
            return False
        
        # 获取当前数据库中的记录数
        cursor = conn.execute("SELECT COUNT(*) FROM import WHERE data_category IN ('update_statistics', 'post_statistics', 'view_statistics')")
        count_before = cursor.fetchone()[0]
        print(f"导入前数据库中有 {count_before} 条记录")
        
        # 读取CSV文件
        with open(CSV_PATH, 'r', encoding='utf-8-sig') as f:
            csv_reader = csv.DictReader(f)
            
            # 统计各类数据的数量
            stats = {'update_statistics': 0, 'post_statistics': 0, 'view_statistics': 0, 'post_ranking': 0, 'author_ranking': 0}
            
            # 处理并导入数据
            for row in csv_reader:
                if 'data_category' in row and row['data_category'] in stats:
                    category = row['data_category']
                    
                    # 检查并设置必要的字段
                    count = int(float(row.get('count', 0))) if row.get('count') else 0
                    type_value = row.get('type', '')
                    datetime_value = row.get('datetime', '')
                    id_value = row.get('id', f"{category}_{stats[category]}")
                    
                    # 构建SQL语句和参数
                    if category == 'author_ranking':
                        # 对于author_ranking，需要添加active_posts字段
                        active_posts = int(float(row.get('active_posts', 0))) if row.get('active_posts') else 0
                        
                        # 插入数据
                        conn.execute("""
                        INSERT INTO import (id, data_category, type, datetime, count, author, active_posts)
                        VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (id_value, category, type_value, datetime_value, count, row.get('author', ''), active_posts))
                    else:
                        # 对于其他类别，使用基本字段
                        conn.execute("""
                        INSERT INTO import (id, data_category, type, datetime, count)
                        VALUES (?, ?, ?, ?, ?)
                        """, (id_value, category, type_value, datetime_value, count))
                    
                    stats[category] += 1
        
        conn.commit()
        
        # 获取导入后的记录数
        cursor = conn.execute("SELECT COUNT(*) FROM import WHERE data_category IN ('update_statistics', 'post_statistics', 'view_statistics')")
        count_after = cursor.fetchone()[0]
        print(f"导入后数据库中有 {count_after} 条记录")
        print(f"新增 {count_after - count_before} 条记录")
        
        # 统计各类别数据
        for category in stats:
            if stats[category] > 0:
                print(f"导入 {stats[category]} 条 {category} 数据")
        
        return True
    except Exception as e:
        print(f"导入CSV数据时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    print("=== 开始导入真实数据 ===")
    # 先检查CSV数据
    if check_csv_data():
        # 导入数据到数据库
        if import_csv_to_db():
            print("数据导入成功")
        else:
            print("数据导入失败")
    else:
        print("CSV数据检查失败，不进行导入")
    print("=== 导入过程结束 ===") 