# API参考文档

本文档描述系统提供的API接口，包括接口说明、参数定义和使用示例。

## API概述

系统提供RESTful API接口，支持以下功能：

- 数据查询：查询帖子、作者等数据
- 词云生成：请求生成词云和获取词云状态
- 统计数据：获取统计数据和趋势数据
- 用户数据：管理用户设置、收藏和评论

所有API接口使用JSON格式进行数据交换，返回的状态码遵循HTTP标准。

## API基础信息

- **基础URL**: `http://localhost:5000/api`
- **认证方式**: 部分接口需要API密钥认证，通过请求头`X-API-Key`传递
- **响应格式**: 所有接口返回JSON格式数据
- **错误处理**: 错误时返回包含`error`字段的JSON对象

## 帖子相关API

### 获取帖子列表

获取符合条件的帖子列表。

- **URL**: `/posts`
- **方法**: `GET`
- **参数**:
  - `page`: 页码，默认为1
  - `page_size`: 每页记录数，默认为20
  - `sort_by`: 排序字段，可选值为`last_active`、`post_time`、`reply_count`、`read_count`，默认为`last_active`
  - `sort_order`: 排序方向，可选值为`asc`、`desc`，默认为`desc`
  - `author`: 按作者筛选
  - `keyword`: 按关键词筛选（标题和内容）
  - `start_date`: 起始日期筛选，格式为`YYYY-MM-DD`
  - `end_date`: 结束日期筛选，格式为`YYYY-MM-DD`

- **响应**:
  ```json
  {
    "total": 1250,
    "page": 1,
    "page_size": 20,
    "posts": [
      {
        "url": "https://example.com/thread/1234567",
        "thread_id": "1234567",
        "title": "示例帖子标题",
        "author": "示例作者",
        "post_time": "2023-03-14T12:30:45",
        "last_active": "2023-03-15T08:15:30",
        "reply_count": 25,
        "read_count": 1200
      },
      // 更多帖子...
    ]
  }
  ```

- **示例**:
  ```bash
  curl -X GET "http://localhost:5000/api/posts?page=1&page_size=10&sort_by=reply_count&sort_order=desc"
  ```

### 获取帖子详情

获取特定帖子的详细信息。

- **URL**: `/posts/{thread_id}`
- **方法**: `GET`
- **参数**:
  - `thread_id`: 帖子ID

- **响应**:
  ```json
  {
    "url": "https://example.com/thread/1234567",
    "thread_id": "1234567",
    "title": "示例帖子标题",
    "author": "示例作者",
    "post_time": "2023-03-14T12:30:45",
    "last_active": "2023-03-15T08:15:30",
    "reply_count": 25,
    "read_count": 1200,
    "content": "帖子的详细内容...",
    "replies": [
      {
        "reply_id": "r123",
        "author": "回复作者",
        "content": "回复内容...",
        "reply_time": "2023-03-14T14:20:10"
      },
      // 更多回复...
    ]
  }
  ```

- **示例**:
  ```bash
  curl -X GET "http://localhost:5000/api/posts/1234567"
  ```

### 获取帖子历史数据

获取特定帖子的历史数据。

- **URL**: `/posts/{thread_id}/history`
- **方法**: `GET`
- **参数**:
  - `thread_id`: 帖子ID
  - `start_date`: 起始日期，格式为`YYYY-MM-DD`
  - `end_date`: 结束日期，格式为`YYYY-MM-DD`

- **响应**:
  ```json
  {
    "thread_id": "1234567",
    "title": "示例帖子标题",
    "history": [
      {
        "date": "2023-03-14",
        "reply_count": 10,
        "read_count": 500
      },
      {
        "date": "2023-03-15",
        "reply_count": 25,
        "read_count": 1200
      },
      // 更多历史数据...
    ]
  }
  ```

- **示例**:
  ```bash
  curl -X GET "http://localhost:5000/api/posts/1234567/history?start_date=2023-03-01&end_date=2023-03-15"
  ```

## 作者相关API

### 获取作者列表

获取符合条件的作者列表。

- **URL**: `/authors`
- **方法**: `GET`
- **参数**:
  - `page`: 页码，默认为1
  - `page_size`: 每页记录数，默认为20
  - `sort_by`: 排序字段，可选值为`post_count`、`reply_count`、`last_active`，默认为`post_count`
  - `sort_order`: 排序方向，可选值为`asc`、`desc`，默认为`desc`
  - `keyword`: 按作者名称筛选

- **响应**:
  ```json
  {
    "total": 500,
    "page": 1,
    "page_size": 20,
    "authors": [
      {
        "name": "示例作者",
        "post_count": 150,
        "reply_count": 320,
        "last_active": "2023-03-15T08:15:30",
        "first_seen": "2022-01-10T09:30:15"
      },
      // 更多作者...
    ]
  }
  ```

- **示例**:
  ```bash
  curl -X GET "http://localhost:5000/api/authors?page=1&page_size=10&sort_by=post_count&sort_order=desc"
  ```

### 获取作者详情

获取特定作者的详细信息。

- **URL**: `/authors/{name}`
- **方法**: `GET`
- **参数**:
  - `name`: 作者名称

- **响应**:
  ```json
  {
    "name": "示例作者",
    "post_count": 150,
    "reply_count": 320,
    "last_active": "2023-03-15T08:15:30",
    "first_seen": "2022-01-10T09:30:15",
    "recent_posts": [
      {
        "thread_id": "1234567",
        "title": "示例帖子标题",
        "post_time": "2023-03-14T12:30:45",
        "reply_count": 25
      },
      // 更多帖子...
    ]
  }
  ```

- **示例**:
  ```bash
  curl -X GET "http://localhost:5000/api/authors/%E7%A4%BA%E4%BE%8B%E4%BD%9C%E8%80%85"
  ```

### 获取作者历史数据

获取特定作者的历史数据。

- **URL**: `/authors/{name}/history`
- **方法**: `GET`
- **参数**:
  - `name`: 作者名称
  - `start_date`: 起始日期，格式为`YYYY-MM-DD`
  - `end_date`: 结束日期，格式为`YYYY-MM-DD`

- **响应**:
  ```json
  {
    "name": "示例作者",
    "history": [
      {
        "date": "2023-03-14",
        "post_count": 145,
        "reply_count": 310
      },
      {
        "date": "2023-03-15",
        "post_count": 150,
        "reply_count": 320
      },
      // 更多历史数据...
    ]
  }
  ```

- **示例**:
  ```bash
  curl -X GET "http://localhost:5000/api/authors/%E7%A4%BA%E4%BE%8B%E4%BD%9C%E8%80%85/history?start_date=2023-03-01&end_date=2023-03-15"
  ```

## 词云相关API

### 请求生成词云

请求为特定作者或帖子生成词云。

- **URL**: `/wordcloud/generate`
- **方法**: `POST`
- **请求体**:
  ```json
  {
    "type": "author",  // 或 "thread"
    "target_id": "示例作者"  // 作者名称或帖子ID
  }
  ```

- **响应**:
  ```json
  {
    "success": true,
    "job_id": 123,
    "message": "词云生成任务已创建"
  }
  ```

- **示例**:
  ```bash
  curl -X POST "http://localhost:5000/api/wordcloud/generate" \
       -H "Content-Type: application/json" \
       -d '{"type":"author","target_id":"示例作者"}'
  ```

### 获取词云任务状态

获取词云生成任务的状态。

- **URL**: `/wordcloud/status/{job_id}`
- **方法**: `GET`
- **参数**:
  - `job_id`: 任务ID

- **响应**:
  ```json
  {
    "job_id": 123,
    "job_type": "author",
    "target_id": "示例作者",
    "status": "completed",  // pending, processing, completed, failed
    "error_message": null,
    "created_at": "2023-03-15T10:20:30",
    "updated_at": "2023-03-15T10:21:45",
    "image_path": "data/wordcloud/author/author_示例作者_20230315_102145.png",
    "word_count": 250
  }
  ```

- **示例**:
  ```bash
  curl -X GET "http://localhost:5000/api/wordcloud/status/123"
  ```

### 获取词云缓存

获取已缓存的词云数据。

- **URL**: `/wordcloud/cache/{cache_type}/{target_id}`
- **方法**: `GET`
- **参数**:
  - `cache_type`: 缓存类型，可选值为`author`、`thread`
  - `target_id`: 目标ID，作者名称或帖子ID

- **响应**:
  ```json
  {
    "cache_exists": true,
    "cache_type": "author",
    "target_id": "示例作者",
    "image_path": "data/wordcloud/author/author_示例作者_20230315_102145.png",
    "word_count": 250,
    "created_at": "2023-03-15T10:21:45",
    "updated_at": "2023-03-15T10:21:45"
  }
  ```

- **示例**:
  ```bash
  curl -X GET "http://localhost:5000/api/wordcloud/cache/author/%E7%A4%BA%E4%BE%8B%E4%BD%9C%E8%80%85"
  ```

## 统计数据API

### 获取总体统计数据

获取系统的总体统计数据。

- **URL**: `/statistics/summary`
- **方法**: `GET`

- **响应**:
  ```json
  {
    "total_posts": 12500,
    "total_authors": 1200,
    "total_replies": 85000,
    "total_reads": 1250000,
    "active_posts_today": 150,
    "active_authors_today": 75,
    "last_update": "2023-03-15T08:00:00"
  }
  ```

- **示例**:
  ```bash
  curl -X GET "http://localhost:5000/api/statistics/summary"
  ```

### 获取趋势数据

获取系统的趋势统计数据。

- **URL**: `/statistics/trends`
- **方法**: `GET`
- **参数**:
  - `period`: 统计周期，可选值为`daily`、`weekly`、`monthly`，默认为`daily`
  - `start_date`: 起始日期，格式为`YYYY-MM-DD`
  - `end_date`: 结束日期，格式为`YYYY-MM-DD`
  - `metric`: 统计指标，可选值为`posts`、`authors`、`replies`、`reads`，默认为`posts`

- **响应**:
  ```json
  {
    "period": "daily",
    "metric": "posts",
    "data": [
      {
        "date": "2023-03-01",
        "value": 120
      },
      {
        "date": "2023-03-02",
        "value": 135
      },
      // 更多数据...
    ]
  }
  ```

- **示例**:
  ```bash
  curl -X GET "http://localhost:5000/api/statistics/trends?period=daily&metric=posts&start_date=2023-03-01&end_date=2023-03-15"
  ```

### 获取热门帖子

获取指定时间段内的热门帖子。

- **URL**: `/statistics/hot_posts`
- **方法**: `GET`
- **参数**:
  - `period`: 统计周期，可选值为`today`、`week`、`month`，默认为`today`
  - `limit`: 返回记录数，默认为10
  - `metric`: 排序指标，可选值为`reply_count`、`read_count`，默认为`reply_count`

- **响应**:
  ```json
  {
    "period": "today",
    "metric": "reply_count",
    "posts": [
      {
        "thread_id": "1234567",
        "title": "示例热门帖子",
        "author": "示例作者",
        "reply_count": 50,
        "read_count": 2000,
        "last_active": "2023-03-15T08:15:30"
      },
      // 更多帖子...
    ]
  }
  ```

- **示例**:
  ```bash
  curl -X GET "http://localhost:5000/api/statistics/hot_posts?period=week&metric=reply_count&limit=5"
  ```

### 获取活跃作者

获取指定时间段内的活跃作者。

- **URL**: `/statistics/active_authors`
- **方法**: `GET`
- **参数**:
  - `period`: 统计周期，可选值为`today`、`week`、`month`，默认为`today`
  - `limit`: 返回记录数，默认为10
  - `metric`: 排序指标，可选值为`post_count`、`reply_count`，默认为`post_count`

- **响应**:
  ```json
  {
    "period": "today",
    "metric": "post_count",
    "authors": [
      {
        "name": "示例活跃作者",
        "post_count": 5,
        "reply_count": 25,
        "last_active": "2023-03-15T08:15:30"
      },
      // 更多作者...
    ]
  }
  ```

- **示例**:
  ```bash
  curl -X GET "http://localhost:5000/api/statistics/active_authors?period=week&metric=post_count&limit=5"
  ```

## 用户数据API

### 获取用户设置

获取当前用户的设置。

- **URL**: `/user/settings`
- **方法**: `GET`
- **请求头**:
  - `X-API-Key`: API密钥

- **响应**:
  ```json
  {
    "user_id": "u123",
    "display_name": "用户昵称",
    "theme": "light",
    "notification_enabled": true,
    "email_notification": false,
    "created_at": "2023-01-15T10:20:30",
    "updated_at": "2023-03-10T15:40:50"
  }
  ```

- **示例**:
  ```bash
  curl -X GET "http://localhost:5000/api/user/settings" \
       -H "X-API-Key: your_api_key_here"
  ```

### 更新用户设置

更新当前用户的设置。

- **URL**: `/user/settings`
- **方法**: `PUT`
- **请求头**:
  - `X-API-Key`: API密钥
- **请求体**:
  ```json
  {
    "display_name": "新昵称",
    "theme": "dark",
    "notification_enabled": true,
    "email_notification": true
  }
  ```

- **响应**:
  ```json
  {
    "success": true,
    "message": "用户设置已更新",
    "settings": {
      "user_id": "u123",
      "display_name": "新昵称",
      "theme": "dark",
      "notification_enabled": true,
      "email_notification": true,
      "created_at": "2023-01-15T10:20:30",
      "updated_at": "2023-03-15T09:25:40"
    }
  }
  ```

- **示例**:
  ```bash
  curl -X PUT "http://localhost:5000/api/user/settings" \
       -H "Content-Type: application/json" \
       -H "X-API-Key: your_api_key_here" \
       -d '{"display_name":"新昵称","theme":"dark","notification_enabled":true,"email_notification":true}'
  ```

### 获取用户收藏

获取当前用户的收藏列表。

- **URL**: `/user/favorites`
- **方法**: `GET`
- **请求头**:
  - `X-API-Key`: API密钥
- **参数**:
  - `page`: 页码，默认为1
  - `page_size`: 每页记录数，默认为20

- **响应**:
  ```json
  {
    "total": 25,
    "page": 1,
    "page_size": 20,
    "favorites": [
      {
        "id": "f123",
        "thread_id": "1234567",
        "title": "收藏的帖子标题",
        "author": "帖子作者",
        "added_at": "2023-03-10T15:40:50",
        "note": "用户添加的笔记"
      },
      // 更多收藏...
    ]
  }
  ```

- **示例**:
  ```bash
  curl -X GET "http://localhost:5000/api/user/favorites?page=1&page_size=10" \
       -H "X-API-Key: your_api_key_here"
  ```

### 添加收藏

添加帖子到收藏。

- **URL**: `/user/favorites`
- **方法**: `POST`
- **请求头**:
  - `X-API-Key`: API密钥
- **请求体**:
  ```json
  {
    "thread_id": "1234567",
    "note": "这是一个很有用的帖子"
  }
  ```

- **响应**:
  ```json
  {
    "success": true,
    "message": "帖子已添加到收藏",
    "favorite": {
      "id": "f124",
      "thread_id": "1234567",
      "title": "帖子标题",
      "author": "帖子作者",
      "added_at": "2023-03-15T09:30:45",
      "note": "这是一个很有用的帖子"
    }
  }
  ```

- **示例**:
  ```bash
  curl -X POST "http://localhost:5000/api/user/favorites" \
       -H "Content-Type: application/json" \
       -H "X-API-Key: your_api_key_here" \
       -d '{"thread_id":"1234567","note":"这是一个很有用的帖子"}'
  ```

### 删除收藏

从收藏中删除帖子。

- **URL**: `/user/favorites/{favorite_id}`
- **方法**: `DELETE`
- **请求头**:
  - `X-API-Key`: API密钥
- **参数**:
  - `favorite_id`: 收藏ID

- **响应**:
  ```json
  {
    "success": true,
    "message": "帖子已从收藏中删除"
  }
  ```

- **示例**:
  ```bash
  curl -X DELETE "http://localhost:5000/api/user/favorites/f124" \
       -H "X-API-Key: your_api_key_here"
  ```

## 关注功能API

### 获取关注列表

获取当前用户的关注列表。

- **URL**: `/thread-follows`
- **方法**: `GET`
- **参数**:
  - `type`: 关注类型，可选值为`my_follow`（我的关注）或`marked`（我的帖子），默认为`my_follow`
  - `page`: 页码，默认为1
  - `page_size`: 每页记录数，默认为10

- **响应**:
  ```json
  {
    "total": 25,
    "page": 1,
    "page_size": 10,
    "data": [
      {
        "id": 1,
        "thread_id": "1234567",
        "url": "https://example.com/t_1234567.html",
        "title": "关注的帖子标题",
        "author": "帖子作者",
        "author_link": "https://example.com/u_123",
        "type": "my_follow",
        "daysold": 5,
        "last_active": 2,
        "repost_count": 3,
        "reply_count": 10,
        "delete_reply_count": 1,
        "created_at": "2023-03-15T09:30:45",
        "updated_at": "2023-03-15T09:30:45"
      },
      // 更多关注记录...
    ]
  }
  ```

- **示例**:
  ```bash
  curl -X GET "http://localhost:5000/api/thread-follows?type=my_follow&page=1&page_size=10"
  ```

### 添加关注

添加帖子到关注列表。

- **URL**: `/thread-follows`
- **方法**: `POST`
- **请求体**:
  ```json
  {
    "thread_id": "1234567",
    "type": "my_follow",
    "url": "https://example.com/t_1234567.html",
    "title": "帖子标题",
    "author": "帖子作者",
    "author_link": "https://example.com/u_123"
  }
  ```

- **响应**:
  ```json
  {
    "success": true,
    "message": "帖子已成功添加到关注列表",
    "follow": {
      "id": 1,
      "thread_id": "1234567",
      "url": "https://example.com/t_1234567.html",
      "title": "帖子标题",
      "author": "帖子作者",
      "author_link": "https://example.com/u_123",
      "type": "my_follow",
      "daysold": 5,
      "last_active": 2,
      "repost_count": 3,
      "reply_count": 10,
      "delete_reply_count": 1,
      "created_at": "2023-03-15T09:30:45",
      "updated_at": "2023-03-15T09:30:45"
    }
  }
  ```

- **示例**:
  ```bash
  curl -X POST "http://localhost:5000/api/thread-follows" \
       -H "Content-Type: application/json" \
       -d '{"thread_id":"1234567","type":"my_follow","url":"https://example.com/t_1234567.html","title":"帖子标题","author":"帖子作者","author_link":"https://example.com/u_123"}'
  ```

### 取消关注

从关注列表中删除帖子。

- **URL**: `/thread-follows`
- **方法**: `DELETE`
- **请求体**:
  ```json
  {
    "thread_id": "1234567",
    "type": "my_follow"
  }
  ```

- **响应**:
  ```json
  {
    "success": true,
    "message": "帖子已从关注列表中删除"
  }
  ```

- **示例**:
  ```bash
  curl -X DELETE "http://localhost:5000/api/thread-follows" \
       -H "Content-Type: application/json" \
       -d '{"thread_id":"1234567","type":"my_follow"}'
  ```

## 错误处理

所有API在发生错误时返回相应的HTTP状态码和包含错误信息的JSON对象：

```json
{
  "error": "错误信息描述",
  "code": "ERROR_CODE",
  "details": {
    // 可选的错误详情
  }
}
```

常见的错误状态码：

- `400 Bad Request`: 请求参数错误
- `401 Unauthorized`: 未提供API密钥或API密钥无效
- `403 Forbidden`: 没有权限访问请求的资源
- `404 Not Found`: 请求的资源不存在
- `500 Internal Server Error`: 服务器内部错误

## API使用示例

### Python示例

```python
import requests
import json

# 基础URL
base_url = "http://localhost:5000/api"

# 获取热门帖子
def get_hot_posts(period="week", limit=5):
    url = f"{base_url}/statistics/hot_posts"
    params = {
        "period": period,
        "limit": limit,
        "metric": "reply_count"
    }
    response = requests.get(url, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# 请求生成词云
def request_wordcloud(type, target_id):
    url = f"{base_url}/wordcloud/generate"
    data = {
        "type": type,
        "target_id": target_id
    }
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        return None

# 使用示例
hot_posts = get_hot_posts()
print(json.dumps(hot_posts, indent=2))

wordcloud_job = request_wordcloud("author", "示例作者")
print(json.dumps(wordcloud_job, indent=2))
```

### JavaScript示例

```javascript
// 基础URL
const baseUrl = "http://localhost:5000/api";

// 获取作者详情
async function getAuthorDetails(authorName) {
  try {
    const response = await fetch(`${baseUrl}/authors/${encodeURIComponent(authorName)}`);
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("获取作者详情失败:", error);
    return null;
  }
}

// 添加收藏
async function addFavorite(threadId, note, apiKey) {
  try {
    const response = await fetch(`${baseUrl}/user/favorites`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-API-Key": apiKey
      },
      body: JSON.stringify({
        thread_id: threadId,
        note: note
      })
    });
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error("添加收藏失败:", error);
    return null;
  }
}

// 使用示例
getAuthorDetails("示例作者")
  .then(data => console.log(data))
  .catch(error => console.error(error));

addFavorite("1234567", "重要帖子", "your_api_key_here")
  .then(data => console.log(data))
  .catch(error => console.error(error));
```

## 相关文档

- [系统架构](./db_system_architecture.md)
- [数据库概览](./db_overview.md)
- [词云生成](./db_wordcloud_generation.md) 