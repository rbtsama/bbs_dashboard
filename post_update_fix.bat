@echo off
REM 数据库更新后修复脚本
REM 建议在每次数据库更新完成后执行此脚本

echo 开始执行数据库更新后修复...
echo 当前时间: %date% %time%

REM 切换到项目根目录
cd /d %~dp0

REM 备份关注数据
echo 步骤1: 备份关注数据
python backup_follows.py

REM 修复排序问题
echo 步骤2: 修复排序问题
python fix_sorting.py

REM 修复关注表
echo 步骤3: 修复关注表
python fix_follows.py

echo 修复完成！
echo -----------------------------
pause 