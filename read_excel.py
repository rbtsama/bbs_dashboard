import pandas as pd
import re
from datetime import datetime

def normalize_brand(brand):
    """统一品牌名称"""
    brand_mapping = {
        # 日系品牌
        'toyota': '丰田',
        'honda': '本田',
        'mazda': '马自达',
        'nissan': '尼桑',
        'lexus': '雷克萨斯',
        'acura': '讴歌',
        'infiniti': '英菲尼迪',
        'subaru': '斯巴鲁',
        'mitsubishi': '三菱',
        
        # 韩系品牌
        'hyundai': '现代',
        'kia': '起亚',
        'genesis': '捷尼赛思',
        
        # 德系品牌
        'bmw': '宝马',
        'benz': '奔驰',
        'mercedes': '奔驰',
        'mercedes-benz': '奔驰',
        'merc': '奔驰',
        'volkswagen': '大众',
        'vw': '大众',
        'audi': '奥迪',
        'porsche': '保时捷',
        
        # 美系品牌
        'ford': '福特',
        'chevrolet': '雪佛兰',
        'chevy': '雪佛兰',
        'chrysler': '克莱斯勒',
        'dodge': '道奇',
        'jeep': '吉普',
        'cadillac': '凯迪拉克',
        'buick': '别克',
        'lincoln': '林肯',
        'tesla': '特斯拉',
        
        # 英系品牌
        'land rover': '路虎',
        'jaguar': '捷豹',
        'bentley': '宾利',
        'mini': '迷你',
        'rolls-royce': '劳斯莱斯',
        
        # 其他品牌
        'volvo': '沃尔沃',
        'maserati': '玛莎拉蒂',
        'alfa romeo': '阿尔法·罗密欧',
        
        # 常见别名
        '日产': '尼桑',
        'bimmer': '宝马',
    }
    
    if not brand:
        return None
        
    brand = brand.lower().strip()
    return brand_mapping.get(brand, brand)

def normalize_model(model, brand=None):
    """统一车型名称"""
    model_mapping = {
        # 丰田
        'corolla': 'Corolla',
        'camry': 'Camry',
        'rav4': 'RAV4',
        'rv4': 'RAV4',
        'highlander': 'Highlander',
        'sienna': 'Sienna',
        'prius': 'Prius',
        '卡罗拉': 'Corolla',
        '凯美瑞': 'Camry',
        '汉兰达': 'Highlander',
        '普拉多': 'Prado',
        '普锐斯': 'Prius',
        '塞纳': 'Sienna',
        '兰德酷路泽': 'Land Cruiser',
        
        # 本田
        'accord': 'Accord',
        'civic': 'Civic',
        'cr-v': 'CR-V',
        'crv': 'CR-V',
        'hr-v': 'HR-V',
        'hrv': 'HR-V',
        'odyssey': 'Odyssey',
        '雅阁': 'Accord',
        '思域': 'Civic',
        '飞度': 'Fit',
        '奥德赛': 'Odyssey',
        
        # 尼桑
        'sentra': 'Sentra',
        'altima': 'Altima',
        'maxima': 'Maxima',
        'rogue': 'Rogue',
        'murano': 'Murano',
        'pathfinder': 'Pathfinder',
        '轩逸': 'Sentra',
        '天籁': 'Maxima',
        '奇骏': 'Rogue',
        '楼兰': 'Murano',
        '大suv': 'Pathfinder',
        
        # 雷克萨斯
        'rx': 'RX',
        'nx': 'NX',
        'es': 'ES',
        'is': 'IS',
        'gs': 'GS',
        'gx': 'GX',
        'lx': 'LX',
        'ct': 'CT',
        
        # 马自达
        'mazda3': 'Mazda3',
        'mazda6': 'Mazda6',
        'cx-5': 'CX-5',
        'cx5': 'CX-5',
        'cx-9': 'CX-9',
        'cx9': 'CX-9',
        '阿特兹': 'Mazda6',
    }
    
    if not model:
        return None
        
    # 处理型号中的空格和大小写
    model = model.lower().strip()
    base_model = model.split()[0]  # 获取基本型号（不含子型号）
    
    # 获取标准化的基本型号
    normalized_base = model_mapping.get(base_model, base_model)
    
    # 如果有子型号，保留它
    if len(model.split()) > 1:
        sub_model = ' '.join(model.split()[1:])
        return f"{normalized_base} {sub_model.upper()}"
    
    return normalized_base

def extract_year(text):
    """提取年份"""
    current_year = datetime.now().year
    
    # 处理"XXXX年"格式
    year_pattern = r'(?:20)?(\d{2})年'
    match = re.search(year_pattern, text)
    if match:
        year = int(match.group(1))
        if year < 50:  # 假设50以下是20XX年
            return 2000 + year
        return 1900 + year
    
    # 处理纯数字年份
    year_pattern2 = r'\b(19|20)\d{2}\b'
    match = re.search(year_pattern2, text)
    if match:
        year = int(match.group(0))
        if 1990 <= year <= current_year + 1:  # 合理的年份范围
            return year
    
    return None

def extract_car_info(text):
    """从文本中提取车辆信息"""
    # 提取年份
    year = extract_year(text)
    
    # 提取品牌
    brands_pattern = r'(?:丰田|本田|马自达|雷克萨斯|奔驰|宝马|日产|尼桑|大众|福特|现代|起亚|沃尔沃|路虎|保时捷|奥迪|雪佛兰|克莱斯勒|道奇|吉普|凯迪拉克|别克|林肯|特斯拉|捷豹|宾利|迷你|玛莎拉蒂|Toyota|Honda|Mazda|Lexus|Mercedes|BMW|Nissan|Volkswagen|VW|Ford|Hyundai|Kia|Volvo|Land Rover|Porsche|Audi|Chevrolet|Chrysler|Dodge|Jeep|Cadillac|Buick|Lincoln|Tesla|Jaguar|Bentley|Mini|Maserati)'
    brand_match = re.search(brands_pattern, text, re.IGNORECASE)
    make = normalize_brand(brand_match.group(0)) if brand_match else None
    
    # 提取型号
    models_pattern = r'(?:Corolla|Camry|RAV4|RV4|Highlander|Sienna|Prius|Land Cruiser|Accord|Civic|CR-V|CRV|HR-V|HRV|Odyssey|Sentra|Altima|Maxima|Rogue|Murano|Pathfinder|RX|NX|ES|IS|GS|GX|LX|CT|Mazda3|Mazda6|CX-5|CX5|CX-9|CX9|卡罗拉|凯美瑞|汉兰达|普拉多|普锐斯|塞纳|雅阁|思域|飞度|奥德赛|轩逸|天籁|奇骏|楼兰|阿特兹)(?:\s+(?:XLE|XSE|LE|SE|Sport|Limited|Touring|Premium|L|S|SV|SL|F-Sport|Luxury|Advanced|Elite|EX|EX-L|LX|Signature))?'
    model_match = re.search(models_pattern, text, re.IGNORECASE)
    model = normalize_model(model_match.group(0), make) if model_match else None
    
    return year, make, model

def analyze_excel():
    try:
        # 读取Excel文件
        df = pd.read_excel('data/processed/detail.xlsx')
        
        # 打印基本信息
        print("\n=== 数据基本信息 ===")
        print(f"总行数: {len(df)}")
        
        # 分析标题和内容中的车辆信息
        results = []
        for idx, row in df.iterrows():
            title = str(row['title'])
            content = str(row['content'])
            car_desc = str(row['car_description'])
            
            # 合并所有文本
            full_text = f"{title} {content} {car_desc}"
            
            # 提取车辆信息
            year, make, model = extract_car_info(full_text)
            
            results.append({
                'title': title,
                'year': year,
                'make': make,
                'model': model,
                'text': full_text[:200]  # 只显示前200个字符
            })
        
        # 转换为DataFrame
        results_df = pd.DataFrame(results)
        
        # 打印统计信息
        print("\n=== 字段统计 ===")
        for col in ['year', 'make', 'model']:
            non_null = results_df[col].notna().sum()
            print(f"{col} 非空值数量: {non_null} ({non_null/len(results_df)*100:.2f}%)")
        
        # 打印一些示例
        print("\n=== 随机样本 ===")
        sample_df = results_df.sample(n=5)
        for _, row in sample_df.iterrows():
            print("\n标题:", row['title'])
            print(f"年份: {row['year'] if pd.notna(row['year']) else '-'}")
            print(f"品牌: {row['make'] if pd.notna(row['make']) else '-'}")
            print(f"型号: {row['model'] if pd.notna(row['model']) else '-'}")
            print("文本片段:", row['text'][:100])
        
        # 分析常见模式
        print("\n=== 常见描述模式 ===")
        patterns = {
            '年份+品牌': r'\d{2,4}年[^,，。]*(?:丰田|本田|马自达|雷克萨斯|奔驰|宝马)',
            '品牌+型号': r'(?:丰田|本田|马自达|雷克萨斯|奔驰|宝马)[^,，。]*(?:凯美瑞|卡罗拉|RAV4|思域|雅阁)',
            '英文品牌': r'(?:Toyota|Honda|Mazda|Lexus|Mercedes|BMW)[^,，。]*',
            '价格信息': r'(?:\d+[万k千]|\$\d+(?:,\d{3})*)',
            '里程信息': r'\d+[万k千]?(?:Mile|迈|英里)',
        }
        
        for pattern_name, pattern in patterns.items():
            matches = sum(1 for text in results_df['text'] if re.search(pattern, text))
            print(f"{pattern_name}: {matches} 条 ({matches/len(results_df)*100:.2f}%)")
        
        # 保存结果
        results_df.to_excel('data/processed/car_info_extracted.xlsx', index=False)
        print("\n结果已保存到 data/processed/car_info_extracted.xlsx")
        
    except Exception as e:
        print(f"错误: {str(e)}")

if __name__ == "__main__":
    analyze_excel() 