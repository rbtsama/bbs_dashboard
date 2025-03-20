# 论坛数据分析后端

## 概述

本项目是一个论坛数据分析系统的后端，提供了数据获取、处理和API服务。主要功能包括词云生成、帖子排行、作者排行、趋势分析等。

## 模块结构

后端代码已完成模块化重构，主要包含以下模块：

- `modules/db_utils.py`：数据库连接和查询工具
- `modules/wordcloud.py`：词云生成和处理模块
- `modules/rankings.py`：排行榜功能模块
- `modules/trends.py`：趋势分析模块
- `modules/car_info.py`：车辆信息处理模块

## API 文档

所有API都使用前缀`/api`，返回JSON格式的数据。

### 健康检查

- **端点**：`/api/health`
- **方法**：GET
- **描述**：检查服务是否正常运行
- **返回示例**：
  ```json
  {
    "status": "ok",
    "message": "服务运行正常",
    "timestamp": "2025-03-17T10:53:14.423233"
  }
  ```

### 词云相关

- **端点**：`/api/title-wordcloud`
- **方法**：GET
- **描述**：获取标题词云数据
- **返回示例**：
  ```json
  [
    {"text": "丰田", "value": 66376},
    {"text": "出售", "value": 55378},
    ...
  ]
  ```

### 排行榜相关

- **端点**：`/api/post-rank`
- **方法**：GET
- **参数**：
  - `sort_by`：排序字段，默认为`views`
  - `limit`：返回数量，默认为20
- **描述**：获取帖子排行数据
- **返回示例**：
  ```json
  {
    "data": [
      {
        "thread_id": "...",
        "title": "...",
        "views": 1000,
        "replies": 50,
        "author": "...",
        "last_update": "..."
      },
      ...
    ]
  }
  ```

- **端点**：`/api/author-rank`
- **方法**：GET
- **参数**：
  - `sort_by`：排序字段，默认为`post_count`
  - `limit`：返回数量，默认为20
- **描述**：获取作者排行数据
- **返回示例**：
  ```json
  {
    "data": [
      {
        "author": "...",
        "post_count": 100,
        "reply_count": 200,
        "view_count": 5000,
        "last_active": "..."
      },
      ...
    ]
  }
  ```

### 趋势相关

- **端点**：`/api/post-trend`
- **方法**：GET
- **参数**：
  - `granularity`：时间粒度，可选值为`daily`、`weekly`、`monthly`，默认为`daily`
  - `days`：数据天数，默认为30
- **描述**：获取发帖趋势数据
- **返回示例**：
  ```json
  {
    "data": [
      {"date": "2025-03-15", "count": 120},
      {"date": "2025-03-16", "count": 150},
      ...
    ]
  }
  ```

- **端点**：`/api/update-trend`
- **方法**：GET
- **参数**：同`/api/post-trend`
- **描述**：获取更新趋势数据

- **端点**：`/api/view-trend`
- **方法**：GET
- **参数**：同`/api/post-trend`
- **描述**：获取浏览趋势数据

- **端点**：`/api/data-trends`
- **方法**：GET
- **参数**：
  - `days`：数据天数，默认为30
  - `granularity`：时间粒度，同上
- **描述**：获取多种数据趋势（发帖、更新、浏览）

### 车辆信息相关

- **端点**：`/api/car-info`
- **方法**：GET
- **参数**：
  - `make`：车辆品牌
  - `model`：车辆型号
  - `year`：年份
  - `limit`：返回数量，默认为20
  - `offset`：偏移量，默认为0
- **描述**：获取车辆信息数据

- **端点**：`/api/car-makes`
- **方法**：GET
- **描述**：获取所有车辆品牌

- **端点**：`/api/car-models`
- **方法**：GET
- **参数**：
  - `make`：车辆品牌
- **描述**：获取指定品牌的所有车辆型号

## 运行方式

```bash
# 在backend目录下运行
python app.py
```

服务将在`http://localhost:5000`启动。 