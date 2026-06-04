# 实施路线

本文档用于指导后续 Agent 分阶段落地。

## 总原则

1. 不做大重构。
2. 不引入重型中间件。
3. 每阶段都要能独立验收。
4. 优先把数据可靠性做扎实。
5. 长任务必须进入任务中心。
6. 回测、策略、信号必须可追溯版本。

## Phase 0：准备工作

### 目标

清理工程基础问题，为后续开发降低阻力。

### 任务

- 统一源码编码为 UTF-8。
- 确认 MySQL 表结构和现有数据。
- 梳理现有 API 和页面。
- 保留旧功能可用。
- 新增数据库迁移或初始化 SQL 管理方式。

### 验收

- 项目可以正常启动。
- 原有股票列表、选股、数据补录接口仍可用。
- 中文不再出现乱码。

## Phase 1：任务中心

### 目标

先建立单体任务系统，为数据同步、补录、策略、回测提供统一执行入口。

### 新增表

```text
task_job
task_step
```

### 新增服务

```text
TaskService
Worker
```

### API

```text
GET /api/tasks
GET /api/tasks/{id}
POST /api/tasks/{id}/retry
```

### 实现要求

- API 创建任务。
- Worker 扫描 pending 任务。
- 同一时间只执行一个任务。
- 每个任务写入步骤日志。
- 失败任务保留异常信息。

### 验收

- 能创建一个测试任务。
- 任务状态从 pending -> running -> success。
- 失败任务能看到失败原因。
- 页面能查看任务列表和步骤。

## Phase 2：数据健康中心

### 目标

实现“发现缺口 -> 影响评估 -> 用户确认修复 -> 自动复检”。

### 新增表

```text
data_quality_issue
data_quality_issue_detail
data_repair_job
```

### 新增服务

```text
DataQualityService
DataRepairService
DataImpactService
```

### API

```text
GET /api/data/quality-summary
GET /api/data/issues
GET /api/data/issues/{id}
POST /api/data/issues/{id}/repair
POST /api/data/quality-scan
```

### 第一版检查

- A 股日线完整率。
- 港股日线完整率。
- 缺失股票明细。
- OHLC 为空或 0。
- high < low。
- 周线/月线是否覆盖最新日线。

### 修复能力

- 仅补缺失。
- 修复后自动复检。
- 自动重聚合周线/月线。

### 验收

- 扫描某天数据后能生成 issue。
- issue 能展示缺失股票和影响策略。
- 用户可创建修复任务。
- 修复完成后自动复检。
- issue 状态变为 resolved 或 failed。

## Phase 3：策略参数化与信号解释

### 目标

把现有选股逻辑升级成策略配置、版本和可解释信号。

### 新增表

```text
strategy
strategy_version
strategy_run
signal
```

### 新增服务

```text
StrategyService
SignalService
```

### API

```text
GET /api/strategies
GET /api/strategies/{id}
POST /api/strategies/{id}/versions
POST /api/strategies/{id}/run
GET /api/signals
GET /api/signals/{id}
```

### 策略类型

先接入现有逻辑：

```text
放量突破
均线趋势
MACD/KDJ 共振
港股趋势
```

### 信号解释

每条信号保存：

```text
reason_text
factor_snapshot_json
risk_snapshot_json
```

### 验收

- 能创建策略版本。
- 能手动运行策略。
- 运行结果写入 signal。
- 信号详情能展示入选原因和指标快照。

## Phase 4：日频回测

### 目标

实现轻量、可追溯的日频回测。

### 新增表

```text
backtest_job
backtest_nav
backtest_position
backtest_trade
```

### 新增服务

```text
BacktestService
```

### API

```text
POST /api/backtests
GET /api/backtests
GET /api/backtests/{id}
GET /api/backtests/{id}/nav
GET /api/backtests/{id}/positions
GET /api/backtests/{id}/trades
```

### 第一版规则

- 日频。
- 收盘后调仓。
- 等权或按信号分加权。
- 固定手续费。
- 固定滑点。
- 最大持仓数。
- 单票权重上限。

### 限制

- 默认最多 3 年。
- 配置允许最多 8 年。
- 一次只跑一个回测。

### 验收

- 提交回测返回任务 ID。
- 任务完成后可查看净值曲线。
- 可查看风险指标。
- 可查看持仓和交易明细。

## Phase 5：模拟组合与观察池

### 目标

不接实盘，但跟踪信号表现和模拟组合风险。

### 新增表

```text
watchlist
portfolio
portfolio_position
portfolio_nav
```

### 新增服务

```text
PortfolioService
WatchlistService
```

### API

```text
GET /api/watchlist
POST /api/watchlist
GET /api/portfolio
GET /api/portfolio/{id}/nav
GET /api/portfolio/{id}/positions
GET /api/portfolio/{id}/risk
```

### 第一版能力

- 信号加入观察池。
- 信号加入模拟组合。
- 每日用收盘价更新净值。
- 计算行业集中度。
- 计算单票权重。
- 计算最大回撤。

### 验收

- 信号可加入观察池。
- 模拟组合每日净值可展示。
- 风险提醒可展示。

## Phase 6：因子实验室增强

### 目标

沉淀因子库和基础因子分析。

### 新增表

```text
factor_def
factor_value
```

### 新增服务

```text
FactorService
```

### API

```text
GET /api/factors
POST /api/factors/analyze
GET /api/factors/{code}/coverage
GET /api/factors/{code}/ic
GET /api/factors/{code}/group-return
```

### 第一版能力

- 因子覆盖率。
- IC 曲线。
- 分层收益。
- 简单相关性。

### 验收

- 能选择因子和时间范围。
- 能生成 IC 曲线。
- 能查看分层收益。

## 不要做

后续 Agent 不应在第一阶段引入：

- Redis
- Celery
- Kafka
- Airflow
- ClickHouse
- Spark
- Kubernetes
- 微服务拆分
- 在线代码 IDE
- 实盘交易
- 券商下单
- 真实资金账户

## 推荐优先级

如果时间有限，只做前三阶段：

```text
1. 任务中心
2. 数据健康中心
3. 策略参数化与信号解释
```

这三阶段完成后，平台已经具备个人量化投研的核心骨架。

## 交接给后续 Agent 的提示

后续实现时应优先阅读：

```text
docs/quant-platform/architecture.md
docs/quant-platform/data-health.md
docs/quant-platform/database-draft.md
prototype/quant-prototype-v2.html
```

实现策略：

- 每次只实现一个阶段。
- 每个阶段先建表和服务，再接 API，最后接页面。
- 保留现有功能。
- 遇到旧代码乱码，先修局部，不要全仓大改。
