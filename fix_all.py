import os
import subprocess
import time
from datetime import datetime

print("=" * 50)
print("数据库全面修复工具")
print("=" * 50)
print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print()

# 检查是否有后端服务运行
print("检查后端服务是否正在运行...")
try:
    import psutil
    python_processes = []
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] == 'python.exe' or proc.info['name'] == 'python':
                cmdline = ' '.join(proc.info['cmdline'])
                if 'app.py' in cmdline:
                    python_processes.append((proc.info['pid'], cmdline))
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    if python_processes:
        print("警告: 检测到后端服务正在运行。")
        print("后端进程:")
        for pid, cmdline in python_processes:
            print(f"PID: {pid}, 命令: {cmdline}")
        print("\n为避免冲突，建议先停止后端服务再继续修复。")
        confirm = input("是否继续修复？(y/n): ")
        if confirm.lower() != 'y':
            print("修复操作已取消")
            exit(0)
    else:
        print("未检测到运行中的后端服务")
except ImportError:
    print("无法检查后端服务状态，缺少psutil模块")

# 步骤1：备份当前关注数据
print("\n步骤1: 备份当前关注数据")
print("-" * 50)
try:
    # 确保备份目录存在
    os.makedirs(os.path.join('backend', 'backups', 'follows'), exist_ok=True)
    
    # 备份数据
    print("执行备份脚本...")
    subprocess.run(['python', 'backup_follows.py'], check=True)
    print("备份完成")
except Exception as e:
    print(f"备份过程中出错: {e}")
    print("继续执行修复...")

# 步骤2：修复排序问题
print("\n步骤2: 修复排序问题")
print("-" * 50)
try:
    print("执行排序修复脚本...")
    subprocess.run(['python', 'fix_sorting.py'], check=True)
    print("排序修复完成")
except Exception as e:
    print(f"排序修复过程中出错: {e}")

# 步骤3：修复关注表
print("\n步骤3: 修复关注表")
print("-" * 50)
try:
    print("执行关注表修复脚本...")
    subprocess.run(['python', 'fix_follows.py'], check=True)
    print("关注表修复完成")
except Exception as e:
    print(f"关注表修复过程中出错: {e}")

# 步骤4：更新数据库工具配置
print("\n步骤4: 验证数据库更新工具配置")
print("-" * 50)
try:
    # 检查update_db.py文件
    update_db_path = os.path.join('py', 'update_db.py')
    with open(update_db_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if "self.protected_tables = ['wordcloud_cache', 'user_data', 'thread_follow']" in content:
        print("数据库更新工具配置正确，thread_follow表已在保护列表中")
    else:
        print("警告: 数据库更新工具配置中未发现thread_follow在保护列表中")
        print("请手动编辑py/update_db.py文件，确保thread_follow在protected_tables列表中")
except Exception as e:
    print(f"验证数据库更新工具配置时出错: {e}")

# 总结
print("\n=" * 25)
print("修复操作完成")
print("=" * 25)
print(f"结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("\n修复完成后，建议重启后端服务以应用所有更改")
print("如需恢复备份数据，可以运行: python restore_follows.py")
print("\n建议将以下脚本添加到定期任务中，确保数据安全:")
print("- backup_follows.py (定期备份关注数据)")
print("- fix_follows.py (在数据库更新后运行，确保关注表结构正确)")
print("- fix_sorting.py (在数据库更新后运行，确保排序正确)")
print("\n感谢使用数据库修复工具！") 