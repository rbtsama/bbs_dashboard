@echo off
cd %~dp0
python -c "import sqlite3; conn = sqlite3.connect('db/forum_data.db'); cursor = conn.cursor(); cursor.execute('DROP TABLE IF EXISTS car_info'); conn.commit(); conn.close(); print('car_info表已成功删除')"
pause 