import sqlite3, os; conn = sqlite3.connect('db/forum_data.db'); cursor = conn.cursor(); cursor.execute('SELECT name FROM sqlite_master WHERE type=\
table\ LIMIT 10'); print('数据库中的表:'); [print(f' - {row[0]}') for row in cursor.fetchall()]; conn.close()
