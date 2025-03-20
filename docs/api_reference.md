# API 参考文档

本文档详细介绍论坛数据分析系统的API接口。

## 帖子历史与动作日志API

### 获取帖子动作日志

获取特定帖子的历史动作记录，包括发布、重发、回帖和删除回帖等事件。

**请求**：
- 方法：`GET`
- 路径：`/api/action-logs`
- 参数：
  - `thread_id`: 帖子ID(优先使用)
  - `url`: 帖子URL(当thread_id未提供或未找到匹配记录时使用)
  - `page`: 页码，默认为1
  - `limit`: 每页记录数，默认为10

**响应**：
```json
{
  "data": [
    {
      "id": 1,
      "thread_id": "1234567890",
      "url": "https://example.com/thread/1234567890",
      "title": "帖子标题",
      "author": "作者名",
      "author_link": "作者链接",
      "action": "新发布",
      "action_time": "2024-03-17T12:00:00Z",
      "event_type": "新发布",
      "event_time": "2024-03-17T12:00:00Z",
      "read_count": 100,
      "reply_count": 5
    }
  ],
  "total": 10,
  "page": 1,
  "limit": 10
}
```

**字段说明**：
- `data`: 包含动作日志的数组
  - `thread_id`: 帖子ID
  - `url`: 帖子URL
  - `title`: 帖子标题
  - `author`: 作者名
  - `author_link`: 作者链接
  - `action`: 动作类型，可能的值：
    - `新发布`: 首次发布帖子
    - `重发`: 帖子被重新发布
    - `回帖`: 有新回复
    - `删回帖`: 删除回复
  - `action_time`: 动作发生时间
  - `event_type`: 与action相同，兼容前端
  - `event_time`: 与action_time相同，兼容前端
  - `read_count`: 当时的阅读数
  - `reply_count`: 当时的回复数
- `total`: 总记录数
- `page`: 当前页码
- `limit`: 每页记录数

**示例请求**：
```
GET /api/action-logs?thread_id=1234567890&page=1&limit=10
```

**错误响应**：
- 如果未提供`thread_id`或`url`参数：
```json
{
  "error": "请提供thread_id或url参数"
}
```
- 如果数据库查询出错，返回空数据和错误信息：
```json
{
  "data": [],
  "total": 0,
  "page": 1,
  "limit": 10,
  "error": "数据库查询错误: [错误详情]"
}
```

### 获取作者发帖历史

获取特定作者的发帖历史记录。

**请求**：
- 方法：`GET`
- 路径：`/api/author-post-history`
- 参数：
  - `author`: 作者名称(必填)
  - `page`: 页码，默认为1
  - `limit`: 每页记录数，默认为10

**响应**：
```json
{
  "data": [
    {
      "url": "https://example.com/thread/1234567890",
      "title": "帖子标题",
      "post_time": "2024-03-17T12:00:00Z",
      "is_active": true
    }
  ],
  "total": 20,
  "page": 1,
  "limit": 10,
  "debug": {
    "total_posts": 20,
    "active_posts": 15,
    "inactive_posts": 5
  }
}
```

**字段说明**：
- `data`: 包含作者发帖历史的数组
  - `url`: 帖子URL
  - `title`: 帖子标题
  - `post_time`: 发帖时间
  - `is_active`: 帖子是否仍然活跃
- `total`: 总记录数
- `page`: 当前页码
- `limit`: 每页记录数
- `debug`: 调试信息(可选)

## 帖子关注API

### 获取关注列表

获取用户关注的帖子列表。

**请求**：
- 方法：`GET`
- 路径：`/api/thread-follows`
- 参数：
  - `type`: 关注类型，可选值：'my_follow'(我的关注)或'marked'(我的帖子)
  - `page`: 页码，默认为1
  - `page_size`: 每页记录数，默认为20

**响应**：
```json
{
  "data": [
    {
      "id": 1,
      "thread_id": "1234567890",
      "url": "https://example.com/thread/1234567890",
      "title": "帖子标题",
      "author": "作者名",
      "author_link": "作者链接",
      "type": "my_follow",
      "days_old": 5,
      "last_active": "3天前",
      "repost_count": 2,
      "reply_count": 10,
      "delete_reply_count": 1,
      "created_at": "2024-03-17T12:00:00Z"
    }
  ],
  "total": 15,
  "page": 1,
  "page_size": 20
}
```

### 添加关注

添加一个帖子到关注列表。

**请求**：
- 方法：`POST`
- 路径：`/api/thread-follows`
- 内容类型：`application/json`
- 请求体：
```json
{
  "thread_id": "1234567890",
  "url": "https://example.com/thread/1234567890",
  "title": "帖子标题",
  "author": "作者名",
  "author_link": "作者链接",
  "type": "my_follow"
}
```

**响应**：
```json
{
  "message": "关注成功",
  "data": {
    "id": 1,
    "thread_id": "1234567890",
    "url": "https://example.com/thread/1234567890",
    "title": "帖子标题",
    "type": "my_follow",
    "created_at": "2024-03-17T12:00:00Z"
  }
}
```

### 取消关注

从关注列表中删除一个帖子。

**请求**：
- 方法：`DELETE`
- 路径：`/api/thread-follows`
- 参数：
  - `thread_id`: 帖子ID
  - `status`: 关注状态(可选)

**响应**：
```json
{
  "message": "成功取消关注，共删除1条记录",
  "affected_rows": 1
}
``` 