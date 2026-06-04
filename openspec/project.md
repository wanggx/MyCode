# Stock 项目上下文

## 项目概述

股票数据分析平台，支持 A 股和港股行情数据下载、技术指标分析、多策略选股，以及企业微信通知。

## 技术栈

- **后端**：Python 3.10+, Flask, pymysql, SQLAlchemy, pandas, tushare, akshare, talib
- **前端**：Vue 3, Element Plus, ECharts, Vuex, Vue Router, Axios
- **数据库**：MySQL 8.0 (阿里云 RDS)
- **部署**：Docker, GitHub Actions
- **虚拟环境**：`backend/.venv`

## 目录结构

```
stock/
├── backend/
│   ├── run.py
│   ├── app/
│   │   ├── api/          # HTTP 路由层
│   │   ├── services/     # 业务逻辑层
│   │   ├── repositories/ # 数据访问层
│   │   ├── analysis/     # 分析算法
│   │   ├── core/         # 基础设施
│   │   └── utils/        # 工具函数
│   ├── hk/               # 港股模块
│   ├── tasks/            # 定时任务
│   ├── tests/
│   ├── .env
│   └── requirements.txt
├── frontend/             # Vue 3 前端
├── openspec/             # 行为规范
└── CLAUDE.md
```

## 后端分层规则

```
api/ → services/ → repositories/
                 → analysis/
                 → core/
                 → utils/
```

禁止跨层调用：api 不可直接调 repositories，services 不可反向依赖 api。

## API 基础路径

所有 API 以 `/api` 为前缀。认证接口使用 Bearer JWT token。

## 代码规范约束

- 单个 Python 文件不得超过 **1000 行**（含空行和注释）
- 单个函数（def）不得超过 **150 行**（含空行和注释）
- 超出限制时必须进行重构：拆分为多个文件或子函数
- 此约束适用于 `backend/` 下所有 `.py` 文件，包括测试文件

## 数据库约束

- MySQL 数据库结构（表、字段、索引、外键等）在重构过程中**不得做任何修改**
- 禁止执行 `ALTER TABLE`、`CREATE TABLE`、`DROP TABLE` 等 DDL 操作
- 现有数据表中的数据也不能被清除或迁移
- 所有数据访问层代码调整必须兼容现有表结构
