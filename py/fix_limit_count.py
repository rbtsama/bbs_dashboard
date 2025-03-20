import sqlite3
import pandas as pd
import os
from pathlib import Path
import sys

# 设置控制台输出编码为UTF-8
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

# 设置数据路径
BASE_DIR = Path(__file__).parent.parent
PROCESSED_DIR = BASE_DIR / 'data' / 'processed'
DB_PATH = BASE_DIR / 'backend' / 'db' / 'forum_data.db'

def check_table_structure():
    """检查表结构"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 检查post_ranking表
        cursor.execute("PRAGMA table_info(post_ranking)")
        columns = cursor.fetchall()
        print("post_ranking表结构:")
        for col in columns:
            print(f"  {col[1]}: {col[2]} (主键: {col[5]})")
        
        # 检查author_ranking表
        cursor.execute("PRAGMA table_info(author_ranking)")
        columns = cursor.fetchall()
        print("\nauthor_ranking表结构:")
        for col in columns:
            print(f"  {col[1]}: {col[2]} (主键: {col[5]})")
        
        # 检查repost_count字段的最大值
        cursor.execute("SELECT MAX(CAST(repost_count AS INTEGER)) FROM post_ranking")
        max_value = cursor.fetchone()[0]
        print(f"\npost_ranking.repost_count最大值: {max_value}")
        
        # 检查重发计数分布
        cursor.execute("SELECT CAST(repost_count AS INTEGER) as rc, COUNT(*) FROM post_ranking GROUP BY rc ORDER BY rc")
        distribution = cursor.fetchall()
        print("\npost_ranking.repost_count分布:")
        for value, count in distribution:
            print(f"  {value}: {count}条记录")
            
        conn.close()
    except Exception as e:
        print(f"检查表结构时出错: {e}")

def convert_tables_to_integer():
    """将TEXT字段转换为INTEGER类型"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # 创建备份
        backup_path = f"{DB_PATH}.bak_before_structure_change"
        if not os.path.exists(backup_path):
            import shutil
            shutil.copy2(DB_PATH, backup_path)
            print(f"数据库备份已创建: {backup_path}")
        
        # 处理post_ranking表
        print("转换post_ranking表...")
        try:
            # 获取表结构
            cursor.execute("PRAGMA table_info(post_ranking)")
            columns = cursor.fetchall()
            column_defs = []
            for col in columns:
                name = col[1]
                type_name = "INTEGER" if name in ['repost_count', 'reply_count', 'delete_reply_count', 'daysold', 'last_active'] else col[2]
                not_null = "NOT NULL" if col[3] else ""
                default = f"DEFAULT {col[4]}" if col[4] is not None else ""
                pk = "PRIMARY KEY" if col[5] else ""
                column_defs.append(f"{name} {type_name} {not_null} {default} {pk}".strip())
            
            # 创建临时表
            column_defs_str = ", ".join(column_defs)
            cursor.execute(f"CREATE TABLE post_ranking_new ({column_defs_str})")
            
            # 复制数据，确保转换类型
            column_names = [col[1] for col in columns]
            column_names_str = ", ".join(column_names)
            value_converts = []
            for col in columns:
                name = col[1]
                if name in ['repost_count', 'reply_count', 'delete_reply_count', 'daysold', 'last_active']:
                    value_converts.append(f"CAST({name} AS INTEGER)")
                else:
                    value_converts.append(name)
            value_converts_str = ", ".join(value_converts)
            
            cursor.execute(f"INSERT INTO post_ranking_new ({column_names_str}) SELECT {value_converts_str} FROM post_ranking")
            
            # 删除原表并重命名新表
            cursor.execute("DROP TABLE post_ranking")
            cursor.execute("ALTER TABLE post_ranking_new RENAME TO post_ranking")
            
            print("post_ranking表转换完成")
        except Exception as e:
            print(f"转换post_ranking表时出错: {e}")
            conn.rollback()
        
        # 处理author_ranking表
        print("转换author_ranking表...")
        try:
            # 获取表结构
            cursor.execute("PRAGMA table_info(author_ranking)")
            columns = cursor.fetchall()
            column_defs = []
            for col in columns:
                name = col[1]
                type_name = "INTEGER" if name in ['repost_count', 'reply_count', 'delete_reply_count', 'post_count', 'active_posts', 'last_active'] else col[2]
                not_null = "NOT NULL" if col[3] else ""
                default = f"DEFAULT {col[4]}" if col[4] is not None else ""
                pk = "PRIMARY KEY" if col[5] else ""
                column_defs.append(f"{name} {type_name} {not_null} {default} {pk}".strip())
            
            # 创建临时表
            column_defs_str = ", ".join(column_defs)
            cursor.execute(f"CREATE TABLE author_ranking_new ({column_defs_str})")
            
            # 复制数据，确保转换类型
            column_names = [col[1] for col in columns]
            column_names_str = ", ".join(column_names)
            value_converts = []
            for col in columns:
                name = col[1]
                if name in ['repost_count', 'reply_count', 'delete_reply_count', 'post_count', 'active_posts', 'last_active']:
                    value_converts.append(f"CAST({name} AS INTEGER)")
                else:
                    value_converts.append(name)
            value_converts_str = ", ".join(value_converts)
            
            cursor.execute(f"INSERT INTO author_ranking_new ({column_names_str}) SELECT {value_converts_str} FROM author_ranking")
            
            # 删除原表并重命名新表
            cursor.execute("DROP TABLE author_ranking")
            cursor.execute("ALTER TABLE author_ranking_new RENAME TO author_ranking")
            
            print("author_ranking表转换完成")
        except Exception as e:
            print(f"转换author_ranking表时出错: {e}")
            conn.rollback()
        
        # 提交所有更改
        conn.commit()
        print("数据库表结构已成功转换")
        return True
    except Exception as e:
        print(f"转换表结构时出错: {e}")
        return False
    finally:
        if conn:
            conn.close()

def fix_repost_count_limit():
    """
    修复数据库中的重发计数限制为9的问题
    将CSV文件中的实际数据同步到数据库中
    """
    print("开始修复数据库中重发计数被限制为9的问题...")
    
    # 检查数据库是否存在
    if not DB_PATH.exists():
        print(f"错误: 数据库文件不存在: {DB_PATH}")
        return False
    
    # 检查CSV文件是否存在
    post_ranking_file = PROCESSED_DIR / 'post_ranking.csv'
    author_ranking_file = PROCESSED_DIR / 'author_ranking.csv'
    
    if not post_ranking_file.exists():
        print(f"错误: 帖子排名CSV文件不存在: {post_ranking_file}")
        return False
    
    if not author_ranking_file.exists():
        print(f"错误: 作者排名CSV文件不存在: {author_ranking_file}")
        return False
    
    # 连接到数据库
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # 创建备份
        print("创建数据库备份...")
        backup_path = f"{DB_PATH}.bak_before_fix_limit"
        if not os.path.exists(backup_path):
            import shutil
            shutil.copy2(DB_PATH, backup_path)
            print(f"数据库备份已创建: {backup_path}")
        else:
            print(f"备份文件已存在，跳过备份: {backup_path}")
        
        # 读取CSV数据
        print("读取CSV数据...")
        post_df = pd.read_csv(post_ranking_file)
        author_df = pd.read_csv(author_ranking_file)
        
        # 确保计数列是整数类型
        post_df['repost_count'] = pd.to_numeric(post_df['repost_count'], errors='coerce').fillna(0).astype(int)
        post_df['delete_reply_count'] = pd.to_numeric(post_df['delete_reply_count'], errors='coerce').fillna(0).astype(int)
        author_df['repost_count'] = pd.to_numeric(author_df['repost_count'], errors='coerce').fillna(0).astype(int)
        author_df['delete_reply_count'] = pd.to_numeric(author_df['delete_reply_count'], errors='coerce').fillna(0).astype(int)
        
        # 检查表结构
        cursor.execute("PRAGMA table_info(post_ranking)")
        post_columns = [row['name'] for row in cursor.fetchall()]
        
        cursor.execute("PRAGMA table_info(author_ranking)")
        author_columns = [row['name'] for row in cursor.fetchall()]
        
        # 检查数据库中是否有delete_count或delete_reply_count字段
        delete_field_in_post = None
        if 'delete_count' in post_columns:
            delete_field_in_post = 'delete_count'
        elif 'delete_reply_count' in post_columns:
            delete_field_in_post = 'delete_reply_count'
        
        delete_field_in_author = None
        if 'delete_count' in author_columns:
            delete_field_in_author = 'delete_count'
        elif 'delete_reply_count' in author_columns:
            delete_field_in_author = 'delete_reply_count'
        
        if 'repost_count' not in post_columns or not delete_field_in_post:
            print(f"错误: 数据库中post_ranking表结构不完整，缺少repost_count或delete字段")
            print(f"现有字段: {post_columns}")
            return False
        
        if 'repost_count' not in author_columns or not delete_field_in_author:
            print(f"错误: 数据库中author_ranking表结构不完整，缺少repost_count或delete字段")
            print(f"现有字段: {author_columns}")
            return False
        
        # 查询数据库中当前的最大值
        cursor.execute(f"SELECT MAX(CAST(repost_count AS INTEGER)) as max_count FROM post_ranking")
        max_db_post_repost_row = cursor.fetchone()
        max_db_post_repost = int(max_db_post_repost_row['max_count']) if max_db_post_repost_row['max_count'] is not None else 0
        
        cursor.execute(f"SELECT MAX(CAST(repost_count AS INTEGER)) as max_count FROM author_ranking")
        max_db_author_repost_row = cursor.fetchone()
        max_db_author_repost = int(max_db_author_repost_row['max_count']) if max_db_author_repost_row['max_count'] is not None else 0
        
        # 获取CSV文件中的最大值
        max_csv_post_repost = int(post_df['repost_count'].max())
        max_csv_author_repost = int(author_df['repost_count'].max())
        
        print(f"帖子重发计数 - 数据库最大值: {max_db_post_repost}, CSV最大值: {max_csv_post_repost}")
        print(f"用户重发计数 - 数据库最大值: {max_db_author_repost}, CSV最大值: {max_csv_author_repost}")
        
        # 如果数据库中的最大值小于CSV中的最大值，则需要更新
        if max_db_post_repost < max_csv_post_repost or max_db_author_repost < max_csv_author_repost:
            print("检测到数据库中的重发计数被限制，需要更新...")
            
            # 验证字段类型
            print("检查字段类型...")
            cursor.execute("PRAGMA table_info(post_ranking)")
            post_schema = {row[1]: row[2] for row in cursor.fetchall()}
            cursor.execute("PRAGMA table_info(author_ranking)")
            author_schema = {row[1]: row[2] for row in cursor.fetchall()}
            
            print(f"post_ranking.repost_count类型: {post_schema.get('repost_count', 'unknown')}")
            print(f"author_ranking.repost_count类型: {author_schema.get('repost_count', 'unknown')}")
            
            # 更新帖子排名表
            print("更新帖子排名表...")
            update_count = 0
            for _, row in post_df.iterrows():
                if 'url' in row and 'repost_count' in row and 'delete_reply_count' in row:
                    try:
                        cursor.execute(
                            f"UPDATE post_ranking SET repost_count = ?, {delete_field_in_post} = ? WHERE url = ?",
                            (int(row['repost_count']), int(row['delete_reply_count']), row['url'])
                        )
                        if cursor.rowcount > 0:
                            update_count += 1
                    except Exception as e:
                        print(f"更新帖子记录时出错: {e}, 行数据: {row}")
            
            print(f"已更新 {update_count} 条帖子记录")
            
            # 更新作者排名表
            print("更新作者排名表...")
            author_update_count = 0
            for _, row in author_df.iterrows():
                if 'author' in row and 'repost_count' in row and 'delete_reply_count' in row:
                    try:
                        cursor.execute(
                            f"UPDATE author_ranking SET repost_count = ?, {delete_field_in_author} = ? WHERE author = ?",
                            (int(row['repost_count']), int(row['delete_reply_count']), row['author'])
                        )
                        if cursor.rowcount > 0:
                            author_update_count += 1
                    except Exception as e:
                        print(f"更新作者记录时出错: {e}, 行数据: {row}")
            
            print(f"已更新 {author_update_count} 条作者记录")
            
            # 提交更改
            conn.commit()
            
            # 验证更新结果
            cursor.execute("SELECT MAX(CAST(repost_count AS INTEGER)) as max_count FROM post_ranking")
            new_max_row = cursor.fetchone()
            new_max_post_repost = int(new_max_row['max_count']) if new_max_row['max_count'] is not None else 0
            
            cursor.execute("SELECT MAX(CAST(repost_count AS INTEGER)) as max_count FROM author_ranking")
            new_max_author_row = cursor.fetchone()
            new_max_author_repost = int(new_max_author_row['max_count']) if new_max_author_row['max_count'] is not None else 0
            
            print(f"更新后帖子重发计数最大值: {new_max_post_repost}")
            print(f"更新后作者重发计数最大值: {new_max_author_repost}")
            
            if new_max_post_repost >= max_csv_post_repost * 0.9 and new_max_author_repost >= max_csv_author_repost * 0.9:
                print("修复成功！数据库中的重发计数现在与CSV文件基本一致")
                
                # 查询值为9的记录数
                cursor.execute("SELECT COUNT(*) as count FROM post_ranking WHERE CAST(repost_count AS INTEGER) = 9")
                post_count_9 = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM author_ranking WHERE CAST(repost_count AS INTEGER) = 9")
                author_count_9 = cursor.fetchone()['count']
                
                print(f"帖子重发计数为9的记录数: {post_count_9}")
                print(f"作者重发计数为9的记录数: {author_count_9}")
                
                # 查询大于9的记录数
                cursor.execute("SELECT COUNT(*) as count FROM post_ranking WHERE CAST(repost_count AS INTEGER) > 9")
                post_count_gt_9 = cursor.fetchone()['count']
                
                cursor.execute("SELECT COUNT(*) as count FROM author_ranking WHERE CAST(repost_count AS INTEGER) > 9")
                author_count_gt_9 = cursor.fetchone()['count']
                
                print(f"帖子重发计数大于9的记录数: {post_count_gt_9}")
                print(f"作者重发计数大于9的记录数: {author_count_gt_9}")
                
                return True
            else:
                print("修复部分成功！数据库中的重发计数提高了，但与CSV文件仍有差异")
                return True
        else:
            print("数据库中的重发计数没有被限制，不需要修复")
            return True
    except Exception as e:
        print(f"修复过程中出错: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        if conn:
            conn.close()

def fix_sql_files():
    """修复SQL文件中的硬编码问题"""
    try:
        # 要修复的SQL文件列表
        sql_files = [
            BASE_DIR / 'sql' / 'process_import_data.sql',
            BASE_DIR / 'sql' / 'incremental_update.sql'
        ]
        
        for sql_file in sql_files:
            if not sql_file.exists():
                print(f"SQL文件不存在: {sql_file}")
                continue
            
            print(f"修复SQL文件: {sql_file}")
            
            # 读取文件内容
            with open(sql_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 创建备份
            backup_file = sql_file.with_suffix('.sql.bak')
            with open(backup_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # 查找和替换硬编码的0值
            replacements = {
                # 修复post_ranking表
                "0 as repost_count,": "COALESCE(pr.repost_count, 0) as repost_count,",
                "0 as delete_count,": "COALESCE(pr.delete_count, 0) as delete_count,",
                # 修复author_ranking表
                "0 as repost_count,": "COALESCE(ar.repost_count, 0) as repost_count,",
                "0 as delete_count,": "COALESCE(ar.delete_count, 0) as delete_count,"
            }
            
            for old, new in replacements.items():
                content = content.replace(old, new)
            
            # 写入修改后的内容
            with open(sql_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            print(f"已修复SQL文件: {sql_file}")
        
        return True
    except Exception as e:
        print(f"修复SQL文件时出错: {e}")
        return False

def fix_update_db():
    """修复update_db.py文件，确保导入数据时保留repost_count值"""
    try:
        update_db_file = BASE_DIR / 'py' / 'update_db.py'
        if not update_db_file.exists():
            print(f"update_db.py文件不存在: {update_db_file}")
            return False
        
        print(f"修复update_db.py文件...")
        
        # 读取文件内容
        with open(update_db_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 创建备份
        backup_file = update_db_file.with_suffix('.py.bak')
        with open(backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # 添加repost_count处理逻辑
        # 寻找导入CSV文件的部分
        if "import_csv_to_temp" in content and "post_ranking" in content:
            print("在update_db.py中找到了CSV导入代码")
            
            # 添加处理repost_count字段的代码
            if "# 处理repost_count字段" not in content:
                # 在导入CSV完成后添加代码确保repost_count和delete_count字段被正确导入
                add_code = """
        # 确保处理post_ranking和author_ranking的特殊字段
        if table_name in ['post_ranking', 'author_ranking']:
            print(f"处理{table_name}表的特殊字段...")
            try:
                # 检查表结构
                cursor.execute(f"PRAGMA table_info({table_name})")
                columns = [row[1] for row in cursor.fetchall()]
                
                # 确定delete字段名称
                delete_field = 'delete_count'
                if 'delete_reply_count' in columns:
                    delete_field = 'delete_reply_count'
                
                # 确保数值字段为整数类型
                if 'repost_count' in columns and delete_field in columns:
                    cursor.execute(f'''
                    UPDATE {table_name} 
                    SET repost_count = CAST(repost_count AS INTEGER),
                        {delete_field} = CAST({delete_field} AS INTEGER)
                    ''')
                    print(f"已将{table_name}表的repost_count和{delete_field}字段转换为整数类型")
            except Exception as e:
                print(f"处理{table_name}表特殊字段时出错: {str(e)}")
"""
                # 找到合适的位置插入代码
                pos = content.find("return len(df)")
                if pos > 0:
                    # 在return语句前插入代码
                    content = content[:pos] + add_code + content[pos:]
                    print("已添加处理repost_count字段的代码")
        
        # 写入修改后的内容
        with open(update_db_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"已修复update_db.py文件")
        return True
    except Exception as e:
        print(f"修复update_db.py文件时出错: {e}")
        return False

if __name__ == "__main__":
    print("=== 检查数据库表结构 ===")
    check_table_structure()
    
    print("\n=== 转换数据库表结构 ===")
    if convert_tables_to_integer():
        print("数据库表结构转换成功")
    else:
        print("数据库表结构转换失败")
    
    print("\n=== 修复重发计数 ===")
    if fix_repost_count_limit():
        print("修复重发计数成功")
    else:
        print("修复重发计数失败")
    
    print("\n=== 修复SQL文件 ===")
    if fix_sql_files():
        print("SQL文件修复成功，未来的数据更新将正确处理重发计数")
    else:
        print("SQL文件修复失败，可能需要手动修改")
    
    print("\n=== 修复update_db.py文件 ===")
    if fix_update_db():
        print("update_db.py文件修复成功，未来的数据导入将正确处理重发计数")
    else:
        print("update_db.py文件修复失败，可能需要手动修改") 