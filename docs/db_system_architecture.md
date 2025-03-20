# 系统架构

本文档描述系统的整体架构设计，包括系统组件、数据流和部署架构。

## 系统组件

系统由以下主要组件构成：

### 1. 数据采集模块

负责从论坛网站采集数据，包括：

- **帖子列表采集器**：定期采集论坛最新发布的帖子列表
- **更新列表采集器**：高频采集论坛最新回复的帖子列表
- **帖子详情采集器**：采集帖子的详细内容和回复

数据采集模块使用Python脚本实现，通过HTTP请求获取网页内容，使用BeautifulSoup等库解析HTML，提取所需数据。

### 2. 数据处理模块

负责对采集的原始数据进行处理，包括：

- **数据清洗**：去除HTML标签、特殊字符等
- **数据转换**：将时间字符串转换为标准格式，提取帖子ID等
- **数据合并**：合并来自不同来源的数据
- **数据去重**：去除重复数据

数据处理模块使用Python脚本实现，处理后的数据保存为标准格式的Excel文件。

### 3. 数据存储模块

负责管理系统的数据存储，包括：

- **SQLite数据库**：存储所有系统数据
- **版本控制**：管理数据版本和变更记录
- **增量更新**：支持数据的增量更新
- **备份恢复**：定期备份数据，支持数据恢复

数据存储模块使用SQLite作为数据库引擎，通过Python的sqlite3库进行操作。

### 4. 数据分析模块

负责对存储的数据进行分析，包括：

- **统计分析**：计算帖子活跃度、作者活跃度等统计指标
- **词云生成**：为作者和帖子生成词云，展示关键词分布
- **趋势分析**：分析帖子和作者的活跃趋势
- **车辆信息分析**：
  - 从帖子内容中提取车辆相关信息
  - 提供品牌型号的标准化处理
  - 统一格式化年份、里程和价格信息
  - 支持中英文车辆信息的智能识别和转换

数据分析模块使用Python实现，利用pandas进行数据处理，wordcloud生成词云，正则表达式和自然语言处理进行车辆信息提取。

### 5. 任务调度模块

负责管理系统的各种定时任务，包括：

- **数据采集任务**：定期触发数据采集
- **数据更新任务**：定期执行数据更新
- **数据备份任务**：定期备份数据库
- **词云生成任务**：处理词云生成请求

任务调度模块使用Windows计划任务实现，通过PowerShell脚本配置和管理任务。

### 6. API服务模块

提供系统功能的API接口，包括：

- **数据查询API**：查询帖子、作者等数据
- **词云生成API**：请求生成词云和获取词云状态
- **统计数据API**：获取统计数据和趋势数据
- **关注管理API**：管理帖子关注列表和查看更新历史

API服务模块使用Flask框架实现，提供RESTful API接口。

### 7. 关注系统模块

提供用户关注帖子的功能，包括：

- **关注管理**：添加和取消关注
- **关注列表**：查看用户的关注帖子列表和标记的帖子
- **更新历史**：查看关注帖子的更新历史
- **数据统计**：统计关注帖子的活跃度和变化趋势

关注系统模块通过前端组件和后端API紧密集成，确保用户能方便地管理和追踪关注的帖子。

## 数据流

系统的数据流如下：

```
+----------------+     +----------------+     +----------------+
|                |     |                |     |                |
|  数据采集模块   +---->+  数据处理模块   +---->+  数据存储模块   |
|                |     |                |     |                |
+----------------+     +----------------+     +-------+--------+
                                                     |
                                                     v
+----------------+     +----------------+     +------+--------+     +---------------+
|                |     |                |     |               |     |               |
|  API服务模块    |<----+  数据分析模块   |<----+  任务调度模块  |---->+  关注系统模块  |
|                |     |                |     |               |     |               |
+----------------+     +----------------+     +---------------+     +---------------+
```

1. **数据采集流程**：
   - 数据采集模块定期从论坛网站采集数据
   - 采集的原始数据保存为Excel文件

2. **数据处理流程**：
   - 数据处理模块读取原始Excel文件
   - 进行数据清洗、转换、合并和去重
   - 处理后的数据保存为标准格式的Excel文件

3. **数据存储流程**：
   - 数据存储模块读取处理后的Excel文件
   - 将数据导入临时数据库
   - 执行增量更新，将变更应用到主数据库
   - 记录数据版本和变更日志

4. **数据分析流程**：
   - 数据分析模块从数据库读取数据
   - 执行统计分析、词云生成等操作
   - 将分析结果存储到数据库

5. **API服务流程**：
   - API服务模块接收客户端请求
   - 从数据库查询数据或触发数据分析
   - 将结果返回给客户端

6. **关注系统流程**：
   - 关注系统模块接收用户请求
   - 处理关注管理、关注列表和更新历史等操作
   - 将结果返回给客户端

## 部署架构

系统采用单机部署架构，所有组件部署在同一台Windows服务器上：

```
+-------------------------------------------------------+
|                     Windows服务器                      |
|                                                       |
|  +----------------+        +---------------------+    |
|  |                |        |                     |    |
|  |  Python环境    |        |  SQLite数据库        |    |
|  |                |        |                     |    |
|  +-------+--------+        +----------+----------+    |
|          |                            |               |
|          v                            v               |
|  +-------+------------------------+---+----------+    |
|  |                                |              |    |
|  |  系统脚本和模块                 |  数据文件     |    |
|  |  (py/, sql/)                  |  (data/)     |    |
|  |                                |              |    |
|  +--------------------------------+--------------+    |
|                     |                                 |
|                     v                                 |
|  +------------------+-------------------+             |
|  |                                      |             |
|  |  Windows计划任务                     |             |
|  |  (任务调度)                          |             |
|  |                                      |             |
|  +--------------------------------------+             |
|                                                       |
+-------------------------------------------------------+
```

### 部署要求

1. **硬件要求**：
   - CPU: 双核及以上
   - 内存: 4GB及以上
   - 存储: 50GB及以上

2. **软件要求**：
   - 操作系统: Windows 10/11 或 Windows Server 2016/2019/2022
   - Python 3.8及以上
   - 必要的Python库: pandas, numpy, flask, wordcloud, jieba等

3. **网络要求**：
   - 稳定的互联网连接，用于数据采集
   - 如需远程访问API，需开放相应端口

### 部署步骤

1. **环境准备**：
   ```powershell
   # 安装必要的Python库
   pip install pandas numpy flask wordcloud jieba beautifulsoup4 requests openpyxl
   ```

2. **目录结构创建**：
   ```powershell
   # 创建必要的目录
   mkdir -Force logs, data\wordcloud\author, data\wordcloud\thread, data\config\fonts, backup\db
   ```

3. **数据库初始化**：
   ```powershell
   # 执行数据库初始化脚本
   python py/execute_sql.py sql/create_tables.sql
   python py/execute_sql.py sql/create_version_tables.sql
   ```

4. **计划任务设置**：
   ```powershell
   # 设置数据采集任务
   $action = New-ScheduledTaskAction -Execute "python" -Argument "py/collect_post_list.py"
   $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Hours 2)
   Register-ScheduledTask -TaskName "CollectPostList" -Action $action -Trigger $trigger
   
   # 设置数据更新任务
   $action = New-ScheduledTaskAction -Execute "python" -Argument "py/update_db.py"
   $trigger = New-ScheduledTaskTrigger -Daily -At "03:00"
   Register-ScheduledTask -TaskName "UpdateDatabase" -Action $action -Trigger $trigger
   
   # 设置数据备份任务
   $action = New-ScheduledTaskAction -Execute "powershell" -Argument "-File scripts/backup_db.ps1"
   $trigger = New-ScheduledTaskTrigger -Daily -At "04:00"
   Register-ScheduledTask -TaskName "BackupDatabase" -Action $action -Trigger $trigger
   
   # 设置词云处理任务
   $action = New-ScheduledTaskAction -Execute "python" -Argument "py/process_wordcloud.py"
   $trigger = New-ScheduledTaskTrigger -Once -At (Get-Date) -RepetitionInterval (New-TimeSpan -Minutes 60)
   Register-ScheduledTask -TaskName "ProcessWordCloud" -Action $action -Trigger $trigger
   ```

5. **API服务启动**：
   ```powershell
   # 启动API服务
   python py/api_server.py
   ```

## 系统扩展性

系统设计考虑了未来的扩展需求：

1. **多数据源支持**：
   - 系统可以扩展支持多个论坛或其他数据源
   - 只需添加相应的数据采集模块和数据处理逻辑

2. **分布式部署**：
   - 可以将数据采集、处理、存储和API服务分离部署
   - 支持更大规模的数据处理和更高的并发访问

3. **高级分析功能**：
   - 可以集成机器学习模块，实现情感分析、主题分类等功能
   - 可以添加更多可视化组件，提供更丰富的数据展示

4. **用户界面**：
   - 可以开发Web界面，提供更友好的用户交互
   - 支持数据可视化、报表生成等功能

## 相关文档

- [数据库概览](./db_overview.md)
- [数据源与采集](./db_data_sources.md)
- [数据处理流程](./db_data_processing.md)
- [增量数据更新](./db_incremental_updates.md)
- [数据版本控制](./db_version_control.md)
- [词云生成](./db_wordcloud_generation.md)
- [数据备份与恢复](./db_backup_recovery.md) 