# Tasks: QT 量化平台重构 — 策略研究 & 回测中心

## Phase 0: 数据库 & 配置（0.5天）

- [ ] `.env` 新增配置项：`DB_NAME=qt_dev`, `PASSWORD_HASH=bcrypt`, `LOG_DIR=logs`, `MAX_CONCURRENT_BACKTESTS=3`
- [ ] MySQL 中执行 `CREATE DATABASE qt_dev DEFAULT CHARSET utf8mb4`
- [ ] 执行 design-v2.md 中的 18 张表 DDL
- [ ] 从 `stock` 库迁移 `stock_basic`（全量）、`stock_daily`（近半年）、`users`（全量）到 `qt_dev`
- [ ] `Settings` 新增字段：`PASSWORD_HASH`, `LOG_DIR`, `MAX_CONCURRENT_BACKTESTS`

## Phase 1: 数据中心（1天）

- [ ] 改造 `repositories/stock_repo.py`：适配 qt_dev 库，查询 stock_basic 列表/详情
- [ ] 改造 `repositories/stock_daily_repo.py`：适配 qt_dev 库，日线数据查询
- [ ] 新建 `repositories/data_source_repo.py`：data_source + data_sync_log CRUD
- [ ] 新建 `services/data_service.py`：Tushare + AKShare 双数据源同步逻辑
- [ ] 新建 `api/data.py`：`GET /api/data/stocks`, `GET /api/data/stocks/:code`, `GET /api/data/stocks/:code/daily`, `GET /api/data/sources`, `POST /api/data/sync`, `GET /api/data/sync-logs`, `GET /api/data/overview`
- [ ] 前端新建 `DataCenter.vue`：股票列表 + 数据源管理 + 同步日志

## Phase 2: 策略管理（2天）

### 后端
- [ ] 新建 `repositories/strategy_repo.py`：strategy + strategy_version 表 CRUD，`strategy_key` 自动生成（pypinyin）
- [ ] 新建 `services/strategy_service.py`：策略创建/更新/删除（级联检查），版本创建/查询/切换
- [ ] 新建 `api/strategies.py`：`GET/POST /api/strategies`, `GET/PUT/DELETE /api/strategies/:id`, `PATCH /api/strategies/:id/status`, `GET/POST /api/strategies/:id/versions`, `GET /api/strategies/:id/versions/:version`

### 前端
- [ ] 安装 `monaco-editor` + `monaco-editor-webpack-plugin`，配置 `vue.config.js`
- [ ] 新建 `components/CodeEditor.vue`：Monaco Editor 封装（Python 语法、vs-dark 主题、Ctrl+S 保存、readOnly 切换）
- [ ] 新建 `views/StrategyResearch.vue`：左侧策略列表 + 右侧代码编辑器 + 策略信息头
- [ ] 新建 `store/modules/strategy.js`：策略列表/当前策略/版本状态
- [ ] 新建 `api/strategy.js`：策略 API 封装

## Phase 3: 回测引擎（2天）

- [ ] 新建 `services/backtest_datasource.py`：`QtDataSource` 继承 rqalpha `BaseDataSource`，从 mysql stock_daily 加载行情，构建 Instrument 映射和交易日历
- [ ] 新建 `services/backtest_engine.py`：`BacktestEngine` 封装 rqalpha.run_func()，实现进度回调注入（builtins）、日志写入（`logs/{strategy_key}/{backtest_id}.log`）、取消回测（threading.Event）、结果提取（sys_analyser）
- [ ] 单元测试：`tests/test_datasource.py`（交易日历、history_bars 返回正确）、`tests/test_backtest_engine.py`（buy_and_hold 策略执行成功、日志文件生成、取消回测）

## Phase 4: 回测 API（1.5天）

- [ ] 新建 `repositories/backtest_repo.py`：backtest_job + 5 张结果表（nav/trade/position/daily_metrics/risk_metrics）CRUD + 级联删除
- [ ] 新建 `services/backtest_service.py`：回测生命周期（create → task_job → Worker 消费 → engine.run → 结果写入 DB → 状态更新）
- [ ] 新建 `api/backtests.py`：`POST /api/backtests`, `GET /api/backtests`, `GET /api/backtests/:id`, `POST /api/backtests/:id/cancel`, `DELETE /api/backtests/:id`, `GET /api/backtests/:id/nav`, `GET /api/backtests/:id/trades`, `GET /api/backtests/:id/positions`, `GET /api/backtests/:id/daily-metrics`, `GET /api/backtests/:id/risk-metrics`, `GET /api/backtests/:id/logs`, `GET /api/backtests/:id/report`
- [ ] WebSocket：Flask-SocketIO 注册 `/ws/backtest/:id` 命名空间，`backtest_progress` / `backtest_completed` / `backtest_failed` / `log_line` 事件推送
- [ ] 单元测试：`tests/test_backtest_api.py`（创建回测/参数校验/结果查询）

## Phase 5: 回测中心前端（2天）

- [ ] 新建 `components/BacktestProgress.vue`：顶部进度条 + 取消按钮
- [ ] 新建 `components/BacktestMetrics.vue`：12 指标网格
- [ ] 新建 `components/NavChart.vue`：ECharts 净值曲线（策略/基准/超额 + DataZoom）
- [ ] 新建 `components/TradeTable.vue`：交易记录表格（分页 + 摘要统计）
- [ ] 新建 `components/LogViewer.vue`：日志查看器（深色终端风格、下载、滚动到底部）
- [ ] 新建 `components/NewBacktestDialog.vue`：新建回测弹窗（策略信息横幅 + 参数配置）
- [ ] 新建 `views/BacktestCenter.vue`：左侧回测列表 + 右侧详情（7 个 Tab：净值/交易/持仓/风险/收益分布/日志）
- [ ] 新建 `composables/useWebSocket.js`：socket.io-client 连接管理，`backtest_progress/backtest_completed/backtest_failed/log_line` 事件监听
- [ ] 新建 `store/modules/backtest.js`：回测列表/当前回测/运行状态/进度
- [ ] 新建 `api/backtest.js`：回测 API 封装

## Phase 6: 工作台 & 路由整合（1天）

- [ ] 新建 `views/WorkspaceView.vue`：KPI 卡片（回测总数/运行中/策略总数/数据覆盖）+ 最近回测列表 + 成功率趋势图表
- [ ] 改造 `router/index.js`：新路由 `/workspace`, `/strategies`, `/strategies/:id`, `/backtest`, `/backtest/:id`, `/data`, `/settings`
- [ ] 改造 `layouts/MainLayout.vue`：新菜单项（工作台/策略研究/回测中心/数据中心/系统设置）
- [ ] 清理：归档旧版 `views/`（StockList, ChartView, StockSelect, VolSelect, VolLine, TrendSelect, DataCheck, RuleSetting, UserInfo, StockSignalsView, PortfolioRiskView, TaskCenterView, FactorLabView, DataCenterView, StrategyWorkspaceView, BacktestCenterView, DashboardView, SystemSettingsView 旧版）

## Phase 7: 认证升级 & 系统接口（0.5天）

- [ ] 改造 `core/security.py`：密码哈希从 MD5 改为 bcrypt（`hash_password` / `verify_password`）
- [ ] 改造 `services/auth_service.py`：注册/登录/改密使用 bcrypt
- [ ] 改造 `repositories/user_repo.py`：`create_user` 使用 bcrypt 哈希，`verify_user_password` 兼容旧 MD5 密码（首次登录后自动升级为 bcrypt）
- [ ] 新建 `api/system.py`：`GET /api/health` (增强：含 rqalpha 版本、数据状态)、`GET /api/system/info`

## Phase 8: 测试 & 验证（1.5天）

- [ ] 单元测试：`test_strategy_service.py`（CRUD/版本管理/级联删除检查）、`test_datasource.py`、`test_backtest_engine.py`、`test_backtest_api.py`
- [ ] E2E 测试：新建策略 → 编辑代码 → 发起回测 → 查看进度 → 查看结果（净值/交易/持仓/风险/日志）→ 取消回测 → 版本切换对比
- [ ] 验证清单对照：12 条验收标准逐条通过

## 不需要做的

- 不修改 MySQL 旧库 `stock` 的任何表结构
- 不做模拟交易、实盘交易（二期）
- 不做因子 IC 分析、分层收益增强（二期）
- 不做组合管理（三期）
- 不做 Docker 沙箱隔离（二期）
