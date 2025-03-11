import pandas as pd
import requests
import json

# 读取 Excel 文件
excel_path = 'data/raw/bbs_update_detail_20250307.xlsx'
df = pd.read_excel(excel_path)

# 输出Excel列信息，调试用
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

# 只处理前 3 条数据
df = df.head(3)

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
        "原始数据": text,
        "提取结果": result
    })
    
    print(f"第 {i+1} 条数据提取结果:\n{result}")

# 将结果保存到文件
with open('car_info_extraction_results.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print("\n数据提取完成，结果已保存到 car_info_extraction_results.json 文件")

# 读取并打印保存的结果，确保编码正确
try:
    with open('car_info_extraction_results.json', 'r', encoding='utf-8') as f:
        saved_results = json.load(f)
    print("\n保存的结果验证:")
    for i, result in enumerate(saved_results):
        print(f"第 {i+1} 条数据:")
        print(f"提取结果: {result['提取结果']}")
except Exception as e:
    print(f"读取保存结果时出错: {e}") 