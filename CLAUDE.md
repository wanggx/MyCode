# Stock 项目 Claude 配置

## 项目概述

股票数据分析平台。

- **后端**：Python Flask, pymysql + SQLAlchemy, pandas, Tushare/AKShare 数据源
- **前端**：Vue 3 + Element Plus + ECharts + Vuex + Vue Router
- **数据库**：阿里云 RDS MySQL
- **Python 虚拟环境**：`backend/.venv`（如不存在则创建）

## 目录结构

```
stock/
├── backend/            # Python 后端
│   ├── app/
│   │   ├── api/        # 路由层 (Controller)
│   │   ├── services/   # 服务层 (Business Logic)
│   │   ├── repositories/ # 数据访问层 (DAO)
│   │   ├── analysis/   # 分析算法 (纯函数)
│   │   ├── core/       # 基础设施 (config/database/security)
│   │   └── utils/      # 工具函数
│   ├── hk/             # 港股模块
│   ├── tasks/          # 定时任务
│   ├── run.py          # 启动入口
│   └── .env            # 环境变量 & 密钥
├── frontend/           # Vue 3 前端
│   └── src/
│       ├── api/        # API 调用层
│       ├── views/      # 页面 (stock/ system/ 子目录分组)
│       ├── layouts/    # 布局组件
│       ├── router/     # 路由
│       └── store/      # 状态管理
└── openspec/           # OpenSpec 行为规范
    ├── project.md
    ├── specs/          # 当前系统 spec（WHAT，单真相源）
    └── changes/        # 变更提案（proposal/tasks/delta-specs）
```

## OpenSpec 规范

### 目录约定

```
openspec/
├── project.md              # 项目上下文（技术栈、目录、规则）
├── specs/                  # 当前系统行为规范（只反映已部署的代码）
│   └── [能力]/
│       └── spec.md         # Purpose + Requirements (SHALL/MUST) + Scenarios (GIVEN/WHEN/THEN)
└── changes/                # 变更提案
    └── [变更名]/
        ├── proposal.md     # 为什么改、改什么、影响范围（≥50字）
        ├── tasks.md        # 可勾选的执行清单
        └── specs/          # Delta spec 文件
            └── [能力]/
                └── spec.md # ADDED/MODIFIED/REMOVED Requirements
```

### spec.md 格式要求

每个 spec.md 文件必须遵循以下结构：

```markdown
# Specification: [能力名称]

## Purpose
≥50 字描述本 spec 覆盖的范围

## Requirements

### Requirement: [需求名称（≤50字）]
SHALL / MUST 描述核心行为

#### Scenario: [场景描述]
- **GIVEN** 初始状态（可选）
- **WHEN** 触发条件
- **THEN** 预期结果
- **AND** 附加结果
```

**格式规则**：
- 每个 Requirement 必须包含 `SHALL` 或 `MUST` 关键词
- 每个 Requirement 必须有 ≥1 个 Scenario
- Scenario 必须使用 **GIVEN / WHEN / THEN / AND** 格式
- Requirement 标题 ≤50 字符，用作唯一标识符
- Requirement 正文 ≤500 字符

### 变更提案工作流

提出变更时，在 `openspec/changes/[变更名]/` 下创建：

1. **proposal.md** — 变更理由（why ≥50 字）和影响范围
2. **tasks.md** — 可勾选的执行步骤清单
3. **specs/[能力]/spec.md** — Delta spec，使用以下标记：

```markdown
## ADDED Requirements
### Requirement: 新增功能
SHALL ...

## MODIFIED Requirements
### Requirement: 修改的功能
（完整的更新后 requirement）

## REMOVED Requirements
### Requirement: 移除的功能
（移除原因）
```

### 后端分层依赖规则

```
api/ → services/ → repositories/
                 → analysis/
                 → core/
                 → utils/
```

- `api/` 只能调 `services/`，禁止直接调 `repositories/`
- `services/` 编排业务，调 `repositories/` 和 `analysis/`
- `repositories/` 只执行 SQL / 外部 API，不包含业务逻辑
- `analysis/` 纯函数，输入 DataFrame 输出 DataFrame
- `core/` 零业务依赖的基础设施

### Python 路径约定

- 后端入口：`python backend/run.py`
- 导入前缀以 `backend/` 为根，如 `from app.core.config import settings`

### 前端端口约束

- **前端开发服务器固定使用端口 5100**
- 启动命令：`cd frontend && npx vue-cli-service serve --port 5100`
- 禁止使用其他端口启动前端

### Python 环境约束

- **后端启动必须使用 `backend/.venv` 虚拟环境下的 Python 解释器**
- 禁止使用全局 Python 或其他路径的虚拟环境来启动后端
- 具体用法：
  - Windows: `backend\.venv\Scripts\python backend\run.py`
  - Linux/Mac: `backend/.venv/bin/python backend/run.py`
- 如 `.venv` 不存在，应先在 `backend/` 目录下通过 `python -m venv .venv` 创建，然后安装依赖

### 代码规范约束

- 单个 Python 文件不得超过 **1000 行**（含空行和注释）
- 单个函数（def）不得超过 **150 行**（含空行和注释）
- 超出限制时必须进行重构：拆分为多个文件或子函数
- 此约束适用于 `backend/` 下所有 `.py` 文件，包括测试文件

### 数据库约束

- MySQL 数据库结构（表、字段、索引、外键等）在重构过程中**不得做任何修改**
- 禁止执行 `ALTER TABLE`、`CREATE TABLE`、`DROP TABLE` 等 DDL 操作
- 现有数据表中的数据也不能被清除或迁移
- 所有数据访问层代码调整必须兼容现有表结构
