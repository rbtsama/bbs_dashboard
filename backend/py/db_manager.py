#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
数据库管理类
提供增强的数据库管理功能，包括：
- 数据库备份和恢复
- 保护表数据迁移
- 数据库替换增强功能
- 错误处理和重试机制
"""

import os
import sys
import sqlite3
import logging
import shutil
import time
import json
import gc
from pathlib import Path
from datetime import datetime
import threading

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(os.path.join(os.path.dirname(__file__), '../logs/db_manager.log'), encoding='utf-8')
    ]
)
logger = logging.getLogger('db_manager')

class DBManager:
    """数据库管理类，提供增强的数据库管理功能"""
    
    def __init__(self, db_path=None, backup_dir=None):
        """初始化数据库管理器"""
        # 获取项目根目录
        self.project_root = Path(__file__).parent.parent.absolute()
        
        # 设置数据库路径
        self.db_path = db_path or os.path.join(self.project_root, "db/forum_data.db")
        
        # 设置临时数据库路径
        self.temp_db_path = os.path.join(self.project_root, "db/temp_forum_data.db")
        
        # 设置备份目录
        self.backup_dir = backup_dir or os.path.join(self.project_root, "db/backups")
        
        # 确保目录存在
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        os.makedirs(self.backup_dir, exist_ok=True)
        os.makedirs(os.path.join(self.project_root, "logs"), exist_ok=True)
        
        # 设置保护表列表
        self.protected_tables = ['wordcloud_cache', 'user_data', 'db_maintenance_log']
        
        # 设置待删除文件列表，用于延迟删除
        self._pending_delete_files = []
        
        # 待删除文件的清理线程
        self._cleaner_thread = None
    
    def backup_database(self, backup_path=None):
        """备份数据库"""
        # 如果没有指定备份路径，使用时间戳生成
        if not backup_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = os.path.join(self.backup_dir, f"forum_data_backup_{timestamp}.db")
        
        try:
            # 确保数据库存在
            if not os.path.exists(self.db_path):
                logger.error(f"数据库文件不存在，无法备份: {self.db_path}")
                return False
            
            # 复制数据库文件
            shutil.copy2(self.db_path, backup_path)
            logger.info(f"数据库备份成功: {backup_path}")
            
            # 记录备份操作
            self._log_maintenance_action('备份数据库', '完成', f'备份文件: {backup_path}')
            
            # 清理旧备份
            self._cleanup_old_backups()
            
            return backup_path
        except Exception as e:
            logger.error(f"备份数据库时出错: {str(e)}")
            self._log_maintenance_action('备份数据库', '失败', error_message=str(e))
            return False
    
    def _cleanup_old_backups(self, max_backups=10):
        """清理旧备份，只保留最新的几个"""
        try:
            # 获取所有备份文件
            backup_files = [f for f in os.listdir(self.backup_dir) 
                           if f.startswith('forum_data_backup_') and f.endswith('.db')]
            
            # 按修改时间排序
            backup_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.backup_dir, x)), reverse=True)
            
            # 删除旧备份
            for old_file in backup_files[max_backups:]:
                old_path = os.path.join(self.backup_dir, old_file)
                os.remove(old_path)
                logger.info(f"删除旧备份: {old_path}")
            
            return True
        except Exception as e:
            logger.error(f"清理旧备份时出错: {str(e)}")
            return False
    
    def restore_database(self, backup_path=None):
        """从备份恢复数据库"""
        try:
            # 如果没有指定备份路径，使用最新的备份
            if not backup_path:
                backup_files = [f for f in os.listdir(self.backup_dir) 
                               if f.startswith('forum_data_backup_') and f.endswith('.db')]
                
                if not backup_files:
                    logger.error("没有找到可用的备份文件")
                    return False
                
                # 按修改时间排序，获取最新的备份
                backup_files.sort(key=lambda x: os.path.getmtime(os.path.join(self.backup_dir, x)), reverse=True)
                backup_path = os.path.join(self.backup_dir, backup_files[0])
            
            # 确保备份文件存在
            if not os.path.exists(backup_path):
                logger.error(f"备份文件不存在: {backup_path}")
                return False
            
            # 备份当前数据库（防止恢复操作出错）
            current_backup = self.backup_database()
            
            # 使用安全的替换方式
            # 先复制到临时位置
            temp_restore_path = f"{self.db_path}.restore_temp"
            shutil.copy2(backup_path, temp_restore_path)
            
            # 替换当前数据库
            try:
                os.replace(temp_restore_path, self.db_path)
            except PermissionError:
                # 如果出现权限错误，可能是文件正在使用中
                # 尝试先关闭所有可能的连接
                gc.collect()  # 尝试回收未关闭的连接
                time.sleep(1)  # 等待1秒
                os.replace(temp_restore_path, self.db_path)
            
            logger.info(f"数据库从备份恢复成功: {backup_path}")
            self._log_maintenance_action('恢复数据库', '完成', f'使用备份: {backup_path}')
            return True
        except Exception as e:
            logger.error(f"从备份恢复数据库时出错: {str(e)}")
            self._log_maintenance_action('恢复数据库', '失败', error_message=str(e))
            return False
    
    def migrate_protected_tables(self, source_db, target_db):
        """迁移保护表数据"""
        try:
            # 确保源数据库和目标数据库都存在
            if not os.path.exists(source_db):
                logger.error(f"源数据库不存在: {source_db}")
                return False
            
            if not os.path.exists(target_db):
                logger.error(f"目标数据库不存在: {target_db}")
                return False
            
            # 连接数据库
            src_conn = sqlite3.connect(source_db)
            src_cursor = src_conn.cursor()
            
            target_conn = sqlite3.connect(target_db)
            target_cursor = target_conn.cursor()
            
            # 对每个保护表进行迁移
            migration_results = {}
            
            for table in self.protected_tables:
                try:
                    # 检查源数据库是否存在该表
                    src_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                    if not src_cursor.fetchone():
                        logger.warning(f"源数据库中不存在表 {table}，跳过")
                        migration_results[table] = {'status': '警告', 'message': '源表不存在'}
                        continue
                    
                    # 检查目标数据库是否存在该表
                    target_cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                    if not target_cursor.fetchone():
                        # 如果目标数据库不存在该表，则创建
                        logger.info(f"目标数据库中不存在表 {table}，创建结构")
                        
                        # 获取表结构
                        src_cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='table' AND name='{table}'")
                        create_table_sql = src_cursor.fetchone()[0]
                        
                        # 在目标数据库创建表
                        target_cursor.execute(create_table_sql)
                        target_conn.commit()
                        
                        # 获取表上的索引
                        src_cursor.execute(f"SELECT sql FROM sqlite_master WHERE type='index' AND tbl_name='{table}'")
                        index_sql_list = src_cursor.fetchall()
                        
                        # 在目标数据库创建索引
                        for index_sql in index_sql_list:
                            if index_sql[0] and 'AUTOINDEX' not in index_sql[0]:
                                target_cursor.execute(index_sql[0])
                        
                        target_conn.commit()
                    
                    # 获取源表中的所有数据
                    src_cursor.execute(f"SELECT * FROM {table}")
                    rows = src_cursor.fetchall()
                    
                    if not rows:
                        logger.info(f"表 {table} 中没有数据，跳过迁移")
                        migration_results[table] = {'status': '完成', 'message': '无数据需要迁移'}
                        continue
                    
                    # 获取列名
                    src_cursor.execute(f"PRAGMA table_info({table})")
                    columns = [col[1] for col in src_cursor.fetchall()]
                    
                    # 先清空目标表数据
                    target_cursor.execute(f"DELETE FROM {table}")
                    
                    # 构建插入语句
                    placeholders = ', '.join(['?' for _ in columns])
                    insert_sql = f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({placeholders})"
                    
                    # 批量插入数据
                    target_cursor.executemany(insert_sql, rows)
                    target_conn.commit()
                    
                    logger.info(f"表 {table} 数据迁移成功，共 {len(rows)} 条记录")
                    migration_results[table] = {'status': '完成', 'message': f'迁移 {len(rows)} 条记录'}
                except Exception as e:
                    logger.error(f"迁移表 {table} 时出错: {str(e)}")
                    migration_results[table] = {'status': '失败', 'message': str(e)}
            
            # 关闭连接
            src_conn.close()
            target_conn.close()
            
            # 记录迁移结果
            self._log_maintenance_action('迁移保护表', '完成', f'迁移结果: {json.dumps(migration_results)}')
            
            return migration_results
        except Exception as e:
            logger.error(f"迁移保护表时出错: {str(e)}")
            self._log_maintenance_action('迁移保护表', '失败', error_message=str(e))
            return False
    
    def replace_database(self):
        """使用临时数据库替换当前数据库，增强的容错版本"""
        # 先备份当前数据库
        backup_path = self.backup_database()
        if not backup_path:
            logger.error("备份当前数据库失败，取消替换操作")
            return False
        
        # 检查临时数据库是否存在
        if not os.path.exists(self.temp_db_path):
            logger.error(f"临时数据库不存在: {self.temp_db_path}")
            return False
        
        # 迁移保护表数据
        migration_result = self.migrate_protected_tables(self.db_path, self.temp_db_path)
        if not migration_result:
            logger.error("迁移保护表失败，取消替换操作")
            return False
        
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
                self._log_maintenance_action('替换数据库', '完成', f'使用临时数据库: {self.temp_db_path}')
                
                # 安排延迟删除临时文件
                self._schedule_delayed_delete(temp_db_copy)
                self._schedule_delayed_delete(self.temp_db_path)
                
                return True
            except (IOError, PermissionError) as e:
                error_msg = f"尝试 {attempt}/{max_attempts} 替换数据库时出现IO错误: {str(e)}"
                logger.warning(error_msg)
                
                if attempt == max_attempts:
                    logger.error(f"替换数据库失败，达到最大尝试次数: {str(e)}")
                    logger.info("尝试恢复原始数据库...")
                    
                    # 尝试恢复原始数据库
                    restore_result = self.restore_database(backup_path)
                    if restore_result:
                        logger.info("成功恢复到原始数据库")
                    else:
                        logger.error("恢复原始数据库失败")
                    
                    self._log_maintenance_action('替换数据库', '失败', error_message=error_msg)
                    return False
                
                # 等待一段时间后重试
                time.sleep(2 * attempt)  # 递增等待时间
            except Exception as e:
                error_msg = f"替换数据库时出现未知错误: {str(e)}"
                logger.error(error_msg)
                self._log_maintenance_action('替换数据库', '失败', error_message=error_msg)
                
                # 尝试恢复原始数据库
                logger.info("尝试恢复原始数据库...")
                restore_result = self.restore_database(backup_path)
                if restore_result:
                    logger.info("成功恢复到原始数据库")
                else:
                    logger.error("恢复原始数据库失败")
                
                return False
    
    def _schedule_delayed_delete(self, file_path):
        """安排延迟删除文件，避免文件锁定问题"""
        self._pending_delete_files.append(file_path)
        
        # 如果清理线程不存在或已经结束，创建新线程
        if not self._cleaner_thread or not self._cleaner_thread.is_alive():
            self._cleaner_thread = threading.Thread(target=self._delayed_delete_worker)
            self._cleaner_thread.daemon = True
            self._cleaner_thread.start()
    
    def _delayed_delete_worker(self):
        """执行延迟删除任务的工作线程"""
        # 等待一段时间，确保文件不再被使用
        time.sleep(10)
        
        files_to_delete = self._pending_delete_files.copy()
        self._pending_delete_files.clear()
        
        for file_path in files_to_delete:
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    logger.info(f"延迟删除文件成功: {file_path}")
            except Exception as e:
                logger.warning(f"延迟删除文件失败: {file_path}, 错误: {str(e)}")
    
    def _log_maintenance_action(self, operation_type, status, details=None, error_message=None):
        """记录维护操作到数据库日志表"""
        try:
            # 尝试连接数据库
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 检查是否存在维护记录表
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='db_maintenance_log'")
            if not cursor.fetchone():
                logger.warning("数据库中不存在维护记录表，无法记录操作")
                conn.close()
                return False
            
            # 记录操作
            insert_sql = """
            INSERT INTO db_maintenance_log 
            (operation_type, start_time, end_time, status, details, error_message) 
            VALUES (?, ?, ?, ?, ?, ?)
            """
            
            cursor.execute(
                insert_sql, 
                (operation_type, 
                 datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # 开始时间
                 datetime.now().strftime('%Y-%m-%d %H:%M:%S'),  # 结束时间
                 status, 
                 details,
                 error_message)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            logger.error(f"记录维护操作时出错: {str(e)}")
            return False
    
    def verify_database_integrity(self):
        """验证数据库完整性"""
        try:
            # 尝试连接数据库
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # 执行PRAGMA integrity_check
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            integrity_ok = result[0] == 'ok'
            
            # 检查表是否存在
            table_count = 0
            cursor.execute("SELECT count(*) FROM sqlite_master WHERE type='table'")
            table_count = cursor.fetchone()[0]
            
            # 检查保护表是否存在
            missing_protected_tables = []
            for table in self.protected_tables:
                cursor.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name='{table}'")
                if not cursor.fetchone():
                    missing_protected_tables.append(table)
            
            conn.close()
            
            # 记录验证结果
            details = {
                'integrity_check': 'ok' if integrity_ok else '失败',
                'table_count': table_count,
                'missing_protected_tables': missing_protected_tables
            }
            
            status = '完成' if integrity_ok and not missing_protected_tables else '警告'
            
            self._log_maintenance_action('验证数据库完整性', status, json.dumps(details))
            
            return {
                'integrity_ok': integrity_ok,
                'table_count': table_count,
                'missing_protected_tables': missing_protected_tables
            }
        except Exception as e:
            error_msg = f"验证数据库完整性时出错: {str(e)}"
            logger.error(error_msg)
            self._log_maintenance_action('验证数据库完整性', '失败', error_message=error_msg)
            return {
                'integrity_ok': False,
                'error': str(e)
            }

if __name__ == "__main__":
    # 测试数据库管理器
    db_manager = DBManager()
    
    # 验证数据库完整性
    integrity_result = db_manager.verify_database_integrity()
    print(f"数据库完整性检查结果: {integrity_result}")
    
    # 备份数据库
    backup_path = db_manager.backup_database()
    if backup_path:
        print(f"备份成功: {backup_path}")
    else:
        print("备份失败") 