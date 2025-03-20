import sqlite3

# 连接数据库
conn = sqlite3.connect("../data.db")
cursor = conn.cursor()

# 检查active_posts字段是否存在
cursor.execute("PRAGMA table_info(authorranking)")
columns = cursor.fetchall()
column_names = [col[1] for col in columns]

if 'active_posts' not in column_names:
    print("添加active_posts字段到authorranking表...")
    cursor.execute("ALTER TABLE authorranking ADD COLUMN active_posts INTEGER DEFAULT 0")
    conn.commit()
    print("成功添加active_posts字段！")
    
    # 更新active_posts值 - 这里设置为post_count的70%作为初始值
    cursor.execute("UPDATE authorranking SET active_posts = CAST(post_count * 0.7 AS INTEGER)")
    conn.commit()
    print("已初始化active_posts值")
else:
    print("active_posts字段已存在")

# 检查是否存在author_link字段
if 'author_link' not in column_names:
    print("添加author_link字段到authorranking表...")
    cursor.execute("ALTER TABLE authorranking ADD COLUMN author_link TEXT DEFAULT NULL")
    conn.commit()
    print("成功添加author_link字段！")
    
    # 更新author_link值为模拟链接
    cursor.execute("UPDATE authorranking SET author_link = 'https://example.com/user/' || author")
    conn.commit()
    print("已初始化author_link值")
else:
    print("author_link字段已存在")

# 显示更新后的表结构
cursor.execute("PRAGMA table_info(authorranking)")
columns = cursor.fetchall()
print("\n更新后的authorranking表结构:")
for col in columns:
    print(f"  {col[1]} ({col[2]})")

conn.close() 