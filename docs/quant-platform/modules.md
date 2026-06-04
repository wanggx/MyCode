# 功能模块技术方案

## 1. 总览

### 目标

给用户一个每日投研状态入口，展示数据、策略、信号、任务和风险的摘要。

### 数据来源

- 数据质量摘要
- 今日策略运行结果
- 今日信号统计
- 模拟组合风险指标
- 最近任务状态

### API

```text
GET /api/dashboard/summary
GET /api/dashboard/recent-tasks
GET /api/dashboard/top-signals
```

### 实现建议

总览页只读聚合结果，不在请求时做重计算。

可以由每日任务结束后写入一张轻量摘要表：

```text
dashboard_snapshot
```

如果第一版不建摘要表，也可以由 service 聚合查询，但要避免大范围扫描。

## 2. 数据中心

### 目标

管理数据获取、数据检查、缺口发现和手动修复。

### 核心能力

- 查看数据完整率
- 查看缺失日期
- 查看缺失股票
- 查看同步记录
- 创建手动补录任务
- 查看修复前后对比

### API

```text
GET /api/data/quality-summary
GET /api/data/issues
GET /api/data/issues/{id}
POST /api/data/issues/{id}/repair
POST /api/data/sync
POST /api/data/backfill
```

### 后端服务

```text
DataProviderService
DataQualityService
DataRepairService
TaskService
```

### 实现边界

第一版只支持：

- A 股日线检查
- 港股日线检查
- 日线缺失补录
- 周线/月线重聚合

不做：

- 分钟级数据
- tick 数据
- Level-2 数据

## 3. 因子实验室

### 目标

把现有技术指标沉淀为可复用因子，并提供基础分析能力。

### 第一版因子

```text
MA3
MA5
MA10
MA20
MACD
KDJ
成交量斜率
涨跌幅
波动率
```

### API

```text
GET /api/factors
POST /api/factors/analyze
GET /api/factors/{code}/coverage
GET /api/factors/{code}/ic
GET /api/factors/{code}/group-return
```

### 计算方式

资源有限时，不建议每天全量重算所有因子。

推荐：

```text
按策略或分析需要计算
  -> 写入 factor_value 缓存
  -> 下次命中缓存直接读取
```

### 指标

第一版可以支持：

- 覆盖率
- IC 曲线
- 分层收益
- 简单相关性

暂不做：

- 风格中性化
- 行业中性化
- 多因子优化器
- 大规模机器学习

## 4. 策略工作台

### 目标

将当前固定选股逻辑升级为参数化策略。

### 策略类型

```text
volume_breakout      放量突破
ma_trend             均线趋势
macd_kdj_resonance   MACD/KDJ 共振
hk_trend             港股趋势
custom_combo         组合条件策略
```

### API

```text
GET /api/strategies
GET /api/strategies/{id}
POST /api/strategies
PUT /api/strategies/{id}
POST /api/strategies/{id}/versions
POST /api/strategies/{id}/run
GET /api/strategies/{id}/runs
```

### 运行方式

策略运行是长任务：

```text
POST /api/strategies/{id}/run
  -> 创建 task_job
  -> Worker 执行
  -> 写入 strategy_run
  -> 写入 signal
```

### 版本管理

每次修改参数都创建策略版本：

```text
strategy_version
```

信号和回测必须绑定版本 ID。

### 不做

第一版不做在线代码编辑器。

如果以后要支持代码策略，也应该后置：

```text
参数化策略稳定后
  -> 再考虑 Python 脚本策略
  -> 再考虑沙箱和安全限制
```

## 5. 回测中心

### 目标

验证策略在历史区间内的表现。

### 第一版能力

- 日频回测
- 收盘后调仓
- 固定手续费
- 固定滑点
- 最大持仓数
- 单票权重上限
- 等权或信号分加权
- 简单止损
- 基准对比

### API

```text
POST /api/backtests
GET /api/backtests
GET /api/backtests/{id}
GET /api/backtests/{id}/nav
GET /api/backtests/{id}/positions
GET /api/backtests/{id}/trades
```

### 执行方式

```text
创建 backtest_job
  -> 创建 task_job
  -> Worker 执行
  -> 保存净值、持仓、交易明细和指标
```

### 资源限制

- 默认回测 3 年。
- 最大回测 8 年。
- 一次只运行一个回测。
- 回测股票池尽量使用策略产生的候选池，不全市场逐日暴力计算。

## 6. 选股信号

### 目标

把策略结果变成可解释信号，而不是只返回股票代码。

### 信号内容

```text
日期
代码
名称
市场
策略
策略版本
信号分
入选原因
因子快照
风险快照
数据质量状态
```

### API

```text
GET /api/signals
GET /api/signals/{id}
POST /api/signals/{id}/watch
POST /api/signals/{id}/portfolio
```

### 解释方式

每个信号保存：

```text
reason_text
factor_snapshot_json
risk_snapshot_json
```

不要在详情页实时重新计算解释，否则历史信号会因为参数变化而失真。

## 7. 组合风控

### 目标

不做实盘，但提供观察池和模拟组合，用于跟踪信号质量和组合风险。

### 第一版能力

- 加入观察池
- 加入模拟组合
- 每日按收盘价更新净值
- 查看持仓
- 行业分布
- 单票权重
- 最大回撤
- 连续回撤
- 数据缺失风险

### API

```text
GET /api/watchlist
POST /api/watchlist
GET /api/portfolio
GET /api/portfolio/{id}/risk
GET /api/portfolio/{id}/nav
GET /api/portfolio/{id}/positions
```

### 实现边界

第一版不用做复杂成交模拟。

可以先用：

```text
加入日收盘价作为买入价
每日收盘价更新市值
```

## 8. 任务中心

### 目标

统一管理所有后台任务。

### 任务类型

```text
sync_stock_basic
sync_daily_data
repair_missing_data
aggregate_week_month
quality_scan
run_strategy
run_backtest
update_portfolio
send_notification
```

### API

```text
GET /api/tasks
GET /api/tasks/{id}
POST /api/tasks/{id}/retry
POST /api/tasks/{id}/cancel
```

### 实现方式

任务状态存 MySQL。

Worker 定时扫描：

```text
status = pending
```

然后串行执行。

## 9. 系统设置

### 目标

管理个人项目必要配置。

### 配置项

- Tushare Token
- 数据同步时间
- 单次补录最大天数
- 回测最大区间
- 企业微信通知地址
- 默认市场
- 简单用户账号

### API

```text
GET /api/settings
PUT /api/settings
POST /api/settings/test-notification
```

### 实现建议

敏感配置仍然优先放 `.env`。

页面可以只展示掩码和测试状态，不直接明文展示 Token。
