import os

# 数据库配置
DATABASE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'db', 'forum_data.db')

# 数据库错误重试配置
DB_RETRY_COUNT = 3
DB_RETRY_DELAY = 1  # seconds

# API配置
API_PREFIX = '/api'

# 服务器配置
DEBUG = True
HOST = '0.0.0.0'
PORT = 5000

# 数据文件路径
LIST_FILE = 'data/processed/list.xlsx'
POST_FILE = 'data/processed/post.xlsx'

# 数据文件路径
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
ANALYSIS_DATA_DIR = os.path.join(DATA_DIR, 'analysis')

# 设置数据文件路径
IMPORT_FILE = os.path.join(ANALYSIS_DATA_DIR, 'import.csv')

# 分页配置
DEFAULT_PAGE_SIZE = 10
MAX_PAGE_SIZE = 100 