#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
创建测试状态文件

此脚本用于创建测试状态文件，方便验证API功能
"""

import json
import os
import datetime

# 确保目录存在
os.makedirs('tmp', exist_ok=True)
os.makedirs('logs', exist_ok=True)

# 创建模拟的状态数据
now = datetime.datetime.now()
ten_minutes_ago = now - datetime.timedelta(minutes=10)

# 模拟一个更新完成的状态
status = {
    "status": "success",
    "start_time": ten_minutes_ago.isoformat(),
    "end_time": now.isoformat(),
    "message": "更新成功完成",
    "steps": {
        "数据预处理": {
            "status": "完成",
            "start_time": ten_minutes_ago.isoformat(),
            "end_time": (ten_minutes_ago + datetime.timedelta(minutes=2)).isoformat()
        },
        "数据分析": {
            "status": "完成",
            "start_time": (ten_minutes_ago + datetime.timedelta(minutes=2)).isoformat(),
            "end_time": (ten_minutes_ago + datetime.timedelta(minutes=4)).isoformat()
        },
        "数据导入": {
            "status": "完成",
            "start_time": (ten_minutes_ago + datetime.timedelta(minutes=4)).isoformat(),
            "end_time": (ten_minutes_ago + datetime.timedelta(minutes=7)).isoformat()
        },
        "词云生成": {
            "status": "完成",
            "start_time": (ten_minutes_ago + datetime.timedelta(minutes=7)).isoformat(), 
            "end_time": (ten_minutes_ago + datetime.timedelta(minutes=8)).isoformat()
        },
        "数据备份": {
            "status": "完成",
            "start_time": (ten_minutes_ago + datetime.timedelta(minutes=8)).isoformat(),
            "end_time": (ten_minutes_ago + datetime.timedelta(minutes=9)).isoformat()
        }
    }
}

# 保存状态文件
with open('tmp/db_update_status.json', 'w', encoding='utf-8') as f:
    json.dump(status, f, ensure_ascii=False, indent=2)

print(f"已创建测试状态文件: tmp/db_update_status.json")

# 创建模拟的日志文件
log_content = """
2023-03-10 15:00:00 - INFO - 开始执行数据库更新
2023-03-10 15:00:01 - INFO - 开始执行数据预处理步骤
2023-03-10 15:00:30 - INFO - 处理新发帖数据完成
2023-03-10 15:01:00 - INFO - 处理帖子更新数据完成
2023-03-10 15:01:30 - INFO - 处理帖子详情数据完成
2023-03-10 15:02:00 - INFO - 生成帖子动态记录完成
2023-03-10 15:02:30 - INFO - 处理车辆信息数据完成
2023-03-10 15:02:31 - INFO - 数据预处理步骤完成
2023-03-10 15:02:32 - INFO - 开始执行数据分析步骤
2023-03-10 15:03:30 - INFO - 数据分析完成
2023-03-10 15:04:00 - INFO - 数据质量测试完成
2023-03-10 15:04:31 - INFO - 数据分析步骤完成
2023-03-10 15:04:32 - INFO - 开始执行数据导入步骤
2023-03-10 15:05:00 - INFO - 数据库备份完成
2023-03-10 15:06:30 - INFO - 数据导入完成
2023-03-10 15:07:00 - INFO - 检查数据库结构完成
2023-03-10 15:07:31 - INFO - 数据导入步骤完成
2023-03-10 15:07:32 - INFO - 开始执行词云生成步骤
2023-03-10 15:08:30 - INFO - 生成词云数据完成
2023-03-10 15:08:31 - INFO - 词云生成步骤完成
2023-03-10 15:08:32 - INFO - 开始执行数据备份步骤
2023-03-10 15:09:30 - INFO - 创建完整备份完成
2023-03-10 15:09:31 - INFO - 数据备份步骤完成
2023-03-10 15:09:32 - INFO - 数据库更新成功完成
"""

log_filename = f"auto_update_db_{now.strftime('%Y%m%d_%H%M%S')}.log"
with open(f"logs/{log_filename}", 'w', encoding='utf-8') as f:
    f.write(log_content)

print(f"已创建测试日志文件: logs/{log_filename}")

# 默认不创建锁文件
create_lock = False

if create_lock:
    with open('tmp/db_update.lock', 'w', encoding='utf-8') as f:
        f.write(now.isoformat())
    print("已创建锁文件: tmp/db_update.lock")
else:
    # 确保没有锁文件
    if os.path.exists('tmp/db_update.lock'):
        os.remove('tmp/db_update.lock')
        print("已删除现有锁文件")

print("测试数据创建完成!") 