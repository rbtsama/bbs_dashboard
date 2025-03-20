import sqlite3
import os
import json

def get_db_connection():
    """获取数据库连接"""
    db_path = os.path.join('db', 'forum_data.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def check_post_history():
    """检查post_history表结构和数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 检查表是否存在
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='post_history'")
    if not cursor.fetchone():
        print("post_history表不存在")
        conn.close()
        return
    
    # 获取表结构
    cursor.execute("PRAGMA table_info(post_history)")
    columns = cursor.fetchall()
    print("表结构:")
    for col in columns:
        print(f"  {col['name']} ({col['type']})")
    
    # 获取记录总数
    cursor.execute("SELECT COUNT(*) FROM post_history")
    count = cursor.fetchone()[0]
    print(f"记录总数: {count}")
    
    # 获取样本数据
    cursor.execute("SELECT * FROM post_history LIMIT 5")
    rows = cursor.fetchall()
    print("\n样本数据:")
    for row in rows:
        row_dict = {key: row[key] for key in row.keys()}
        print(json.dumps(row_dict, ensure_ascii=False, indent=2))
    
    # 统计action字段的分布
    cursor.execute("SELECT action, COUNT(*) as count FROM post_history GROUP BY action")
    actions = cursor.fetchall()
    print("\naction字段分布:")
    for action in actions:
        print(f"  {action['action']}: {action['count']}")
    
    conn.close()

def check_specific_thread(thread_id):
    """检查特定thread_id的记录"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    print(f"\n检查thread_id={thread_id}的记录:")
    
    # 尝试整数查询
    try:
        int_thread_id = int(thread_id)
        cursor.execute("SELECT COUNT(*) FROM post_history WHERE thread_id = ?", (int_thread_id,))
        count = cursor.fetchone()[0]
        print(f"使用整数方式查询 (thread_id = {int_thread_id})，找到 {count} 条记录")
    except (ValueError, TypeError):
        print(f"thread_id '{thread_id}' 无法转换为整数")
    
    # 尝试字符串精确匹配
    cursor.execute("SELECT COUNT(*) FROM post_history WHERE thread_id = ?", (str(thread_id),))
    count = cursor.fetchone()[0]
    print(f"使用字符串方式查询 (thread_id = '{thread_id}')，找到 {count} 条记录")
    
    # 尝试模糊匹配
    cursor.execute("SELECT COUNT(*) FROM post_history WHERE thread_id LIKE ?", (f"%{thread_id}%",))
    count = cursor.fetchone()[0]
    print(f"使用模糊匹配 (thread_id LIKE '%{thread_id}%')，找到 {count} 条记录")
    
    # 查看thread_id字段的典型值
    cursor.execute("SELECT DISTINCT thread_id FROM post_history LIMIT 5")
    thread_ids = cursor.fetchall()
    print(f"数据库中thread_id字段的典型值示例:")
    for tid in thread_ids:
        print(f"  {tid['thread_id']} (类型: {type(tid['thread_id']).__name__})")
    
    # 检查是否有对应的URL
    cursor.execute("SELECT COUNT(*) FROM post_history WHERE url LIKE ?", (f"%{thread_id}%",))
    count = cursor.fetchone()[0]
    print(f"通过URL查询 (url LIKE '%{thread_id}%')，找到 {count} 条记录")
    
    if count > 0:
        cursor.execute("SELECT url FROM post_history WHERE url LIKE ? LIMIT 5", (f"%{thread_id}%",))
        urls = cursor.fetchall()
        print(f"通过thread_id={thread_id}找到的URL示例:")
        for url in urls:
            print(f"  {url['url']}")
    
    conn.close()

if __name__ == "__main__":
    check_post_history()
    
    # 测试几个特定的thread_id
    test_ids = ["2852536", 2852536, "2854697", "123456"]
    for test_id in test_ids:
        check_specific_thread(test_id) 