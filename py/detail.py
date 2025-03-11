import pandas as pd
import os
import glob
import re
import tqdm  # 导入tqdm用于显示进度条

def main():
    # 获取脚本所在目录的父目录作为项目根目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # 步骤1: 读取所有bbs_update_detail开头的源文件
    print("开始读取原始数据文件...")
    raw_dir = os.path.join(project_root, 'data', 'raw')
    pattern = os.path.join(raw_dir, 'bbs_update_detail_*.xlsx')
    excel_files = glob.glob(pattern)
    
    if not excel_files:
        print(f"错误: 在 {raw_dir} 目录下未找到任何 bbs_update_detail_*.xlsx 文件")
        return
    
    print(f"找到以下文件: {', '.join(excel_files)}")
    
    # 读取所有文件并合并
    df_list = []
    for file in tqdm.tqdm(excel_files, desc="读取文件"):
        try:
            df = pd.read_excel(file)
            # 确保所有字段都是字符串类型
            for col in ['title', 'tags', 'related_tags', 'content']:
                if col in df.columns:
                    df[col] = df[col].astype(str)
            df_list.append(df)
        except Exception as e:
            print(f"  - 读取文件 {file} 时出错: {e}")
    
    if not df_list:
        print("错误: 未能成功读取任何文件")
        return
    
    # 合并所有数据
    print("合并所有数据...")
    df_combined = pd.concat(df_list, ignore_index=True)
    print(f"合并后共有 {len(df_combined)} 条记录")
    
    # 步骤1: 根据url去重，保留scraping_time最新的记录
    print("根据url去重...")
    # 确保scraping_time列是日期时间类型
    if 'scraping_time' in df_combined.columns:
        df_combined['scraping_time'] = pd.to_datetime(df_combined['scraping_time'], errors='coerce')
    
    # 按url分组，取scraping_time最新的记录
    df_combined = df_combined.sort_values('scraping_time', ascending=False)
    df_deduped = df_combined.drop_duplicates(subset=['url'], keep='first').copy()  # 使用.copy()创建副本避免警告
    print(f"去重后共有 {len(df_deduped)} 条记录")
    
    # 步骤2: 新增car_description字段，合并title，tags，related_tags，content
    print("创建car_description字段...")
    
    def create_car_description(row):
        # 初始化一个列表来存储非空值
        parts = []
        
        # 添加title
        if pd.notna(row.get('title')) and row.get('title') != 'nan':
            parts.append(row['title'])
        
        # 添加tags
        if pd.notna(row.get('tags')) and row.get('tags') != 'nan':
            parts.append(row['tags'])
        
        # 添加related_tags
        if pd.notna(row.get('related_tags')) and row.get('related_tags') != 'nan':
            parts.append(row['related_tags'])
        
        # 添加content
        if pd.notna(row.get('content')) and row.get('content') != 'nan':
            parts.append(row['content'])
        
        # 合并所有部分
        return ' '.join(parts)
    
    # 使用进度条显示处理进度
    tqdm.tqdm.pandas(desc="处理记录")
    df_deduped['car_description'] = df_deduped.progress_apply(create_car_description, axis=1)
    
    # 保存结果
    output_path = os.path.join(project_root, 'data', 'processed', 'detail.xlsx')
    print(f"保存结果到 {output_path}...")
    
    # 确保目录存在
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 保存Excel文件
    df_deduped.to_excel(output_path, index=False)
    print("处理完成！")

if __name__ == "__main__":
    main() 