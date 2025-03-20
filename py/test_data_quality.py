import sqlite3
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import json
import sys
import logging

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('data_quality_test.log', encoding='utf-8')
    ]
)

class DataQualityTest:
    def __init__(self):
        self.BASE_DIR = Path(__file__).parent.parent
        self.DB_PATH = self.BASE_DIR / 'backend' / 'db' / 'forum_data.db'
        logging.info(f"数据库路径: {self.DB_PATH}")
        
        if not self.DB_PATH.exists():
            raise FileNotFoundError(f"数据库文件不存在: {self.DB_PATH}")
        
        self.report_data = {
            'test_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_tests': 0,
            'passed_tests': 0,
            'failed_tests': 0,
            'critical_failures': 0,
            'warnings': 0,
            'test_results': []
        }
    
    def connect_db(self):
        """连接数据库"""
        try:
            conn = sqlite3.connect(str(self.DB_PATH))
            logging.info("成功连接到数据库")
            return conn
        except sqlite3.Error as e:
            logging.error(f"连接数据库失败: {e}")
            raise
    
    def add_test_result(self, test_name, status, message, details=None, is_critical=False):
        """添加测试结果"""
        result = {
            'test_name': test_name,
            'status': status,
            'message': message,
            'details': details,
            'is_critical': is_critical
        }
        self.report_data['test_results'].append(result)
        self.report_data['total_tests'] += 1
        if status == 'PASS':
            self.report_data['passed_tests'] += 1
        elif status == 'FAIL':
            self.report_data['failed_tests'] += 1
            if is_critical:
                self.report_data['critical_failures'] += 1
        elif status == 'WARNING':
            self.report_data['warnings'] += 1
    
    def test_table_existence(self, conn):
        """测试所有必需表是否存在"""
        print("\n测试表存在性...")
        required_tables = [
            'post_action', 'post_statistic', 'update_statistic', 'view_statistic',
            'post_ranking', 'author_ranking', 'thread_follow', 'post_history',
            'author_history', 'car_detail', 'thread_history'
        ]
        
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        existing_tables = [row[0] for row in cursor.fetchall()]
        
        missing_tables = [table for table in required_tables if table not in existing_tables]
        
        if not missing_tables:
            self.add_test_result('表存在性测试', 'PASS', '所有必需的表都存在', is_critical=True)
        else:
            self.add_test_result('表存在性测试', 'FAIL', f'缺少以下表：{", ".join(missing_tables)}', is_critical=True)
    
    def test_required_fields(self, conn):
        """测试必需字段是否存在"""
        print("\n测试必需字段...")
        
        required_fields = {
            'all': ['url', 'title', 'author', 'author_link', 'created_at', 'updated_at'],
            'post_ranking': ['days_old', 'last_active', 'read_count', 'reply_count'],
            'thread_follow': ['days_old', 'last_active', 'read_count', 'reply_count'],
            'author_ranking': ['days_old', 'last_active', 'active_posts']
        }
        
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [row[1] for row in cursor.fetchall()]
            
            # 检查通用必需字段
            if table_name in ['post_ranking', 'author_ranking', 'thread_follow']:
                missing_common = [field for field in required_fields['all'] 
                                if field not in columns]
                
                # 检查特定表的必需字段
                if table_name in required_fields:
                    missing_specific = [field for field in required_fields[table_name] 
                                      if field not in columns]
                    missing_common.extend(missing_specific)
                
                if missing_common:
                    self.add_test_result(
                        f'字段完整性测试 - {table_name}',
                        'FAIL',
                        f'表 {table_name} 缺少以下字段：{", ".join(missing_common)}',
                        is_critical=True  # 必需字段缺失是关键错误
                    )
                else:
                    self.add_test_result(
                        f'字段完整性测试 - {table_name}',
                        'PASS',
                        f'表 {table_name} 包含所有必需字段',
                        is_critical=True
                    )
    
    def test_data_consistency(self, conn):
        """测试数据一致性"""
        print("\n测试数据一致性...")
        
        cursor = conn.cursor()
        
        # 检查car_detail表是否存在
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='car_detail'")
        car_detail_exists = cursor.fetchone() is not None
        
        if car_detail_exists:
            # 测试url一致性
            cursor.execute("""
                SELECT DISTINCT p.url 
                FROM post_ranking p
                LEFT JOIN car_detail c ON p.url = c.url
                WHERE c.url IS NULL
            """)
            inconsistent_threads = cursor.fetchall()
            
            if inconsistent_threads:
                self.add_test_result(
                    '数据一致性测试 - url',
                    'WARNING',
                    f'发现 {len(inconsistent_threads)} 个帖子在post_ranking中存在但在car_detail中不存在',
                    {'inconsistent_threads': [row[0] for row in inconsistent_threads[:5]]}
                )
            else:
                self.add_test_result(
                    '数据一致性测试 - url',
                    'PASS',
                    'post_ranking和car_detail的url完全匹配'
                )
        else:
            # car_detail表不存在，跳过相关检查
            self.add_test_result(
                '数据一致性测试 - car_detail',
                'WARNING',
                'car_detail表不存在，跳过相关一致性检查'
            )
        
        # 测试author一致性
        cursor.execute("""
            SELECT DISTINCT p.author
            FROM post_ranking p
            LEFT JOIN author_ranking a ON p.author = a.author
            WHERE a.author IS NULL
        """)
        inconsistent_authors = cursor.fetchall()
        
        if inconsistent_authors:
            self.add_test_result(
                '数据一致性测试 - author',
                'WARNING',
                f'发现 {len(inconsistent_authors)} 个作者在post_ranking中存在但在author_ranking中不存在',
                {'inconsistent_authors': [row[0] for row in inconsistent_authors[:5]]}
            )
        else:
            self.add_test_result(
                '数据一致性测试 - author',
                'PASS',
                'post_ranking和author_ranking的author完全匹配'
            )
    
    def test_data_validity(self, conn):
        """测试数据有效性"""
        print("\n测试数据有效性...")
        
        # 检查car_detail表是否存在
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='car_detail'")
        car_detail_exists = cursor.fetchone() is not None
        
        # 测试数值字段的有效性
        numeric_tests = [
            ("SELECT COUNT(*) FROM post_ranking WHERE days_old < 0", "post_ranking.days_old"),
            ("SELECT COUNT(*) FROM post_ranking WHERE last_active < 0", "post_ranking.last_active"),
            ("SELECT COUNT(*) FROM author_ranking WHERE days_old < 0", "author_ranking.days_old"),
            ("SELECT COUNT(*) FROM author_ranking WHERE last_active < 0", "author_ranking.last_active"),
            ("SELECT COUNT(*) FROM post_ranking WHERE read_count < 0", "post_ranking.read_count"),
            ("SELECT COUNT(*) FROM post_ranking WHERE reply_count < 0", "post_ranking.reply_count")
        ]
        
        # 添加car_detail表的测试，如果表存在
        if car_detail_exists:
            numeric_tests.extend([
                ("SELECT COUNT(*) FROM car_detail WHERE price < 0", "car_detail.price"),
                ("SELECT COUNT(*) FROM car_detail WHERE miles < 0", "car_detail.miles"),
                ("SELECT COUNT(*) FROM car_detail WHERE year < 1900 OR year > 2100", "car_detail.year")
            ])
        
        cursor = conn.cursor()
        for query, field_name in numeric_tests:
            try:
                cursor.execute(query)
                invalid_count = cursor.fetchone()[0]
                
                if invalid_count > 0:
                    self.add_test_result(
                        f'数值有效性测试 - {field_name}',
                        'WARNING',
                        f'发现 {invalid_count} 条无效数据',
                        {'field': field_name, 'invalid_count': invalid_count}
                    )
                else:
                    self.add_test_result(
                        f'数值有效性测试 - {field_name}',
                        'PASS',
                        f'{field_name} 的所有值都有效'
                    )
            except sqlite3.OperationalError:
                self.add_test_result(
                    f'数值有效性测试 - {field_name}',
                    'WARNING',
                    f'无法测试字段 {field_name}，可能不存在'
                )
        
        # 测试日期时间字段的有效性
        datetime_tests = [
            ("SELECT COUNT(*) FROM post_history WHERE action_time > datetime('now')", "post_history.action_time"),
            ("SELECT COUNT(*) FROM author_history WHERE action_time > datetime('now')", "author_history.action_time"),
            ("SELECT COUNT(*) FROM post_ranking WHERE created_at > datetime('now')", "post_ranking.created_at"),
            ("SELECT COUNT(*) FROM post_ranking WHERE updated_at > datetime('now')", "post_ranking.updated_at")
        ]
        
        for query, field_name in datetime_tests:
            try:
                cursor.execute(query)
                invalid_count = cursor.fetchone()[0]
                
                if invalid_count > 0:
                    self.add_test_result(
                        f'时间有效性测试 - {field_name}',
                        'WARNING',
                        f'发现 {invalid_count} 条未来时间',
                        {'field': field_name, 'invalid_count': invalid_count}
                    )
                else:
                    self.add_test_result(
                        f'时间有效性测试 - {field_name}',
                        'PASS',
                        f'{field_name} 的所有时间都有效'
                    )
            except sqlite3.OperationalError:
                self.add_test_result(
                    f'时间有效性测试 - {field_name}',
                    'WARNING',
                    f'无法测试字段 {field_name}，可能不存在'
                )
    
    def test_data_completeness(self, conn):
        """测试数据完整性"""
        print("\n测试数据完整性...")
        
        # 检查car_detail表是否存在
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='car_detail'")
        car_detail_exists = cursor.fetchone() is not None
        
        # 测试必填字段是否有空值
        required_field_tests = [
            ("SELECT COUNT(*) FROM post_ranking WHERE url IS NULL OR url = ''", "post_ranking.url"),
            ("SELECT COUNT(*) FROM post_ranking WHERE author IS NULL OR author = ''", "post_ranking.author"),
            ("SELECT COUNT(*) FROM author_ranking WHERE author IS NULL OR author = ''", "author_ranking.author")
        ]
        
        # 添加car_detail表的测试，如果表存在
        if car_detail_exists:
            required_field_tests.extend([
                ("SELECT COUNT(*) FROM car_detail WHERE url IS NULL OR url = ''", "car_detail.url"),
                ("SELECT COUNT(*) FROM car_detail WHERE author IS NULL OR author = ''", "car_detail.author")
            ])
        
        cursor = conn.cursor()
        for query, field_name in required_field_tests:
            try:
                cursor.execute(query)
                null_count = cursor.fetchone()[0]
                
                if null_count > 0:
                    self.add_test_result(
                        f'数据完整性测试 - {field_name}',
                        'FAIL',
                        f'发现 {null_count} 条空值',
                        {'field': field_name, 'null_count': null_count},
                        is_critical=True  # 必填字段为空是关键错误
                    )
                else:
                    self.add_test_result(
                        f'数据完整性测试 - {field_name}',
                        'PASS',
                        f'{field_name} 没有空值',
                        is_critical=True
                    )
            except sqlite3.OperationalError:
                self.add_test_result(
                    f'数据完整性测试 - {field_name}',
                    'WARNING',
                    f'无法测试字段 {field_name}，可能不存在'
                )
    
    def test_data_trends(self, conn):
        """测试数据趋势"""
        print("\n测试数据趋势...")
        
        cursor = conn.cursor()
        
        # 测试发帖量趋势
        try:
            cursor.execute("""
                SELECT date(action_time) as post_date, COUNT(*) as post_count
                FROM post_action
                WHERE action_type = 'post'
                GROUP BY post_date
                ORDER BY post_date DESC
                LIMIT 7
            """)
            post_trends = cursor.fetchall()
            
            if post_trends:
                avg_posts = sum(row[1] for row in post_trends) / len(post_trends)
                max_posts = max(row[1] for row in post_trends)
                min_posts = min(row[1] for row in post_trends)
                
                if max_posts > avg_posts * 2 or min_posts < avg_posts * 0.5:
                    self.add_test_result(
                        '数据趋势测试 - 发帖量',
                        'WARNING',
                        '发帖量存在异常波动',
                        {
                            'average': avg_posts,
                            'max': max_posts,
                            'min': min_posts,
                            'trend': [{'date': row[0], 'count': row[1]} for row in post_trends]
                        }
                    )
                else:
                    self.add_test_result(
                        '数据趋势测试 - 发帖量',
                        'PASS',
                        '发帖量趋势正常'
                    )
            else:
                self.add_test_result(
                    '数据趋势测试 - 发帖量',
                    'WARNING',
                    '没有发帖量数据'
                )
        except sqlite3.OperationalError:
            self.add_test_result(
                '数据趋势测试 - 发帖量',
                'WARNING',
                '无法测试发帖量趋势，可能表或字段不存在'
            )
    
    def test_index_effectiveness(self, conn):
        """测试索引有效性"""
        print("\n测试索引有效性...")
        
        cursor = conn.cursor()
        
        # 获取所有表
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = cursor.fetchall()
        
        for table in tables:
            table_name = table[0]
            
            # 获取表的索引
            cursor.execute(f"SELECT name, sql FROM sqlite_master WHERE type='index' AND tbl_name='{table_name}'")
            indexes = cursor.fetchall()
            
            if not indexes:
                self.add_test_result(
                    f'索引测试 - {table_name}',
                    'WARNING',  # 索引缺失是警告级别
                    f'表 {table_name} 没有索引'
                )
                continue
            
            # 检查重要字段是否有索引
            important_fields = ['url', 'title', 'author', 'author_link', 'action_time', 'created_at', 'updated_at']
            indexed_fields = []
            for idx in indexes:
                if idx[1]:  # 如果索引定义不为空
                    for field in important_fields:
                        if field in idx[1].lower():
                            indexed_fields.append(field)
            
            missing_indexes = [f for f in important_fields if f not in indexed_fields]
            
            if missing_indexes:
                self.add_test_result(
                    f'索引测试 - {table_name}',
                    'WARNING',  # 索引缺失是警告级别
                    f'表 {table_name} 缺少以下字段的索引：{", ".join(missing_indexes)}',
                    {'existing_indexes': [idx[0] for idx in indexes]}
                )
            else:
                self.add_test_result(
                    f'索引测试 - {table_name}',
                    'PASS',
                    f'表 {table_name} 的所有重要字段都有索引'
                )
    
    def generate_report(self):
        """生成测试报告"""
        print("\n生成测试报告...")
        
        report_time = datetime.now().strftime('%Y%m%d_%H%M%S')
        report_file = self.BASE_DIR / 'data' / 'reports' / f'data_quality_report_{report_time}.json'
        report_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 添加总结信息
        self.report_data['summary'] = {
            'pass_rate': f"{(self.report_data['passed_tests'] / self.report_data['total_tests'] * 100):.2f}%",
            'total_issues': self.report_data['failed_tests'] + self.report_data['warnings'],
            'critical_failures': self.report_data['critical_failures']  # 添加关键失败数
        }
        
        # 保存报告
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(self.report_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n测试报告已保存到：{report_file}")
        print(f"总测试数: {self.report_data['total_tests']}")
        print(f"通过测试: {self.report_data['passed_tests']}")
        print(f"失败测试: {self.report_data['failed_tests']}")
        print(f"关键失败: {self.report_data['critical_failures']}")  # 添加关键失败数显示
        print(f"警告数: {self.report_data['warnings']}")
        print(f"通过率: {self.report_data['summary']['pass_rate']}")
    
    def run_all_tests(self):
        """运行所有测试"""
        try:
            logging.info("开始运行测试...")
            conn = self.connect_db()
            
            # 运行所有测试
            test_functions = [
                self.test_table_existence,
                self.test_required_fields,
                self.test_data_consistency,
                self.test_data_validity,
                self.test_data_completeness,
                self.test_index_effectiveness,
                self.test_data_trends
            ]
            
            for test_func in test_functions:
                try:
                    logging.info(f"执行测试: {test_func.__name__}")
                    test_func(conn)
                except Exception as e:
                    logging.error(f"测试 {test_func.__name__} 失败: {e}")
                    self.add_test_result(
                        test_func.__name__,
                        'FAIL',
                        f'测试执行出错: {str(e)}',
                        is_critical=True
                    )
            
            # 生成报告
            self.generate_report()
            
            conn.close()
            logging.info("测试完成")
            
            # 只有关键测试失败时才返回非零值
            return 1 if self.report_data['critical_failures'] > 0 else 0
            
        except Exception as e:
            logging.error(f"测试过程中出错: {e}")
            return 1

def main():
    """主函数"""
    try:
        tester = DataQualityTest()
        exit_code = tester.run_all_tests()
        sys.exit(exit_code)
    except Exception as e:
        logging.error(f"程序执行出错: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 