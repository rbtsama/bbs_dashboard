import pandas as pd
import requests
import json
import os

# 输出目录
output_dir = 'car_info_extraction'
os.makedirs(output_dir, exist_ok=True)

# 读取 Excel 文件
excel_path = 'data/raw/bbs_update_detail_20250307.xlsx'
df = pd.read_excel(excel_path)

# 输出Excel列信息
print(f"Excel 文件的列: {df.columns.tolist()}")
print(f"Excel 文件的行数: {len(df)}")

# 只保留需要的列
try:
    df = df[['title', 'tags', 'related_tags', 'content']]
    print("成功提取所需列")
except KeyError as e:
    print(f"提取列时出错: {e}")
    print(f"可用的列: {df.columns.tolist()}")
    exit(1)

# 只处理第10-20条数据
df = df.iloc[9:20]  # Python索引从0开始，所以第10条是索引9
print(f"处理第10-20条数据，共 {len(df)} 条记录")

# SiliconFlow API 配置
API_URL = "https://api.siliconflow.cn/v1/chat/completions"
API_KEY = "sk-ezyttcnxzkeixmghbfwujlmlwupseddmuzigtkyivxeionse"
MODEL = "deepseek-ai/DeepSeek-R1-Distill-Qwen-7B"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

def analyze_car_info(text):
    """调用 SiliconFlow API 分析车辆信息"""
    
    prompt = f"""请从以下文本中提取汽车信息，仅包括：
1. 年份（year）
2. 车辆品牌（make, model, trim）- 用中文表示
3. 公里数（miles）- 用 XXX mi 格式表示
4. 价格（price）- 用 $XX,XXX 格式表示
如有模糊价格如 $3000-6000 或 13xxx刀 等，保留原格式。

如果无法找到某项信息，请明确表示"找不到"。请勿编造或推测信息。

文本内容：
{text}

请按以下格式输出：
年份: [提取的年份，若找不到则填"找不到"]
品牌: [提取的品牌，若找不到则填"找不到"]
型号: [提取的型号，若找不到则填"找不到"]
配置: [提取的配置，若找不到则填"找不到"]
公里数: [提取的公里数，若找不到则填"找不到"]
价格: [提取的价格，若找不到则填"找不到"]
"""

    data = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 1000,
        "temperature": 0.1
    }
    
    try:
        response = requests.post(API_URL, headers=headers, data=json.dumps(data, ensure_ascii=False))
        response.raise_for_status()
        result = response.json()
        return result["choices"][0]["message"]["content"]
    except Exception as e:
        return f"API 调用失败: {str(e)}"

# 处理每条数据
results = []
for i, row in df.iterrows():
    # 合并所有文本字段
    title = row['title'] if not pd.isna(row['title']) else ""
    tags = row['tags'] if not pd.isna(row['tags']) else ""
    related_tags = row['related_tags'] if not pd.isna(row['related_tags']) else ""
    content = row['content'] if not pd.isna(row['content']) else ""
    
    text = f"标题: {title}\n标签: {tags}\n相关标签: {related_tags}\n内容: {content}"
    
    print(f"\n处理第 {i+1} 条数据...")
    result = analyze_car_info(text)
    
    results.append({
        "索引": i+1,
        "原始数据": text,
        "提取结果": result
    })
    
    print(f"第 {i+1} 条数据提取结果:\n{result}")
    
    # 将每条记录保存为单独的文件
    with open(f"{output_dir}/record_{i+1}_input.txt", 'w', encoding='utf-8') as f:
        f.write(text)
    
    with open(f"{output_dir}/record_{i+1}_output.txt", 'w', encoding='utf-8') as f:
        f.write(result)

# 将所有结果保存到 JSON 文件
with open(f'{output_dir}/car_info_extraction_results_10_to_20.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

# 创建输入输出对照文件
with open(f'{output_dir}/input_output_comparison.md', 'w', encoding='utf-8') as f:
    f.write("# 汽车信息提取 - 输入与输出对照\n\n")
    f.write("本文档展示了第10-20条数据的原始输入和提取输出的对照。\n\n")
    
    for item in results:
        f.write(f"## 第 {item['索引']} 条记录\n\n")
        f.write("### 输入数据\n\n")
        f.write("```\n")
        f.write(item['原始数据'])
        f.write("\n```\n\n")
        
        f.write("### 提取结果\n\n")
        f.write("```\n")
        f.write(item['提取结果'])
        f.write("\n```\n\n")
        f.write("---\n\n")

print(f"\n数据提取完成，结果已保存到 {output_dir} 目录")
print(f"- JSON结果文件: {output_dir}/car_info_extraction_results_10_to_20.json")
print(f"- 输入输出对照文件: {output_dir}/input_output_comparison.md")
print(f"- 每条记录的输入和输出已分别保存为单独的文件") 