# 此文件中的代码已被禁用（由car_info清理脚本处理）
# 原始功能已被移除，但保留文件以备参考
# 原始备份文件: alter_car_info.py.bak_carinfo

import sqlite3
import os

def alter_car_info_table():
    """修改car_info表结构"""
    try:
        # 连接数据库
        db_path = os.path.join(os.path.dirname(__file__), 'db', 'forum_data.db')
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # 添加author_link字段
        cursor.execute("ALTER TABLE car_info ADD COLUMN author_link TEXT;")
        
        # 提交更改
        conn.commit()
        print("成功添加author_link字段")
        
        # 验证表结构
        cursor.execute("PRAGMA table_info(car_info)")
        columns = cursor.fetchall()
        print("\n更新后的表结构:")
        for col in columns:
            print(f"- {col[1]} ({col[2]})")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"修改失败: {str(e)}")
        return False

if __name__ == "__main__":
    alter_car_info_table() 
