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
        return "-"
    
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
    
    return "-"

def standardize_mileage(mileage_str):
    """统一里程格式"""
    if not mileage_str or mileage_str == '找不到':
        return "-"
    
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
        
    return "-"

def standardize_price(price_str):
    """统一价格格式"""
    if not price_str or price_str == '找不到':
        return "-"
    
    # 如果已经是标准格式，直接返回
    if re.match(r'^\$\d{1,3}(,\d{3})*$', price_str):
        return price_str
    
    # 处理单个具体价格
    price_match = re.search(r'(?:售价|价格|只要|价位)?[约]?\s*(\d+)(?:刀|美元|块钱)?(?:包过户)?', price_str)
    if price_match:
        price = int(price_match.group(1))
        # 如果价格小于1000或大于50000，可能是错误的
        if price < 1000:
            return "-"
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
            
        return f"${start_price:,}~${end_price:,}"
    
    return "-"

def standardize_output(content):
    """标准化输出内容"""
    # 如果内容为空或None，返回"-"
    if not content or content == "找不到":
        return "-"
    
    # 如果内容是数字，添加千位分隔符
    if isinstance(content, (int, float)):
        return f"{content:,}"
    
    # 如果内容是字符串
    content = str(content).strip()
    
    # 如果内容为空字符串或"找不到"，返回"-"
    if not content or content.lower() == "找不到":
        return "-"
    
    # 如果内容已经包含千位分隔符，直接返回
    if re.match(r'^\$?\d{1,3}(,\d{3})*(\s*mi)?$', content):
        return content
    
    # 如果内容是纯数字，添加千位分隔符
    if re.match(r'^\d+$', content):
        return f"{int(content):,}"
    
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

def extract_field(result_text, field_name):
    """从API返回的文本中提取指定字段的值"""
    if not result_text:
        return None
        
    match = re.search(f"{field_name}: (.*?)(?=\n|$)", result_text)
    if not match:
        return None
        
    value = match.group(1).strip()
    if not value or value.lower() == "null" or value == "找不到":
        return None
        
    return value

def extract_car_info_with_ai(text):
    """使用AI提取车辆信息"""
    prompt = f"""请从以下文本中提取车辆信息：

{text}

请仔细分析文本，提取以下字段信息：
1. 年份：提取4位数年份，如"2019"。如找不到则返回null
2. 品牌：统一使用中文名称，如"丰田"。如找不到则返回null
3. 型号：保持原始格式，如"RAV4"。如找不到则返回null
4. 价格：保持原文表述，如"一万多"、"$15,000"、"8000-10000"。如找不到则返回null
5. 里程：保持原文表述，如"8.5万迈"、"75000 mile"。如找不到则返回null

注意事项：
1. 价格和里程可能会有数字重叠，请仔细分析上下文区分
2. 如果出现多个价格或里程，请选择最可能的一个
3. 保持原文的表达方式，不要转换格式
4. 如果确实找不到某个字段信息，返回null，不要随意猜测

请用JSON格式返回，示例：
{
    "year": "2019",
    "make": "丰田",
    "model": "RAV4",
    "price": "一万多",
    "mileage": "8.5万迈"
}"""

    try:
        # 准备API请求数据
        data = {
            "model": MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000,
            "temperature": 0.1
        }
        
        # 发送请求
        response = requests.post(
            API_URL, 
            headers=headers, 
            json=data,  # 使用json参数自动处理编码
            timeout=10
        )
        
        # 检查响应状态
        if response.status_code != 200:
            print(f"API请求失败: HTTP {response.status_code}")
            print(f"响应内容: {response.text}")
            return None
            
        # 解析响应
        result = response.json()
        if not result or 'choices' not in result:
            print("API响应格式错误")
            return None
            
        # 获取AI响应内容
        content = result['choices'][0]['message']['content']
        
        # 提取JSON部分
        try:
            # 找到JSON字符串的开始和结束位置
            start = content.find('{')
            end = content.rfind('}') + 1
            if start == -1 or end == -1:
                print("未找到有效的JSON格式响应")
                return None
                
            json_str = content[start:end]
            car_info = json.loads(json_str)
            
            # 验证必要的字段
            required_fields = ['year', 'make', 'model', 'price', 'mileage']
            for field in required_fields:
                if field not in car_info:
                    car_info[field] = None
                    
            return car_info
            
        except json.JSONDecodeError as e:
            print(f"JSON解析失败: {e}")
            print(f"原始响应: {content}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"API请求异常: {e}")
        return None
    except Exception as e:
        print(f"处理异常: {e}")
        return None

def analyze_car_info(text, use_mock=False):
    """分析车辆信息"""
    # 如果文本为空，返回所有字段为"-"的结果
    if not text:
        return {
            'year': '-',
            'make': '-',
            'model': '-',
            'price': '-',
            'miles': '-',
            'trade_type': '-',
            'location': '洛杉矶'
        }
    
    # 首先尝试识别需求类型
    trade_type = identify_demand(text)
    
    # 构建提示词
    prompt = f"""请仔细分析以下车辆信息文本，提取关键信息。如果无法确定某个字段的信息，请返回null。宁可不提取，也不要提供不准确的信息：

{text}

请提取以下字段信息：

1. 年份：
- 需要识别中英文年份表达，如：2019年、19年、2019 model、19款等
- 必须确保是车辆年份，而不是发帖时间或其他年份
- 如果看到多个年份，需要通过上下文确定哪个是车辆年份
- 如果无法确定具体年份，返回null

2. 品牌：
- 需要同时识别中英文品牌名称及其变体，例如：
  * 丰田/Toyota/TOYOTA/豐田
  * 本田/Honda/HONDA
  * 日产/尼桑/Nissan/NISSAN
  * 雷克萨斯/凌志/Lexus/LEXUS
  * 奔驰/奔驰/Benz/Mercedes/BENZ/MB
  * 宝马/BMW/bmw
- 有时品牌信息会包含在型号中，如Camry暗示是丰田
- 如果品牌信息模糊或存在多个可能，返回null

3. 型号：
- 保持原文的表达方式，包括配置信息
- 需要识别中英文混合的表达，例如：
  * Camry/凯美瑞 SE/豪华版
  * Civic/思域 Type-R
  * RAV4/荣放 Limited
  * Sienna/塞纳 XLE
  * GLC300/E300/GLS450
- 包括重要的配置信息：
  * SE/LE/XLE/Limited/Sport/Base
  * Hybrid/混动/油电混合
  * AWD/四驱/前驱
- 如果型号信息不完整或不确定，返回null

4. 价格：
- 保持原文的价格表达方式
- 价格通常在3000美元以上
- 需要识别各种价格表达：
  * 具体价格：$3000、3000刀、3k、3千
  * 价格范围：3000-4000、3k到4k、3-4万
  * 首付表达：首付3000、down payment 3k
  * 月供表达：月供300、monthly 300
- 注意区分价格和里程数
- 如果价格不合理（如低于3000）或不确定，返回null

5. 里程：
- 保持原文的里程表达方式
- 里程范围通常在几千到20万迈之间
- 需要识别各种里程表达：
  * 具体里程：3万迈、30k miles、30000英里
  * 里程范围：3-4万迈、3万多mile
  * 中英混合：30000迈、3万miles、30k英里
- 确保提取的是里程而不是价格
- 如果里程数不合理或不确定，返回null

注意事项：
1. 价格和里程的区分：
   - 价格通常与这些词关联：price、价格、刀、美元、$、售价、开价、价位
   - 里程通常与这些词关联：mile、迈、英里、公里、mileage、里程表、跑了
   - 如果无法确定是价格还是里程，宁可返回null

2. 数字的合理性判断：
   - 价格：通常在3000美元以上，不合理的价格返回null
   - 里程：通常不超过20万迈，不合理的里程数返回null

3. 多个可能值的处理：
   - 选择描述最详细、最明确的信息
   - 如果多个值都合理但无法确定，返回null
   - 不要随意选择或猜测

请按以下格式返回（保持字段名不变）：
年份: 2019
品牌: 丰田
型号: 凯美瑞 SE
价格: 3000刀
公里数: 3万迈

对于任何无法确定的字段，请返回null而不是猜测或编造信息。"""
    
    # 调用API获取分析结果
    result = call_api_with_retry(prompt, use_mock=use_mock)
    if not result:
        # 如果API调用失败，返回所有字段为"-"的结果
        return {
            'year': '-',
            'make': '-',
            'model': '-',
            'price': '-',
            'miles': '-',
            'trade_type': trade_type or '-',
            'location': '洛杉矶'
        }
    
    # 提取各个字段
    year = extract_field(result, '年份')
    make = extract_field(result, '品牌')
    model = extract_field(result, '型号')
    price = extract_field(result, '价格')
    miles = extract_field(result, '公里数')
    
    # 标准化处理
    year = standardize_year(year)
    make, model = standardize_brand_and_model(make, model)
    price = standardize_price(price)
    miles = standardize_mileage(miles)
    
    # 返回结果
    return {
        'year': year or '-',
        'make': make or '-',
        'model': model or '-',
        'price': price or '-',
        'miles': miles or '-',
        'trade_type': trade_type or '-',
        'location': '洛杉矶'  # 固定为洛杉矶
    }

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
    
    # 加载 post.xlsx 和 update.xlsx 文件，用于获取额外信息
    post_path = os.path.join(project_root, 'data', 'processed', 'post.xlsx')
    update_path = os.path.join(project_root, 'data', 'processed', 'update.xlsx')
    
    print(f"读取输入文件: {input_path}")
    print(f"读取 post.xlsx: {post_path}")
    print(f"读取 update.xlsx: {update_path}")
    
    # 检查输入文件是否存在
    if not os.path.exists(input_path):
        print(f"错误: 输入文件 {input_path} 不存在！")
        return
    
    # 读取 post.xlsx 文件
    post_df = None
    if os.path.exists(post_path):
        try:
            post_df = pd.read_excel(post_path)
            print(f"成功读取 post.xlsx 中的 {len(post_df)} 条记录")
        except Exception as e:
            print(f"读取 post.xlsx 时出错: {e}")
    else:
        print(f"警告: post.xlsx 文件不存在")
    
    # 读取 update.xlsx 文件
    update_df = None
    if os.path.exists(update_path):
        try:
            update_df = pd.read_excel(update_path)
            print(f"成功读取 update.xlsx 中的 {len(update_df)} 条记录")
        except Exception as e:
            print(f"读取 update.xlsx 时出错: {e}")
    else:
        print(f"警告: update.xlsx 文件不存在")
    
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
    
    # 定义结果列，增加 post_time, title, author, author_link, scraping_time_R 字段
    result_columns = ['url', 'year', 'make', 'model', 'miles', 'price', 'trade_type', 'location', 
                     'post_time', 'title', 'author', 'author_link', 'scraping_time_R']
    
    # 读取已处理的记录，用于保留已有URL的车辆信息
    existing_records = {}
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
                # 构建URL到记录的映射
                for idx, row in existing_df.iterrows():
                    existing_records[row['url']] = row
                print(f"已从输出文件中读取 {len(existing_records)} 条已处理的记录")
        except Exception as e:
            print(f"读取已处理记录时出错: {e}")
            existing_records = {}
    
    # 对所有URL进行处理
    print(f"需要处理 {len(df)} 条记录")
    
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
                # 检查是否已有URL的记录
                if url in existing_records:
                    print("  - 已有URL，跳过模型分析，仅更新元数据")
                    # 使用已有记录的车辆信息
                    existing_record = existing_records[url]
                    result = {
                        'url': url,
                        'year': existing_record['year'],
                        'make': existing_record['make'],
                        'model': existing_record['model'],
                        'miles': existing_record['miles'],
                        'price': existing_record['price'],
                        'trade_type': existing_record['trade_type'],
                        'location': existing_record['location']
                    }
                else:
                    # 新URL需要调用大模型分析
                    try:
                        print("  - 提取车辆信息...")
                        result = analyze_car_info(description, use_mock=use_mock)
                        print(f"  - 提取结果: {result}")
                        
                        # 构建结果字典
                        result['url'] = url
                    except Exception as e:
                        print(f"  ! 处理失败: {e}")
                        result = {
                            'url': url,
                            'year': '-',
                            'make': '-',
                            'model': '-',
                            'miles': '-',
                            'price': '-',
                            'trade_type': '-',
                            'location': '洛杉矶'
                        }
            
            # 从 post.xlsx 中获取 post_time
            if post_df is not None:
                post_info = post_df[post_df['url'] == url]
                if not post_info.empty:
                    post_time = post_info.iloc[0]['post_time']
                    if pd.notna(post_time):
                        result['post_time'] = post_time
                    else:
                        result['post_time'] = pd.Timestamp('2020-01-01')  # 如果为空设置为2020年1月1日
                else:
                    result['post_time'] = pd.Timestamp('2020-01-01')  # 如果查询不到设置为2020年1月1日
            else:
                result['post_time'] = pd.Timestamp('2020-01-01')  # 如果post.xlsx不存在设置为2020年1月1日
            
            # 从 update.xlsx 中获取 scraping_time_R, title, author, author_link
            if update_df is not None:
                # 按照url分组，然后找出每组中最新的scraping_time_R的记录
                update_info = update_df[update_df['url'] == url]
                if not update_info.empty:
                    # 找出最新的记录
                    latest_update = update_info.loc[update_info['scraping_time_R'].idxmax()]
                    
                    if pd.notna(latest_update['scraping_time_R']):
                        result['scraping_time_R'] = latest_update['scraping_time_R']
                    else:
                        result['scraping_time_R'] = None
                    
                    if pd.notna(latest_update['title']):
                        result['title'] = latest_update['title']
                    else:
                        result['title'] = None
                    
                    if pd.notna(latest_update['author']):
                        result['author'] = latest_update['author']
                    else:
                        result['author'] = None
                    
                    if pd.notna(latest_update['author_link']):
                        result['author_link'] = latest_update['author_link']
                    else:
                        result['author_link'] = None
                else:
                    result['scraping_time_R'] = None
                    result['title'] = None
                    result['author'] = None
                    result['author_link'] = None
            else:
                result['scraping_time_R'] = None
                result['title'] = None
                result['author'] = None
                result['author_link'] = None
            
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
        
        # 保存总结果到输出文件
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