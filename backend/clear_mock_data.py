import sqlite3
import os

def get_db_connection():
    """获取数据库连接"""
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db', 'forum_data.db')
    print(f"正在连接数据库: {db_path}")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

def clear_mock_data():
    """清理模拟数据"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # 打印表信息
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print("数据库中的表:")
    for table in tables:
        table_name = table['name']
        print(f"- {table_name}")
        
        # 显示每个表的记录数
        try:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            print(f"  * 记录数: {count}")
            
            # 对于post_ranking和import表，显示模拟数据数量
            if table_name == 'post_ranking':
                cursor.execute("SELECT COUNT(*) FROM post_ranking WHERE thread_id LIKE 'thread%'")
                mock_count = cursor.fetchone()[0]
                print(f"  * 疑似模拟数据记录数: {mock_count}")
                
                # 显示重复的thread_id记录数
                cursor.execute("""
                    SELECT thread_id, COUNT(*) as count
                    FROM post_ranking
                    GROUP BY thread_id
                    HAVING COUNT(*) > 1 AND thread_id IS NOT NULL AND thread_id != ''
                """)
                duplicates = cursor.fetchall()
                if duplicates:
                    print(f"  * 有 {len(duplicates)} 个thread_id有重复记录:")
                    for dup in duplicates[:5]:  # 只显示前5个
                        print(f"    - thread_id: {dup['thread_id']}, 重复次数: {dup['count']}")
                    if len(duplicates) > 5:
                        print(f"    - ... 还有 {len(duplicates) - 5} 个重复记录未显示")
            
            elif table_name == 'import':
                cursor.execute("SELECT COUNT(*) FROM import WHERE data_category = 'post_ranking' AND thread_id LIKE 'thread%'")
                mock_count = cursor.fetchone()[0]
                print(f"  * 疑似模拟数据记录数(post_ranking): {mock_count}")
        except Exception as e:
            print(f"  * 无法获取表信息: {str(e)}")
    
    print("\n开始清理模拟数据...")
    
    # 清理post_ranking表中可能的模拟数据
    try:
        # 检查表是否存在
        cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='post_ranking'")
        if cursor.fetchone()[0] > 0:
            print("\n处理post_ranking表:")
            
            # 删除thread_id为空或null的记录
            cursor.execute("DELETE FROM post_ranking WHERE thread_id IS NULL OR thread_id = ''")
            print(f"- 已删除 {cursor.rowcount} 条thread_id为空的记录")
            
            # 删除thread_id以'thread'开头的记录（可能是模拟数据）
            cursor.execute("DELETE FROM post_ranking WHERE thread_id LIKE 'thread%'")
            print(f"- 已删除 {cursor.rowcount} 条thread_id以'thread'开头的记录")
            
            # 删除重复的thread_id记录，保留最新的一条
            cursor.execute("""
                DELETE FROM post_ranking
                WHERE rowid NOT IN (
                    SELECT MIN(rowid)
                    FROM post_ranking
                    GROUP BY thread_id
                    HAVING thread_id IS NOT NULL AND thread_id != ''
                )
            """)
            print(f"- 已删除 {cursor.rowcount} 条重复的thread_id记录")
            
            # 统计剩余记录数
            cursor.execute("SELECT COUNT(*) FROM post_ranking")
            print(f"- post_ranking表中剩余 {cursor.fetchone()[0]} 条记录")
    except Exception as e:
        print(f"清理post_ranking表时出错: {str(e)}")
    
    # 清理author_ranking表中可能的模拟数据
    try:
        # 检查表是否存在
        cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='author_ranking'")
        if cursor.fetchone()[0] > 0:
            print("\n处理author_ranking表:")
            
            # 删除author为空或null的记录
            cursor.execute("DELETE FROM author_ranking WHERE author IS NULL OR author = ''")
            print(f"- 已删除 {cursor.rowcount} 条author为空的记录")
            
            # 删除author以'用户'开头的记录（可能是模拟数据）
            cursor.execute("DELETE FROM author_ranking WHERE author LIKE '用户%'")
            print(f"- 已删除 {cursor.rowcount} 条author以'用户'开头的记录")
            
            # 删除重复的author记录，保留最新的一条
            cursor.execute("""
                DELETE FROM author_ranking
                WHERE rowid NOT IN (
                    SELECT MIN(rowid)
                    FROM author_ranking
                    GROUP BY author
                    HAVING author IS NOT NULL AND author != ''
                )
            """)
            print(f"- 已删除 {cursor.rowcount} 条重复的author记录")
            
            # 统计剩余记录数
            cursor.execute("SELECT COUNT(*) FROM author_ranking")
            print(f"- author_ranking表中剩余 {cursor.fetchone()[0]} 条记录")
    except Exception as e:
        print(f"清理author_ranking表时出错: {str(e)}")
    
    # 清理import表中可能的模拟数据
    try:
        # 检查表是否存在
        cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table' AND name='import'")
        if cursor.fetchone()[0] > 0:
            print("\n处理import表:")
            
            # 删除data_category为'post_ranking'且thread_id为特定格式的记录
            cursor.execute("DELETE FROM import WHERE data_category = 'post_ranking' AND (thread_id IS NULL OR thread_id = '' OR thread_id LIKE 'thread%')")
            print(f"- 已删除 {cursor.rowcount} 条可能的模拟帖子排行记录")
            
            # 删除data_category为'author_ranking'且author为特定格式的记录
            cursor.execute("DELETE FROM import WHERE data_category = 'author_ranking' AND (author IS NULL OR author = '' OR author LIKE '用户%')")
            print(f"- 已删除 {cursor.rowcount} 条可能的模拟作者排行记录")
            
            # 删除重复的thread_id记录，保留最新的一条
            cursor.execute("""
                DELETE FROM import
                WHERE data_category = 'post_ranking' AND rowid NOT IN (
                    SELECT MIN(rowid)
                    FROM import
                    WHERE data_category = 'post_ranking'
                    GROUP BY thread_id
                    HAVING thread_id IS NOT NULL AND thread_id != ''
                )
            """)
            print(f"- 已删除 {cursor.rowcount} 条重复的thread_id记录(import表)")
            
            # 统计剩余记录数
            cursor.execute("SELECT COUNT(*) FROM import")
            print(f"- import表中剩余 {cursor.fetchone()[0]} 条记录")
    except Exception as e:
        print(f"清理import表时出错: {str(e)}")
    
    # 提交更改
    conn.commit()
    conn.close()
    print("\n数据清理完成!")

if __name__ == "__main__":
    clear_mock_data() 