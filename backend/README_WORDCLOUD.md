# 词云功能说明

## 功能概述

词云功能用于生成论坛帖子标题的词频统计可视化，帮助用户直观了解论坛热门话题。系统会定期生成词云数据并缓存，以提高访问性能。

## 修复的问题

1. **中文编码问题**：修复了词云生成过程中的中文编码问题，确保中文字符能够正确处理和显示。
   - 添加了对标题文本的编码检测和转换
   - 使用 `ensure_ascii=False` 确保 JSON 序列化时正确处理中文

2. **数据库表结构问题**：完善了词云缓存表的结构
   - 将主键设置为自增
   - 为 version 字段添加默认值
   - 添加了缺失列的检查和创建逻辑

3. **错误处理和日志**：增强了错误处理和日志输出
   - 添加了详细的时间戳日志
   - 增加了异常捕获和处理
   - 添加了处理过程中的状态日志

## 数据库表结构

词云缓存表 `wordcloud_cache` 结构如下：

```sql
CREATE TABLE wordcloud_cache (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    data TEXT,                   -- 词云JSON数据
    created_date TEXT,           -- 创建日期
    version INTEGER DEFAULT 1,   -- 版本号
    expire_date TEXT             -- 过期日期
)
```

## API接口

系统提供以下词云相关的API接口：

1. **获取标题词云数据**
   - URL: `/api/title-wordcloud`
   - 方法: `GET`
   - 参数: 
     - `refresh`: 是否强制刷新缓存 (0或1，默认0)
   - 返回: 词云数据的JSON数组

2. **手动刷新词云缓存**
   - URL: `/api/refresh-wordcloud`
   - 方法: `POST`
   - 返回: 刷新结果的JSON对象

## 词云生成流程

1. 从数据库获取所有帖子标题
2. 使用jieba进行中文分词
3. 统计词频并过滤停用词和单字词
4. 按词频排序并选取前300个高频词
5. 将词语分为大、中、小三组，分别设置不同的显示参数
6. 生成词云数据并缓存到数据库

## 测试工具

提供了两个测试脚本用于验证词云功能：

1. **test_wordcloud.py**: 测试词云数据库表结构和数据
2. **test_wordcloud_api.py**: 测试词云API接口

## 使用示例

```python
# 获取词云数据
import requests

# 获取缓存的词云数据
response = requests.get("http://localhost:5000/api/title-wordcloud")
if response.status_code == 200:
    word_cloud_data = response.json()
    print(f"获取到 {len(word_cloud_data)} 个词")

# 强制刷新词云数据
response = requests.get("http://localhost:5000/api/title-wordcloud?refresh=1")
if response.status_code == 200:
    word_cloud_data = response.json()
    print(f"刷新后获取到 {len(word_cloud_data)} 个词")
```

## 定时任务

系统设置了定时任务，每天凌晨2点自动生成词云数据：

```python
# 在定时任务函数中添加词云生成
schedule.every().day.at("02:00").do(generate_wordcloud)
```

## 注意事项

1. 词云数据缓存有效期为7天，过期数据会自动清理
2. 强制刷新操作会消耗较多服务器资源，请谨慎使用
3. 如遇到词云显示异常，可尝试手动刷新缓存 