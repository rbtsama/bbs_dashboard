import pandas as pd
import os
import re
import requests
import json
import time
import random
import sys
import tqdm  # 导入tqdm用于显示进度条
import argparse  # 导入argparse用于解析命令行参数

# SiliconFlow API 配置
API_URL = "https://api.siliconflow.cn/v1/chat/completions"
API_KEY = "sk-ezyttcnxzkeixmghbfwujlmlwupseddmuzigtkyivxeionse"
MODEL = "Qwen/Qwen2.5-32B-Instruct"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {API_KEY}"
}

# 检查API是否可用
def check_api_availability():
    """检查API是否可用"""
    try:
        data = {
            "model": MODEL,
            "messages": [{"role": "user", "content": "测试API是否可用"}],
            "max_tokens": 10,
            "temperature": 0.1
        }
        
        response = requests.post(
            API_URL, 
            headers=headers, 
            data=json.dumps(data, ensure_ascii=False),
            timeout=5  # 设置较短的超时时间
        )
        
        if response.status_code == 200:
            print("✓ API连接正常")
            return True
        else:
            print(f"✗ API连接失败: HTTP {response.status_code}")
            print(f"  响应内容: {response.text}")
            return False
    except Exception as e:
        print(f"✗ API连接异常: {e}")
        return False

# 基于extract_car_info_batch3.py中的函数，但做了适当修改
def identify_demand(text):
    """识别需求类型"""
    # 租车相关关键词
    rent_keywords = ['租车', '出租', '租售', '租', '月租']
    # 买车相关关键词
    buy_keywords = ['买车', '求购', '求车', '收车', '想买']
    # 卖车相关关键词（增加新品和全新）
    sell_keywords = ['卖车', '出售', '转让', '出', '售', '新品', '全新']
    
    # 优先检查租车需求
    for keyword in rent_keywords:
        if keyword in text:
            return "租车"
            
    # 然后检查买车需求
    for keyword in buy_keywords:
        if keyword in text:
            return "买车"
            
    # 最后检查卖车需求
    for keyword in sell_keywords:
        if keyword in text:
            return "卖车"
            
    # 如果都没找到，返回None让模型判断
    return None

def standardize_brand_and_model(brand, model):
    """统一品牌和型号"""
    # 品牌映射
    brand_mapping = {
        'Toyota': '丰田',
        'Honda': '本田',
        'Mazda': '马自达',
        'BMW': '宝马',
        'Benz': '奔驰',
        'Mercedes': '奔驰',
        'Mercedes-Benz': '奔驰',
        'Volkswagen': '大众',
        'Nissan': '尼桑',
        'Tesla': '特斯拉',
        '塞纳': '丰田',  # 塞纳是丰田的型号
        '轩逸': '尼桑',  # 轩逸是尼桑的型号
        '日产': '尼桑',  # 统一日产为尼桑
    }
    
    # 型号映射
    model_mapping = {
        '塞纳': 'Sienna',
        '轩逸': 'Sentra',
        '雅阁': 'Accord',
        '飞度': 'Fit',
        '卡罗拉': 'Corolla',
        '大SUV': 'Pathfinder',  # 尼桑的大型SUV通常是Pathfinder
        '普锐斯': 'Prius',
        '欧蓝德': 'Outlander',  # 三菱欧蓝德的英文名
    }
    
    # 品牌和型号的对应关系
    brand_model_pairs = {
        'Sentra': '尼桑',
        'Sienna': '丰田',
        'Accord': '本田',
        'Civic': '本田',
        'Fit': '本田',
        'Corolla': '丰田',
        'Camry': '丰田',
        'RAV4': '丰田',
        'Pathfinder': '尼桑',
        'Prius': '丰田',
        'Outlander': '三菱',
    }
    
    # 处理多个品牌的情况
    if ',' in brand:
        brands = [b.strip() for b in brand.split(',')]
        brand = brands[0]  # 使用第一个品牌
    
    # 修正品牌
    if brand in brand_mapping:
        brand = brand_mapping[brand]
    
    # 修正型号
    if model in model_mapping:
        model = model_mapping[model]
    
    # 根据型号修正品牌
    if model in brand_model_pairs:
        brand = brand_model_pairs[model]
    
    # 如果品牌是车型，调整品牌和型号
    if brand == '塞纳':
        brand = '丰田'
        model = 'Sienna'
    elif brand == '轩逸':
        brand = '尼桑'
        model = 'Sentra'
    
    # 处理模糊的型号
    if model == '大SUV' and brand == '尼桑':
        model = 'Pathfinder'
    elif model == '找不到' and brand == '丰田' and ('塞纳' in str(brand).lower() or 'sienna' in str(brand).lower()):
        model = 'Sienna'
    
    return brand, model

def standardize_year(year_str):
    """统一年份格式"""
    if not year_str or year_str == '找不到':
        return year_str
    
    # 处理"XX年"格式
    year_match = re.search(r'(\d{2})年', year_str)
    if year_match:
        year = int(year_match.group(1))
        if year < 50:  # 假设50以下的年份是20XX年
            return f"20{year:02d}"
        else:  # 50以上的年份是19XX年
            return f"19{year:02d}"
    
    # 如果已经是4位数年份，直接返回
    if re.match(r'^\d{4}$', year_str):
        return year_str
    
    return year_str

def standardize_mileage(mileage_str):
    """统一里程格式"""
    if not mileage_str or mileage_str == '找不到':
        return mileage_str
    
    # 处理范围格式（如"6-10万Mile"）
    range_match = re.search(r'(\d+)[-~](\d+)万(?:Mile|迈|英里)', mileage_str)
    if range_match:
        start_val = int(float(range_match.group(1)) * 10000)
        end_val = int(float(range_match.group(2)) * 10000)
        return f"{start_val:,}~{end_val:,} mi"
    
    # 处理"X万多迈"格式
    exact_match = re.search(r'(\d+)万多迈', mileage_str)
    if exact_match:
        mileage = int(float(exact_match.group(1)) * 10000)
        return f"{mileage:,} mi"
    
    # 处理带"万"的数字
    if '万' in mileage_str:
        match = re.search(r'(\d+(?:\.\d+)?)', mileage_str)
        if match:
            mileage = float(match.group(1)) * 10000
            return f"{int(mileage):,} mi"
    
    # 处理纯数字（添加千位分隔符和mi单位）
    if re.match(r'^\d+$', mileage_str):
        mileage = int(mileage_str)
        return f"{mileage:,} mi"
    
    # 已经是标准格式的情况
    if re.match(r'^\d{1,3}(,\d{3})*\s*mi$', mileage_str):
        return mileage_str
        
    return mileage_str

def standardize_price(price_str):
    """统一价格格式"""
    if not price_str or price_str == '找不到':
        return price_str
    
    # 如果已经是标准格式，直接返回
    if re.match(r'^\$\d{1,3}(,\d{3})*$', price_str):
        return price_str
    
    # 处理单个具体价格
    price_match = re.search(r'(?:售价|价格|只要|价位)?[约]?\s*(\d+)(?:刀|美元|块钱)?(?:包过户)?', price_str)
    if price_match:
        price = int(price_match.group(1))
        # 如果价格小于1000或大于50000，可能是错误的
        if price < 1000:
            return "找不到"
        if price > 50000:
            price = price // 10  # 可能多了一个0
        return f"${price:,}"
    
    # 处理范围价格
    range_match = re.search(r'(\d+)(?:k|千|万)?(?:[~-]|到)(\d+)(?:k|千|万)?', price_str)
    if range_match:
        start_price = int(range_match.group(1))
        end_price = int(range_match.group(2))
        
        # 处理单位
        if 'k' in price_str or '千' in price_str:
            start_price *= 1000
            end_price *= 1000
        elif '万' in price_str:
            start_price *= 10000
            end_price *= 10000
        # 如果价格都小于100，可能是以"万"为单位
        elif start_price < 100 and end_price < 100:
            start_price *= 1000
            end_price *= 1000
            
        # 验证价格范围的合理性
        if start_price < 1000 or end_price > 50000:
            return "找不到"
            
        return f"${start_price:,}~${end_price:,}"
    
    return price_str

def standardize_output(content):
    """统一输出格式"""
    # 统一"不知道"、"无"、"无法提取"等为"找不到"
    content = re.sub(r'(?:不知道|无|无法提取|求购二手车|找到)(?=\n|$)', '找不到', content)
    
    # 标准化年份
    year_match = re.search(r'年份: (.*?)(?=\n|$)', content)
    if year_match:
        year = year_match.group(1)
        standardized_year = standardize_year(year)
        if standardized_year:
            content = content.replace(f'年份: {year}', f'年份: {standardized_year}')
    
    # 标准化品牌和型号
    brand_match = re.search(r'品牌: (.*?)(?=\n|$)', content)
    model_match = re.search(r'型号: (.*?)(?=\n|$)', content)
    if brand_match and model_match:
        brand = brand_match.group(1)
        model = model_match.group(1)
        if brand != '找不到' or model != '找不到':
            new_brand, new_model = standardize_brand_and_model(brand, model)
            if new_brand != brand:
                content = content.replace(f'品牌: {brand}', f'品牌: {new_brand}')
            if model != '找不到' and new_model != model:
                content = content.replace(f'型号: {model}', f'型号: {new_model}')
    
    # 标准化里程数
    mileage_match = re.search(r'公里数: (.*?)(?=\n|$)', content)
    if mileage_match:
        mileage = mileage_match.group(1)
        standardized_mileage = standardize_mileage(mileage)
        if standardized_mileage:
            content = content.replace(f'公里数: {mileage}', f'公里数: {standardized_mileage}')
    
    # 标准化价格
    price_match = re.search(r'价格: (.*?)(?=\n|$)', content)
    if price_match:
        price = price_match.group(1)
        standardized_price = standardize_price(price)
        if standardized_price:
            content = content.replace(f'价格: {price}', f'价格: {standardized_price}')
    
    # 确保所有价格都有千位分隔符
    def add_thousands_separator(match):
        price = match.group(1)
        if not ',' in price:
            return f"价格: ${int(price):,}"
        return match.group(0)
    
    content = re.sub(r'价格: \$(\d+)(?=\n|$)', add_thousands_separator, content)
    
    return content

# 模拟API调用的函数
def mock_analyze_car_info(text):
    """模拟API分析车辆信息，用于测试"""
    # 尝试从文本中提取一些基本信息
    year = "找不到"
    year_match = re.search(r'20\d{2}', text)
    if year_match:
        year = year_match.group(0)
    
    # 尝试识别品牌
    brand = "找不到"
    for b in ["丰田", "本田", "马自达", "宝马", "奔驰", "大众", "尼桑", "特斯拉"]:
        if b in text:
            brand = b
            break
    
    # 尝试识别需求
    demand = identify_demand(text)
    if not demand:
        demand = "卖车"  # 默认为卖车
    
    # 构建模拟响应
    response = f"""年份: {year}
品牌: {brand}
型号: 找不到
公里数: 找不到
价格: 找不到
需求: {demand}"""
    
    return standardize_output(response)

def call_api_with_retry(prompt, max_retries=3, initial_delay=1, use_mock=False):
    """调用API并实现重试机制"""
    # 如果使用模拟模式，直接返回模拟数据
    if use_mock:
        time.sleep(0.5)  # 模拟API调用延迟
        return mock_analyze_car_info(prompt)
    
    # 使用与extract_car_info_batch3.py相同的API调用方式
    delay = initial_delay
    
    for attempt in range(max_retries):
        try:
            data = {
                "model": MODEL,
                "messages": [{"role": "user", "content": prompt}],
                "max_tokens": 1000,
                "temperature": 0.1
            }
            
            response = requests.post(API_URL, headers=headers, data=json.dumps(data, ensure_ascii=False))
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"]
            
        except requests.exceptions.RequestException as e:
            if attempt == max_retries - 1:  # 最后一次尝试
                print(f"API调用失败（尝试 {attempt + 1}/{max_retries}）: {str(e)}")
                # 返回一个基本的结果结构
                return """年份: 找不到
品牌: 找不到
型号: 找不到
公里数: 找不到
价格: 找不到
需求: 找不到"""
            
            print(f"API调用失败（尝试 {attempt + 1}/{max_retries}），{delay}秒后重试: {str(e)}")
            time.sleep(delay)
            delay *= 2  # 指数退避
            delay += random.uniform(0, 1)  # 添加随机抖动

def analyze_car_info(text, use_mock=False):
    """调用API分析车辆信息"""
    # 如果使用模拟模式，调用模拟函数
    if use_mock:
        return mock_analyze_car_info(text)
    
    # 首先尝试直接从文本中识别需求
    identified_demand = identify_demand(text)
    
    prompt = f"""请从以下文本中提取汽车信息，仅包括：
1. 年份（year）
2. 车辆品牌（make）- 用中文表示
3. 型号（model）- 如果原文使用英文（如Accord、Civic等），请保持英文
4. 公里数（miles）
5. 价格（price）
6. 需求（demand）- 只能是以下三种之一：买车、卖车、租车

关于需求的判断规则：
- 如果文本中明确包含"租车"、"出租"、"租售"等表述，则需求为"租车"
- 如果文本中明确包含"买车"、"求购"、"求车"、"收车"、"想买"等表述，则需求为"买车"
- 如果文本中明确包含"卖车"、"出售"、"转让"、"出"、"售"、"新品"、"全新"等表述，则需求为"卖车"
- 如果无法明确判断，请根据上下文推断最可能的需求
- 如果实在无法判断，则默认为"卖车"

如果无法找到某项信息，请明确表示"找不到"。请勿编造或推测信息。
对于型号，如果原文使用英文（如Accord、Civic等），请保持英文形式，不要翻译为中文。

文本内容：
{text}

请按以下格式输出：
年份: [提取的年份，若找不到则填"找不到"]
品牌: [提取的品牌，若找不到则填"找不到"]
型号: [提取的型号，若找不到则填"找不到"]
公里数: [提取的公里数，若找不到则填"找不到"]
价格: [提取的价格，若找不到则填"找不到"]
需求: [买车/卖车/租车]
"""

    # 使用重试机制调用API
    content = call_api_with_retry(prompt, use_mock=use_mock)
    
    # 如果API调用完全失败，使用预处理提取的信息构建结果
    if content == """年份: 找不到
品牌: 找不到
型号: 找不到
公里数: 找不到
价格: 找不到
需求: 找不到""" and identified_demand:
        content = content.replace("需求: 找不到", f"需求: {identified_demand}")
    
    # 统一输出格式
    content = standardize_output(content)
    
    return content

def extract_field(result_text, field_name):
    """从结果文本中提取特定字段的值"""
    pattern = f"{field_name}: (.*?)(?=\n|$)"
    match = re.search(pattern, result_text)
    if match:
        return match.group(1).strip()
    return "找不到"

def process_car_info(batch_size=200, resume=True, use_mock=False, auto_mock=True):
    """处理车辆信息
    
    Args:
        batch_size (int): 每次处理的记录数量，默认为200
        resume (bool): 是否从上次处理的位置继续，默认为True
        use_mock (bool): 是否使用模拟模式，默认为False
        auto_mock (bool): 当API不可用时是否自动切换到模拟模式，默认为True
    """
    # 确保pandas正确处理中文
    pd.set_option('display.unicode.east_asian_width', True)
    pd.set_option('display.unicode.ambiguous_as_wide', True)
    
    # 获取脚本所在目录的父目录作为项目根目录
    script_dir = os.path.dirname(os.path.abspath(__file__))
    project_root = os.path.dirname(script_dir)
    
    # 创建临时目录
    temp_dir = os.path.join(project_root, 'data', 'temp')
    os.makedirs(temp_dir, exist_ok=True)
    
    # 首先检查API是否可用
    api_available = check_api_availability()
    if not api_available:
        if auto_mock:
            print("API不可用，自动切换到模拟模式")
            use_mock = True
        elif use_mock:
            print("API不可用，将使用模拟模式继续")
        else:
            print("错误: API不可用，请确保API服务已启动")
            print("提示: 可以使用 --mock 参数启用模拟模式，或使用 --no-auto-mock 禁用自动切换到模拟模式")
            return
    
    input_path = os.path.join(project_root, 'data', 'processed', 'detail.xlsx')
    output_path = os.path.join(project_root, 'data', 'processed', 'car_info.csv')
    
    print(f"读取输入文件: {input_path}")
    
    # 检查输入文件是否存在
    if not os.path.exists(input_path):
        print(f"错误: 输入文件 {input_path} 不存在！")
        return
    
    # 读取Excel文件
    try:
        df = pd.read_excel(input_path)
        print(f"成功读取 {len(df)} 条记录")
    except Exception as e:
        print(f"读取文件时出错: {e}")
        return
    
    # 检查必需的列是否存在
    if 'url' not in df.columns or 'car_description' not in df.columns:
        print("错误: 输入文件缺少必要的列（url 或 car_description）")
        return
    
    # 定义结果列
    result_columns = ['url', 'year', 'make', 'model', 'miles', 'price', 'trade_type', 'location']
    
    # 如果resume=True且输出文件存在，读取已处理的记录
    processed_urls = set()
    if resume and os.path.exists(output_path):
        try:
            # 尝试多种编码方式读取文件
            try:
                existing_df = pd.read_csv(output_path, encoding='utf-8-sig')
            except UnicodeDecodeError:
                try:
                    existing_df = pd.read_csv(output_path, encoding='utf-8')
                except UnicodeDecodeError:
                    try:
                        existing_df = pd.read_csv(output_path, encoding='gbk')
                    except UnicodeDecodeError:
                        existing_df = pd.read_csv(output_path, encoding='gb18030')
            
            if 'url' in existing_df.columns:
                processed_urls = set(existing_df['url'].tolist())
                print(f"已从输出文件中读取 {len(processed_urls)} 条已处理的记录")
        except Exception as e:
            print(f"读取已处理记录时出错: {e}")
    
    # 过滤掉已处理的记录
    if processed_urls:
        df = df[~df['url'].isin(processed_urls)]
        print(f"过滤已处理记录后，还有 {len(df)} 条记录需要处理")
    
    # 如果没有需要处理的记录，直接返回
    if len(df) == 0:
        print("没有新记录需要处理，任务完成")
        return
    
    # 准备结果DataFrame
    results_df = pd.DataFrame(columns=result_columns)
    
    # 分批处理记录
    total_batches = (len(df) + batch_size - 1) // batch_size
    for batch_idx in range(total_batches):
        start_idx = batch_idx * batch_size
        end_idx = min((batch_idx + 1) * batch_size, len(df))
        batch_df = df.iloc[start_idx:end_idx]
        
        print(f"\n处理第 {batch_idx+1}/{total_batches} 批记录 (记录 {start_idx+1}-{end_idx})")
        
        # 创建批次目录
        batch_dir = os.path.join(temp_dir, f'batch_{batch_idx+1}')
        os.makedirs(batch_dir, exist_ok=True)
        
        # 处理批次中的每条记录
        batch_results = []
        for i, row in enumerate(batch_df.itertuples(), 1):
            url = row.url
            description = row.car_description
            
            # 显示当前处理的记录信息
            record_num = start_idx + i
            print(f"\n[{record_num}/{len(df)}] 处理记录: {url}")
            
            if pd.isna(description) or str(description).strip() == '':
                print("  - 跳过：车辆描述为空")
                # 创建空结果
                result = {
                    'url': url,
                    'year': '找不到',
                    'make': '找不到',
                    'model': '找不到',
                    'miles': '找不到',
                    'price': '找不到',
                    'trade_type': '找不到',
                    'location': '洛杉矶'  # 添加固定的location字段
                }
            else:
                try:
                    print("  - 提取车辆信息...")
                    car_info = analyze_car_info(description, use_mock=use_mock)
                    print(f"  - 提取结果:\n{car_info}")
                    
                    # 从car_info中提取各个字段
                    result = {
                        'url': url,
                        'year': extract_field(car_info, '年份'),
                        'make': extract_field(car_info, '品牌'),
                        'model': extract_field(car_info, '型号'),
                        'miles': extract_field(car_info, '公里数'),
                        'price': extract_field(car_info, '价格'),
                        'trade_type': extract_field(car_info, '需求'),
                        'location': '洛杉矶'  # 添加固定的location字段
                    }
                except Exception as e:
                    print(f"  - 提取车辆信息时出错: {e}")
                    # 创建错误结果
                    result = {
                        'url': url,
                        'year': '提取出错',
                        'make': '提取出错',
                        'model': '提取出错',
                        'miles': '提取出错',
                        'price': '提取出错',
                        'trade_type': '提取出错',
                        'location': '洛杉矶'  # 添加固定的location字段
                    }
            
            # 添加到批次结果
            batch_results.append(result)
            
            # 每处理一条记录，保存一次临时结果
            temp_df = pd.DataFrame(batch_results)
            temp_output_path = os.path.join(batch_dir, f'record_{i}.csv')
            
            # 使用BOM标记确保Excel正确识别UTF-8编码
            with open(temp_output_path, 'w', encoding='utf-8-sig', newline='') as f:
                temp_df.to_csv(f, index=False)
            
            print(f"  - 已保存临时结果到 {temp_output_path}")
        
        # 将批次结果添加到总结果
        batch_results_df = pd.DataFrame(batch_results)
        results_df = pd.concat([results_df, batch_results_df], ignore_index=True)
        
        # 保存批次结果
        batch_output_path = os.path.join(temp_dir, f'batch_{batch_idx+1}_results.csv')
        
        # 使用BOM标记确保Excel正确识别UTF-8编码
        with open(batch_output_path, 'w', encoding='utf-8-sig', newline='') as f:
            batch_results_df.to_csv(f, index=False)
        
        print(f"已保存批次结果到 {batch_output_path}")
        
        # 如果输出文件已存在，将新结果追加到现有文件
        if os.path.exists(output_path):
            try:
                # 尝试多种编码方式读取文件
                try:
                    existing_df = pd.read_csv(output_path, encoding='utf-8-sig')
                except UnicodeDecodeError:
                    try:
                        existing_df = pd.read_csv(output_path, encoding='utf-8')
                    except UnicodeDecodeError:
                        try:
                            existing_df = pd.read_csv(output_path, encoding='gbk')
                        except UnicodeDecodeError:
                            existing_df = pd.read_csv(output_path, encoding='gb18030')
                
                # 如果现有文件中没有location列，添加该列
                if 'location' not in existing_df.columns:
                    existing_df['location'] = '洛杉矶'
                
                combined_df = pd.concat([existing_df, batch_results_df], ignore_index=True)
                
                # 使用BOM标记确保Excel正确识别UTF-8编码
                with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
                    combined_df.to_csv(f, index=False)
                
                print(f"已将批次结果追加到 {output_path}")
            except Exception as e:
                print(f"追加结果到输出文件时出错: {e}")
                # 如果追加失败，至少保存当前批次的结果
                latest_path = os.path.join(temp_dir, 'latest_results.csv')
                with open(latest_path, 'w', encoding='utf-8-sig', newline='') as f:
                    results_df.to_csv(f, index=False)
                print(f"已保存最新结果到 {latest_path}")
        else:
            # 如果输出文件不存在，直接保存当前所有结果
            with open(output_path, 'w', encoding='utf-8-sig', newline='') as f:
                results_df.to_csv(f, index=False)
            print(f"已保存所有结果到 {output_path}")
    
    print("\n处理完成！")

if __name__ == "__main__":
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='处理车辆信息')
    parser.add_argument('--batch-size', type=int, default=200, help='每批处理的记录数量，默认为200')
    parser.add_argument('--no-resume', action='store_true', help='不从上次处理的位置继续，重新处理所有记录')
    parser.add_argument('--mock', action='store_true', help='使用模拟模式，不调用实际API')
    parser.add_argument('--no-auto-mock', action='store_true', help='禁用自动切换到模拟模式')
    args = parser.parse_args()
    
    # 调用处理函数
    process_car_info(
        batch_size=args.batch_size, 
        resume=not args.no_resume,
        use_mock=args.mock,
        auto_mock=not args.no_auto_mock
    ) 