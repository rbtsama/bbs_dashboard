import sqlite3
import os

def init_database():
    # 确保数据库目录存在
    os.makedirs(os.path.dirname('database.db'), exist_ok=True)
    
    # 连接数据库
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()
    
    # 创建posts表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS posts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        thread_id TEXT,
        title TEXT,
        author TEXT, 
        author_url TEXT,
        post_time TEXT,
        forum TEXT,
        views INTEGER,
        page_num INTEGER,
        num INTEGER
    )
    ''')
    
    # 创建thread_history表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS thread_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        thread_id TEXT,
        scraping_time TEXT,
        update_reason TEXT,
        view_count INTEGER,
        page_num INTEGER,
        num INTEGER
    )
    ''')
    
    # 创建list表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS list (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT,
        title TEXT,
        author TEXT,
        author_link TEXT,
        read_count INTEGER,
        reply_count INTEGER,
        scraping_time TEXT,
        update_reason TEXT
    )
    ''')
    
    # 创建postranking表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS postranking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        url TEXT,
        title TEXT,
        Days_Old INTEGER,
        author TEXT,
        author_link TEXT,
        repost_count INTEGER,
        reply_count INTEGER,
        delete_count INTEGER,
        last_active INTEGER
    )
    ''')
    
    # 创建authorranking表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS authorranking (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT,
        author TEXT,
        author_link TEXT,
        repost_count INTEGER,
        reply_count INTEGER,
        delete_count INTEGER,
        last_active INTEGER
    )
    ''')
    
    # 创建updatestatistics表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS updatestatistics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        datetime TEXT,
        update_reason TEXT,
        count INTEGER
    )
    ''')
    
    # 创建poststatistics表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS poststatistics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        datetime TEXT,
        type TEXT,
        count INTEGER
    )
    ''')
    
    # 创建viewstatistics表
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS viewstatistics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        datetime TEXT,
        type TEXT,
        count INTEGER,
        view_gap INTEGER
    )
    ''')
    
    # 创建索引
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_thread_id ON posts(thread_id)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_post_time ON posts(post_time)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_scraping_time ON thread_history(scraping_time)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_list_url ON list(url)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_list_author ON list(author)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_postranking_url ON postranking(url)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_authorranking_author ON authorranking(author)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_updatestatistics_datetime ON updatestatistics(datetime)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_poststatistics_datetime ON poststatistics(datetime)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_viewstatistics_datetime ON viewstatistics(datetime)')
    
    # 提交更改
    conn.commit()
    
    # 添加一些测试数据到updatestatistics表
    # 生成60个小时的数据
    for i in range(60):
        hour = 23 - (i % 24)
        day = 6 - (i // 24)
        datetime_str = f"2025-02-{day:02d} {hour:02d}:00:00"
        
        # 添加重发数据
        cursor.execute('''
        INSERT INTO updatestatistics (datetime, update_reason, count)
        VALUES (?, ?, ?)
        ''', (datetime_str, '重发', i % 10 + 1))
        
        # 添加回帖数据
        cursor.execute('''
        INSERT INTO updatestatistics (datetime, update_reason, count)
        VALUES (?, ?, ?)
        ''', (datetime_str, '回帖', i % 15 + 5))
        
        # 添加删回帖数据
        cursor.execute('''
        INSERT INTO updatestatistics (datetime, update_reason, count)
        VALUES (?, ?, ?)
        ''', (datetime_str, '删回帖', i % 8))
    
    # 提交更改
    conn.commit()
    
    # 关闭连接
    conn.close()
    
    print("数据库初始化完成，并添加了测试数据")

if __name__ == "__main__":
    init_database() 