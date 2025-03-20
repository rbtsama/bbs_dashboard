import sqlite3

def check_table_schema():
    try:
        # 连接数据库
        conn = sqlite3.connect('backend/db/forum_data.db')
        cursor = conn.cursor()
        
        # 获取post_ranking表的结构
        cursor.execute("SELECT sql FROM sqlite_master WHERE type='table' AND name='post_ranking';")
        schema = cursor.fetchone()
        
        if schema:
            print("post_ranking表结构:")
            print(schema[0])
            
            # 获取表中的一些示例数据
            cursor.execute("SELECT * FROM post_ranking LIMIT 1;")
            row = cursor.fetchone()
            if row:
                # 获取列名
                columns = [description[0] for description in cursor.description]
                print("\n列名:")
                print(columns)
                print("\n示例数据:")
                for i, value in enumerate(row):
                    print(f"{columns[i]}: {value}")
            else:
                print("\n表中没有数据")
        else:
            print("post_ranking表不存在")
            
    except sqlite3.Error as e:
        print(f"数据库错误: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    check_table_schema() 