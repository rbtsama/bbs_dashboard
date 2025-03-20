# 数据来源与采集

## 原始数据获取逻辑

论坛数据采集是通过专门的爬虫程序完成的，产生三类主要文件：

1. **论坛发帖列表爬取 (bbs_post_list_YYYYMMDD.xlsx)**
   - 爬取论坛"最新发布"页面的帖子
   - 每天爬取1-3次，捕获新发布的帖子
   - 文件按爬取日期命名，如`bbs_post_list_20250310.xlsx`
   - 关键字段：url, title, author, post_time_str, scraping_time_str

2. **论坛更新列表爬取 (bbs_update_list_YYYYMMDD.xlsx)**
   - 爬取论坛"最新回复"页面的帖子
   - 每天爬取3-6次，捕获被更新的帖子
   - 文件按爬取日期命名，如`bbs_update_list_20250310.xlsx`
   - 关键字段：url, title, author, list_time_str, scraping_time_str, read_count, reply_count

3. **帖子详情爬取 (bbs_update_detail_YYYYMMDD.xlsx)**
   - 爬取论坛帖子的详细内容页面
   - 每2小时爬取一次，获取帖子正文、回复内容等详情
   - 文件按爬取日期命名，如`bbs_update_detail_20250310.xlsx`
   - 关键字段：url, title, author, content, reply_list, post_time_str, scraping_time_str

## 源数据到处理后文件的转换逻辑

### post.xlsx 文件生成逻辑

1. 读取所有 `bbs_post_list_*.xlsx` 文件，提取所有帖子记录
2. 处理时间格式，统一为标准datetime格式
3. 计算 `scraping_time_R`（将时间向上取整到15分钟）
4. 对每个URL去重，保留最早的一条记录（首次发现记录）
5. 添加 source_file（来源文件）和 sheet_name（工作表名）字段用于溯源

### list.xlsx 文件生成逻辑

1. 读取所有 `bbs_update_list_*.xlsx` 文件，提取所有更新记录
2. 处理时间格式，统一为标准datetime格式
3. 计算 `scraping_time_R` 和 `list_time_R`（将时间向上取整到15分钟）
4. 计算 `update_reason` 字段，通过以下规则判断更新类型：
   - 如果序号(num)变化小于-5且当前序号<15：
     - 如果reply_count没变化：标记为"重发"
     - 如果reply_count增加：标记为"回帖"
   - 如果序号增加但reply_count减少：标记为"删回帖"
5. 保留所有记录，不去重，以保存更新历史
6. 添加 source_file 和 sheet_name 字段用于溯源

### detail.xlsx 文件生成逻辑

1. 读取所有 `bbs_update_detail_*.xlsx` 文件，提取所有详情记录
2. 确保字段类型：
   - title, tags, related_tags, content 转为字符串类型
3. 处理时间字段：
   - 将 scraping_time 转换为 datetime 类型
   - 计算 scraping_time_R：四舍五入到15分钟，23:45后统一设为23:45
4. 根据url去重，保留scraping_time最新的记录
5. 创建car_description字段：
   - 合并 title + tags + related_tags + content
   - 去除空值和'nan'值
6. 添加 source_file 和 sheet_name 字段用于溯源

### action.csv 文件生成逻辑

1. 读取已处理的 `post.xlsx` 和 `update.xlsx` 文件
2. 将两个数据源的记录合并，构建完整的帖子行为时间线
3. 从 `post.xlsx` 提取"新发布"行为
4. 从 `update.xlsx` 提取"重发"、"回帖"、"删回帖"行为
5. 按帖子ID（thread_id）和行为时间（action_time）排序
6. 保存为 CSV 格式，便于后续导入和分析

### car_info.csv 文件生成逻辑

1. 读取 `post.xlsx` 和 `update.xlsx` 中的帖子标题和内容
2. 使用正则表达式和自然语言处理方法提取：
   - 车辆年份（year）：从标题中提取四位数字年份
   - 品牌（make）：匹配预定义的品牌词典
   - 型号（model）：匹配品牌对应的型号词典
   - 里程（miles）：提取带有"k"、"miles"等关键词的数字
   - 价格（price）：提取带有"$"、"asking"等关键词的数字
   - 交易类型（trade_type）：识别"for sale"、"want to buy"等关键短语
   - 地点（location）：识别地名、州名、邮编等
3. 计算 daysold（已发布天数）：当前日期 - post_time
4. 计算 last_active（最后活跃时间）：从 update.xlsx 中获取最新的 list_time_r

### import.csv 文件生成逻辑

1. 通过 `py/analysis.py` 脚本生成，包含以下数据：
   - 时间序列统计数据（按小时/日/周/月）
   - 帖子活跃度排行
   - 用户活跃度排行
   - 词频统计数据
2. 使用UTF-8-sig编码保存，确保Excel可以正确读取中文
3. 用于批量导入主数据库的统计数据

## 相关文档

- [数据库概览](./db_overview.md)
- [数据处理流程](./db_data_processing.md) 