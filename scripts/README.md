# 数据库自动更新脚本

本目录包含用于自动化数据库更新流程的PowerShell脚本。

## 文件说明

- `auto_update_db.ps1` - 主执行脚本，执行完整的数据库更新流程
- `register_scheduled_task.ps1` - 用于注册Windows计划任务的脚本

## 使用方法

### 设置自动更新计划任务

1. 以管理员身份打开PowerShell
2. 导航到项目根目录
3. 执行以下命令：

```powershell
.\scripts\register_scheduled_task.ps1
```

此命令会创建一个名为"BBS数据库每日更新"的Windows计划任务，设置为每天凌晨3点（加州时间）自动执行。脚本会自动计算时区差异，确保在正确的时间执行。

### 手动执行更新流程

如需手动执行完整的数据库更新流程，可以按以下步骤操作：

1. 打开PowerShell
2. 导航到项目根目录
3. 执行以下命令：

```powershell
.\scripts\auto_update_db.ps1
```

### 查看更新日志

执行日志保存在项目的 `logs` 目录中，命名格式为 `auto_update_db_YYYYMMDD_HHMMSS.log`。

## 自动更新流程

自动更新流程包括以下步骤：

1. **数据预处理**
   - 处理新发帖数据（post.py）
   - 处理帖子更新数据（update.py）
   - 处理帖子详情数据（detail.py）
   - 生成帖子动态记录（action.py）
   - 处理车辆信息数据（car_info.py）

2. **数据分析**
   - 执行数据分析（analysis.py）
   - 执行数据质量测试（test_data_quality.py）

3. **数据导入**
   - 执行数据库更新（update_db.py）
   - 检查数据库结构（check_db_structure.py）

4. **词云生成**
   - 生成词云数据（generate_wordcloud.py）

5. **数据备份**
   - 创建数据库备份（backup_db.py）

## 故障排除

如果自动更新过程中遇到问题，请检查：

1. **计划任务未执行**
   - 在任务计划程序中查看任务状态和历史记录
   - 确认计算机在计划执行时间处于开机状态

2. **脚本执行错误**
   - 查看日志文件了解具体错误原因
   - 确保所有依赖的Python模块已安装
   - 检查文件路径和权限

3. **数据处理问题**
   - 验证原始数据文件是否存在且格式正确
   - 检查Python环境和依赖库版本

## 更多信息

详细的自动更新流程文档请参考：[数据库自动更新流程](../docs/db_automated_updates.md) 