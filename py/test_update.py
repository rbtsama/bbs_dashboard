import os
import json
import time
import sys
from datetime import datetime

# 设置控制台输出编码为UTF-8
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

def create_test_status():
    """创建测试状态文件"""
    status = {
        "status": "success",
        "start_time": datetime.now().isoformat(),
        "end_time": datetime.now().isoformat(),
        "message": "测试更新成功",
        "steps": {
            "数据预处理": {
                "status": "完成",
                "start_time": datetime.now().isoformat(),
                "end_time": datetime.now().isoformat()
            }
        }
    }
    
    # 确保tmp目录存在
    if not os.path.exists("tmp"):
        os.makedirs("tmp")
        
    # 写入状态文件
    with open("tmp/db_update_status.json", "w", encoding="utf-8") as f:
        json.dump(status, f, ensure_ascii=False, indent=2)
        
    print("测试状态文件已创建")

if __name__ == "__main__":
    create_test_status() 