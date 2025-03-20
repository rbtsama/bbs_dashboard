# 前端组件文档

本文档详细介绍论坛数据分析系统中的关键前端组件，特别是与帖子历史和动作日志相关的组件。

## 帖子历史与动作日志组件

### ActionLogs.js

`ActionLogs`组件展示特定帖子的所有历史动作，包括发布、重发、回帖和删除回帖等事件。

#### 主要功能

- 获取并展示帖子的完整历史记录
- 支持按时间线方式展示事件
- 提供分页功能
- 支持通过`threadId`或`url`参数查询特定帖子

#### 属性

| 属性名 | 类型 | 说明 |
|-------|------|------|
| threadId | String | 帖子ID(TEXT类型) |
| url | String | 帖子URL |

#### API接口

- 接口：`/api/action-logs`
- 参数：
  - `thread_id`: 帖子ID
  - `url`: 帖子URL
  - `page`: 页码
  - `limit`: 每页记录数

#### 示例用法

```jsx
// 使用threadId查询帖子历史
<ActionLogs threadId="1234567890" />

// 使用url查询帖子历史
<ActionLogs url="https://example.com/thread/1234567890" />
```

#### 字段映射

组件从后端接收数据后，确保以下字段的映射：
- `event_type` 映射自 `action`
- `event_time` 映射自 `action_time`

### HoverActionLogs

`HoverActionLogs`是`ActionLogs`的简化版本，专为悬停预览设计，显示最近的几条记录。

#### 属性

| 属性名 | 类型 | 说明 |
|-------|------|------|
| threadId | String | 帖子ID |
| url | String | 帖子URL |
| onViewMore | Function | 点击"查看更多"按钮时的回调函数 |

### PostHistoryLogs.js

`PostHistoryLogs`组件展示特定作者的发帖历史记录。

#### 主要功能

- 获取并展示作者的发帖历史
- 区分活跃和不活跃的帖子
- 提供分页功能
- 支持外部链接

#### 属性

| 属性名 | 类型 | 说明 |
|-------|------|------|
| author | String | 作者名称 |

#### API接口

- 接口：`/api/author-post-history`
- 参数：
  - `author`: 作者名称
  - `page`: 页码
  - `limit`: 每页记录数

#### 示例用法

```jsx
// 显示指定作者的发帖历史
<PostHistoryLogs author="用户名" />
```

### HistoryButton.js

`HistoryButton`组件提供一个按钮，用于查看帖子历史。悬停时显示简要预览，点击时打开完整历史模态框。

#### 属性

| 属性名 | 类型 | 说明 |
|-------|------|------|
| threadId | String | 帖子ID |
| url | String | 帖子URL |
| size | String | 按钮大小，可选值：'small'、'middle'、'large' |

#### 示例用法

```jsx
// 添加历史按钮到帖子列表中
<HistoryButton threadId="1234567890" size="small" />
```

### HistoryModal.js

`HistoryModal`组件显示完整的帖子历史记录模态框。

#### 属性

| 属性名 | 类型 | 说明 |
|-------|------|------|
| visible | Boolean | 是否显示模态框 |
| onCancel | Function | 关闭模态框的回调函数 |
| threadId | String | 帖子ID |
| url | String | 帖子URL |
| title | String | 模态框标题 |

#### 示例用法

```jsx
// 在父组件中使用历史模态框
<HistoryModal 
  visible={isModalVisible}
  onCancel={() => setIsModalVisible(false)}
  threadId="1234567890"
  title="帖子历史记录"
/>
```

## 组件之间的关系

- `HistoryButton` 组件内部使用 `HoverActionLogs` 提供悬停预览
- 点击 `HistoryButton` 会打开 `HistoryModal`
- `HistoryModal` 内部使用 `ActionLogs` 展示完整历史
- `PostHistoryLogs` 与作者页面集成，展示作者的发帖历史

## 与后端API的交互

这些组件依赖以下后端API：
- `/api/action-logs` - 获取帖子动作日志
- `/api/author-post-history` - 获取作者发帖历史

API返回的数据结构包括：
- `data` - 包含日志数据的数组
- `total` - 记录总数
- `debug` - 调试信息(可选) 