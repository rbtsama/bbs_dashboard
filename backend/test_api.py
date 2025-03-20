#!/usr/bin/env python
"""
测试API返回数据
"""

import requests
import json
import sys
from pprint import pprint

def test_api(url):
    """测试API并打印结果"""
    print(f"测试API: {url}")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            print(json.dumps(data, indent=2, ensure_ascii=False))
            return data
        else:
            print(f"错误: {response.status_code}, {response.text}")
    except Exception as e:
        print(f"请求出错: {str(e)}")
    print("-" * 50)

def test_post_rank_api():
    """测试帖子排行榜API"""
    try:
        # 测试默认参数
        print("测试默认参数:")
        response = requests.get("http://localhost:5000/api/post-rank")
        if response.status_code == 200:
            data = response.json()
            print(f"API返回状态码: {response.status_code}")
            print(f"返回数据结构: {type(data)}")
            if isinstance(data, dict):
                print(f"顶层键: {list(data.keys())}")
                if 'data' in data:
                    print(f"data字段类型: {type(data['data'])}")
                    print(f"data字段长度: {len(data['data'])}")
                    if data['data'] and len(data['data']) > 0:
                        print("第一条记录:")
                        pprint(data['data'][0])
                    else:
                        print("data字段为空")
                else:
                    print("返回数据中没有data字段")
            else:
                print(f"返回数据不是字典: {data}")
        else:
            print(f"API请求失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
        
        # 测试分页参数
        print("\n测试分页参数 (page=2, limit=5):")
        response = requests.get("http://localhost:5000/api/post-rank", params={
            "page": 2,
            "limit": 5
        })
        if response.status_code == 200:
            data = response.json()
            print(f"API返回状态码: {response.status_code}")
            if isinstance(data, dict) and 'data' in data:
                print(f"data字段长度: {len(data['data'])}")
                print(f"页码信息: page={data.get('page', 'N/A')}, limit={data.get('limit', 'N/A')}, total={data.get('total', 'N/A')}")
                if data['data'] and len(data['data']) > 0:
                    print("第一条记录:")
                    pprint(data['data'][0])
            else:
                print(f"返回数据结构不符合预期: {data}")
        else:
            print(f"API请求失败，状态码: {response.status_code}")
        
        # 测试排序参数
        print("\n测试排序参数 (sort_field=reply_count, sort_order=desc):")
        response = requests.get("http://localhost:5000/api/post-rank", params={
            "sort_field": "reply_count",
            "sort_order": "desc",
            "limit": 5
        })
        if response.status_code == 200:
            data = response.json()
            print(f"API返回状态码: {response.status_code}")
            if isinstance(data, dict) and 'data' in data and data['data']:
                print(f"data字段长度: {len(data['data'])}")
                print("前5条记录的reply_count值:")
                for i, item in enumerate(data['data'][:5]):
                    print(f"  {i+1}. {item.get('reply_count', 'N/A')}")
            else:
                print(f"返回数据结构不符合预期或为空: {data}")
        else:
            print(f"API请求失败，状态码: {response.status_code}")
    
    except Exception as e:
        print(f"测试API时出错: {e}")

if __name__ == "__main__":
    base_url = "http://localhost:5000/api"
    
    # 测试更新趋势API
    update_trend = test_api(f"{base_url}/update-trend")
    
    # 如果有数据，显示统计信息
    if update_trend and 'data' in update_trend and update_trend['data']:
        data = update_trend['data']
        print(f"更新趋势数据项数: {len(data)}")
        
        # 统计不同类型的更新数据
        type_counts = {}
        for item in data:
            if 'type' in item:
                type_name = item['type']
                if type_name not in type_counts:
                    type_counts[type_name] = 0
                type_counts[type_name] += int(item.get('count', 0))
        
        print("各类型更新总数:")
        for type_name, count in type_counts.items():
            print(f"  {type_name}: {count}次")
    
    # 测试数据趋势API
    data_trends = test_api(f"{base_url}/data-trends")
    
    # 如果有合并数据，显示统计信息
    if data_trends and 'data' in data_trends and 'combined' in data_trends['data']:
        combined = data_trends['data']['combined']
        print(f"合并趋势数据项数: {len(combined)}")
        
        # 统计不同类型的数据
        type_counts = {}
        for item in combined:
            if 'type' in item:
                type_name = item['type']
                if type_name not in type_counts:
                    type_counts[type_name] = 0
                type_counts[type_name] += int(item.get('count', 0))
        
        print("各类型总数:")
        for type_name, count in type_counts.items():
            print(f"  {type_name}: {count}次")

    test_post_rank_api() 