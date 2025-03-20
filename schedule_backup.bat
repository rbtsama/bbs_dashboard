@echo off
REM 关注数据定期备份脚本
REM 建议通过Windows任务计划程序设置定期执行此脚本

echo 开始执行关注数据备份...
echo 当前时间: %date% %time%

REM 切换到项目根目录
cd /d %~dp0

REM 执行备份脚本
python backup_follows.py

echo 备份完成！
echo ----------------------------- 