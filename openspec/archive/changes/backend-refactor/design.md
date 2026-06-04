# Design: Backend Refactoring

## 硬性约束

**前端代码零改动**：本次重构不修改 `frontend/` 目录下的任何文件，不移入、不删除、不重命名。后端 API 的路径（`/api/...`）、HTTP 方法（GET/POST）、请求参数（query string / body）、响应 JSON 结构（字段名、嵌套层级、数据类型）全部保持与重构前完全一致。前端在重构前后看到的每个页面、每个弹窗、每个表格列、每个图表都完全一样。

## 目标目录结构

```
backend/
├── run.py
├── requirements.txt
├── .env
├── Dockerfile
│
├── app/
│   ├── __init__.py               # create_app() 工厂函数
│   │
│   ├── api/                      # Blueprint 路由
│   │   ├── __init__.py
│   │   ├── auth.py               # /api/user/*
│   │   ├── stocks.py             # /api/stocks/*, /api/stock/data
│   │   ├── stock_select.py       # /api/stock_select, /api/stock/select/mock
│   │   ├── stock_check.py        # /api/stock/check, /api/stock/daily/add
│   │   └── vol_line.py           # /api/vol_line
│   │
│   ├── services/                 # 业务编排
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── stock_service.py
│   │   ├── select_service.py
│   │   ├── data_service.py
│   │   └── notify_service.py
│   │
│   ├── repositories/             # 数据访问
│   │   ├── __init__.py
│   │   ├── base.py               # 通用分页
│   │   ├── user_repo.py
│   │   ├── stock_repo.py
│   │   ├── stock_daily_repo.py
│   │   ├── stock_select_repo.py
│   │   ├── tushare_repo.py
│   │   └── hk_stock_repo.py
│   │
│   ├── analysis/                 # 纯函数计算
│   │   ├── __init__.py
│   │   ├── indicators.py         # MACD/KDJ
│   │   ├── ma_analysis.py        # 均线
│   │   ├── volume_analysis.py    # 成交量
│   │   └── aggregation.py        # 周月聚合
│   │
│   ├── core/                     # 基础设施
│   │   ├── __init__.py
│   │   ├── config.py             # Settings 对象
│   │   ├── database.py           # 统一 DB 引擎
│   │   ├── security.py           # JWT + 密码
│   │   ├── response.py           # 统一响应
│   │   └── logger.py             # 日志
│   │
│   └── utils/
│       ├── __init__.py
│       ├── dateutil.py
│       └── notify.py
│
├── hk/
│   ├── __init__.py
│   ├── hkutil.py
│   └── hk_daily.py
│
└── tasks/
    ├── __init__.py
    └── scheduler.py

## 三层依赖规则

```
api/ → services/ → repositories/
                 → analysis/
                 → core/
                 → utils/
```

各层依赖限制：

| 层 | 可依赖 | 禁止依赖 |
|----|--------|---------|
| api/ | services/, core/response.py | repositories/, analysis/ |
| services/ | repositories/, analysis/, core/, utils/ | api/ |
| repositories/ | core/database.py, core/config.py | services/, api/ |
| analysis/ | pandas, talib, numpy 等第三方库 | 所有业务模块 |
| core/ | 第三方库 | 所有业务模块 |

## 关键设计决策

| 决策 | 选择 | 理由 |
|------|------|------|
| DB 连接 | SQLAlchemy Engine + pandas | 现有代码大量依赖 pd.read_sql / df.to_sql，ORM 改动过大 |
| 路由注册 | Flask Blueprint | stock_check.py 已示范该模式，其他路由统一迁移 |
| 配置读取 | python-dotenv + dataclass | 最轻量方案，仅新增一个依赖 |
| 异步任务 | threading.Thread | 当前架构够用，Celery 过度设计 |
| analysis/ | 纯函数，不依赖任何业务模块 | 方便独立测试和复用 |

## 文件映射

| 原始路径 | 目标路径 | 操作 |
|----------|---------|------|
| `stock/main.py` | `run.py` + `app/__init__.py` + `tasks/scheduler.py` | 三拆 |
| `stock/backend/user.py` | `api/auth.py` + `services/auth_service.py` + `core/security.py` + `repositories/user_repo.py` | 四拆 |
| `stock/backend/stock_list.py` | `api/stocks.py` + `services/stock_service.py` + `repositories/stock_repo.py` + `repositories/stock_daily_repo.py` | 四拆 |
| `stock/backend/stock_select.py` | `api/stock_select.py` + `api/vol_line.py` + `services/select_service.py` + `repositories/stock_select_repo.py` | 四拆 |
| `stock/backend/stock_check.py` | `api/stock_check.py` + `services/data_service.py` (部分) | 两拆 |
| `stock/backend/dbutil.py` | `repositories/base.py` + `core/database.py` | 两拆 |
| `stock/backend/db_config.py` | 合并入 `core/config.py` + `.env` | 迁移+删除 |
| `stock/moduledir/stockutil.py` | `repositories/tushare_repo.py` + `repositories/stock_daily_repo.py` + `repositories/stock_repo.py` | 三拆 |
| `stock/moduledir/chatutil.py` | `utils/notify.py` | 改名+移入 |
| `stock/moduledir/dateutil.py` | `utils/dateutil.py` | 移入 |
| `stock/db/db.py` | 合并入 `core/database.py` | 合并删除 |
| `stock/utils/logger.py` | `core/logger.py` | 移入 |
| `stock/backend/data/talib_metric.py` | `analysis/indicators.py` | 移入 |
| `stock/backend/data/select_ma.py` | `analysis/ma_analysis.py` | 移入 |
| `stock/backend/data/select_daily.py` | `analysis/volume_analysis.py` (算法) + `services/select_service.py` (编排) | 两拆 |
| `stock/backend/data/wm.py` | `analysis/aggregation.py` (算法) + `services/data_service.py` (编排) | 两拆 |
| `stock/backend/data/select.py` | `services/select_service.py` (编排) | 合并入 service |
| `stock/backend/data/daily.py` | `services/data_service.py` (编排) | 合并入 service |
| `stock/hk/` | `backend/hk/` | 整体移入 |

## 配置统一方案

5 处硬编码全部消除，统一由 `.env` 管理：

```ini
# backend/.env
DB_HOST=rm-bp160jkc22y874i30to.mysql.rds.aliyuncs.com
DB_PORT=3306
DB_USER=root
DB_PASSWORD=8Dm4PQU2pp6!C3y
DB_NAME=stock

JWT_SECRET=your-secret-key-change-in-production
JWT_EXPIRY_HOURS=24

TUSHARE_TOKEN=3252a9af155128787f44d053c563d6b156f03e80f0254899e8668ecc

WECHAT_WEBHOOK_KEY=2d426b1f-4b3e-4905-b403-f69222c947cd
```

通过 `core/config.py` 中的 `Settings` dataclass 统一读取，全局单例 `settings`。

## 部署脚本更新

### `bin/start.sh`

第 18 行硬编码了旧路径，需更新：

```bash
# 旧:
MAIN_PY="$PROJECT_ROOT/stock/main.py"

# 新:
MAIN_PY="$PROJECT_ROOT/backend/run.py"
```

启动脚本自动确定 `PROJECT_ROOT`，因此只需改这一行。`stop.sh` 通过 PID 文件管理进程，不受路径变化影响。

### `.github/workflows/backend-deploy.yml`

第 8 行路径监听条件需要更新：

```yaml
# 旧:
paths:
  - 'stock/**'

# 新:
paths:
  - 'backend/**'
```

## 需要留意的 CSV 输出路径

下列代码使用相对路径输出 CSV 文件，重构后工作目录从 `stock/stock/` 变为 `backend/`，CSV 写入位置会跟着变：

| 文件 | CSV 输出 |
|------|----------|
| `select_daily.py` | `{date}_vol.csv`, `{date}_hk_vol.csv`, `trend.csv`, `litter.csv` |
| `select.py` | `{date}_select.csv`, `{date}_hk_select.csv` |
| `stockutil.py` | `stock.csv` |

这些 CSV 通过 `sendGroupFile()` 发送到企业微信后被丢弃，**没有外部依赖**，位置变化无影响。

## `.gitignore` 补充

当前 `.gitignore` 只有 `node_modules`，缺少必要的忽略规则。重构前需补充：

```gitignore
# Python
__pycache__/
*.py[cod]
*.egg-info/
.venv/
.env
venv/

# IDE
.idea/
.vscode/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Project specific
logs/
*.pid
*.csv
```

## 测试策略

### 测试目录结构

```
backend/tests/
├── __init__.py
├── conftest.py              # pytest 夹具：Flask test client、测试 DB
├── test_core/
│   ├── test_config.py       # Settings 读取 & 环境变量覆盖
│   ├── test_security.py     # JWT 生成/验证、密码哈希
│   └── test_response.py     # 统一响应格式
├── test_api/                # 全栈 API 集成测试（使用 Flask test client）
│   ├── test_auth.py         # 注册/登录/信息/改密完整流程
│   ├── test_stocks.py       # 股票列表/搜索/日线数据
│   ├── test_select.py       # 选股查询/异步触发
│   ├── test_check.py        # 数据补录/校验
│   └── test_vol_line.py     # 成交量线
├── test_analysis/
│   ├── test_indicators.py   # MACD/KDJ 计算验证
│   ├── test_ma.py           # 均线计算验证
│   ├── test_volume.py       # 成交量斜率/放大计算
│   └── test_aggregation.py  # 周月聚合逻辑
├── test_migration/          # 重构迁移专项测试
│   ├── test_imports.py      # 验证所有模块可正确导入
│   ├── test_structure.py    # 验证新旧目录结构完整性
│   └── test_secrets.py      # grep 验证无硬编码密钥残留
├── test_deploy/             # 部署脚本测试
│   └── test_start_stop.sh   # start.sh/stop.sh 语法+路径+进程集成测试
└── smoke_test.py            # 快速冒烟测试脚本（独立运行，不依赖 pytest）

### 测试层级

| 层级 | 覆盖范围 | 运行方式 | 阶段 |
|------|---------|---------|------|
| 冒烟测试 | 启动 + `/api/health` 返回 200 | `python backend/tests/smoke_test.py` | 每阶段末尾 |
| 导入验证 | 所有模块 import 不报错 | `pytest backend/tests/test_migration/test_imports.py` | 每阶段末尾 |
| API 集成测试 | 15 个接口的请求/响应完整匹配 | `pytest backend/tests/test_api/` | 阶段六后 |
| 分析算法测试 | MACD/KDJ/MA/成交量 计算结果正确 | `pytest backend/tests/test_analysis/` | 阶段三后 |
| 迁移专项测试 | 密钥无残留、旧目录已清理、结构正确 | `pytest tests/test_migration/` | 阶段八 |
| 部署脚本测试 | 语法检查 + 路径解析 + 进程启动/停止 | `bash backend/tests/test_deploy/test_start_stop.sh` | 阶段九 |

### 冒烟测试脚本设计

`backend/tests/smoke_test.py` 设计为可独立运行的快速验证工具，不依赖 pytest，用于每阶段末尾快速确认系统可用：

```
smoke_test.py 执行流程:
  1. 验证 Python 可导入 core 模块
  2. 验证 Flask app 可创建 (create_app)
  3. 启动 app 并发送 GET /api/health → 检查 200 + status=healthy
  4. 验证 .env 已加载 (settings.DB_HOST != None)
  5. 报告各检查项 PASS/FAIL
```

### API 集成测试核心场景

每个 API 测试文件使用 Flask test client，验证：

| 测试文件 | 覆盖场景数 | 核心验证点 |
|----------|-----------|-----------|
| `test_auth.py` | 8 | 注册成功/重复/缺字段、登录成功/密码错/缺字段、获取信息、改密成功 |
| `test_stocks.py` | 6 | 列表分页、关键词搜索、地域行业列表、日线查询参数校验、认证拦截 |
| `test_select.py` | 4 | 查询现有数据、空数据触发异步、重复请求拦截、mock 选股 |
| `test_check.py` | 3 | 数据覆盖查询、补录提交、日期格式校验 |
| `test_vol_line.py` | 2 | 正常查询、缺参数错误 |

### 部署脚本测试设计

`tests/test_deploy/test_start_stop.sh` 是独立的 shell 测试脚本，验证部署脚本的语法正确性和路径解析：

```
test_start_stop.sh 执行流程:
  1. bash -n bin/start.sh          ← shell 语法检查
  2. bash -n bin/stop.sh           ← shell 语法检查  
  3. 模拟 PROJECT_ROOT 推导        ← 验证路径解析逻辑
     - 从 bin/start.sh 中提取 SCRIPT_DIR/PROJECT_ROOT 计算逻辑
     - 验证 PROJECT_ROOT/backend/run.py 存在
     - 验证 PROJECT_ROOT/backend/.env 存在
  4. 集成测试 (可选，需人工确认不阻塞 CI):
     - bash bin/start.sh           ← 启动应用
     - 等待 3 秒
     - 检查 .backend_pid 文件存在
     - 检查 PID 对应进程存活
     - curl /api/health → 200
     - bash bin/stop.sh            ← 停止应用
     - 检查 .backend_pid 文件已删除
     - 检查进程已终止
     - 重复执行 start.sh 验证 "already running" 检测
```

### 迁移验证清单

阶段八执行以下验证，全部通过方可清理旧目录：

```
验证项                          方法
─────────────────────────────────────────────────────
所有模块可正确导入              pytest backend/tests/test_migration/test_imports.py
旧目录已删除                    pytest backend/tests/test_migration/test_structure.py
新目录结构完整                  pytest backend/tests/test_migration/test_structure.py
无硬编码密钥残留                pytest backend/tests/test_migration/test_secrets.py
API 全部 15 接口正常            pytest backend/tests/test_api/
分析算法计算一致                pytest backend/tests/test_analysis/
部署脚本语法正确               bash -n bin/start.sh && bash -n bin/stop.sh
部署脚本路径解析正确            bash backend/tests/test_deploy/test_start_stop.sh
部署集成测试                   start → health → stop → 进程清理（手动）

