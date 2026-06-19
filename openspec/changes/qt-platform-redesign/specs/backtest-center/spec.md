# Specification (Delta): Backtest Center — 回测中心

## ADDED Requirements

### Requirement: 创建并启动回测

系统 SHALL 接受回测配置并异步启动 rqalpha 回测任务。

#### Scenario: 正常创建回测
- **GIVEN** 一个已存在的策略（strategy_id=1, version=3）
- **WHEN** 客户端发送 POST `/api/backtests`，body 含 `strategy_id=1, version=3, config={start_date: "2024-01-01", end_date: "2024-12-31", initial_capital: 100000, benchmark: "000300.XSHG", frequency: "1d", commission: 0.0003, slippage: 0.01}`
- **THEN** 系统 SHALL 在 `backtest_job` 表中创建状态为 `pending` 的记录
- **AND** 系统 SHALL 创建一个 `task_type=backtest` 的 task_job
- **AND** 系统 SHALL 响应 HTTP 202，body 含 `data.id`（回测ID）和 `data.status="pending"`

#### Scenario: 缺少必填参数
- **WHEN** 客户端发送 POST `/api/backtests` 缺少 `strategy_id` 或 `config.start_date`
- **THEN** 系统 SHALL 响应 HTTP 400，body 含错误信息

#### Scenario: 策略不存在
- **GIVEN** strategy_id=999 不存在
- **WHEN** 客户端发送 POST `/api/backtests` 指定该策略
- **THEN** 系统 SHALL 响应 HTTP 404

#### Scenario: 超过并发上限
- **GIVEN** 当前用户已有 3 个 `running` 状态的回测
- **WHEN** 客户端发送 POST `/api/backtests` 创建新回测
- **THEN** 系统 SHALL 响应 HTTP 429，提示超出并发限制

### Requirement: 回测列表查询

系统 SHALL 返回分页的回测列表，支持按策略和状态筛选。

#### Scenario: 查询全部回测
- **GIVEN** 数据库中存在 128 条回测记录
- **WHEN** 客户端发送 GET `/api/backtests?page=1&page_size=20`
- **THEN** 系统 SHALL 响应 HTTP 200
- **AND** body 含 `data.items[0]` 包含 `id, strategy_name, strategy_version, status, total_return, sharpe_ratio, max_drawdown, created_at`
- **AND** body 含 `data.total=128, data.page=1, data.page_size=20`

#### Scenario: 按策略筛选
- **WHEN** 客户端发送 GET `/api/backtests?strategy_id=1`
- **THEN** 系统 SHALL 仅返回该策略的回测记录

#### Scenario: 按状态筛选
- **WHEN** 客户端发送 GET `/api/backtests?status=running`
- **THEN** 系统 SHALL 仅返回 `status=running` 的回测记录

### Requirement: 回测详情

系统 SHALL 返回回测的完整摘要指标和配置信息。

#### Scenario: 查询已完成的回测
- **GIVEN** backtest_id=128 状态为 `completed`
- **WHEN** 客户端发送 GET `/api/backtests/128`
- **THEN** 系统 SHALL 响应 HTTP 200
- **AND** body 含 `data.summary` 包含 12 项指标：`total_return, annualized_return, max_drawdown, sharpe_ratio, sortino_ratio, win_rate, profit_loss_ratio, annual_volatility, alpha, beta, final_value, total_trades`
- **AND** body 含 `data.config`（回测配置快照）和 `data.timing`（开始/结束时间、耗时）

### Requirement: 回测净值曲线

系统 SHALL 返回回测的日度净值数据用于绘制曲线。

#### Scenario: 查询完整净值数据
- **GIVEN** backtest_id=128 对应的净值数据有 242 条
- **WHEN** 客户端发送 GET `/api/backtests/128/nav?format=full`
- **THEN** 系统 SHALL 响应 HTTP 200
- **AND** body 含 `data.dates`（日期数组）、`data.nav`（单位净值数组）、`data.benchmark_nav`（基准净值数组）、`data.excess_return`（超额收益数组）

#### Scenario: 查询采样净值数据
- **WHEN** 客户端发送 GET `/api/backtests/128/nav?format=compact`
- **THEN** 系统 SHALL 返回 ≤300 个采样点的净值数据

### Requirement: 回测交易记录

系统 SHALL 返回回测的完整交易记录及摘要统计。

#### Scenario: 查询交易记录
- **GIVEN** backtest_id=128 有 47 笔交易
- **WHEN** 客户端发送 GET `/api/backtests/128/trades?page=1&page_size=50`
- **THEN** 系统 SHALL 响应 HTTP 200
- **AND** body 含 `data.items` 每项含 `ts_code, symbol, buy_date, sell_date, buy_price, sell_price, quantity, pnl, pnl_pct, holding_days, sell_reason`
- **AND** body 含 `data.summary` 含 `total_trades, win_trades, lose_trades, avg_profit, avg_loss`

### Requirement: 回测持仓分析

系统 SHALL 返回回测的持仓快照数据。

#### Scenario: 查询某日持仓
- **WHEN** 客户端发送 GET `/api/backtests/128/positions?trade_date=2024-06-15`
- **THEN** 系统 SHALL 返回该日所有持仓明细（ts_code, quantity, market_value, weight, pnl）

### Requirement: 回测风险指标

系统 SHALL 返回回测的完整风险指标。

#### Scenario: 查询风险指标
- **WHEN** 客户端发送 GET `/api/backtests/128/risk-metrics`
- **THEN** 系统 SHALL 响应 HTTP 200
- **AND** body 含 `data.max_drawdown, max_drawdown_start, max_drawdown_end, max_drawdown_days, annual_volatility, downside_volatility, var_95, cvar_95, calmar_ratio, information_ratio, tracking_error, avg_holding_days`

### Requirement: 回测日志查看

系统 SHALL 返回回测的执行日志，日志文件按 `logs/{strategy_key}/{backtest_id}.log` 存储。

#### Scenario: 查询完整日志
- **GIVEN** backtest_id=128 日志文件已生成
- **WHEN** 客户端发送 GET `/api/backtests/128/logs?mode=full`
- **THEN** 系统 SHALL 响应 HTTP 200
- **AND** body 含 `data.log_path`（日志文件路径）和 `data.lines`（日志行数组）

#### Scenario: 查询末尾日志
- **WHEN** 客户端发送 GET `/api/backtests/128/logs?mode=tail&lines=100`
- **THEN** 系统 SHALL 返回日志文件的最后 100 行

#### Scenario: 日志文件不存在
- **GIVEN** backtest_id=128 的日志文件尚未生成
- **WHEN** 客户端发送 GET `/api/backtests/128/logs`
- **THEN** 系统 SHALL 响应 HTTP 404，提示日志文件不存在

### Requirement: 取消回测

系统 SHALL 支持取消正在运行的回测。

#### Scenario: 取消运行中的回测
- **GIVEN** backtest_id=128 状态为 `running`
- **WHEN** 客户端发送 POST `/api/backtests/128/cancel`
- **THEN** 系统 SHALL 设置 `threading.Event` 信号通知回测线程中断
- **AND** 系统 SHALL 更新 backtest_job 状态为 `cancelled`
- **AND** 系统 SHALL 响应 HTTP 200

#### Scenario: 取消已完成的回测
- **GIVEN** backtest_id=128 状态为 `completed`
- **WHEN** 客户端发送 POST `/api/backtests/128/cancel`
- **THEN** 系统 SHALL 响应 HTTP 400，提示回测已完成无法取消

### Requirement: 删除回测

系统 SHALL 级联删除回测及其所有关联数据。

#### Scenario: 删除回测
- **GIVEN** backtest_id=128 存在
- **WHEN** 客户端发送 DELETE `/api/backtests/128`
- **THEN** 系统 SHALL 删除 backtest_job 记录
- **AND** 系统 SHALL 级联删除 backtest_nav, backtest_trade, backtest_position, backtest_daily_metrics, backtest_risk_metrics 中该回测的所有记录
- **AND** 系统 SHALL 删除日志文件 `logs/{strategy_key}/128.log`
- **AND** 系统 SHALL 响应 HTTP 200

### Requirement: 回测实时进度推送

系统 SHALL 通过 WebSocket 推送回测实时进度。

#### Scenario: 进度推送
- **GIVEN** backtest_id=128 正在运行
- **WHEN** 回测线程处理每个 bar
- **THEN** 系统 SHALL 通过 WebSocket 推送 `backtest_progress` 事件
- **AND** 事件 data 含 `progress, current_date, completed_bars, total_bars, elapsed_seconds`

#### Scenario: 回测完成推送
- **WHEN** 回测执行完成
- **THEN** 系统 SHALL 推送 `backtest_completed` 事件
- **AND** 事件 data 含 `total_return, sharpe_ratio, duration_ms`

#### Scenario: 回测失败推送
- **WHEN** 回测执行抛出异常
- **THEN** 系统 SHALL 推送 `backtest_failed` 事件
- **AND** 事件 data 含 `error` 异常信息

### Requirement: 回测报告聚合

系统 SHALL 提供聚合接口一次返回回测的所有数据。

#### Scenario: 查询回测报告
- **WHEN** 客户端发送 GET `/api/backtests/128/report`
- **THEN** 系统 SHALL 响应 HTTP 200
- **AND** body 含 `data.summary`（摘要指标）、`data.nav`（净值曲线，采样到 300 点）、`data.risk`（风险指标）、`data.trades_summary`（交易摘要）、`data.positions_summary`（持仓摘要）

### Requirement: 回测使用 rqalpha 真实执行

系统 SHALL 使用 rqalpha 框架执行回测，通过自定义 DataSource 从 MySQL 加载行情数据。

#### Scenario: CustomDataSource 加载数据
- **GIVEN** MySQL stock_daily 表中有 2024 年 A 股日线数据
- **WHEN** BacktestEngine 初始化 QtDataSource(2024-01-01, 2024-12-31)
- **THEN** QtDataSource SHALL 从 stock_daily 加载所有 stock_basic 日线数据
- **AND** QtDataSource SHALL 构建 Instrument 映射（SZ000001 / SH600000 格式）
- **AND** QtDataSource SHALL 返回交易日历（DISTINCT trade_date）

#### Scenario: rqalpha 回测执行
- **GIVEN** QtDataSource 已初始化
- **WHEN** BacktestEngine.run() 调用 rqalpha.run_func()
- **THEN** rqalpha SHALL 使用 QtDataSource 提供的行情数据执行策略
- **AND** sys_analyser mod SHALL 返回 summary/trades/positions/daily_nav/risk 结果
- **AND** BacktestEngine SHALL 将结果写入对应的 backtest_* 表
