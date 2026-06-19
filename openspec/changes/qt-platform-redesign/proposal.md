# Change Proposal: QT 量化平台重构 — 策略研究 & 回测中心

## Why

当前系统虽然提供了策略、回测、信号、组合等模块，但全部使用 mock 数据，不具备真实的量化回测能力。用户无法编写 Python 策略代码、无法使用真实行情数据执行回测、无法查看回测的净值曲线和交易明细。系统需要一个真正的量化回测引擎来替代所有 mock 实现。

同时，项目目录下已有 rqalpha 回测框架源码（`/Users/gxwang/QT/rqalpha`），以及 QTrade 项目的 rqalpha 集成参考实现（`/Users/gxwang/QT/QTrade`），具备引入真实回测能力的技术基础。

本次重构聚焦两个核心模块——策略研究和回测中心，对标米筐（RiceQuant）产品体验，其余模块（模拟交易、因子增强、组合管理）留到后续版本。

## What

基于 rqalpha 6.x 回测框架，重建策略管理和回测中心两大模块：

1. **策略管理**：支持在线编写 Python 策略代码（Monaco Editor），多版本管理，版本间可切换和对比回测结果
2. **回测中心**：策略 → 回测配置 → 异步执行（rqalpha）→ WebSocket 实时进度 → 完整结果分析（净值曲线/交易记录/持仓分析/风险指标/收益分布/执行日志）
3. **数据中心**（支撑）：Tushare + AKShare 双数据源，支持行情同步和覆盖度监控
4. **基础设施升级**：密码加密从 MD5 升级为 bcrypt，新建数据库 `qt_dev`，连接池沿用

变更范围：
- **新建数据库**：`qt_dev`（18 张表），从旧 `stock` 库迁移 stock_basic（全量）+ stock_daily（近半年）
- **后端新建/重写**：backtest_engine.py（rqalpha 封装）、backtest_datasource.py（CustomDataSource）、strategy_service.py、backtest_service.py、data_service.py、对应 api/ 路由和 repositories/
- **前端新建/重写**：StrategyResearch.vue、BacktestCenter.vue、CodeEditor.vue（Monaco Editor）、各类图表组件
- **移除**：旧的 mock backtest/strategy/portfolio/signals 实现
- **不动**：核心基础设施（core/config.py、core/database.py、core/security.py 改造但保留），数据库地址不变

## Impact

- **功能提升**：从全部 mock 数据变为真实 rqalpha 回测，用户可编写策略代码并查看完整回测结果
- **数据库**：新建 `qt_dev` 库，旧 `stock` 库保留不动，仅读取迁移
- **API 变更**：策略和回测相关 API 全部重写（路径、请求/响应格式变化），认证模块 API 不变（仅内部密码哈希升级），数据查询 API 路径调整
- **前端路由**：新增 `/strategies`、`/backtest`、`/workspace`、`/data`，移除旧的 `/table`、`/chart`、`/stockselect` 等
- **新依赖**：monaco-editor（前端代码编辑器）、socket.io-client（WebSocket）
- **配置变更**：`.env` 新增 `DB_NAME=qt_dev`、`PASSWORD_HASH=bcrypt`、`LOG_DIR=logs` 等
