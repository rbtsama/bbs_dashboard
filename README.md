# 论坛数据库自动更新系统

这是一个基于Next.js和Python的论坛数据库自动更新系统，支持在Vercel环境下部署。

## 功能特点

- 自动数据库更新：通过API触发，支持定时执行
- 手动更新界面：提供Web界面手动触发更新
- 实时监控：查看更新状态和日志
- 回滚机制：更新失败时自动回滚数据库

## 部署说明

### 环境要求

- Node.js 14+ 
- Python 3.6+
- Vercel账户
- 外部Cron服务（如cron-job.org）

### 部署步骤

1. 克隆此仓库
2. 安装依赖：
   ```bash
   npm install
   pip install -r requirements.txt
   ```

3. 设置环境变量：
   - `DB_UPDATE_API_KEY`：API密钥
   - `DB_ADMIN_KEY`：管理员密钥

4. 部署到Vercel：
   ```bash
   vercel --prod
   ```

5. 配置外部Cron服务：
   - 设置URL为：`https://[your-domain]/api/db-update?key=[DB_UPDATE_API_KEY]`
   - 请求方法：POST
   - 执行时间：每天凌晨3点（加州时间）

## 文档

详细文档请参考：

- [Vercel环境下的数据库自动更新机制](docs/vercel-db-update.md)
- [数据库自动更新流程](docs/db-automated-updates.md)

## 开发

本地开发：

```bash
npm run dev
```

## 许可证

MIT
