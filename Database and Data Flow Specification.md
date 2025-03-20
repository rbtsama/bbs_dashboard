# BBS数据系统数据库与数据流程管理文档

## 目录

1. [数据库概览](#数据库概览)
2. [数据来源与采集](#数据来源与采集)
3. [数据处理流程](#数据处理流程)
4. [字段派生规则](#字段派生规则)
5. [系统模块划分](#系统模块划分)
6. [数据表定义](#数据表定义)
7. [数据流动关系图](#数据流动关系图)
8. [增量数据更新流程](#增量数据更新流程)
9. [数据版本控制](#数据版本控制)
10. [数据备份与恢复](#数据备份与恢复)
11. [定时任务管理](#定时任务管理)
12. [词云生成系统](#词云生成系统)
13. [数据使用指南](#数据使用指南)

## 数据库概览

数据库位置：`backend/db/forum_data.db`

系统使用SQLite数据库存储所有处理后的数据，主要包含以下类型的表：

1. **原始数据表**：存储经过预处理的原始数据
   - `post` - 发帖列表数据
   - `list` - 更新列表数据
   - `post_action` - 帖子行为记录数据
   - `car_info` - 车辆信息数据

2. **统计数据表**：存储聚合统计数据
   - `post_statistic` - 发帖量统计
   - `update_statistic` - 更新量统计
   - `view_statistic` - 浏览量统计
   - `post_ranking` - 帖子排行
   - `author_ranking` - 作者排行
   - `post_history` - 帖子历史记录
   - `author_history` - 作者历史记录
   - `car_detail` - 车辆详细信息

3. **功能数据表**：支持应用功能的数据
   - `thread_follow` - 帖子关注记录
   - `thread_history_cache` - 帖子历史缓存
   - `wordcloud_cache` - 词云缓存
   - `wordcloud_job` - 词云生成任务队列

4. **版本控制表**：管理数据更新和变更
   - `data_version` - 数据版本信息
   - `data_change_log` - 数据变更日志

5. **用户数据表**：存储用户相关信息
   - `user_settings` - 用户设置
   - `user_favorites` - 用户收藏
   - `user_comments` - 用户评论
   - `user_votes` - 用户投票
   - `user_profile` - 用户个人资料
   - `user_notifications` - 用户通知

## 数据来源与采集

### 原始数据获取逻辑

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

### 源数据到处理后文件的转换逻辑

#### post.xlsx 文件生成逻辑

1. 读取所有 `bbs_post_list_*.xlsx` 文件，提取所有帖子记录
2. 处理时间格式，统一为标准datetime格式
3. 计算 `scraping_time_R`（将时间向上取整到15分钟）
4. 对每个URL去重，保留最早的一条记录（首次发现记录）
5. 添加 source_file（来源文件）和 sheet_name（工作表名）字段用于溯源

#### list.xlsx 文件生成逻辑

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

#### detail.xlsx 文件生成逻辑

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

#### action.csv 文件生成逻辑

1. 读取已处理的 `post.xlsx` 和 `update.xlsx` 文件
2. 将两个数据源的记录合并，构建完整的帖子行为时间线
3. 从 `post.xlsx` 提取"新发布"行为
4. 从 `update.xlsx` 提取"重发"、"回帖"、"删回帖"行为
5. 按帖子ID（thread_id）和行为时间（action_time）排序
6. 保存为 CSV 格式，便于后续导入和分析

#### car_info.csv 文件生成逻辑

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

#### import.csv 文件生成逻辑

1. 通过 `py/analysis.py` 脚本生成，包含以下数据：
   - 时间序列统计数据（按小时/日/周/月）
   - 帖子活跃度排行
   - 用户活跃度排行
   - 词频统计数据
2. 使用UTF-8-sig编码保存，确保Excel可以正确读取中文
3. 用于批量导入主数据库的统计数据

## 数据处理流程

#### 1. 数据采集
- 论坛帖子列表：每2小时抓取一次，生成 `bbs_post_list_YYYYMMDD.xlsx`
- 论坛更新列表：每15分钟抓取一次，生成 `bbs_update_list_YYYYMMDD.xlsx`
- 帖子详情内容：每2小时抓取一次，生成 `bbs_update_detail_YYYYMMDD.xlsx`

#### 2. 数据预处理
处理脚本包括：
- `post.py`: 处理新发帖数据，生成 `post.xlsx`
  - 特殊处理：23:45之后的抓取时间统一设置为23:45，避免数据跨天
  - 时间处理：scraping_time_R 使用四舍五入到15分钟
- `update.py`: 处理帖子更新数据，生成 `update.xlsx`
  - 特殊处理：23:45之后的抓取时间统一设置为23:45，避免数据跨天
  - 更新原因判断：重发、回帖、删回帖
- `detail.py`: 处理帖子详情数据，生成 `detail.xlsx`
  - 特殊处理：23:45之后的抓取时间统一设置为23:45，避免数据跨天
  - 时间处理：scraping_time_R 使用四舍五入到15分钟
  - 内容处理：合并title、tags等生成car_description
- `action.py`: 生成帖子动态记录，生成 `action.csv`
- `car_info.py`: 处理车辆信息数据，生成 `car_info.csv`

#### 3. 数据导入与更新
- `py/update_db.py`: 增量更新数据库
  - 创建临时数据库
  - 导入Excel和CSV数据
  - 执行SQL处理脚本
  - 生成变更日志
  - 应用更改到主数据库

#### 4. 数据备份与维护
- `py/backup_db.py`: 创建数据库备份
  - 定期备份数据库文件
  - 管理备份历史，保留最近30个备份
- `py/check_db_structure.py`: 检查数据库结构
  - 验证表结构和索引
  - 检查行数统计

#### 5. 词云生成
- `py/generate_wordcloud.py`: 生成词云
  - 处理词云生成任务队列
  - 为热门主题和活跃作者生成词云
  - 更新词云缓存

## 字段派生规则

### 时间处理相关字段

| 字段名 | 派生规则 | 特殊说明 |
|-------|---------|---------|
| scraping_time_R | 将 scraping_time 四舍五入到15分钟：<br>1. 分钟数四舍五入到15的倍数（0,15,30,45）<br>2. 特殊处理：23:45以后的时间点统一设为23:45 | 1. 防止跨天并保证时间点均匀分布<br>2. 适用于post.xlsx和update.xlsx的处理<br>3. 便于时间序列分析 |
| list_time_R | 将 list_time 四舍五入到15分钟（规则同上） | 用于时间序列分析和数据聚合 |
| post_time | 对于只有日期没有时间的记录，补充为当天00:00:00 | 确保时间格式统一完整 |

### 帖子属性计算字段

| 字段名 | 派生规则 | 特殊说明 |
|-------|---------|---------|
| daysold | 计算方式：`(当前日期 - post_time).days`<br>表示帖子已发布的天数<br>不足1天计算为0天 | 用于分析帖子寿命 |
| post_last_active | 计算方式：`(当前日期 - update.xlsx中该帖子最大的抓取时间).days`<br>表示帖子最后活跃距今的天数<br>不足1天计算为0天 | 用于分析帖子最近活跃时间 |
| author_last_active | 计算方式：`(当前日期 - update.xlsx中该作者最大的抓取时间).days`<br>表示作者最后活跃距今的天数<br>不足1天计算为0天 | 用于分析作者最近活跃时间 |
| thread_id | 从URL中提取的唯一标识，通常是URL最后部分的数字ID<br>计算方式：`SUBSTR(url, -10, 7)` | 用作关联不同表中同一帖子的主键 |
| update_reason | 基于连续两次抓取记录的对比判断：<br>1. 如果序号(num)下降超过5且当前序号<15：<br>   - 如果回复数不变：标记为"重发"<br>   - 如果回复数增加：标记为"回帖"<br>2. 如果序号上升但回复数减少：标记为"删回帖" | 用于分析帖子更新类型和用户行为 |
| action_type | 基于数据来源和状态变化判断：<br>1. 来自post.xlsx的首次记录：标记为"新发布"<br>2. 来自update.xlsx的记录：使用update_reason值 | 用于构建完整的帖子行为时间线 |

### 统计和分析字段

| 字段名 | 派生规则 | 特殊说明 |
|-------|---------|---------|
| post_count | 计算特定时间段内的新发帖数量或特定帖子/作者的发帖次数 | 用于排行榜和时间趋势分析 |
| update_count | 计算特定时间段内的帖子更新数量 | 用于时间趋势分析 |
| view_count | 两次抓取之间read_count的差值 | 计算特定时间段内的阅读增量 |
| active_posts | 作者当前活跃的帖子数量<br>计算方式：`COUNT(DISTINCT url)` | 用于作者活跃度分析 |
| last_active | 最后活跃时间戳<br>计算方式：`CAST(JULIANDAY(scraping_time) - JULIANDAY('1970-01-01') AS INTEGER)` | 用于排序和筛选最近活跃的帖子/作者 |

### 车辆信息字段

| 字段名 | 派生规则 | 特殊说明 |
|-------|---------|---------|
| year | 使用正则表达式 `\b(19|20)\d{2}\b` 从标题提取4位年份<br>特殊处理：`CASE WHEN year < 1900 OR year > 2100 THEN NULL ELSE year END` | 优先匹配1900-2099范围的年份 |
| make | 通过预定义的汽车品牌词典匹配标题中的品牌名称 | 支持常见简写和全称 |
| model | 基于已识别的品牌，匹配对应的型号词典 | 依赖于准确的品牌识别 |
| miles | 提取格式如 "xxxk miles", "xxx,xxx miles" 的里程信息<br>规范化为整数值 | 单位统一转换为英里 |
| price | 提取格式如 "$xxxx", "asking xxxx" 的价格信息<br>规范化为数值 | 单位统一为美元 |
| trade_type | 基于关键词识别：<br>- "for sale", "selling" → "出售"<br>- "wtb", "looking for" → "求购"<br>- "trade" → "交换" | 用于分类交易类型 |
| location | 使用地名词典和格式模式（如州缩写、邮编）识别地点信息 | 提取精度依赖于标题描述 |

## 系统模块划分

系统分为以下主要功能模块，每个模块使用不同的数据表和字段：

### 1. 数据采集与预处理模块

**主要功能**：
- 每日定时爬取论坛数据
- 处理原始数据，生成标准格式文件
- 提取车辆信息

**使用的数据表与字段**：
- 原始Excel文件（采集结果）
- `post.xlsx`（处理后的发帖数据）
- `list.xlsx`（处理后的更新数据）
- `detail.xlsx`（处理后的详情数据）
- `action.csv`（处理后的行为数据）
- `car_info.csv`（提取的车辆信息）

**核心脚本**：
- `py/post.py`：处理发帖列表
- `py/list.py`：处理更新列表
- `py/detail.py`：处理帖子详情
- `py/action.py`：生成行为数据
- `py/car_info.py`：提取车辆信息

### 2. 数据库管理模块

**主要功能**：
- 数据库初始化与结构创建
- 数据导入与更新
- 数据备份与恢复
- 数据库结构检查与维护

**使用的数据表与字段**：
- 所有数据库表
- 版本控制表：`data_version`, `data_change_log`

**核心脚本**：
- `py/update_db.py`：数据库更新
- `py/backup_db.py`：数据库备份
- `py/check_db_structure.py`：检查数据库结构
- `py/execute_sql.py`：执行SQL脚本
- `py/reset_db.py`：重置数据库

**核心SQL脚本**：
- `sql/create_tables.sql`：创建表结构
- `sql/create_version_tables.sql`：创建版本控制表
- `sql/init_protected_tables.sql`：初始化受保护表
- `sql/process_import_data.sql`：处理导入数据
- `sql/incremental_update.sql`：增量更新数据

### 3. 数据分析与可视化模块

**主要功能**：
- 生成统计数据
- 生成词云
- 提供数据查询接口

**使用的数据表与字段**：
- 统计数据表：`post_ranking`, `author_ranking`, `car_detail`
- 历史数据表：`post_history`, `author_history`
- 词云相关表：`wordcloud_job`, `wordcloud_cache`

**核心脚本**：
- `py/analysis.py`：数据分析
- `py/generate_wordcloud.py`：生成词云

### 4. 用户交互模块

**主要功能**：
- 用户设置管理
- 用户收藏与评论
- 用户通知

**使用的数据表与字段**：
- 用户数据表：`user_settings`, `user_favorites`, `user_comments`, `user_votes`, `user_profile`, `user_notifications`
- 关注数据表：`thread_follow`

## 数据表定义（增强版）

### 版本控制表

#### data_version 表
- `id` - 自增主键
- `version_id` - 版本标识(如20250314_001)
- `update_type` - 更新类型(incremental/full)
- `started_at` - 开始时间
- `completed_at` - 完成时间
- `status` - 状态(in_progress/completed/failed)
- `affected_rows` - 影响的行数
- `details` - 详细信息
- `created_at` - 创建时间

#### data_change_log 表
- `id` - 自增主键
- `version_id` - 关联的版本ID
- `table_name` - 表名
- `record_id` - 记录主键(url或其他ID)
- `change_type` - 变更类型(insert/update/delete)
- `old_values` - 旧值(JSON格式)
- `new_values` - 新值(JSON格式)
- `created_at` - 创建时间

### 统计数据表

#### post_ranking 表
- `url` - 帖子URL (主键)
- `title` - 帖子标题
- `author` - 作者名
- `author_link` - 作者链接
- `thread_id` - 帖子ID (从URL提取)
- `days_old` - 已发布天数
- `last_active` - 最后活跃时间戳
- `read_count` - 阅读数
- `reply_count` - 回复数
- `repost_count` - 重发次数
- `delete_count` - 删除次数
- `created_at` - 创建时间
- `updated_at` - 更新时间

#### author_ranking 表
- `author` - 作者名 (主键)
- `author_link` - 作者链接
- `url` - 最新帖子URL
- `title` - 最新帖子标题
- `days_old` - 首次发帖距今天数
- `last_active` - 最后活跃时间戳
- `active_posts` - 活跃帖子数
- `repost_count` - 重发次数
- `reply_count` - 回复总数
- `delete_count` - 删除次数
- `created_at` - 创建时间
- `updated_at` - 更新时间

#### post_history 表
- `id` - 自增主键
- `thread_id` - 帖子ID
- `url` - 帖子URL
- `title` - 帖子标题
- `author` - 作者名
- `author_link` - 作者链接
- `action_type` - 动作类型(新发布/重发/回帖/删回帖)
- `action_time` - 动作时间
- `read_count` - 当时的阅读数
- `reply_count` - 当时的回复数
- `created_at` - 创建时间
- `updated_at` - 更新时间

#### author_history 表
- `id` - 自增主键
- `author_id` - 作者ID
- `author` - 作者名
- `author_link` - 作者链接
- `action_type` - 动作类型
- `action_time` - 动作时间
- `active_posts` - 当时的活跃帖子数
- `post_count` - 当时的发帖总数
- `created_at` - 创建时间
- `updated_at` - 更新时间

#### car_detail 表
- `thread_id` - 帖子ID (主键)
- `url` - 帖子URL
- `title` - 帖子标题
- `author` - 作者名
- `author_link` - 作者链接
- `days_old` - 已发布天数
- `last_active` - 最后活跃时间戳
- `price` - 价格
- `miles` - 里程
- `year` - 车辆年份
- `model` - 车型
- `created_at` - 创建时间
- `updated_at` - 更新时间

### 词云相关表

#### wordcloud_job 表
- `id` - 自增主键
- `job_type` - 作业类型(author/thread)
- `target_id` - 目标ID(作者名或thread_id)
- `status` - 状态(pending/processing/completed/failed)
- `last_updated` - 上次更新时间
- `next_update` - 下次计划更新时间
- `created_at` - 创建时间
- `updated_at` - 更新时间

#### wordcloud_cache 表
- `id` - 自增主键
- `cache_type` - 缓存类型(author/thread)
- `target_id` - 目标ID(作者名或thread_id)
- `title` - 标题
- `image_path` - 图片路径
- `word_data` - 词频数据(JSON格式)
- `generated_at` - 生成时间
- `created_at` - 创建时间
- `updated_at` - 更新时间

### 用户数据表

#### thread_follow 表
- `id` - 自增主键
- `url` - 帖子URL
- `title` - 帖子标题
- `author` - 作者名
- `author_link` - 作者链接
- `days_old` - 已发布天数
- `last_active` - 最后活跃时间戳
- `read_count` - 阅读数
- `reply_count` - 回复数
- `repost_count` - 重发次数
- `delete_count` - 删除次数
- `follow_type` - 关注类型
- `created_at` - 创建时间
- `updated_at` - 更新时间

#### user_settings 表
- `id` - 自增主键
- `user_id` - 用户ID (唯一)
- `theme` - 主题设置
- `notification_enabled` - 通知开关
- `data_preferences` - 数据偏好设置(JSON格式)
- `created_at` - 创建时间
- `updated_at` - 更新时间

#### user_favorites 表
- `id` - 自增主键
- `user_id` - 用户ID
- `url` - 收藏的URL
- `title` - 收藏的标题
- `note` - 用户笔记
- `created_at` - 创建时间
- `updated_at` - 更新时间

## 数据流动关系图

```
原始数据采集 → 数据预处理 → 数据导入 → 数据库更新 → 数据分析与可视化 → 用户界面展示
```

### 详细数据流程

1. **原始数据采集**
   ```
   爬虫程序 → bbs_post_list_*.xlsx
              bbs_update_list_*.xlsx
              bbs_update_detail_*.xlsx
   ```

2. **数据预处理**
   ```
   bbs_post_list_*.xlsx → post.py → post.xlsx
   bbs_update_list_*.xlsx → update.py → update.xlsx
   bbs_update_detail_*.xlsx → detail.py → detail.xlsx
   post.xlsx + update.xlsx → action.py → action.csv
   post.xlsx + detail.xlsx → car_info.py → car_info.csv
## 数据流动关系图（续）

3. **数据导入与更新**
   ```
   post.xlsx + update.xlsx + detail.xlsx + car_info.csv → update_db.py → 临时数据库 → 主数据库
                                                                      ↓
                                                                 变更日志记录
   ```

4. **数据分析与处理**
   ```
   主数据库 → analysis.py → 统计数据
           → generate_wordcloud.py → 词云图像和数据
   ```

5. **数据备份与维护**
   ```
   主数据库 → backup_db.py → 备份文件
           → check_db_structure.py → 结构检查报告
   ```

6. **用户界面数据流**
   ```
   主数据库 → 前端API → 用户界面展示
           ↑
   用户交互 → 用户数据表
   ```

## 增量数据更新流程

增量数据更新是系统的核心功能，通过 `py/update_db.py` 脚本实现。该流程设计为每日自动执行，确保数据库中的信息保持最新状态，同时不影响用户数据。

### 表分类管理

系统将数据库表分为三类，采用不同的更新策略：

1. **受保护表**：这些表包含用户数据，不会在更新过程中被修改
   ```
   thread_follow, user_settings, user_favorites, user_comments, 
   user_votes, user_profile, user_notifications, data_version, 
   data_change_log, wordcloud_cache
   ```

2. **合并表**：这些表使用合并策略更新，保留现有数据的同时添加或更新新数据
   ```
   post_ranking, car_detail, author_ranking, post_history, author_history
   ```

3. **常规表**：这些表在更新过程中可以完全替换
   ```
   post, detail, car_info, import, update
   ```

### 增量更新步骤

1. **初始化更新过程**
   - 创建新的版本记录，生成唯一的版本ID
   - 记录更新类型（增量/完全）和开始时间
   - 设置状态为"进行中"

2. **创建临时数据库**
   - 复制主数据库的表结构到临时数据库
   - 复制受保护表的数据到临时数据库

3. **导入新数据**
   - 从Excel文件导入数据到临时数据库的相应表
   - 从CSV文件导入数据到临时数据库的相应表

4. **处理导入的数据**
   - 执行SQL脚本处理导入的数据
   - 生成派生字段和计算值
   - 更新关联表之间的关系

5. **生成变更日志**
   - 比较临时数据库和主数据库中的数据
   - 记录所有插入、更新和删除操作
   - 保存旧值和新值用于审计和回滚

6. **应用更改**
   - 对于合并表，使用合并策略应用更改
   - 对于常规表，使用替换策略应用更改
   - 保护表不受影响

7. **完成更新过程**
   - 更新版本记录的状态为"已完成"
   - 记录完成时间和影响的行数
   - 删除临时数据库

### 增量更新SQL脚本

`sql/incremental_update.sql` 脚本包含以下主要操作：

1. **更新帖子排名表**
   ```sql
   INSERT OR REPLACE INTO post_ranking (
       url, title, author, author_link, thread_id, days_old, last_active,
       read_count, reply_count, repost_count, delete_count,
       created_at, updated_at
   )
   SELECT 
       p.url, 
       COALESCE(d.title, p.title, '无标题') as title, 
       p.author, 
       p.author_link,
       SUBSTR(p.url, -10, 7) as thread_id,
       CAST(JULIANDAY('now') - JULIANDAY(p.post_time) AS INTEGER) as days_old,
       CAST(JULIANDAY(p.scraping_time) - JULIANDAY('1970-01-01') AS INTEGER) as last_active,
       p.read_count, 
       p.reply_count, 
       COALESCE(pr.repost_count, 0) as repost_count, 
       COALESCE(pr.delete_count, 0) as delete_count,
       COALESCE(pr.created_at, DATETIME('now')) as created_at,
       DATETIME('now') as updated_at
   FROM post p
   LEFT JOIN detail d ON p.url = d.url
   LEFT JOIN post_ranking pr ON p.url = pr.url
   WHERE pr.url IS NULL OR p.scraping_time > pr.updated_at;
   ```

2. **更新汽车详情表**
   ```sql
   INSERT OR REPLACE INTO car_detail (
       thread_id, url, title, author, author_link,
       days_old, last_active, price, miles, year, model,
       created_at, updated_at
   )
   SELECT 
       SUBSTR(p.url, -10, 7) as thread_id,
       p.url, 
       COALESCE(d.title, p.title, '无标题') as title,
       p.author, 
       p.author_link,
       CAST(JULIANDAY('now') - JULIANDAY(p.post_time) AS INTEGER) as days_old,
       CAST(JULIANDAY(p.scraping_time) - JULIANDAY('1970-01-01') AS INTEGER) as last_active,
       CAST(ci.price AS REAL) as price,
       CAST(ci.miles AS REAL) as miles,
       CASE WHEN ci.year < 1900 OR ci.year > 2100 THEN NULL ELSE CAST(ci.year AS INTEGER) END as year,
       ci.model,
       COALESCE(cd.created_at, DATETIME('now')) as created_at,
       DATETIME('now') as updated_at
   FROM post p
   LEFT JOIN detail d ON p.url = d.url
   LEFT JOIN car_info ci ON p.url = ci.url
   LEFT JOIN car_detail cd ON p.url = cd.url
   WHERE cd.url IS NULL OR p.scraping_time > cd.updated_at;
   ```

3. **更新作者排名表**
   ```sql
   INSERT OR REPLACE INTO author_ranking (
       author, author_link, url, title, days_old, last_active,
       active_posts, repost_count, reply_count, delete_count,
       created_at, updated_at
   )
   SELECT 
       p.author, 
       p.author_link,
       (SELECT url FROM post_ranking WHERE author = p.author ORDER BY last_active DESC LIMIT 1),
       (SELECT title FROM post_ranking WHERE author = p.author ORDER BY last_active DESC LIMIT 1),
       MIN(CAST(JULIANDAY('now') - JULIANDAY(p.post_time) AS INTEGER)) as days_old,
       MAX(CAST(JULIANDAY(p.scraping_time) - JULIANDAY('1970-01-01') AS INTEGER)) as last_active,
       COUNT(DISTINCT p.url) as active_posts,
       COALESCE(ar.repost_count, 0) as repost_count,
       SUM(p.reply_count) as reply_count,
       COALESCE(ar.delete_count, 0) as delete_count,
       COALESCE(ar.created_at, DATETIME('now')) as created_at,
       DATETIME('now') as updated_at
   FROM post p
   LEFT JOIN author_ranking ar ON p.author = ar.author
   GROUP BY p.author, p.author_link;
   ```

4. **记录帖子历史数据**
   ```sql
   INSERT INTO post_history (
       thread_id, url, title, author, author_link, action_type, action_time,
       read_count, reply_count, created_at, updated_at
   )
   SELECT 
       SUBSTR(p.url, -10, 7) as thread_id,
       p.url, 
       COALESCE(d.title, p.title, '无标题') as title,
       p.author, 
       p.author_link,
       'update' as action_type,
       p.scraping_time as action_time,
       p.read_count,
       p.reply_count,
       DATETIME('now') as created_at,
       DATETIME('now') as updated_at
   FROM post p
   LEFT JOIN detail d ON p.url = d.url
   WHERE p.scraping_time > (
       SELECT MAX(action_time) FROM post_history ph WHERE ph.url = p.url
   ) OR NOT EXISTS (
       SELECT 1 FROM post_history ph WHERE ph.url = p.url
   );
   ```

5. **记录作者历史数据**
   ```sql
   INSERT INTO author_history (
       author_id, author, author_link, action_type, action_time,
       active_posts, post_count, created_at, updated_at
   )
   SELECT 
       p.author as author_id,
       p.author,
       p.author_link,
       'update' as action_type,
       MAX(p.scraping_time) as action_time,
       COUNT(DISTINCT p.url) as active_posts,
       COUNT(DISTINCT p.url) as post_count,
       DATETIME('now') as created_at,
       DATETIME('now') as updated_at
   FROM post p
   GROUP BY p.author, p.author_link
   HAVING MAX(p.scraping_time) > (
       SELECT MAX(action_time) FROM author_history ah WHERE ah.author = p.author
   ) OR NOT EXISTS (
       SELECT 1 FROM author_history ah WHERE ah.author = p.author
   );
   ```

6. **更新词云任务队列**
   ```sql
   INSERT OR REPLACE INTO wordcloud_job (
       job_type, target_id, status, last_updated, next_update, 
       created_at, updated_at
   )
   SELECT 
       'thread' as job_type,
       thread_id as target_id,
       'pending' as status,
       DATETIME('now') as last_updated,
       DATETIME('now', '+1 day') as next_update,
       COALESCE(
           (SELECT created_at FROM wordcloud_job WHERE job_type = 'thread' AND target_id = thread_id), 
           DATETIME('now')
       ) as created_at,
       DATETIME('now') as updated_at
   FROM (
       SELECT DISTINCT thread_id 
       FROM car_detail 
       WHERE thread_id IS NOT NULL AND thread_id != ''
       ORDER BY last_active DESC
       LIMIT 50  -- 只为最活跃的50个主题生成词云
   );
   ```

## 数据版本控制

系统使用版本控制表跟踪所有数据更改，确保数据完整性和可追溯性。

### 版本控制表结构

1. **data_version 表**：记录每次更新的元数据
   ```sql
   CREATE TABLE IF NOT EXISTS data_version (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       version_id TEXT NOT NULL,         -- 版本标识(如20250314_001)
       update_type TEXT NOT NULL,        -- 更新类型(incremental/full)
       started_at DATETIME NOT NULL,     -- 开始时间
       completed_at DATETIME,            -- 完成时间
       status TEXT NOT NULL,             -- 状态(in_progress/completed/failed)
       affected_rows INTEGER DEFAULT 0,  -- 影响的行数
       details TEXT,                     -- 详细信息
       created_at DATETIME DEFAULT CURRENT_TIMESTAMP
   );
   ```

2. **data_change_log 表**：记录每个记录的具体变更
   ```sql
   CREATE TABLE IF NOT EXISTS data_change_log (
       id INTEGER PRIMARY KEY AUTOINCREMENT,
       version_id TEXT NOT NULL,         -- 关联的版本ID
       table_name TEXT NOT NULL,         -- 表名
       record_id TEXT NOT NULL,          -- 记录主键(url或其他ID)
       change_type TEXT NOT NULL,        -- 变更类型(insert/update/delete)
       old_values TEXT,                  -- 旧值(JSON格式)
       new_values TEXT,                  -- 新值(JSON格式)
       created_at DATETIME DEFAULT CURRENT_TIMESTAMP
   );
   ```

### 版本控制流程

1. **版本创建**：每次更新开始时，创建新的版本记录
   ```python
   def start_update_process(self, update_type="incremental"):
       """开始更新过程，记录版本信息"""
       conn = sqlite3.connect(self.db_path)
       cursor = conn.cursor()
       
       # 确保版本表存在
       cursor.execute('''
       CREATE TABLE IF NOT EXISTS data_version (
           id INTEGER PRIMARY KEY AUTOINCREMENT,
           version_id TEXT NOT NULL,
           update_type TEXT NOT NULL,
           started_at DATETIME NOT NULL,
           completed_at DATETIME,
           status TEXT NOT NULL,
           affected_rows INTEGER DEFAULT 0,
           details TEXT,
           created_at DATETIME DEFAULT CURRENT_TIMESTAMP
       )
       ''')
       
       # 插入新版本记录
       cursor.execute('''
       INSERT INTO data_version 
       (version_id, update_type, started_at, status) 
       VALUES (?, ?, ?, ?)
       ''', (self.version_id, update_type, datetime.datetime.now(), 'in_progress'))
       
       conn.commit()
       conn.close()
       
       logger.info(f"开始数据更新，版本ID: {self.version_id}, 类型: {update_type}")
       return self.version_id
   ```

2. **变更记录**：记录每个表的每条记录的变更
   ```python
   def generate_change_log(self, main_tables):
       """生成变更日志，比较临时数据库和主数据库中指定表的差异"""
       # 对于每个表
       for table_name in main_tables:
           # 获取表的主键列
           primary_key = self._get_table_primary_key(main_cursor, table_name)
           
           # 获取临时数据库中的所有记录
           temp_cursor.execute(f"SELECT * FROM {table_name}")
           temp_records = temp_cursor.fetchall()
           
           # 获取主数据库中的所有记录ID
           main_cursor.execute(f"SELECT {primary_key} FROM {table_name}")
           main_record_ids = set(row[0] for row in main_cursor.fetchall())
           
           # 记录变更
           for record in temp_records:
               record_dict = dict(zip(columns, record))
               record_id = record_dict[primary_key]
               
               if record_id in main_record_ids:
                   # 记录存在，检查是否有更新
                   main_cursor.execute(
                       f"SELECT * FROM {table_name} WHERE {primary_key} = ?", 
                       (record_id,)
                   )
                   main_record = main_cursor.fetchone()
                   main_record_dict = dict(zip(columns, main_record))
                   
                   # 检查是否有变更
                   if main_record_dict != record_dict:
                       # 记录更新
                       main_cursor.execute(f'''
                       INSERT INTO data_change_log 
                       (version_id, table_name, record_id, change_type, old_values, new_values)
                       VALUES (?, ?, ?, ?, ?, ?)
                       ''', (
                           self.version_id, 
                           table_name, 
                           record_id, 
                           'update',
                           json.dumps(main_record_dict),
                           json.dumps(record_dict)
                       ))
               else:
                   # 新记录，记录插入
                   main_cursor.execute(f'''
                   INSERT INTO data_change_log 
                   (version_id, table_name, record_id, change_type, old_values, new_values)
                   VALUES (?, ?, ?, ?, ?, ?)
                   ''', (
                       self.version_id, 
                       table_name, 
                       record_id, 
                       'insert',
                       None,
                       json.dumps(record_dict)
                   ))
   ```

3. **版本完成**：更新完成后，更新版本状态
   ```python
   # 更新版本记录
   main_cursor.execute('''
   UPDATE data_version 
   SET completed_at = ?, status = ?, affected_rows = ?
   WHERE version_id = ?
   ''', (datetime.datetime.now(), 'completed', affected_rows, self.version_id))
   ```

## 数据备份与恢复

系统通过 `py/backup_db.py` 脚本实现自动数据库备份功能，确保数据安全。

### 备份流程

1. **备份创建**：定期创建数据库完整备份
   ```python
   def create_backup():
       """创建数据库备份"""
       try:
           # 确保备份目录存在
           os.makedirs(BACKUP_DIR, exist_ok=True)
           os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
           
           # 生成备份文件名
           timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
           backup_file = os.path.join(BACKUP_DIR, f"forum_data_{timestamp}.db")
           
           # 检查数据库是否存在
           if not os.path.exists(DB_PATH):
               logging.error(f"数据库文件不存在: {DB_PATH}")
               return False
           
           # 检查数据库完整性
           conn = sqlite3.connect(DB_PATH)
           cursor = conn.cursor()
           cursor.execute("PRAGMA integrity_check")
           result = cursor.fetchone()
           conn.close()
           
           if result[0] != "ok":
               logging.error(f"数据库完整性检查失败: {result[0]}")
               return False
           
           # 创建备份
           shutil.copy2(DB_PATH, backup_file)
           logging.info(f"数据库备份成功: {backup_file}")
           
           # 删除旧备份，只保留最近30个
           backup_files = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith("forum_data_")])
           if len(backup_files) > 30:
               for old_file in backup_files[:-30]:
                   old_path = os.path.join(BACKUP_DIR, old_file)
                   os.remove(old_path)
                   logging.info(f"删除旧备份: {old_path}")
           
           return True
       except Exception as e:
           logging.error(f"创建备份时出错: {e}")
           return False
   ```

2. **备份管理**：自动管理备份历史，保留最近30个备份
   ```python
   # 删除旧备份，只保留最近30个
   backup_files = sorted([f for f in os.listdir(BACKUP_DIR) if f.startswith("forum_data_")])
   if len(backup_files) > 30:
       for old_file in backup_files[:-30]:
           old_path = os.path.join(BACKUP_DIR, old_file)
           os.remove(old_path)
           logging.info(f"删除旧备份: {old_path}")
   ```

### 恢复流程

恢复数据库可以通过以下步骤手动完成：

1. 停止所有使用数据库的进程
2. 将备份文件复制回原始位置，替换当前数据库文件
3. 重新启动相关进程

## 定时任务管理

系统使用定时任务自动执行数据更新、备份和词云生成。根据操作系统不同，提供了两种实现方式。

### Linux/Unix 系统 (Cron)

使用 `setup_cron.sh` 脚本设置 cron 任务：

```bash
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
```

### Windows 系统 (计划任务)

为Windows系统创建PowerShell脚本 `setup_windows_task.ps1`：

```powershell
# 设置Windows计划任务，在加州时间(PT)半夜3点执行数据更新

# 获取当前脚本路径
$scriptPath = Split-Path -Parent $MyInvocation.MyCommand.Path

# 计算加州时间凌晨3点对应的本地时间
# 注意：这里简化处理，实际应考虑时区和夏令时
$updateTime = New-ScheduledTaskTrigger -Daily -At 3AM
$backupTime = New-ScheduledTaskTrigger -Daily -At 2AM
$wordcloudTime = New-ScheduledTaskTrigger -Daily -At 4AM

# 创建任务动作
$updateAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath\py\update_db.py`"" -WorkingDirectory $scriptPath
$backupAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath\py\backup_db.py`"" -WorkingDirectory $scriptPath
$wordcloudAction = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-NoProfile -ExecutionPolicy Bypass -File `"$scriptPath\py\generate_wordcloud.py`"" -WorkingDirectory $scriptPath

# 设置任务主体（当前用户）
$principal = New-ScheduledTaskPrincipal -UserId (Get-CimInstance -ClassName Win32_ComputerSystem | Select-Object -ExpandProperty UserName) -LogonType S4U -RunLevel Highest

# 设置任务设置
$settings = New-ScheduledTaskSettingsSet -DontStopOnIdleEnd -ExecutionTimeLimit (New-TimeSpan -Hours 2)

# 检查任务是否已存在
$updateTaskExists = Get-ScheduledTask -TaskName "BBS数据库更新" -ErrorAction SilentlyContinue
$backupTaskExists = Get-ScheduledTask -TaskName "BBS数据库备份" -ErrorAction SilentlyContinue
$wordcloudTaskExists = Get-ScheduledTask -TaskName "BBS词云生成" -ErrorAction SilentlyContinue

# 注册或更新任务
if ($updateTaskExists) {
    Set-ScheduledTask -TaskName "BBS数据库更新" -Trigger $updateTime -Action $updateAction -Principal $principal -Settings $settings
    Write-Host "已更新数据库更新任务：每天凌晨3点执行"
} else {
    Register-ScheduledTask -TaskName "BBS数据库更新" -Trigger $updateTime -Action $updateAction -Principal $principal -Settings $settings -Description "每天凌晨3点执行BBS数据库更新"
    Write-Host "已创建数据库更新任务：每天凌晨3点执行"
}

if ($backupTaskExists) {
    Set-ScheduledTask -TaskName "BBS数据库备份" -Trigger $backupTime -Action $backupAction -Principal $principal -Settings $settings
    Write-Host "已更新数据库备份任务：每天凌晨2点执行"
} else {
    Register-ScheduledTask -TaskName "BBS数据库备份" -Trigger $backupTime -Action $backupAction -Principal $principal -Settings $settings -Description "每天凌晨2点执行BBS数据库备份"
    Write-Host "已创建数据库备份任务：每天凌晨2点执行"
}

if ($wordcloudTaskExists) {
    Set-ScheduledTask -TaskName "BBS词云生成" -Trigger $wordcloudTime -Action $wordcloudAction -Principal $principal -Settings $settings
    Write-Host "已更新词云生成任务：每天凌晨4点执行"
} else {
    Register-ScheduledTask -TaskName "BBS词云生成" -Trigger $wordcloudTime -Action $wordcloudAction -Principal $principal -Settings $settings -Description "每天凌晨4点执行BBS词云生成"
    Write-Host "已创建词云生成任务：每天凌晨4点执行"
}

Write-Host "定时任务设置完成！"
```

## 词云生成系统

系统通过 `py/generate_wordcloud.py` 脚本实现词云生成功能，为热门主题和活跃作者生成可视化词云。

### 词云生成流程

1. **任务获取**：从 `wordcloud_job` 表获取待处理任务
   ```python
   def get_pending_jobs(self, limit=10):
       """获取待处理的任务"""
       try:
           conn = sqlite3.connect(self.db_path)
           cursor = conn.cursor()
           
           # 获取状态为pending且下次更新时间已到的任务
           cursor.execute("""
           SELECT id, job_type, target_id 
           FROM wordcloud_job 
           WHERE status = 'pending' AND next_update <= DATETIME('now')
           ORDER BY next_update ASC
           LIMIT ?
           """, (limit,))
           
           jobs = cursor.fetchall()
           conn.close()
           
           return jobs
       except Exception as e:
           logger.error(f"获取待处理任务时出错: {e}")
           return []
   ```

2. **词云生成**：根据任务类型生成相应的词云
   ```python
   def generate_author_wordcloud(self, author):
       """为作者生成词云"""
       try:
           conn = sqlite3.connect(self.db_path)
           cursor = conn.cursor()
           
           # 获取作者的所有帖子内容
           cursor.execute("""
           SELECT d.title,
```python
           SELECT d.title, d.content
           FROM detail d
           JOIN post p ON d.url = p.url
           WHERE p.author = ?
           """, (author,))
           
           posts = cursor.fetchall()
           conn.close()
           
           if not posts:
               logger.warning(f"作者 {author} 没有帖子内容")
               return None
           
           # 合并所有帖子内容
           all_text = ""
           for title, content in posts:
               if title:
                   all_text += title + " "
               if content:
                   all_text += content + " "
           
           # 生成词云
           output_dir = os.path.join(self.wordcloud_dir, "author")
           os.makedirs(output_dir, exist_ok=True)
           
           image_path = os.path.join(output_dir, f"{author}.png")
           data = self._generate_wordcloud(all_text, image_path, author)
           
           # 更新缓存
           if data:
               self._update_wordcloud_cache("author", author, author, image_path, data)
               return image_path
           
           return None
       except Exception as e:
           logger.error(f"为作者 {author} 生成词云时出错: {e}")
           return None
   ```

3. **词云处理**：处理文本并生成词云图像
   ```python
   def _generate_wordcloud(self, text, output_path, title):
       """生成词云"""
       try:
           # 清理文本
           text = re.sub(r'https?://\S+', '', text)  # 移除URL
           text = re.sub(r'[^\w\s]', '', text)       # 移除标点符号
           
           # 分词
           words = jieba.lcut(text)
           
           # 过滤停用词和单字词
           filtered_words = []
           for word in words:
               if word not in self.stopwords and len(word) > 1:
                   filtered_words.append(word)
           
           # 统计词频
           word_counts = Counter(filtered_words)
           
           # 如果没有足够的词，返回None
           if len(word_counts) < 5:
               logger.warning(f"'{title}'的有效词汇不足，无法生成词云")
               return None
           
           # 生成词云
           wc = WordCloud(
               font_path=self.font_path,
               width=800,
               height=400,
               background_color='white',
               max_words=100,
               collocations=False
           )
           
           wc.generate_from_frequencies(word_counts)
           
           # 保存图像
           plt.figure(figsize=(10, 5))
           plt.imshow(wc, interpolation='bilinear')
           plt.axis('off')
           plt.title(title)
           plt.tight_layout()
           plt.savefig(output_path, dpi=300, bbox_inches='tight')
           plt.close()
           
           # 返回词频数据
           return {
               'title': title,
               'generated_at': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
               'word_counts': {word: count for word, count in word_counts.most_common(100)}
           }
       except Exception as e:
           logger.error(f"生成词云时出错: {e}")
           return None
   ```

4. **缓存更新**：更新词云缓存表
   ```python
   def _update_wordcloud_cache(self, cache_type, target_id, title, image_path, data):
       """更新词云缓存"""
       try:
           conn = sqlite3.connect(self.db_path)
           cursor = conn.cursor()
           
           # 检查是否已存在
           cursor.execute("""
           SELECT id FROM wordcloud_cache 
           WHERE cache_type = ? AND target_id = ?
           """, (cache_type, target_id))
           
           existing = cursor.fetchone()
           
           if existing:
               # 更新现有记录
               cursor.execute("""
               UPDATE wordcloud_cache 
               SET title = ?, image_path = ?, word_data = ?, 
                   generated_at = ?, updated_at = DATETIME('now')
               WHERE cache_type = ? AND target_id = ?
               """, (
                   title, 
                   image_path, 
                   json.dumps(data), 
                   data['generated_at'],
                   cache_type, 
                   target_id
               ))
           else:
               # 插入新记录
               cursor.execute("""
               INSERT INTO wordcloud_cache 
               (cache_type, target_id, title, image_path, word_data, generated_at, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, DATETIME('now'), DATETIME('now'))
               """, (
                   cache_type, 
                   target_id, 
                   title, 
                   image_path, 
                   json.dumps(data), 
                   data['generated_at']
               ))
           
           conn.commit()
           conn.close()
           
           logger.info(f"已更新词云缓存: {cache_type}/{target_id}")
           return True
       except Exception as e:
           logger.error(f"更新词云缓存时出错: {e}")
           return False
   ```

5. **任务处理**：处理所有待处理任务
   ```python
   def process_jobs(self, limit=10):
       """处理词云生成任务"""
       jobs = self.get_pending_jobs(limit)
       
       if not jobs:
           logger.info("没有待处理的词云任务")
           return 0
       
       logger.info(f"开始处理 {len(jobs)} 个词云任务")
       processed = 0
       
       for job_id, job_type, target_id in jobs:
           try:
               # 更新任务状态为处理中
               self.update_job_status(job_id, 'processing')
               
               # 根据任务类型生成词云
               if job_type == 'author':
                   result = self.generate_author_wordcloud(target_id)
               elif job_type == 'thread':
                   result = self.generate_thread_wordcloud(target_id)
               else:
                   logger.warning(f"未知的任务类型: {job_type}")
                   self.update_job_status(job_id, 'failed')
                   continue
               
               # 更新任务状态
               if result:
                   self.update_job_status(job_id, 'completed')
                   processed += 1
               else:
                   self.update_job_status(job_id, 'failed')
           
           except Exception as e:
               logger.error(f"处理任务 {job_id} 时出错: {e}")
               self.update_job_status(job_id, 'failed')
       
       logger.info(f"完成处理 {processed} 个词云任务")
       return processed
   ```

## 数据使用指南

### 初始设置

1. **创建必要目录**
   ```powershell
   # Windows PowerShell
   mkdir logs, data\wordcloud\author, data\wordcloud\thread, data\config\fonts, backup\db -Force
   ```

2. **初始化数据库**
   ```powershell
   # 创建版本控制表
   python py/execute_sql.py sql/create_version_tables.sql
   
   # 初始化受保护表
   python py/execute_sql.py sql/init_protected_tables.sql
   
   # 修改表结构以适应增量更新
   python py/execute_sql.py sql/modify_tables.sql
   ```

3. **设置定时任务**
   ```powershell
   # Windows
   .\setup_windows_task.ps1
   
   # Linux/Unix
   bash setup_cron.sh
   ```

### 手动触发更新

1. **执行数据库更新**
   ```powershell
   python py/update_db.py
   ```

2. **创建数据库备份**
   ```powershell
   python py/backup_db.py
   ```

3. **生成词云**
   ```powershell
   python py/generate_wordcloud.py
   ```

### 数据库维护

1. **检查数据库结构**
   ```powershell
   python py/check_db_structure.py
   ```

2. **检查特定表结构**
   ```powershell
   python py/check_table_structure.py post_ranking
   ```

3. **执行SQL脚本**
   ```powershell
   python py/execute_sql.py sql/your_script.sql
   ```

### 数据库重置

如需完全重置数据库，可以使用以下步骤：

1. **备份当前数据库**
   ```powershell
   python py/backup_db.py
   ```

2. **删除现有数据库**
   ```powershell
   # 确保没有程序正在使用数据库
   Remove-Item backend\db\forum_data.db -Force
   ```

3. **重新创建数据库**
   ```powershell
   # 创建表结构
   python py/execute_sql.py sql/create_tables.sql
   
   # 创建版本控制表
   python py/execute_sql.py sql/create_version_tables.sql
   
   # 初始化受保护表
   python py/execute_sql.py sql/init_protected_tables.sql
   ```

4. **导入数据**
   ```powershell
   python py/update_db.py
   ```

## 系统扩展点

系统设计考虑了未来扩展的可能性，主要扩展点包括：

1. **新数据源集成**：可以通过添加新的预处理脚本和导入逻辑，集成更多数据源

2. **高级分析功能**：可以基于现有数据结构，开发更复杂的分析功能，如趋势预测、用户行为分析等

3. **用户交互增强**：可以扩展用户相关表，支持更丰富的用户交互功能

4. **数据可视化**：可以基于现有数据和词云系统，开发更多可视化组件

5. **API扩展**：可以开发更完善的API，支持第三方应用集成
