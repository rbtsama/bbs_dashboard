# 数据处理流程

## 处理步骤

### 1. 数据采集
- 论坛帖子列表：每2小时抓取一次，生成 `bbs_post_list_YYYYMMDD.xlsx`
- 论坛更新列表：每15分钟抓取一次，生成 `bbs_update_list_YYYYMMDD.xlsx`
- 帖子详情内容：每2小时抓取一次，生成 `bbs_update_detail_YYYYMMDD.xlsx`

### 2. 数据预处理
处理脚本包括：
- `py/post.py`: 处理新发帖数据，生成 `post.xlsx`
  - 特殊处理：23:45之后的抓取时间统一设置为23:45，避免数据跨天
  - 时间处理：scraping_time_R 使用四舍五入到15分钟
- `py/update.py`: 处理帖子更新数据，生成 `update.xlsx`（原list.py）
  - 特殊处理：23:45之后的抓取时间统一设置为23:45，避免数据跨天
  - 更新原因判断：重发、回帖、删回帖
- `py/detail.py`: 处理帖子详情数据，生成 `detail.xlsx`
  - 特殊处理：23:45之后的抓取时间统一设置为23:45，避免数据跨天
  - 时间处理：scraping_time_R 使用四舍五入到15分钟
  - 内容处理：合并title、tags等生成car_description
- `py/action.py`: 生成帖子动态记录，生成 `action.csv`
  - 更新数据源引用：使用update.xlsx替代list.xlsx
  - 使用scraping_time_R替代scraping_time作为action_time
- `py/car_info.py`: 处理车辆信息数据，生成 `car_info.csv`
  - 空值处理：所有"找不到"值统一改为"-"
  - 包括年份、品牌、型号、公里数、价格、需求等字段

### 3. 数据分析
- `py/analysis_final.py`: 最终版数据分析脚本
  - 时间序列分析
  - 用户行为分析
  - 帖子生命周期分析
- `py/analysis_fixed.py`: 修复版数据分析脚本
  - 修复了原analysis.py中的问题
  - 优化了分析性能
- `py/test_data_quality.py`: 数据质量测试
  - 数据完整性检查
  - 数据一致性验证
  - 异常值检测
  - 生成质量报告

### 4. 数据导入与更新
- `py/update_db.py`: 增量更新数据库
  - 创建临时数据库
  - 导入Excel和CSV数据
  - 数据格式验证和清洗
  - 执行SQL处理脚本
  - 数据一致性检查
  - 生成变更日志
  - 事务管理确保原子性
  - 应用更改到主数据库
  - 特殊字段处理：
    - 将post_ranking和author_ranking表中的repost_count和delete_reply_count字段转换为INTEGER类型
    - 确保词云表结构正确并在数据更新后生成新的词云数据

### 5. 数据库维护
- `py/backup_db.py`: 创建数据库备份
  - 定期备份数据库文件
  - 管理备份历史，保留最近30个备份
- `py/check_db_structure.py`: 检查数据库结构
  - 验证表结构和索引
  - 检查数据完整性
  - 检查行数统计
- `py/execute_sql.py`: 执行SQL脚本
  - 支持批量执行SQL文件
  - 错误处理和回滚机制
- `py/fix_limit_count.py`: 修复数量限制问题
  - 修复post_ranking和author_ranking表中repost_count字段的类型问题
  - 将TEXT类型字段转换为INTEGER类型
  - 确保数值正确比较
  - 修复重发数量限制为9的问题
- `py/fix_wordcloud.py`: 修复词云表结构
  - 检查词云表结构
  - 修复缺失的字段
  - 恢复词云数据
  - 确保与API兼容

### 6. 词云生成系统
- `py/generate_wordcloud.py`: 生成词云
  - 检查并确保词云表结构正确
  - 从update.xlsx中提取所有title
  - 使用jieba分词处理中文
  - 过滤停用词和单字词
  - 生成高质量JSON格式词云数据
  - 保存到wordcloud_cache表

## 数据处理规则

### 时间处理规则
所有模块统一使用以下时间处理逻辑：
1. 超过23:45的时间统一设置为23:45，避免数据跨天
2. scraping_time_R 使用四舍五入到15分钟（0,15,30,45）
3. 对于只有日期没有时间的记录，补充为当天00:00:00

### 空值处理规则
所有模块统一使用以下空值处理逻辑：
1. 文本类型字段：统一使用"-"表示空值
2. 数值类型字段：使用NULL或0（根据字段语义）
3. 时间类型字段：使用NULL
4. 删除含有'nan'的值

### 数据验证规则
1. **数据完整性检查**：
   - 必填字段不能为空
   - 外键约束检查
   - 唯一性约束检查

2. **数据一致性检查**：
   - 时间字段格式统一
   - 数值范围验证
   - 枚举值验证

3. **异常值检测**：
   - 数值字段范围检查
   - 时间字段合理性检查
   - 文本字段长度检查

## 错误处理机制

1. **数据导入错误**：
   - 记录详细错误信息
   - 支持部分导入回滚
   - 生成错误报告

2. **数据处理错误**：
   - 记录处理失败的记录
   - 支持断点续处理
   - 错误原因分析

3. **数据验证错误**：
   - 生成验证报告
   - 标记问题数据
   - 提供修复建议

## 监控和日志

1. **处理进度监控**：
   - 记录每个步骤的耗时
   - 统计处理记录数
   - 监控资源使用

2. **错误日志记录**：
   - 详细的错误堆栈
   - 错误发生时的上下文
   - 错误分类统计

3. **性能监控**：
   - 数据处理速度
   - 内存使用情况
   - CPU使用率

## 相关文档

- [数据库概览](./db_overview.md)
- [数据来源与采集](./db_data_sources.md)
- [数据表定义](./db_table_definitions.md)
- [增量数据更新](./db_incremental_updates.md)
- [数据版本控制](./db_version_control.md)
- [数据备份与恢复](./db_backup_recovery.md)
- [词云生成系统](./db_wordcloud_system.md) 