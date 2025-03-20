# Vercel环境下的数据库自动更新机制

本文档详细说明了如何在Vercel环境下设置和配置数据库自动更新机制。由于Vercel是无服务器(serverless)环境，我们采用了API驱动的更新方案，结合外部定时服务实现自动更新功能。

## 系统架构

数据库更新系统由以下几个主要组件组成：

1. **API端点**：Vercel上的API路由，负责接收更新请求并执行数据库更新操作
2. **外部定时触发器**：外部服务（如cron-job.org）定时调用API端点
3. **管理界面**：Web界面，用于手动触发更新和监控更新状态
4. **备份与回滚机制**：自动备份和错误恢复机制

## 环境要求

- Vercel账户
- 外部Cron服务账户（如cron-job.org、EasyCron或Google Cloud Scheduler）
- 项目使用Next.js框架

## 部署说明

### 1. 设置环境变量

在Vercel项目设置中，配置以下环境变量：

- `DB_UPDATE_API_KEY`：用于验证自动更新API调用的密钥
- `DB_ADMIN_KEY`：用于验证管理界面的管理员密钥

为了安全起见，请使用复杂、随机生成的密钥。

### 2. 设置外部定时服务

使用外部Cron服务（如cron-job.org）设置定时任务：

1. 创建新的Cron作业
2. 设置URL为：`https://[your-vercel-domain]/api/db-update?key=[DB_UPDATE_API_KEY]`
3. 请求方法设为：`POST`
4. 设置执行频率为每天凌晨3点（UTC-7，加州时间）
5. 启用作业

### 3. 部署到Vercel

1. 确保项目代码包含所有必要文件：
   - `pages/api/db-update.js` - 主更新API端点
   - `pages/api/db-update-manual.js` - 手动触发API端点
   - `pages/admin/db-update.js` - 管理界面
   - `py/rollback_db.py` - 数据库回滚脚本

2. 部署项目到Vercel：
   ```bash
   vercel --prod
   ```

3. 确保在Vercel环境中安装了所需的Python包：
   ```
   sqlite3
   pandas
   numpy
   matplotlib
   wordcloud
   ```

## 文件结构

```
项目根目录/
├── pages/
│   ├── api/
│   │   ├── db-update.js           # 主更新API端点
│   │   └── db-update-manual.js    # 手动触发API端点
│   └── admin/
│       └── db-update.js           # 管理界面
├── py/
│   ├── post.py                    # 处理帖子数据
│   ├── update.py                  # 处理更新数据
│   ├── detail.py                  # 处理详情数据
│   ├── action.py                  # 处理动作数据
│   ├── car_info.py                # 处理车辆信息
│   ├── analysis.py                # 数据分析脚本
│   ├── update_db.py               # 数据库更新脚本
│   ├── backup_db.py               # 数据库备份脚本
│   ├── rollback_db.py             # 数据库回滚脚本
│   └── generate_wordcloud.py      # 词云生成脚本
├── db/
│   ├── forum_data.db              # 主数据库文件
│   └── backups/                   # 备份目录
├── logs/                          # 日志目录
└── tmp/                           # 临时文件目录
```

## 使用方法

### 自动更新

一旦设置完成，系统将根据Cron设置自动执行更新。默认为每天凌晨3点（加州时间）。

### 手动触发更新

1. 访问管理界面：`https://[your-vercel-domain]/admin/db-update`
2. 输入管理员密钥（DB_ADMIN_KEY）
3. 点击"触发数据库更新"按钮

### 查看更新状态

1. 访问管理界面：`https://[your-vercel-domain]/admin/db-update`
2. 查看"更新状态"面板，获取最新的更新状态
3. 查看"最新日志"面板，查看详细的执行日志

## 更新流程详解

### 1. 预处理阶段

执行以下脚本处理原始数据：
- `post.py` - 处理新发帖数据
- `update.py` - 处理帖子更新数据
- `detail.py` - 处理帖子详情数据
- `action.py` - 生成帖子动态记录
- `car_info.py` - 处理车辆信息数据

### 2. 分析阶段

执行数据分析与质量检查：
- `analysis.py` - 执行数据分析
- `test_data_quality.py` - 数据质量测试

### 3. 数据导入阶段

更新数据库并验证结构：
- 先执行备份以便回滚
- `update_db.py` - 将数据导入数据库
- `check_db_structure.py` - 验证数据库结构

### 4. 词云生成阶段

更新词云数据：
- `generate_wordcloud.py` - 生成词云数据

### 5. 备份阶段

创建完整数据库备份：
- `backup_db.py` - 创建完整备份

## 错误处理与回滚

当更新过程中发生错误时：

1. 非关键步骤失败：记录错误但继续执行后续步骤
2. 关键步骤失败（如数据导入）：
   - 自动执行数据库回滚
   - 使用更新前创建的备份恢复数据库
   - 中止后续步骤

## 日志与监控

系统保存两种类型的日志：

1. **状态记录**：保存在`tmp/db_update_status.json`中，包含每个步骤的状态、开始和结束时间
2. **详细日志**：保存在`logs/`目录下，文件名格式为`auto_update_db_YYYYMMDD_HHMMSS.log`

管理界面提供实时监控功能：
- 显示当前更新状态
- 显示各步骤执行情况
- 显示最新的日志内容

## 故障排除

### 更新没有自动执行

1. 检查外部Cron服务是否正常运行
2. 验证API密钥是否正确设置
3. 查看Vercel函数日志，检查是否有API调用错误

### 更新执行失败

1. 访问管理界面查看详细错误信息
2. 检查日志文件了解具体失败原因
3. 验证数据文件是否存在和格式正确

### 手动强制回滚

如需手动回滚数据库：

1. 使用Vercel CLI连接到项目：
   ```
   vercel env pull
   vercel dev
   ```

2. 执行回滚脚本：
   ```
   cd py
   python rollback_db.py --force
   ```

## 安全注意事项

1. **API密钥保护**：
   - 确保API密钥足够复杂
   - 不要在前端代码中暴露密钥
   - 定期更换密钥

2. **访问控制**：
   - 管理界面需要密钥验证
   - 限制对API的直接访问

3. **数据备份**：
   - 系统会自动创建备份
   - 建议定期下载备份文件以防意外 