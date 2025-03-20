# 论坛数据管理与分析系统

这是一个集成了数据采集、存储、分析和可视化的综合论坛数据管理平台。系统支持自动化数据更新，提供丰富的数据分析功能和直观的用户界面，适用于论坛数据的全面管理和深度挖掘。

## 系统概述

本系统由以下核心模块组成：
- 数据采集与更新模块：自动从多个论坛源获取并更新数据
- 数据存储与管理模块：高效存储和管理大量论坛数据
- 数据分析与处理模块：提供丰富的数据分析和文本挖掘功能
- 可视化展示模块：直观展示数据分析结果和关键指标
- 用户交互界面：提供友好的操作界面和权限管理

## 快速开始

### 环境要求

- Node.js 16+ 
- Python 3.8+
- SQLite数据库

### 安装步骤

1. 克隆此仓库
   ```bash
   git clone https://github.com/rbtsama/bbs_dashboard.git
   cd bbs_dashboard
   ```

2. 安装前端依赖
   ```bash
   cd frontend
   npm install
   ```

3. 安装后端依赖
   ```bash
   cd ../backend
   pip install -r requirements.txt
   ```

4. 运行前端开发服务器
   ```bash
   cd ../frontend
   npm run dev
   ```

5. 运行后端服务
   ```bash
   cd ../backend
   python app.py
   ```

6. 访问系统：默认地址为 http://localhost:3000

## 文档目录

### 用户文档

- [平台介绍](docs/用户_平台介绍.md) - 系统功能和特点概述
- [使用教程](docs/用户_使用教程.md) - 详细的系统使用指南
- [设计逻辑](docs/用户_设计逻辑.md) - 系统设计理念和实现逻辑

### 技术文档

#### 项目指南
- [项目启动指南](docs/技术_项目启动指南.md) - 快速启动和配置项目
- [部署指南](docs/技术_部署指南.md) - 系统部署和环境配置说明

#### 架构设计
- [系统架构](docs/技术_系统架构.md) - 系统整体架构和模块设计
- [前端架构](docs/技术_前端架构.md) - 前端技术栈和组件设计
- [模块设计](docs/技术_模块设计.md) - 各功能模块的详细设计

#### 数据管理
- [数据库设计](docs/技术_数据库设计.md) - 数据库结构和关系设计
- [自动化更新](docs/技术_自动化更新.md) - 数据自动更新机制
- [API接口文档](docs/技术_API接口文档.md) - 系统API接口说明

#### 其他技术文档
- [数据库概述](docs/db_overview.md) - 数据库系统概述
- [数据源说明](docs/db_data_sources.md) - 数据来源和采集机制
- [数据表定义](docs/db_table_definitions.md) - 详细数据表结构说明
- [数据处理流程](docs/db_data_processing.md) - 数据处理和转换流程
- [增量更新机制](docs/db_incremental_updates.md) - 数据增量更新的实现
- [备份恢复策略](docs/db_backup_recovery.md) - 数据备份和恢复方案
- [版本控制机制](docs/db_version_control.md) - 数据库版本控制机制
- [词云生成](docs/db_wordcloud_generation.md) - 文本分析和词云生成
- [线程跟踪系统](docs/thread_follow_system.md) - 论坛线程跟踪功能
- [前端组件](docs/frontend_components.md) - 前端组件详解
- [数据库API参考](docs/db_api_reference.md) - 数据库API详细说明
- [系统改进](docs/update_system_improvements.md) - 系统更新和改进说明
- [数据库恢复能力](docs/db_update_resilience.md) - 数据更新故障恢复能力

## 系统架构图

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│                 │      │                 │      │                 │
│  数据采集模块    │ ──→ │  数据存储模块    │ ──→ │  数据分析模块    │
│                 │      │                 │      │                 │
└─────────────────┘      └─────────────────┘      └─────────────────┘
                                                          │
                                                          ↓
                          ┌─────────────────┐      ┌─────────────────┐
                          │                 │      │                 │
                          │  用户界面模块    │ ←── │  可视化模块      │
                          │                 │      │                 │
                          └─────────────────┘      └─────────────────┘
```

## 贡献指南

欢迎对本项目进行贡献。请遵循以下步骤：

1. Fork本仓库
2. 创建您的特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交您的更改 (`git commit -m '添加一些惊人的特性'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建一个Pull请求

## 许可证

本项目采用MIT许可证 - 详情请查看LICENSE文件
