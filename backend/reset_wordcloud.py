import sqlite3
import os
import sys
from datetime import datetime

def get_db_connection():
    """建立数据库连接"""
    db_file = os.path.join('db', 'forum_data.db')
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row  # 使结果可以通过列名访问
    return conn

def reset_wordcloud():
    """重置词云数据"""
    print(f"[{datetime.now()}] 开始重置词云数据...")
    
    conn = get_db_connection()
    try:
        # 删除词云缓存表中的所有数据
        conn.execute("DELETE FROM wordcloud_cache WHERE type = 'wordcloud'")
        conn.commit()
        print(f"[{datetime.now()}] 词云数据已清除")
        
        # 从app模块导入初始化函数并执行
        print(f"[{datetime.now()}] 开始重新生成词云数据...")
        from app import generate_wordcloud
        new_wordcloud = generate_wordcloud()
        
        if new_wordcloud:
            print(f"[{datetime.now()}] 成功生成新的词云数据，共{len(new_wordcloud)}个词")
            
            # 打印前10个词语和其频率，以便验证
            print(f"[{datetime.now()}] 前10个高频词:")
            for i, item in enumerate(new_wordcloud[:10]):
                print(f"  {i+1}. {item['text']}: {item['value']}次")
        else:
            print(f"[{datetime.now()}] 生成词云数据失败")
            return False
        
        # 查询验证
        result = conn.execute("SELECT COUNT(*) FROM wordcloud_cache WHERE type = 'wordcloud'").fetchone()
        count = result[0]
        print(f"[{datetime.now()}] 数据库中现有词云记录：{count}条")
        
        # 检查数据格式
        data_row = conn.execute("SELECT data FROM wordcloud_cache WHERE type = 'wordcloud' LIMIT 1").fetchone()
        if data_row:
            import json
            try:
                data_json = json.loads(data_row['data'])
                if isinstance(data_json, list) and len(data_json) > 0:
                    item = data_json[0]
                    fields = ', '.join(list(item.keys()))
                    print(f"[{datetime.now()}] 数据格式正确，包含字段: {fields}")
                else:
                    print(f"[{datetime.now()}] 警告: 数据不是列表或为空")
            except json.JSONDecodeError:
                print(f"[{datetime.now()}] 警告: 数据不是有效的JSON格式")
        
        return True
    except Exception as e:
        print(f"[{datetime.now()}] 重置词云数据时出错: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        conn.close()

if __name__ == "__main__":
    success = reset_wordcloud()
    print(f"[{datetime.now()}] 词云重置{'成功' if success else '失败'}") 