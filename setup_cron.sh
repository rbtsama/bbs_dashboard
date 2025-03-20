#!/bin/bash
# 设置定时任务，在加州时间(PT)半夜3点执行数据更新

# 获取当前脚本的绝对路径
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# 创建临时crontab文件
TMP_CRON=$(mktemp)

# 导出当前的crontab内容
crontab -l > "$TMP_CRON" 2>/dev/null || echo "# 创建新的crontab文件" > "$TMP_CRON"

# 检查是否已经有相同的任务
if ! grep -q "update_db.py" "$TMP_CRON"; then
    # 添加数据更新任务 (每天加州时间凌晨3点，即UTC时间10:00或11:00，取决于夏令时)
    echo "# 数据库每日更新任务 - 加州时间凌晨3点" >> "$TMP_CRON"
    echo "0 3 * * * cd $SCRIPT_DIR && python py/update_db.py >> logs/update_cron.log 2>&1" >> "$TMP_CRON"
    echo "任务已添加: 每天加州时间凌晨3点执行数据库更新"
else
    echo "数据库更新任务已存在"
fi

# 检查是否已经有备份任务
if ! grep -q "backup_db.py" "$TMP_CRON"; then
    # 添加数据库备份任务 (每天加州时间凌晨2点)
    echo "# 数据库每日备份任务 - 加州时间凌晨2点" >> "$TMP_CRON"
    echo "0 2 * * * cd $SCRIPT_DIR && python py/backup_db.py >> logs/backup_cron.log 2>&1" >> "$TMP_CRON"
    echo "任务已添加: 每天加州时间凌晨2点执行数据库备份"
else
    echo "数据库备份任务已存在"
fi

# 检查是否已经有词云生成任务
if ! grep -q "generate_wordcloud.py" "$TMP_CRON"; then
    # 添加词云生成任务 (每天加州时间凌晨4点)
    echo "# 词云生成任务 - 加州时间凌晨4点" >> "$TMP_CRON"
    echo "0 4 * * * cd $SCRIPT_DIR && python py/generate_wordcloud.py >> logs/wordcloud_cron.log 2>&1" >> "$TMP_CRON"
    echo "任务已添加: 每天加州时间凌晨4点执行词云生成"
else
    echo "词云生成任务已存在"
fi

# 应用新的crontab
crontab "$TMP_CRON"
rm "$TMP_CRON"

echo "定时任务设置完成！"
echo "可以运行 'crontab -l' 查看当前任务" 