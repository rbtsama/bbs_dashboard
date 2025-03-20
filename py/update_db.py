import sqlite3
import pandas as pd
import os
import json
from datetime import datetime
import time
import logging
import sys
import shutil
import random
from typing import Dict, List, Any, Tuple
import msvcrt
import argparse
import traceback
import csv
import re
import gc

# 导入词云生成模块
try:
    from generate_wordcloud import main as generate_wordcloud
except ImportError:
    # 如果在不同目录下
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    try:
        from generate_wordcloud import main as generate_wordcloud
    except ImportError:
        def generate_wordcloud():
            logging.warning("词云生成模块导入失败")
            return 0

# 设置日志
# 确保日志目录存在
os.makedirs(os.path.join(os.path.dirname(__file__), "logs"), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(os.path.join(os.path.dirname(__file__), "logs", "update_db.log")),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("update_db")

class DatabaseUpdater:
    def __init__(self, db_path=None):
        """初始化数据库更新器
        
        Args:
            db_path: 数据库文件路径，默认使用项目根目录下的backend/db/forum_data.db
        """
        # 获取项目根目录
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        
        # 如果未提供路径，使用默认路径
        if db_path is None:
            db_path = os.path.join(project_root, "backend/db/forum_data.db")
            
        # 使用环境变量中的路径（如果有）
        self.db_path = os.environ.get('DATABASE_PATH', db_path)
        
        # 生成唯一的临时数据库文件名
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_suffix = random.randint(1000, 9999)
        self.version_id = f"{timestamp}_{random_suffix}"
        self.temp_db_path = f"{self.db_path}.temp_{self.version_id}"
        
        # 保护表列表 - 添加thread_follow
        self.protected_tables = ['wordcloud_cache', 'user_data', 'thread_follow']
        
        logger.info(f"数据库更新器初始化完成，目标数据库：{self.db_path}")
        logger.info(f"临时数据库将使用路径：{self.temp_db_path}")
        
        # 确保目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        os.makedirs("logs", exist_ok=True)
        
        # 关键业务表 - 这些表将使用合并策略更新而不是替换
        self.merge_tables = [
            'post_ranking',        # 帖子排名
            'car_detail',          # 汽车详情
            'author_ranking',      # 作者排名
            'post_history',        # 帖子历史
            'author_history'       # 作者历史
        ]
    
    def start_update_process(self, update_type="incremental"):
        """开始更新过程，记录版本信息"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 确保版本表存在
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS data_version (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version_id TEXT NOT NULL,
            update_type TEXT NOT NULL,
            started_at DATETIME NOT NULL,
            completed_at DATETIME,
            status TEXT NOT NULL,
            affected_rows INTEGER DEFAULT 0,
            details TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 确保变更日志表存在
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS data_change_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version_id TEXT NOT NULL,
            table_name TEXT NOT NULL,
            record_id TEXT NOT NULL,
            change_type TEXT NOT NULL,
            old_values TEXT,
            new_values TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        
        # 插入新版本记录
        cursor.execute('''
        INSERT INTO data_version 
        (version_id, update_type, started_at, status) 
        VALUES (?, ?, ?, ?)
        ''', (self.version_id, update_type, datetime.now(), 'in_progress'))
        
        conn.commit()
        conn.close()
        
        logger.info(f"开始数据更新，版本ID: {self.version_id}, 类型: {update_type}")
        return self.version_id
    
    def create_temp_database(self):
        """创建临时数据库"""
        try:
            # 删除已存在的临时数据库
            if os.path.exists(self.temp_db_path):
                try:
                    os.remove(self.temp_db_path)
                    logger.info(f"已删除旧的临时数据库: {self.temp_db_path}")
                except PermissionError:
                    # 如果文件被占用，使用新的临时文件名
                    random_suffix = random.randint(1000, 9999)
                    self.temp_db_path = f"{self.db_path}.temp_{self.version_id}_{random_suffix}_alt"
                    logger.info(f"旧临时数据库被占用，使用新路径: {self.temp_db_path}")
            
            # 如果存在原数据库，则复制保护表
            if os.path.exists(self.db_path):
                # 创建空的临时数据库
                with sqlite3.connect(self.temp_db_path) as temp_conn:
                    # 仅创建连接以初始化数据库文件
                    pass
                
                # 从原数据库复制保护表
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    
                    # 获取所有表
                    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
                    all_tables = [row[0] for row in cursor.fetchall()]
                    
                    # 检查保护表是否存在并复制
                    for table in self.protected_tables:
                        if table in all_tables:
                            try:
                                # 获取表结构
                                cursor.execute(f"PRAGMA table_info({table})")
                                columns = [row[1] for row in cursor.fetchall()]
                                columns_str = ", ".join(columns)
                                
                                # 获取数据
                                cursor.execute(f"SELECT {columns_str} FROM {table}")
                                rows = cursor.fetchall()
                                
                                if rows:
                                    # 将数据复制到临时数据库
                                    with sqlite3.connect(self.temp_db_path) as temp_conn:
                                        temp_cursor = temp_conn.cursor()
                                        
                                        # 创建表
                                        cursor.execute(f"PRAGMA table_info({table})")
                                        columns_info = cursor.fetchall()
                                        create_table_sql = f"CREATE TABLE IF NOT EXISTS {table} ("
                                        for i, col_info in enumerate(columns_info):
                                            name = col_info[1]
                                            type_name = col_info[2]
                                            not_null = "NOT NULL" if col_info[3] else ""
                                            default = f"DEFAULT {col_info[4]}" if col_info[4] is not None else ""
                                            pk = "PRIMARY KEY" if col_info[5] else ""
                                            create_table_sql += f"{name} {type_name} {not_null} {default} {pk}"
                                            if i < len(columns_info) - 1:
                                                create_table_sql += ", "
                                        create_table_sql += ")"
                                        temp_cursor.execute(create_table_sql)
                                        
                                        # 插入数据
                                        placeholders = ", ".join(["?" for _ in columns])
                                        insert_sql = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
                                        temp_cursor.executemany(insert_sql, rows)
                                        temp_conn.commit()
                                    
                                    logger.info(f"复制保护表 {table} 的 {len(rows)} 行数据到临时数据库")
                                else:
                                    logger.warning(f"保护表 {table} 无数据")
                            except Exception as e:
                                logger.warning(f"复制保护表 {table} 时出错: {str(e)}")
                        else:
                            logger.warning(f"复制保护表 {table} 时出错: no such table: {table}")
            else:
                # 如果原数据库不存在，直接创建空的临时数据库
                with sqlite3.connect(self.temp_db_path) as temp_conn:
                    # 仅创建连接以初始化数据库文件
                    pass
                logger.warning(f"原数据库不存在，已创建空的临时数据库: {self.temp_db_path}")
            
            logger.info(f"临时数据库创建完成: {self.temp_db_path}")
            return True
        except Exception as e:
            logger.error(f"创建临时数据库时出错: {str(e)}")
            return False
    
    def import_excel_to_temp(self, file_path, table_name):
        """将Excel文件数据导入到临时数据库的指定表中"""
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.error(f"Excel文件不存在: {file_path}")
                return False
                
            logger.info(f"开始导入Excel文件到{table_name}表: {file_path}")
            
            # 读取Excel文件
            df = pd.read_excel(file_path)
            if df.empty:
                logger.warning(f"Excel文件为空: {file_path}")
                return True
            
            # 处理列名中的特殊字符
            df.columns = [self._sanitize_column_name(col) for col in df.columns]
                
            # 连接临时数据库
            with sqlite3.connect(self.temp_db_path) as conn:
                # 创建表结构（如果表不存在）
                columns = ", ".join([f'"{col}" TEXT' for col in df.columns])
                conn.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns})')
                
                # 将数据转换为文本并写入数据库
                df = df.astype(str)
                df.replace('nan', '', inplace=True)
                df.to_sql(table_name, conn, if_exists='replace', index=False)
                
                # 验证导入结果
                cursor = conn.cursor()
                cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
                count = cursor.fetchone()[0]
                
                logger.info(f"成功导入 {count} 条记录到 {table_name} 表")
                return True
        except Exception as e:
            logger.error(f"导入Excel文件失败 {file_path} -> {table_name}: {str(e)}")
            return False

    def import_csv_to_temp(self, file_path, table_name):
        """将CSV文件数据导入到临时数据库的指定表中"""
        try:
            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.error(f"CSV文件不存在: {file_path}")
                return False
                
            logger.info(f"开始导入CSV文件到{table_name}表: {file_path}")
            
            # 读取CSV文件
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            if df.empty:
                logger.warning(f"CSV文件为空: {file_path}")
                return True
            
            # 处理列名中的特殊字符
            df.columns = [self._sanitize_column_name(col) for col in df.columns]
                
            # 连接临时数据库
            with sqlite3.connect(self.temp_db_path) as conn:
                # 创建表结构（如果表不存在）
                columns = ", ".join([f'"{col}" TEXT' for col in df.columns])
                conn.execute(f'CREATE TABLE IF NOT EXISTS "{table_name}" ({columns})')
                
                # 将数据转换为文本并写入数据库
                df = df.astype(str)
                df.replace('nan', '', inplace=True)
                df.to_sql(table_name, conn, if_exists='replace', index=False)
                
                # 验证导入结果
                cursor = conn.cursor()
                cursor.execute(f'SELECT COUNT(*) FROM "{table_name}"')
                count = cursor.fetchone()[0]
                
                logger.info(f"成功导入 {count} 条记录到 {table_name} 表")
                return True
        except Exception as e:
            logger.error(f"导入CSV文件失败 {file_path} -> {table_name}: {str(e)}")
            return False
    
    def execute_sql_on_temp(self, sql_file_path):
        """在临时数据库上执行SQL文件
        
        Args:
            sql_file_path: SQL文件路径
            
        Returns:
            bool: 执行是否成功
        """
        try:
            if not os.path.exists(sql_file_path):
                logger.error(f"SQL文件不存在: {sql_file_path}")
                return False
                
            logger.info(f"执行SQL文件: {sql_file_path}")
            
            # 读取SQL文件内容
            with open(sql_file_path, 'r', encoding='utf-8') as f:
                sql_content = f.read()
                
            # 如果SQL内容为空，直接返回成功
            if not sql_content.strip():
                logger.warning(f"SQL文件为空: {sql_file_path}")
                return True
                
            # 拆分SQL语句（考虑存储过程和触发器等多行语句）
            statements = []
            current_statement = []
            delimiter = ';'
            
            for line in sql_content.split('\n'):
                # 忽略注释行
                stripped_line = line.strip()
                if stripped_line.startswith('--') or stripped_line.startswith('#'):
                    continue
                    
                # 检查是否更改了分隔符（如DELIMITER //）
                if stripped_line.upper().startswith('DELIMITER '):
                    if current_statement:
                        statements.append('\n'.join(current_statement))
                        current_statement = []
                    delimiter = stripped_line.split()[1]
                    continue
                
                # 添加当前行到语句
                current_statement.append(line)
                
                # 检查是否到达语句结束
                if stripped_line.endswith(delimiter):
                    statements.append('\n'.join(current_statement))
                    current_statement = []
            
            # 添加最后一个语句（如果有）
            if current_statement:
                statements.append('\n'.join(current_statement))
            
            # 连接到临时数据库并执行SQL语句
            with sqlite3.connect(self.temp_db_path) as conn:
                cursor = conn.cursor()
                
                for i, statement in enumerate(statements):
                    if statement.strip():
                        try:
                            cursor.execute(statement)
                        except sqlite3.Error as e:
                            logger.error(f"执行SQL语句 #{i+1} 时出错: {str(e)}")
                            logger.error(f"问题语句: {statement}")
                            # 继续执行其他语句，不中断整个执行过程
                
                conn.commit()
            
            logger.info(f"成功执行SQL文件: {sql_file_path}")
            return True
        except Exception as e:
            logger.error(f"执行SQL文件时出错: {str(e)}")
            return False
    
    def generate_change_log(self, main_tables):
        """生成变更日志，比较临时数据库和主数据库中指定表的差异"""
        try:
            temp_conn = sqlite3.connect(self.temp_db_path)
            temp_cursor = temp_conn.cursor()
            
            main_conn = sqlite3.connect(self.db_path)
            main_cursor = main_conn.cursor()
            
            total_changes = 0
            
            for table_name in main_tables:
                # 跳过保护表
                if table_name in self.protected_tables:
                    continue
                
                try:
                    # 获取表的主键列
                    primary_key = self._get_table_primary_key(main_cursor, table_name)
                    if not primary_key:
                        primary_key = 'url'  # 默认使用url作为主键
                    
                    # 获取表的所有列
                    temp_cursor.execute(f"PRAGMA table_info({table_name})")
                    columns = [row[1] for row in temp_cursor.fetchall()]
                    
                    if not columns:
                        logger.warning(f"表 {table_name} 在临时数据库中不存在或没有列")
                        continue
                    
                    if primary_key not in columns:
                        logger.warning(f"表 {table_name} 没有主键列 {primary_key}")
                        continue
                    
                    # 获取临时数据库中的所有记录
                    temp_cursor.execute(f"SELECT * FROM {table_name}")
                    temp_records = temp_cursor.fetchall()
                    
                    # 获取主数据库中的所有记录ID
                    main_cursor.execute(f"SELECT {primary_key} FROM {table_name}")
                    main_record_ids = set(row[0] for row in main_cursor.fetchall())
                    
                    # 记录变更
                    for record in temp_records:
                        record_dict = dict(zip(columns, record))
                        record_id = record_dict[primary_key]
                        
                        if record_id in main_record_ids:
                            # 记录存在，检查是否有更新
                            main_cursor.execute(
                                f"SELECT * FROM {table_name} WHERE {primary_key} = ?", 
                                (record_id,)
                            )
                            main_record = main_cursor.fetchone()
                            main_record_dict = dict(zip(columns, main_record))
                            
                            # 检查是否有变更
                            if main_record_dict != record_dict:
                                # 记录更新
                                main_cursor.execute(f'''
                                INSERT INTO data_change_log 
                                (version_id, table_name, record_id, change_type, old_values, new_values)
                                VALUES (?, ?, ?, ?, ?, ?)
                                ''', (
                                    self.version_id, 
                                    table_name, 
                                    record_id, 
                                    'update',
                                    json.dumps(main_record_dict),
                                    json.dumps(record_dict)
                                ))
                                total_changes += 1
                        else:
                            # 新记录，记录插入
                            main_cursor.execute(f'''
                            INSERT INTO data_change_log 
                            (version_id, table_name, record_id, change_type, old_values, new_values)
                            VALUES (?, ?, ?, ?, ?, ?)
                            ''', (
                                self.version_id, 
                                table_name, 
                                record_id, 
                                'insert',
                                None,
                                json.dumps(record_dict)
                            ))
                            total_changes += 1
                    
                    # 检查删除的记录
                    temp_cursor.execute(f"SELECT {primary_key} FROM {table_name}")
                    temp_record_ids = set(row[0] for row in temp_cursor.fetchall())
                    
                    deleted_ids = main_record_ids - temp_record_ids
                    for deleted_id in deleted_ids:
                        # 获取将被删除的记录
                        main_cursor.execute(
                            f"SELECT * FROM {table_name} WHERE {primary_key} = ?", 
                            (deleted_id,)
                        )
                        main_record = main_cursor.fetchone()
                        main_record_dict = dict(zip(columns, main_record))
                        
                        # 记录删除
                        main_cursor.execute(f'''
                        INSERT INTO data_change_log 
                        (version_id, table_name, record_id, change_type, old_values, new_values)
                        VALUES (?, ?, ?, ?, ?, ?)
                        ''', (
                            self.version_id, 
                            table_name, 
                            deleted_id, 
                            'delete',
                            json.dumps(main_record_dict),
                            None
                        ))
                        total_changes += 1
                
                except Exception as e:
                    logger.error(f"处理表 {table_name} 的变更日志时出错: {e}")
            
            main_conn.commit()
            main_conn.close()
            temp_conn.close()
            
            logger.info(f"生成变更日志完成，共 {total_changes} 处变更")
            return total_changes
        except Exception as e:
            logger.error(f"生成变更日志时出错: {e}")
            return 0
    
    def _get_table_primary_key(self, cursor, table_name):
        """获取表的主键字段名"""
        try:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # 查找设置了主键的列
            for col in columns:
                if col[5] == 1:  # pk字段为1表示主键
                    return col[1]  # 返回列名
            
            # 如果没有明确的主键，尝试查找表的所有索引
            cursor.execute(f"PRAGMA index_list({table_name})")
            indexes = cursor.fetchall()
            
            for idx in indexes:
                if idx[2] == 1:  # 唯一索引
                    # 获取索引的列
                    cursor.execute(f"PRAGMA index_info({idx[1]})")
                    index_columns = cursor.fetchall()
                    if index_columns:
                        return index_columns[0][2]  # 返回第一个索引列名
            
            return None
        except Exception as e:
            logger.error(f"获取表 {table_name} 的主键时出错: {e}")
            return None
    
    def apply_changes(self, main_tables):
        """将临时数据库中的更改应用到主数据库"""
        try:
            temp_conn = sqlite3.connect(self.temp_db_path)
            temp_cursor = temp_conn.cursor()
            
            main_conn = sqlite3.connect(self.db_path)
            main_cursor = main_conn.cursor()
            
            affected_rows = 0
            
            for table_name in main_tables:
                # 跳过保护表
                if table_name in self.protected_tables:
                    continue
                
                try:
                    if table_name in self.merge_tables:
                        # 使用合并策略处理这些表
                        affected_rows += self._merge_table_data(temp_cursor, main_cursor, table_name)
                    else:
                        # 对于其他表使用替换策略
                        # 备份原表
                        main_cursor.execute(f"ALTER TABLE {table_name} RENAME TO {table_name}_backup")
                        
                        # 从临时数据库中附加表
                        main_cursor.execute(f"ATTACH DATABASE '{self.temp_db_path}' AS temp_db")
                        
                        # 创建新表
                        main_cursor.execute(f"CREATE TABLE {table_name} AS SELECT * FROM temp_db.{table_name}")
                        
                        # 分离临时数据库
                        main_cursor.execute("DETACH DATABASE temp_db")
                        
                        # 获取行数
                        main_cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
                        new_count = main_cursor.fetchone()[0]
                        
                        main_cursor.execute(f"SELECT COUNT(*) FROM {table_name}_backup")
                        old_count = main_cursor.fetchone()[0]
                        
                        # 删除备份表
                        main_cursor.execute(f"DROP TABLE {table_name}_backup")
                        
                        affected_rows += abs(new_count - old_count)
                        logger.info(f"表 {table_name} 更新完成，从 {old_count} 行变为 {new_count} 行")
                
                except Exception as e:
                    logger.error(f"更新表 {table_name} 时出错: {e}")
                    # 尝试恢复
                    try:
                        main_cursor.execute(f"DROP TABLE IF EXISTS {table_name}")
                        main_cursor.execute(f"ALTER TABLE {table_name}_backup RENAME TO {table_name}")
                    except:
                        pass
            
            # 更新版本记录
            main_cursor.execute('''
            UPDATE data_version 
            SET completed_at = ?, status = ?, affected_rows = ?
            WHERE version_id = ?
            ''', (datetime.now(), 'completed', affected_rows, self.version_id))
            
            main_conn.commit()
            main_conn.close()
            temp_conn.close()
            
            # 删除临时数据库
            try:
                # 先尝试直接删除
                try:
                    os.remove(self.temp_db_path)
                    logger.info(f"临时数据库已删除: {self.temp_db_path}")
                except PermissionError:
                    # 如果因为文件被占用导致删除失败，先尝试关闭所有连接
                    time.sleep(1)  # 等待1秒，确保连接已关闭
                    
                    # 如果还是不能删除，尝试重命名
                    try:
                        temp_rename = f"{self.temp_db_path}.to_delete"
                        os.rename(self.temp_db_path, temp_rename)
                        logger.info(f"临时数据库已重命名为待删除状态: {temp_rename}")
                        
                        # 使用系统任务启动延迟删除（仅Windows系统）
                        try:
                            # 创建一个批处理文件来延迟删除
                            bat_path = os.path.join(os.path.dirname(self.db_path), "delete_temp.bat")
                            with open(bat_path, 'w') as f:
                                f.write(f"@echo off\n")
                                f.write(f"timeout /t 5 /nobreak >nul\n")  # 等待5秒
                                f.write(f"del /q /f \"{temp_rename}\"\n")
                                f.write(f"del /q /f \"{bat_path}\"\n")  # 自删除
                            
                            # 使用无窗口启动批处理
                            os.system(f"start /b cmd /c \"{bat_path}\"")
                            logger.info(f"已创建延迟删除任务")
                        except Exception as e:
                            logger.warning(f"创建延迟删除任务失败: {str(e)}")
                    except Exception as e:
                        logger.warning(f"重命名临时数据库失败: {str(e)}")
            except Exception as e:
                logger.warning(f"删除临时数据库失败: {str(e)}")
            
            logger.info(f"数据更新完成，影响了 {affected_rows} 行")
            return affected_rows
        except Exception as e:
            logger.error(f"应用更改时出错: {e}")
            
            # 记录失败状态
            try:
                fail_conn = sqlite3.connect(self.db_path)
                fail_cursor = fail_conn.cursor()
                
                fail_cursor.execute('''
                UPDATE data_version 
                SET completed_at = ?, status = ?, details = ?
                WHERE version_id = ?
                ''', (datetime.now(), 'failed', str(e), self.version_id))
                
                fail_conn.commit()
                fail_conn.close()
            except:
                pass
            
            return 0
    
    def _merge_table_data(self, temp_cursor, main_cursor, table_name):
        """合并表数据而不是替换"""
        affected_rows = 0
        try:
            # 获取表的主键
            main_cursor.execute(f"PRAGMA table_info({table_name})")
            columns_info = main_cursor.fetchall()
            columns = [col[1] for col in columns_info]
            
            primary_key = self._get_table_primary_key(main_cursor, table_name)
            if not primary_key:
                primary_key = 'url'  # 默认使用url
            
            if primary_key not in columns:
                logger.warning(f"表 {table_name} 找不到主键 {primary_key}，跳过合并")
                return 0
            
            # 从临时数据库中获取所有记录
            temp_cursor.execute(f"SELECT * FROM {table_name}")
            temp_records = temp_cursor.fetchall()
            
            for record in temp_records:
                record_dict = dict(zip(columns, record))
                record_id = record_dict[primary_key]
                
                # 检查记录是否存在
                main_cursor.execute(f"SELECT COUNT(*) FROM {table_name} WHERE {primary_key} = ?", (record_id,))
                exists = main_cursor.fetchone()[0] > 0
                
                if exists:
                    # 更新现有记录
                    set_clause = ", ".join([f"{col} = ?" for col in columns if col != primary_key])
                    values = [record_dict[col] for col in columns if col != primary_key]
                    values.append(record_id)
                    
                    main_cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE {primary_key} = ?", 
                                        values)
                else:
                    # 插入新记录
                    placeholders = ", ".join(["?" for _ in columns])
                    main_cursor.execute(f"INSERT INTO {table_name} VALUES ({placeholders})", record)
                
                affected_rows += 1
            
            logger.info(f"表 {table_name} 合并完成，处理了 {affected_rows} 行记录")
            return affected_rows
        
        except Exception as e:
            logger.error(f"合并表 {table_name} 数据时出错: {e}")
            return 0
    
    def run_full_update(self, excel_files, csv_files, sql_files, main_tables):
        """执行完整的更新流程"""
        try:
            # 开始更新过程
            self.start_update_process(update_type="full")
            
            # 创建临时数据库
            self.create_temp_database()
            
            # 导入Excel数据
            for file_path, table_name in excel_files.items():
                self.import_excel_to_temp(file_path, table_name)
            
            # 导入CSV数据
            for file_path, table_name in csv_files.items():
                self.import_csv_to_temp(file_path, table_name)
            
            # 执行SQL文件
            for sql_file in sql_files:
                self.execute_sql_on_temp(sql_file)
            
            # 生成变更日志
            self.generate_change_log(main_tables)
            
            # 应用更改
            affected_rows = self.apply_changes(main_tables)
            
            return True, affected_rows
        except Exception as e:
            logger.error(f"执行更新流程时出错: {e}")
            return False, 0
    
    def run_incremental_update(self, excel_files, csv_files, sql_files, main_tables):
        """执行增量更新流程"""
        try:
            # 开始更新过程
            self.start_update_process(update_type="incremental")
            
            # 创建临时数据库
            self.create_temp_database()
            
            # 导入Excel数据
            for file_path, table_name in excel_files.items():
                self.import_excel_to_temp(file_path, table_name)
            
            # 导入CSV数据
            for file_path, table_name in csv_files.items():
                self.import_csv_to_temp(file_path, table_name)
            
            # 执行SQL文件
            for sql_file in sql_files:
                self.execute_sql_on_temp(sql_file)
            
            # 生成变更日志
            self.generate_change_log(main_tables)
            
            # 应用更改
            affected_rows = self.apply_changes(main_tables)
            
            return True, affected_rows
        except Exception as e:
            logger.error(f"执行增量更新流程时出错: {e}")
            return False, 0
    
    def _sanitize_column_name(self, name):
        """清理列名，确保SQLite兼容性"""
        # 替换特殊字符为下划线
        import re
        name = re.sub(r'[^\w]', '_', str(name))
        # 确保列名不以数字开头
        if name and name[0].isdigit():
            name = 'col_' + name
        # 确保名称不是空的
        if not name:
            name = 'column'
        return name

    def replace_database(self):
        """将临时数据库替换为正式数据库"""
        try:
            if not os.path.exists(self.temp_db_path):
                logger.error(f"临时数据库不存在，无法替换: {self.temp_db_path}")
                return False
                
            # 检查临时数据库是否有效
            try:
                with sqlite3.connect(self.temp_db_path) as conn:
                    cursor = conn.cursor()
                    # 检查是否至少包含一个表
                    cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
                    table_count = cursor.fetchone()[0]
                    if table_count == 0:
                        logger.error("临时数据库无效，不包含任何表")
                        return False
            except sqlite3.Error as e:
                logger.error(f"临时数据库无效，无法连接或查询: {str(e)}")
                return False
                
            # 创建备份
            backup_path = f"{self.db_path}.bak_{self.version_id}"
            backup_created = False
            
            if os.path.exists(self.db_path):
                # 尝试最多5次创建备份
                max_attempts = 5
                attempt = 0
                while attempt < max_attempts:
                    attempt += 1
                    try:
                        # 创建备份前确保数据库连接关闭
                        try:
                            # 强制关闭所有可能的连接
                            gc.collect()  # 尝试回收未关闭的连接
                            time.sleep(1)  # 等待1秒
                        except:
                            pass
                        
                        # 创建备份
                        shutil.copy2(self.db_path, backup_path)
                        backup_created = True
                        logger.info(f"已创建数据库备份: {backup_path}")
                        break
                    except (IOError, PermissionError) as e:
                        logger.warning(f"尝试第 {attempt} 次创建备份时遇到文件锁定: {str(e)}")
                        if attempt < max_attempts:
                            time.sleep(2)  # 等待2秒后重试
                        else:
                            logger.error(f"创建数据库备份失败，文件被锁定: {str(e)}")
                            return False
                    except Exception as e:
                        logger.error(f"创建数据库备份时出错: {str(e)}")
                        return False
            
            # 替换数据库
            # 尝试最多5次替换数据库
            max_attempts = 5
            attempt = 0
            while attempt < max_attempts:
                attempt += 1
                try:
                    # 替换前确保数据库连接关闭
                    try:
                        # 强制关闭所有可能的连接
                        gc.collect()  # 尝试回收未关闭的连接
                        time.sleep(1)  # 等待1秒
                    except:
                        pass
                    
                    temp_db_copy = f"{self.temp_db_path}.copy"
                    # 先创建临时数据库的副本，以防原始副本被锁定
                    shutil.copy2(self.temp_db_path, temp_db_copy)
                    
                    if os.path.exists(self.db_path):
                        # 使用新文件替换旧文件的方式，可能更容易绕过文件锁
                        os.replace(temp_db_copy, self.db_path)
                    else:
                        shutil.copy2(temp_db_copy, self.db_path)
                    
                    logger.info(f"数据库替换完成")
                    
                    # 删除临时文件
                    if os.path.exists(temp_db_copy):
                        try:
                            os.remove(temp_db_copy)
                        except:
                            pass
                    
                    # 尝试删除原始临时数据库
                    try:
                        if os.path.exists(self.temp_db_path):
                            os.remove(self.temp_db_path)
                            logger.info(f"临时数据库已删除: {self.temp_db_path}")
                    except Exception as e:
                        logger.warning(f"无法立即删除临时数据库: {str(e)}")
                        # 使用延迟删除策略
                        self._schedule_delayed_delete(self.temp_db_path)
                    
                    return True
                    
                except (IOError, PermissionError) as e:
                    logger.warning(f"尝试第 {attempt} 次替换数据库时遇到文件锁定: {str(e)}")
                    # 如果数据库已备份但替换失败，尝试从备份恢复
                    if backup_created and attempt == max_attempts:
                        try:
                            logger.warning("尝试从备份恢复数据库...")
                            shutil.copy2(backup_path, self.db_path)
                            logger.info("已从备份恢复数据库")
                        except Exception as restore_error:
                            logger.error(f"恢复数据库失败: {str(restore_error)}")
                    
                    if attempt < max_attempts:
                        time.sleep(2)  # 等待2秒后重试
                    else:
                        logger.error(f"替换数据库失败，文件被锁定: {str(e)}")
                        return False
                except Exception as e:
                    logger.error(f"替换数据库时出错: {str(e)}")
                    # 如果数据库已备份但替换失败，尝试从备份恢复
                    if backup_created:
                        try:
                            logger.warning("尝试从备份恢复数据库...")
                            shutil.copy2(backup_path, self.db_path)
                            logger.info("已从备份恢复数据库")
                        except Exception as restore_error:
                            logger.error(f"恢复数据库失败: {str(restore_error)}")
                    return False
        except Exception as e:
            logger.error(f"替换数据库时发生未预期错误: {str(e)}")
            return False
    
    def _schedule_delayed_delete(self, file_path):
        """安排延迟删除文件"""
        try:
            # 如果还是不能删除，尝试重命名
            temp_rename = f"{file_path}.to_delete"
            try:
                if os.path.exists(temp_rename):
                    os.remove(temp_rename)
            except:
                pass
                
            try:
                os.rename(file_path, temp_rename)
                logger.info(f"文件已重命名为待删除状态: {temp_rename}")
            except Exception as e:
                logger.warning(f"重命名文件失败: {str(e)}")
                return
            
            # 使用系统任务启动延迟删除（仅Windows系统）
            try:
                # 创建一个批处理文件来延迟删除
                bat_path = os.path.join(os.path.dirname(self.db_path), f"delete_temp_{int(time.time())}.bat")
                with open(bat_path, 'w') as f:
                    f.write(f"@echo off\n")
                    f.write(f"timeout /t 10 /nobreak >nul\n")  # 等待10秒
                    f.write(f"del /q /f \"{temp_rename}\"\n")
                    f.write(f"if exist \"{temp_rename}\" (\n")
                    f.write(f"  timeout /t 30 /nobreak >nul\n")  # 如果第一次删除失败，再等待30秒
                    f.write(f"  del /q /f \"{temp_rename}\"\n")
                    f.write(f")\n")
                    f.write(f"del /q /f \"{bat_path}\"\n")  # 自删除
                
                # 使用无窗口启动批处理
                os.system(f"start /b cmd /c \"{bat_path}\"")
                logger.info(f"已创建延迟删除任务")
            except Exception as e:
                logger.warning(f"创建延迟删除任务失败: {str(e)}")
        except Exception as e:
            logger.warning(f"安排延迟删除失败: {str(e)}")

    def import_car_info_data(self):
        """导入车辆信息到car_info表，不影响其他表"""
        try:
            # 读取数据文件
            car_info_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data/processed/car_info.csv")
            
            # 检查所需文件是否存在
            if not os.path.exists(car_info_path):
                logger.warning(f"车辆信息文件不存在: {car_info_path}")
                return False
                
            # 读取CSV文件
            try:
                df = pd.read_csv(car_info_path)
                logger.info(f"成功读取车辆信息CSV文件: {car_info_path}, 共 {len(df)} 行")
            except Exception as e:
                logger.error(f"读取车辆信息文件时出错: {str(e)}")
                return False
            
            # 数据验证 - 只记录警告，不跳过任何记录
            invalid_records = self.validate_car_info_data(df, skip_invalid=False)
            if invalid_records:
                logger.warning(f"发现 {invalid_records} 条不完整记录，但仍将继续导入")
            
            # 确保时间列是正确的格式
            if 'post_time' in df.columns:
                df['post_time'] = pd.to_datetime(df['post_time'], errors='coerce')
            if 'scraping_time_R' in df.columns:
                df['scraping_time_R'] = pd.to_datetime(df['scraping_time_R'], errors='coerce')
            
            # 直接连接到原始数据库而非临时数据库
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # 备份原有car_info表（如果存在）
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='car_info'")
                if cursor.fetchone():
                    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
                    cursor.execute(f"ALTER TABLE car_info RENAME TO car_info_bak_{timestamp}")
                    logger.info(f"已将原car_info表重命名为car_info_bak_{timestamp}")
                
                # 创建car_info表结构
                cursor.execute('''
                CREATE TABLE car_info (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT,
                    year TEXT,
                    make TEXT,
                    model TEXT,
                    miles TEXT,
                    price TEXT,
                    trade_type TEXT,
                    location TEXT,
                    post_time TEXT,
                    scraping_time_R TEXT,
                    title TEXT,
                    author TEXT,
                    author_link TEXT,
                    thread_id TEXT,
                    daysold INTEGER DEFAULT 999,
                    last_active INTEGER DEFAULT 999,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
                ''')
                
                # 创建索引
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_car_info_url ON car_info(url)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_car_info_make ON car_info(make)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_car_info_model ON car_info(model)")
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_car_info_title ON car_info(title)")
                
                # 准备插入数据的SQL语句
                # 动态构建SQL插入语句，只包含df中存在的列
                columns = [col for col in df.columns if col != 'id']
                placeholders = ', '.join(['?' for _ in columns])
                columns_str = ', '.join(columns)
                
                insert_sql = f'''
                INSERT INTO car_info (
                    {columns_str}
                ) VALUES ({placeholders})
                '''
                
                # 统计信息
                total_records = len(df)
                rows_inserted = 0
                rows_skipped = 0
                errors = 0
                
                # 逐行插入数据
                for index, row in df.iterrows():
                    try:
                        url = row.get('url')
                        # 不再跳过没有URL的记录，只记录警告
                        if not url:
                            logger.warning(f"记录 #{index+1} URL为空，但仍将导入")
                        
                        # 格式化时间字段
                        if 'post_time' in row and pd.notna(row['post_time']):
                            post_time = row['post_time']
                            if isinstance(post_time, pd.Timestamp):
                                row['post_time'] = post_time.strftime('%Y-%m-%d %H:%M:%S')
                        
                        if 'scraping_time_R' in row and pd.notna(row['scraping_time_R']):
                            scraping_time = row['scraping_time_R']
                            if isinstance(scraping_time, pd.Timestamp):
                                row['scraping_time_R'] = scraping_time.strftime('%Y-%m-%d %H:%M:%S')
                        
                        # 提取thread_id（如果没有）
                        if 'thread_id' not in row or pd.isna(row['thread_id']):
                            thread_id = None
                            if url:
                                thread_id_match = re.search(r't_(\d+)\.html', url)
                                if thread_id_match:
                                    thread_id = thread_id_match.group(1)
                            row['thread_id'] = thread_id
                        
                        # 准备插入的数据
                        values = [row.get(col) for col in columns]
                        
                        # 插入数据
                        cursor.execute(insert_sql, values)
                        rows_inserted += 1
                        
                        # 每100条记录记录一次进度
                        if rows_inserted % 100 == 0:
                            logger.info(f"已导入 {rows_inserted}/{total_records} 条记录")
                        
                    except Exception as e:
                        logger.warning(f"插入记录 #{index+1} 时出错 [URL: {url}]: {str(e)}")
                        errors += 1
                
                conn.commit()
                logger.info(f"车辆信息导入完成: 总数据量 {total_records}, 成功导入 {rows_inserted}, 跳过 {rows_skipped}, 错误 {errors}")
                
                # 验证导入结果
                cursor.execute("SELECT COUNT(*) FROM car_info")
                total_rows = cursor.fetchone()[0]
                logger.info(f"导入后car_info表中共有 {total_rows} 条记录")
                
                if total_rows != total_records:
                    logger.warning(f"数据导入可能不完整：CSV中有 {total_records} 行，但数据库中有 {total_rows} 行")
                    
                    # 输出前10个缺失的记录
                    if total_rows < total_records:
                        cursor.execute("SELECT url FROM car_info")
                        db_urls = [row[0] for row in cursor.fetchall()]
                        csv_urls = df['url'].tolist()
                        missing_urls = set(csv_urls) - set(db_urls)
                        if missing_urls:
                            logger.warning(f"前10个缺失的URL: {list(missing_urls)[:10]}")
                
                return True
                
        except Exception as e:
            logger.error(f"导入车辆信息过程中出错: {str(e)}\n{traceback.format_exc()}")
            return False

    def validate_car_info_data(self, df, skip_invalid=False):
        """验证车辆信息数据，返回无效记录数量"""
        invalid_count = 0
        
        # 计算缺失值
        required_fields = ['url']
        for field in required_fields:
            if field in df.columns:
                missing = df[field].isna().sum()
                if missing > 0:
                    logger.warning(f"字段 '{field}' 有 {missing} 条记录缺失值")
                    invalid_count += missing
            else:
                logger.warning(f"数据中缺少必要字段: {field}")
        
        # 如果需要跳过无效记录
        if skip_invalid and invalid_count > 0:
            for field in required_fields:
                if field in df.columns:
                    df = df[df[field].notna()]
        
        return invalid_count

    def backup_protected_tables(self, tables=None):
        """备份保护表到临时数据库"""
        if tables is None:
            tables = self.protected_tables
        
        logger.info(f"开始备份保护表: {', '.join(tables)}")
        
        # 确保临时数据库存在
        if not os.path.exists(self.temp_db_path):
            logger.error("临时数据库不存在，无法备份保护表")
            return False
        
        # 检查源数据库是否存在
        if not os.path.exists(self.db_path):
            logger.warning("源数据库不存在，跳过保护表备份")
            return True  # 返回True因为这不是致命错误
        
        try:
            # 关闭所有可能的连接
            if hasattr(self, '_close_all_connections'):
                self._close_all_connections()
            
            # 创建源数据库连接
            src_conn = None
            dst_conn = None
            
            try:
                # 使用URI模式连接源数据库（只读模式）
                src_conn = sqlite3.connect(f"file:{self.db_path}?mode=ro", uri=True)
                src_conn.row_factory = sqlite3.Row
                
                # 连接目标数据库（临时数据库）
                dst_conn = sqlite3.connect(self.temp_db_path)
                
                # 对每个保护表，尝试复制
                for table in tables:
                    try:
                        # 检查源表是否存在
                        src_cursor = src_conn.cursor()
                        src_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
                        if not src_cursor.fetchone():
                            logger.warning(f"源数据库中不存在表 {table}，跳过")
                            continue
                        
                        # 获取表结构
                        src_cursor.execute(f"PRAGMA table_info({table})")
                        columns = src_cursor.fetchall()
                        
                        if not columns:
                            logger.warning(f"无法获取表 {table} 的结构，跳过")
                            continue
                        
                        # 获取所有列名
                        column_names = [column["name"] for column in columns]
                        columns_str = ', '.join(column_names)
                        
                        # 检查目标表是否存在，如果存在则先删除
                        dst_cursor = dst_conn.cursor()
                        dst_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
                        if dst_cursor.fetchone():
                            dst_cursor.execute(f"DROP TABLE {table}")
                            logger.info(f"已删除目标数据库中的表 {table}，准备重新创建")
                        
                        # 创建表结构
                        create_table_sql = f"CREATE TABLE {table} ("
                        for i, column in enumerate(columns):
                            create_table_sql += f"\n    {column['name']} {column['type']}"
                            if column['notnull']:
                                create_table_sql += " NOT NULL"
                            if column['pk']:
                                create_table_sql += " PRIMARY KEY"
                            if column['dflt_value'] is not None:
                                create_table_sql += f" DEFAULT {column['dflt_value']}"
                            if i < len(columns) - 1:
                                create_table_sql += ","
                        create_table_sql += "\n)"
                        
                        dst_cursor.execute(create_table_sql)
                        logger.info(f"已在目标数据库中创建表 {table}")
                        
                        # 复制表数据
                        try:
                            # 分批获取数据，避免一次性读取过多
                            batch_size = 1000
                            offset = 0
                            
                            while True:
                                src_cursor.execute(f"SELECT {columns_str} FROM {table} LIMIT {batch_size} OFFSET {offset}")
                                rows = src_cursor.fetchall()
                                
                                if not rows:
                                    break
                                
                                # 构建INSERT语句
                                placeholders = ', '.join(['?'] * len(column_names))
                                insert_sql = f"INSERT INTO {table} ({columns_str}) VALUES ({placeholders})"
                                
                                # 准备数据
                                for row in rows:
                                    values = [row[col] for col in column_names]
                                    try:
                                        dst_cursor.execute(insert_sql, values)
                                    except sqlite3.IntegrityError as e:
                                        logger.warning(f"插入数据到表 {table} 时出现完整性错误: {str(e)}")
                                        # 如果是主键冲突，尝试更新而不是插入
                                        if "UNIQUE constraint failed" in str(e):
                                            # 假设第一列是主键
                                            pk_col = column_names[0]
                                            update_cols = [col for col in column_names if col != pk_col]
                                            if update_cols:
                                                update_sql = f"UPDATE {table} SET "
                                                update_sql += ", ".join([f"{col} = ?" for col in update_cols])
                                                update_sql += f" WHERE {pk_col} = ?"
                                                
                                                # 准备更新值（不包括主键）+ 主键作为WHERE条件
                                                update_values = [row[col] for col in update_cols]
                                                update_values.append(row[pk_col])
                                                
                                                dst_cursor.execute(update_sql, update_values)
                                    except Exception as e:
                                        logger.error(f"插入数据到表 {table} 时出错: {str(e)}")
                                
                                # 提交每一批
                                dst_conn.commit()
                                
                                # 更新偏移量
                                offset += batch_size
                                logger.info(f"已复制表 {table} 的 {offset} 行数据")
                                
                                # 如果读取的行数小于批量大小，说明已经复制完所有数据
                                if len(rows) < batch_size:
                                    break
                        
                            # 创建索引（如果有）
                            src_cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name=? AND sql IS NOT NULL", (table,))
                            indexes = src_cursor.fetchall()
                            
                            for index in indexes:
                                try:
                                    # 跳过与主键相关的自动索引
                                    if "sqlite_autoindex" not in index['sql']:
                                        dst_cursor.execute(index['sql'])
                                        logger.info(f"已创建索引: {index['sql']}")
                                except Exception as e:
                                    logger.warning(f"创建索引时出错: {str(e)}")
                            
                            logger.info(f"成功完整复制表 {table} 数据({len(rows)}行)")
                        
                        except Exception as e:
                            logger.warning(f"复制保护表 {table} 时出错: {str(e)}")
                        else:
                            logger.warning(f"复制保护表 {table} 时出错: no such table: {table}")
                    
                    except Exception as e:
                        logger.error(f"处理表 {table} 时出错: {str(e)}")
                        # 继续处理其他表
                
                # 最终提交
                dst_conn.commit()
                logger.info("所有保护表备份完成")
                return True
                
            except Exception as e:
                logger.error(f"备份保护表过程中出错: {str(e)}")
                return False
                
        except Exception as e:
            logger.error(f"备份保护表过程中发生未预期错误: {str(e)}")
            return False

    def create_post_ranking_table(self, conn):
        """创建帖子排行表"""
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS post_ranking (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT,
            author TEXT,
            author_link TEXT,
            thread_id TEXT,
            post_time TIMESTAMP,
            重发 INTEGER DEFAULT 0,
            回帖 INTEGER DEFAULT 0,
            翻回帖 INTEGER DEFAULT 0,
            帖龄 INTEGER DEFAULT 0,
            活跃 INTEGER DEFAULT 0,
            关注 INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(url)
        )
        ''')
        conn.commit()

    def import_post_ranking_data(self):
        """导入帖子排行数据"""
        try:
            # 获取文件路径
            file_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 
                                    "data/processed/post_ranking.csv")
            
            if not os.path.exists(file_path):
                logger.warning(f"帖子排行数据文件不存在: {file_path}")
                return False
            
            # 读取CSV文件
            df = pd.read_csv(file_path)
            
            # 确保数值列为整数类型
            numeric_columns = ['重发', '回帖', '翻回帖', '帖龄', '活跃', '关注']
            for col in numeric_columns:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
            
            # 准备数据
            records = []
            for _, row in df.iterrows():
                record = (
                    row['url'] if pd.notna(row.get('url')) else None,
                    row['title'] if pd.notna(row.get('title')) else None,
                    row['author'] if pd.notna(row.get('author')) else None,
                    row['author_link'] if pd.notna(row.get('author_link')) else None,
                    row['thread_id'] if pd.notna(row.get('thread_id')) else None,
                    row['post_time'] if pd.notna(row.get('post_time')) else None,
                    int(row['重发']) if pd.notna(row.get('重发')) else 0,
                    int(row['回帖']) if pd.notna(row.get('回帖')) else 0,
                    int(row['翻回帖']) if pd.notna(row.get('翻回帖')) else 0,
                    int(row['帖龄']) if pd.notna(row.get('帖龄')) else 0,
                    int(row['活跃']) if pd.notna(row.get('活跃')) else 0,
                    int(row['关注']) if pd.notna(row.get('关注')) else 0
                )
                records.append(record)
            
            # 连接数据库
            conn = sqlite3.connect(self.temp_db_path)
            cursor = conn.cursor()
            
            # 创建表
            self.create_post_ranking_table(conn)
            
            # 清空现有数据
            cursor.execute("DELETE FROM post_ranking")
            
            # 批量插入数据
            cursor.executemany("""
                INSERT INTO post_ranking (
                    url, title, author, author_link, thread_id, post_time,
                    重发, 回帖, 翻回帖, 帖龄, 活跃, 关注
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, records)
            
            conn.commit()
            conn.close()
            
            logger.info(f"成功导入 {len(records)} 条帖子排行数据")
            return True
        except Exception as e:
            logger.error(f"导入帖子排行数据失败: {str(e)}")
            return False

# 主函数
def main():
    """主函数"""
    try:
        # 获取命令行参数
        parser = argparse.ArgumentParser(description='更新SQLite数据库')
        
        # 获取项目根目录的绝对路径
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        default_db_path = os.path.join(project_root, "backend/db/forum_data.db")
        default_sql_dir = os.path.join(project_root, "backend/sql")
        
        parser.add_argument('--db-path', type=str, help='数据库文件路径', default=default_db_path)
        parser.add_argument('--sql-dir', type=str, help='SQL脚本目录', default=default_sql_dir)
        parser.add_argument('--import-car-info', action='store_true', help='导入车辆信息数据')
        parser.add_argument('--only-car-info', action='store_true', help='只导入车辆信息数据而不更新其他表')
        args = parser.parse_args()
        
        # 允许从环境变量设置数据库路径
        db_path = os.environ.get('DATABASE_PATH', args.db_path)
        sql_dir = args.sql_dir
        
        # 初始化数据库更新器
        updater = DatabaseUpdater(db_path)
        
        # 如果只需要导入车辆信息
        if args.only_car_info:
            logger.info("只导入车辆信息数据")
            if updater.import_car_info_data():
                logger.info("车辆信息导入完成")
                return 0
            else:
                logger.error("车辆信息导入失败")
                return 1
        
        # 执行完整的数据库更新
        # 创建临时数据库
        if not updater.create_temp_database():
            logger.error("创建临时数据库失败，更新终止")
            return 1
        
        # 执行SQL脚本
        sql_files = []
        if os.path.exists(sql_dir):
            sql_files = sorted([os.path.join(sql_dir, f) for f in os.listdir(sql_dir) if f.endswith('.sql')])
        
        if sql_files:
            for sql_file in sql_files:
                if not updater.execute_sql_on_temp(sql_file):
                    logger.error(f"执行SQL文件失败: {sql_file}")
                    return 1
            logger.info(f"已执行 {len(sql_files)} 个SQL文件")
        else:
            logger.warning(f"SQL目录不存在或没有SQL文件: {sql_dir}")
        
        # 获取项目根目录的绝对路径
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        
        # 导入Excel和CSV数据
        excel_files = {
            "posts": os.path.join(project_root, "data/processed/post.xlsx"),
            "list": os.path.join(project_root, "data/processed/update.xlsx"),
            "detail": os.path.join(project_root, "data/processed/detail.xlsx")
        }
        
        csv_files = {
            "post_history": os.path.join(project_root, "data/processed/action.csv"),
            "import": os.path.join(project_root, "data/processed/import.csv"),
            "author_ranking": os.path.join(project_root, "data/processed/author_ranking.csv"),
            "post_ranking": os.path.join(project_root, "data/processed/post_ranking.csv")
        }
        
        # 导入Excel文件
        for table, file_path in excel_files.items():
            if not updater.import_excel_to_temp(file_path, table):
                logger.warning(f"导入Excel失败: {file_path} -> {table}")
        
        # 导入CSV文件
        for table, file_path in csv_files.items():
            if not updater.import_csv_to_temp(file_path, table):
                logger.warning(f"导入CSV失败: {file_path} -> {table}")
        
        # 替换数据库
        if not updater.replace_database():
            logger.error("替换数据库失败，更新终止")
            return 1
        
        # 最后导入car_info数据，这样可以确保不会影响其他表
        if args.import_car_info or os.path.exists(os.path.join(project_root, "data/processed/car_info.csv")):
            logger.info("导入车辆信息数据")
            if not updater.import_car_info_data():
                logger.warning("导入车辆信息数据失败")
        
        logger.info("数据库更新完成")
        return 0
    except Exception as e:
        logger.error(f"数据库更新过程中发生未预期错误: {str(e)}")
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    main() 