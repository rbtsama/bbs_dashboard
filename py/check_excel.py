import pandas as pd
import sys
from pathlib import Path

# 设置数据路径
DATA_DIR = Path(__file__).parent.parent / 'data'
PROCESSED_DIR = DATA_DIR / 'processed'

def display_file_info(file_name):
    """显示Excel文件的基本信息"""
    file_path = PROCESSED_DIR / file_name
    
    if not file_path.exists():
        print(f"文件 {file_path} 不存在")
        return
    
    print(f"\n===== {file_name} 信息 =====")
    df = pd.read_excel(file_path)
    
    print(f"行数: {len(df)}")
    print(f"列数: {len(df.columns)}")
    print("\n列名:")
    for col in df.columns:
        print(f"  - {col}")
    
    print("\n前2行示例:")
    print(df.head(2).to_string())
    
    print("\n数据类型:")
    print(df.dtypes)

# 主程序
if __name__ == "__main__":
    display_file_info('list.xlsx')
    display_file_info('post.xlsx') 