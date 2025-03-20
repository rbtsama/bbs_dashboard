import requests
import json
from pprint import pprint

def test_post_rank():
    """测试帖子排行榜API"""
    try:
        print("测试帖子排行榜API...")
        response = requests.get("http://localhost:5000/api/post-rank")
        
        if response.status_code == 200:
            data = response.json()
            print(f"API返回状态码: {response.status_code}")
            print(f"返回数据类型: {type(data)}")
            
            if isinstance(data, dict):
                print(f"顶层键: {list(data.keys())}")
                
                if 'data' in data:
                    print(f"data字段类型: {type(data['data'])}")
                    print(f"data字段长度: {len(data['data'])}")
                    
                    if data['data'] and len(data['data']) > 0:
                        print("\n第一条记录:")
                        pprint(data['data'][0])
                    else:
                        print("data字段为空")
                else:
                    print("返回数据中没有data字段")
                
                # 打印分页信息
                if 'page' in data:
                    print(f"\n分页信息:")
                    print(f"  页码: {data.get('page')}")
                    print(f"  每页记录数: {data.get('limit')}")
                    print(f"  总记录数: {data.get('total')}")
            else:
                print(f"返回数据不是字典: {data}")
        else:
            print(f"API请求失败，状态码: {response.status_code}")
            print(f"错误信息: {response.text}")
    
    except Exception as e:
        print(f"测试API时出错: {e}")

if __name__ == "__main__":
    test_post_rank() 