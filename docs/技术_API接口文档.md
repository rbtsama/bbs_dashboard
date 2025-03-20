# API接口文档

*最后更新日期：2025年3月19日*

本文档详细描述论坛数据洞察平台提供的所有API接口，包括请求参数、返回格式和使用示例，帮助开发人员进行应用集成和功能扩展。

## 目录

1. [基本信息](#基本信息)
2. [状态码说明](#状态码说明)
3. [错误处理](#错误处理)
4. [API接口列表](#API接口列表)
5. [常见问题排查](#常见问题排查)
6. [相关文档](#相关文档)

## 基本信息

- **基础URL**: `http://localhost:5000/api` (开发环境)
- **生产环境URL**: `https://您的域名/api`
- **请求格式**: 除文件上传外，所有请求均使用JSON格式
- **认证**: 部分API需要携带管理员密钥(`key=管理员密钥`)
- **CORS**: 支持跨域请求
- **速率限制**: 默认每IP每分钟60次请求

## 状态码说明

| 状态码 | 说明 |
|------|------|
| 200  | 成功 |
| 400  | 请求参数错误 |
| 401  | 未认证或认证失败 |
| 403  | 权限不足 |
| 404  | 资源不存在 |
| 429  | 请求频率超限 |
| 500  | 服务器内部错误 |

## 错误处理

所有API错误返回统一格式，便于前端处理：

```json
{
  "success": false,
  "error": {
    "code": "ERROR_CODE",
    "message": "错误描述信息",
    "details": {
      // 可选的错误详情
    }
  }
}
```

### 常见错误代码

| 错误代码 | 说明 | 解决方案 |
|---------|------|---------|
| INVALID_PARAMS | 参数格式错误 | 检查请求参数格式和类型 |
| MISSING_REQUIRED | 缺少必要参数 | 确保提供所有必需的参数 |
| UNAUTHORIZED | 未授权访问 | 检查认证信息是否正确 |
| RESOURCE_NOT_FOUND | 请求的资源不存在 | 确认使用正确的标识符 |
| RATE_LIMITED | 请求频率超过限制 | 降低请求频率或实现请求队列 |
| DB_ERROR | 数据库操作错误 | 重试请求，若持续报错请联系管理员 |
| SERVER_ERROR | 服务器内部错误 | 检查服务器日志，联系管理员 |

## API接口列表

### 1. 获取系统状态

检查系统运行状态。

**请求**:
- 方法: `GET`
- 路径: `/status`
- 参数: 无

**响应**:
```json
{
  "status": "ok",
  "version": "1.0.0",
  "uptime": "1d 2h 3m",
  "db_status": "connected",
  "last_update": "2025-03-20T09:30:15Z"
}
```

**示例**:
```bash
curl -X GET http://localhost:5000/api/status
```

### 2. 获取仪表盘数据

获取数据仪表盘所需的统计数据。

**请求**:
- 方法: `GET`
- 路径: `/dashboard`
- 参数: 
  - `period` (可选): 时间周期，可选值为`day`, `week`, `month`, `year`，默认为`week`

**响应**:
```json
{
  "post_stats": {
    "total_posts": 12503,
    "new_posts": 158,
    "active_posts": 423,
    "trend": [
      {"date": "2025-03-15", "value": 30},
      {"date": "2025-03-16", "value": 25},
      {"date": "2025-03-17", "value": 45},
      {"date": "2025-03-18", "value": 38},
      {"date": "2025-03-19", "value": 42},
      {"date": "2025-03-20", "value": 35}
    ]
  },
  "view_stats": {
    "total_views": 1528642,
    "average_views": 122,
    "trend": [
      {"date": "2025-03-15", "value": 5200},
      {"date": "2025-03-16", "value": 4800},
      {"date": "2025-03-17", "value": 6100},
      {"date": "2025-03-18", "value": 5800},
      {"date": "2025-03-19", "value": 6300},
      {"date": "2025-03-20", "value": 5900}
    ]
  },
  "action_stats": {
    "new_posts": 45,
    "reply_posts": 87,
    "repost_count": 356,
    "distribution": [
      {"name": "新发布", "value": 45},
      {"name": "回帖", "value": 87},
      {"name": "重发", "value": 356},
      {"name": "删回帖", "value": 12}
    ]
  },
  "top_authors": [
    {"name": "用户A", "post_count": 45, "activity_score": 89},
    {"name": "用户B", "post_count": 32, "activity_score": 76},
    {"name": "用户C", "post_count": 28, "activity_score": 65}
  ],
  "updated_at": "2025-03-20T12:30:00Z"
}
```

**示例**:
```bash
curl -X GET http://localhost:5000/api/dashboard?period=week
```

### 3. 获取帖子列表

获取论坛帖子列表，支持分页和筛选。

**请求**:
- 方法: `GET`
- 路径: `/posts`
- 参数:
  - `page` (可选): 页码，默认为1
  - `limit` (可选): 每页条数，默认为20，最大50
  - `sort` (可选): 排序方式，可选值为`newest`, `active`, `popular`，默认为`newest`
  - `author` (可选): 按作者筛选
  - `query` (可选): 按标题搜索

**响应**:
```json
{
  "posts": [
    {
      "id": 12345,
      "url": "https://example.com/thread/12345",
      "title": "帖子标题示例",
      "author": "用户名",
      "created_at": "2025-03-15T10:30:00Z",
      "updated_at": "2025-03-18T15:45:22Z",
      "read_count": 128,
      "reply_count": 15
    },
    // 更多帖子...
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 958,
    "pages": 48
  }
}
```

**示例**:
```bash
curl -X GET "http://localhost:5000/api/posts?page=1&limit=20&sort=active&author=用户A"
```

### 4. 获取单个帖子详情

获取单个帖子的详细信息。

**请求**:
- 方法: `GET`
- 路径: `/posts/:id`
- 参数:
  - `id`: 帖子ID

**响应**:
```json
{
  "id": 12345,
  "url": "https://example.com/thread/12345",
  "title": "帖子标题示例",
  "author": "用户名",
  "author_link": "https://example.com/user/用户名",
  "created_at": "2025-03-15T10:30:00Z",
  "updated_at": "2025-03-18T15:45:22Z",
  "content": "帖子内容...",
  "image_count": 5,
  "view_count": 128,
  "reply_count": 15,
  "repost_count": 3,
  "likes": 25,
  "car_info": {
    "make": "品牌",
    "model": "型号",
    "year": 2025,
    "price": "200,000",
    "features": "特性描述..."
  }
}
```

**示例**:
```bash
curl -X GET http://localhost:5000/api/posts/12345
```

### 5. 获取帖子动作历史

获取特定帖子的动作历史记录。

**请求**:
- 方法: `GET`
- 路径: `/posts/:id/actions`
- 参数:
  - `id`: 帖子ID
  - `page` (可选): 页码，默认为1
  - `limit` (可选): 每页条数，默认为20

**响应**:
```json
{
  "thread_id": 12345,
  "url": "https://example.com/thread/12345",
  "title": "帖子标题示例",
  "actions": [
    {
      "id": 1,
      "action": "新发布",
      "timestamp": "2025-03-15T10:30:00Z",
      "author": "用户名",
      "details": "首次发布"
    },
    {
      "id": 2,
      "action": "回帖",
      "timestamp": "2025-03-16T14:22:15Z",
      "author": "其他用户",
      "details": "回复内容..."
    },
    {
      "id": 3,
      "action": "重发",
      "timestamp": "2025-03-18T15:45:22Z",
      "author": "用户名",
      "details": "更新内容"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 3,
    "pages": 1
  }
}
```

**示例**:
```bash
curl -X GET http://localhost:5000/api/posts/12345/actions
```

### 6. 获取帖子排行榜

获取帖子排行榜数据。

**请求**:
- 方法: `GET`
- 路径: `/ranking/posts`
- 参数:
  - `type` (可选): 排行类型，可选值为`views`, `replies`, `activity`，默认为`activity`
  - `period` (可选): 时间周期，可选值为`day`, `week`, `month`, `all`，默认为`week`
  - `limit` (可选): 返回数量，默认为20，最大100

**响应**:
```json
{
  "type": "activity",
  "period": "week",
  "rankings": [
    {
      "rank": 1,
      "id": 12345,
      "url": "https://example.com/thread/12345",
      "title": "帖子标题1",
      "author": "用户A",
      "read_count": 1256,
      "reply_count": 45,
      "last_active": "2025-03-19T18:30:25Z",
      "days_old": 5,
      "score": 98.5
    },
    {
      "rank": 2,
      "id": 12346,
      "url": "https://example.com/thread/12346",
      "title": "帖子标题2",
      "author": "用户B",
      "read_count": 958,
      "reply_count": 32,
      "last_active": "2025-03-20T10:15:18Z",
      "days_old": 8,
      "score": 92.3
    }
    // 更多排名...
  ],
  "updated_at": "2025-03-20T12:30:00Z"
}
```

**示例**:
```bash
curl -X GET "http://localhost:5000/api/ranking/posts?type=activity&period=week&limit=20"
```

### 7. 获取作者排行榜

获取作者排行榜数据。

**请求**:
- 方法: `GET`
- 路径: `/ranking/authors`
- 参数:
  - `type` (可选): 排行类型，可选值为`posts`, `replies`, `activity`，默认为`activity`
  - `period` (可选): 时间周期，可选值为`day`, `week`, `month`, `all`，默认为`week`
  - `limit` (可选): 返回数量，默认为20，最大100

**响应**:
```json
{
  "type": "activity",
  "period": "week",
  "rankings": [
    {
      "rank": 1,
      "author": "用户A",
      "author_link": "https://example.com/user/用户A",
      "post_count": 45,
      "reply_count": 128,
      "last_active": "2025-03-20T10:30:15Z",
      "activity_score": 98.5
    },
    {
      "rank": 2,
      "author": "用户B",
      "author_link": "https://example.com/user/用户B",
      "post_count": 32,
      "reply_count": 95,
      "last_active": "2025-03-19T14:25:10Z",
      "activity_score": 92.3
    }
    // 更多排名...
  ],
  "updated_at": "2025-03-20T12:30:00Z"
}
```

**示例**:
```bash
curl -X GET "http://localhost:5000/api/ranking/authors?type=activity&period=week&limit=20"
```

### 8. 获取历史追踪数据

获取特定指标的历史数据。

**请求**:
- 方法: `GET`
- 路径: `/tracking/history`
- 参数:
  - `metric` (必选): 指标名称，可选值为`posts`, `views`, `replies`, `active_users`
  - `period` (可选): 时间周期，可选值为`day`, `week`, `month`, `year`，默认为`month`
  - `start_date` (可选): 开始日期，格式为`YYYY-MM-DD`
  - `end_date` (可选): 结束日期，格式为`YYYY-MM-DD`

**响应**:
```json
{
  "metric": "posts",
  "period": "month",
  "start_date": "2025-02-20",
  "end_date": "2025-03-20",
  "data": [
    {"date": "2025-02-20", "value": 35},
    {"date": "2025-02-21", "value": 28},
    {"date": "2025-02-22", "value": 42},
    // 更多数据点...
    {"date": "2025-03-20", "value": 38}
  ],
  "summary": {
    "total": 1256,
    "average": 42.5,
    "min": 28,
    "max": 65,
    "trend": "up" // up, down, stable
  }
}
```

**示例**:
```bash
curl -X GET "http://localhost:5000/api/tracking/history?metric=posts&period=month&start_date=2025-02-20&end_date=2025-03-20"
```

### 9. 获取追踪目标

获取当前设置的追踪目标列表。

**请求**:
- 方法: `GET`
- 路径: `/tracking/targets`
- 参数:
  - `page` (可选): 页码，默认为1
  - `limit` (可选): 每页条数，默认为20

**响应**:
```json
{
  "targets": [
    {
      "id": 1,
      "url": "https://example.com/thread/12345",
      "title": "帖子标题1",
      "created_at": "2025-03-15T10:30:00Z",
      "notes": "需要关注的重要帖子",
      "stats": {
        "views": 1256,
        "replies": 45,
        "reposts": 12,
        "last_update": "2025-03-20T09:15:30Z"
      }
    },
    {
      "id": 2,
      "url": "https://example.com/thread/12346",
      "title": "帖子标题2",
      "created_at": "2025-03-16T14:22:15Z",
      "notes": "竞品讨论",
      "stats": {
        "views": 958,
        "replies": 32,
        "reposts": 8,
        "last_update": "2025-03-19T16:45:12Z"
      }
    }
    // 更多目标...
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 15,
    "pages": 1
  }
}
```

**示例**:
```bash
curl -X GET http://localhost:5000/api/tracking/targets
```

### 10. 添加追踪目标

添加新的追踪目标。

**请求**:
- 方法: `POST`
- 路径: `/tracking/targets`
- 内容类型: `application/json`
- 请求体:
```json
{
  "url": "https://example.com/thread/12347",
  "title": "新的追踪目标",
  "notes": "需要密切关注的竞品信息"
}
```

**响应**:
```json
{
  "id": 3,
  "url": "https://example.com/thread/12347",
  "title": "新的追踪目标",
  "created_at": "2025-03-20T12:30:00Z",
  "notes": "需要密切关注的竞品信息",
  "status": "added"
}
```

**示例**:
```bash
curl -X POST \
  http://localhost:5000/api/tracking/targets \
  -H "Content-Type: application/json" \
  -d '{"url":"https://example.com/thread/12347","title":"新的追踪目标","notes":"需要密切关注的竞品信息"}'
```

### 11. 删除追踪目标

删除已有的追踪目标。

**请求**:
- 方法: `DELETE`
- 路径: `/tracking/targets/:id`
- 参数:
  - `id`: 目标ID

**响应**:
```json
{
  "id": 3,
  "status": "deleted",
  "message": "追踪目标已成功删除"
}
```

**示例**:
```bash
curl -X DELETE http://localhost:5000/api/tracking/targets/3
```

### 12. 获取词云数据

获取特定类型的词云数据。

**请求**:
- 方法: `GET`
- 路径: `/wordcloud/:type`
- 参数:
  - `type`: 词云类型，可选值为`thread`, `author`
  - `id` (可选): 特定帖子或作者ID，不提供则返回全局词云
  - `period` (可选): 时间周期，可选值为`day`, `week`, `month`, `all`，默认为`week`
  - `limit` (可选): 返回词数量，默认为100，最大500

**响应**:
```json
{
  "type": "thread",
  "id": 12345,
  "title": "帖子标题示例",
  "period": "week",
  "words": [
    {"text": "车型", "weight": 58},
    {"text": "性能", "weight": 45},
    {"text": "价格", "weight": 42},
    {"text": "配置", "weight": 38},
    {"text": "油耗", "weight": 36},
    // 更多词...
  ],
  "image_url": "https://example.com/wordcloud/thread_12345.png",
  "updated_at": "2025-03-20T12:30:00Z"
}
```

**示例**:
```bash
curl -X GET "http://localhost:5000/api/wordcloud/thread?id=12345&period=week&limit=100"
```

### 13. 获取车辆信息

获取从帖子中提取的车辆信息。

**请求**:
- 方法: `GET`
- 路径: `/car-info`
- 参数:
  - `page` (可选): 页码，默认为1
  - `limit` (可选): 每页条数，默认为20
  - `make` (可选): 按品牌筛选
  - `model` (可选): 按型号筛选
  - `year` (可选): 按年份筛选
  - `min_price` (可选): 最低价格
  - `max_price` (可选): 最高价格

**响应**:
```json
{
  "cars": [
    {
      "id": 1,
      "post_id": 12345,
      "url": "https://example.com/thread/12345",
      "title": "帖子标题示例",
      "make": "品牌A",
      "model": "型号X",
      "year": 2025,
      "price": "350,000",
      "features": ["全景天窗", "自动驾驶", "电动尾门"],
      "extracted_at": "2025-03-15T10:30:00Z"
    },
    {
      "id": 2,
      "post_id": 12346,
      "url": "https://example.com/thread/12346",
      "title": "另一个帖子标题",
      "make": "品牌B",
      "model": "型号Y",
      "year": 2024,
      "price": "280,000",
      "features": ["皮质座椅", "360度全景影像", "无线充电"],
      "extracted_at": "2025-03-16T14:22:15Z"
    }
    // 更多车辆信息...
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 345,
    "pages": 18
  },
  "summary": {
    "make_distribution": [
      {"name": "品牌A", "count": 120},
      {"name": "品牌B", "count": 98},
      {"name": "品牌C", "count": 86},
      {"name": "其他", "count": 41}
    ],
    "price_range": {
      "min": 150000,
      "max": 980000,
      "avg": 320000
    }
  }
}
```

**示例**:
```bash
curl -X GET "http://localhost:5000/api/car-info?page=1&limit=20&make=品牌A&min_price=200000&max_price=400000"
```

### 14. 触发数据库更新

触发数据库更新流程，需要管理员密钥。

**请求**:
- 方法: `POST`
- 路径: `/db-update`
- 参数:
  - `key` (必选): 管理员密钥
  - `steps` (可选): 要执行的步骤数组，默认执行所有步骤

**响应**:
```json
{
  "status": "started",
  "update_id": "update_20250320_123000",
  "steps": ["数据预处理", "数据分析", "数据导入", "词云生成", "数据备份"],
  "started_at": "2025-03-20T12:30:00Z",
  "estimated_completion": "2025-03-20T12:45:00Z"
}
```

**示例**:
```bash
curl -X POST \
  "http://localhost:5000/api/db-update?key=your_admin_key" \
  -H "Content-Type: application/json" \
  -d '{"steps":["数据预处理","数据分析","数据导入"]}'
```

### 15. 获取更新状态

获取数据库更新的状态。

**请求**:
- 方法: `GET`
- 路径: `/db-update/status`
- 参数:
  - `key` (必选): 管理员密钥
  - `update_id` (可选): 特定更新ID，不提供则返回最近一次更新

**响应**:
```json
{
  "update_id": "update_20250320_123000",
  "status": "in_progress",
  "progress": {
    "current_step": "数据分析",
    "completed_steps": ["数据预处理"],
    "pending_steps": ["数据导入", "词云生成", "数据备份"],
    "percent_complete": 35
  },
  "started_at": "2025-03-20T12:30:00Z",
  "estimated_completion": "2025-03-20T12:45:00Z",
  "logs": [
    {"time": "2025-03-20T12:30:00Z", "level": "info", "message": "开始更新流程"},
    {"time": "2025-03-20T12:32:15Z", "level": "info", "message": "数据预处理完成"},
    {"time": "2025-03-20T12:32:16Z", "level": "info", "message": "开始数据分析"}
  ]
}
```

**示例**:
```bash
curl -X GET "http://localhost:5000/api/db-update/status?key=your_admin_key"
```

### 16. 回滚数据库更新

触发数据库回滚操作，撤销最近一次更新。

**请求**:
- 方法: `POST`
- 路径: `/db-update/rollback`
- 参数:
  - `key` (必选): 管理员密钥
  - `update_id` (可选): 特定更新ID，不提供则回滚最近一次更新
  - `force` (可选): 是否强制回滚，布尔值，默认为false

**响应**:
```json
{
  "status": "started",
  "operation": "rollback",
  "update_id": "update_20250320_123000",
  "started_at": "2025-03-20T12:50:00Z",
  "backup_used": "backup_20250320_123000.db"
}
```

**示例**:
```bash
curl -X POST \
  "http://localhost:5000/api/db-update/rollback?key=your_admin_key" \
  -H "Content-Type: application/json" \
  -d '{"force":true}'
```

## 常见问题排查

### 1. 接口返回空数据

**可能原因**:
- 数据库中没有符合条件的数据
- 筛选参数过于严格
- 分页参数设置不正确

**解决方案**:
- 检查筛选参数，尝试放宽条件
- 确认分页参数正确(page从1开始)
- 查看系统日志确认数据库状态

### 2. 请求超时

**可能原因**:
- 查询涉及大量数据处理
- 服务器负载过高
- 网络连接问题

**解决方案**:
- 优化查询参数，减少数据量
- 实现分页或增量加载
- 检查网络连接和服务器状态

### 3. 认证失败

**可能原因**:
- 密钥错误或过期
- 权限不足
- 请求格式错误

**解决方案**:
- 确认使用最新的密钥
- 检查权限设置
- 确保请求头格式正确

## 实际使用示例

### 主题排行榜数据获取 - 完整示例

**请求**:
```javascript
// 使用Axios库示例
async function fetchThreadRanking() {
  try {
    const response = await axios.get('http://localhost:5000/api/thread-ranking', {
      params: {
        page: 1,
        limit: 20,
        sort_field: 'heat',
        sort_order: 'desc',
        days: 7,
        min_heat: 100
      }
    });
    
    if (response.data && response.data.success) {
      const { data, total, page, limit } = response.data;
      console.log(`获取到${data.length}条记录，总记录数：${total}`);
      
      // 处理数据
      data.forEach(thread => {
        console.log(`${thread.title} - 热度: ${thread.heat}`);
      });
      
      // 计算总页数
      const totalPages = Math.ceil(total / limit);
      console.log(`当前页 ${page}/${totalPages}`);
    } else {
      throw new Error('请求成功但返回错误');
    }
  } catch (error) {
    // 错误处理
    if (error.response) {
      // 服务器返回错误状态码
      console.error(`服务器错误 ${error.response.status}:`, error.response.data);
      
      // 处理特定错误
      if (error.response.status === 429) {
        console.error('请求频率过高，请稍后再试');
      }
    } else if (error.request) {
      // 请求发送但未收到响应
      console.error('服务器无响应，请检查网络连接');
    } else {
      // 请求设置错误
      console.error('请求错误:', error.message);
    }
  }
}
```

### 车辆信息查询 - 带错误处理

**请求**:
```javascript
async function searchCarInfo() {
  const searchParams = {
    make: 'Toyota',       // 车辆品牌
    model: 'Camry',       // 车型
    min_year: 2018,       // 最小年份
    max_year: 2022,       // 最大年份
    min_price: 15000,     // 最低价格
    max_price: 30000,     // 最高价格
    trade_type: 'sale',   // 交易类型: 'sale'(出售)/'buy'(求购)
    page: 1,
    limit: 15
  };
  
  try {
    const response = await axios.get('http://localhost:5000/api/car-info', {
      params: searchParams,
      timeout: 10000 // 设置10秒超时
    });
    
    return response.data;
  } catch (error) {
    // 定义重试函数
    const retry = async (retryCount = 3, delay = 1000) => {
      if (retryCount <= 0) {
        throw new Error('重试次数已用完');
      }
      
      console.log(`请求失败，${delay/1000}秒后重试，剩余重试次数: ${retryCount}`);
      
      await new Promise(resolve => setTimeout(resolve, delay));
      
      try {
        const retryResponse = await axios.get('http://localhost:5000/api/car-info', {
          params: searchParams,
          timeout: 10000
        });
        return retryResponse.data;
      } catch (retryError) {
        return retry(retryCount - 1, delay * 1.5);
      }
    };
    
    // 对特定错误类型进行重试
    if (error.code === 'ECONNABORTED' || error.response?.status >= 500) {
      return retry();
    }
    
    // 其他类型错误直接抛出
    throw error;
  }
}
```

### 词云数据获取 - 带缓存

**请求**:
```javascript
// 使用localStorage缓存词云数据
async function fetchWordCloudWithCache() {
  const CACHE_KEY = 'wordcloud_data';
  const CACHE_TTL = 30 * 60 * 1000; // 30分钟缓存
  
  // 检查缓存
  const cachedData = localStorage.getItem(CACHE_KEY);
  if (cachedData) {
    const { data, timestamp } = JSON.parse(cachedData);
    const now = Date.now();
    
    // 缓存未过期，直接使用
    if (now - timestamp < CACHE_TTL) {
      console.log('使用缓存的词云数据');
      return data;
    }
  }
  
  // 缓存不存在或已过期，发起请求
  try {
    const response = await axios.get('http://localhost:5000/api/title-wordcloud');
    
    if (response.data && Array.isArray(response.data)) {
      // 更新缓存
      localStorage.setItem(CACHE_KEY, JSON.stringify({
        data: response.data,
        timestamp: Date.now()
      }));
      
      return response.data;
    } else {
      throw new Error('无效的词云数据格式');
    }
  } catch (error) {
    console.error('获取词云数据失败:', error);
    
    // 如果有缓存，即使过期也返回缓存数据作为后备
    if (cachedData) {
      console.log('使用过期缓存作为后备');
      return JSON.parse(cachedData).data;
    }
    
    throw error;
  }
}
```

## 相关文档

- [模块技术设计文档](./技术_模块设计.md) - 了解系统各功能模块的详细设计
- [数据库设计文档](./技术_数据库设计.md) - 了解数据结构和关系
- [自动化更新文档](./技术_自动化更新.md) - 了解数据自动更新流程
- [前端架构文档](./技术_前端架构.md) - 了解前端实现和组件设计

## 变更日志

### 2025-03-19
- 增加了更多使用示例和错误处理方案
- 增加了与其他文档的交叉引用
- 修正了API参数描述中的错误

### 2025-03-14
- 初始版本 