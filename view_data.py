import pandas as pd

# 读取 Excel 文件
excel_path = 'data/raw/bbs_update_detail_20250307.xlsx'
df = pd.read_excel(excel_path)

# 只保留需要的列
cols = ['title', 'tags', 'related_tags', 'content']
df = df[cols]

# 只处理前 3 条数据
df = df.head(3)

# 打印每条数据
for i, row in df.iterrows():
    print(f"\n{'='*80}\n第 {i+1} 条数据:")
    for col in cols:
        print(f"{col}: {row[col]}") 