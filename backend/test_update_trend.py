#!/usr/bin/env python
"""
专门测试更新趋势API
"""

import requests
import json
import sys

def test_update_trend_api():
    """测试更新趋势API并分析结果"""
    url = "http://localhost:5000/api/update-trend"
    print(f"测试API: {url}")
    try:
        response = requests.get(url)
        data = response.json()
        
        if 'data' in data and data['data']:
            items = data['data']
            print(f"API返回数据项数: {len(items)}")
            
            # 按日期分组
            by_date = {}
            by_type = {}
            
            for item in items:
                date = item.get('datetime', '')
                type_name = item.get('type', '')
                count = int(item.get('count', 0))
                
                # 按日期统计
                if date not in by_date:
                    by_date[date] = {}
                if type_name not in by_date[date]:
                    by_date[date][type_name] = 0
                by_date[date][type_name] += count
                
                # 按类型统计
                if type_name not in by_type:
                    by_type[type_name] = 0
                by_type[type_name] += count
            
            print("按日期和类型统计:")
            for date, types in by_date.items():
                print(f"  {date}:", end=" ")
                for type_name, count in types.items():
                    print(f"{type_name}={count}", end=" ")
                print()
            
            print("\n按类型统计总数:")
            for type_name, count in by_type.items():
                print(f"  {type_name}: {count}次")
            
            # 检查数据问题
            print("\n数据分析:")
            
            # 检查type字段
            all_types = set(item.get('type', '') for item in items)
            print(f"数据中出现的type值: {all_types}")
            
            # 检查是否有中文类型名(重发/回帖/删回帖)
            cn_types = {'重发', '回帖', '删回帖'}
            if not any(t in cn_types for t in all_types):
                print("警告: 未找到中文类型名(重发/回帖/删回帖)，这可能是问题所在")
            
            # 检查是否为每天每种类型都有数据
            dates = sorted(by_date.keys())
            print(f"总共有{len(dates)}个日期的数据")
            
            for date in dates:
                types = by_date[date].keys()
                if 'update' in types and len(types) == 1:
                    print(f"警告: {date}只有'update'类型，缺少详细类型分类")
        else:
            print("API返回的数据为空或格式不正确")
    except Exception as e:
        print(f"测试更新趋势API出错: {str(e)}")

if __name__ == "__main__":
    test_update_trend_api() 