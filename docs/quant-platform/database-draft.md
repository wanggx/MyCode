# 数据库设计草案

本文档是轻量量化投研平台的数据库草案，供后续实现参考。

表结构不要求一次性全部落地，应按阶段逐步增加。

## 命名原则

- 日期字段统一使用 `YYYYMMDD` 字符串或 `DATE`，由项目现状决定。
- 股票代码统一使用 `ts_code`。
- JSON 字段用于保存参数快照和解释快照。
- 大表必须建立索引。
- 所有任务、策略、回测、信号都保留创建时间。

## 1. 行情与基础数据

当前项目已有股票基础表和日线、周线、月线相关表，可在现有表基础上补索引。

### stock_basic

用途：股票基础信息。

关键字段：

```text
ts_code
symbol
name
area
industry
market
list_date
status
```

索引：

```text
PRIMARY KEY (ts_code)
INDEX (market)
INDEX (industry)
```

### stock_daily

用途：A 股日线。

关键字段：

```text
ts_code
trade_date
open
high
low
close
pre_close
change
pct_chg
vol
amount
```

索引：

```text
UNIQUE KEY (ts_code, trade_date)
INDEX (trade_date)
```

### stock_week / stock_month

用途：由日线聚合得到的周线、月线。

索引：

```text
UNIQUE KEY (ts_code, trade_date)
INDEX (trade_date)
```

### hk_stock_daily

用途：港股日线。

索引：

```text
UNIQUE KEY (ts_code, trade_date)
INDEX (trade_date)
```

## 2. 数据质量

### data_quality_issue

用途：记录数据质量问题。

字段：

```text
id
issue_code
market
data_type
start_date
end_date
expected_count
actual_count
missing_count
severity
status
impact_summary_json
discovered_at
resolved_at
created_at
updated_at
```

状态：

```text
open
repairing
resolved
ignored
failed
```

索引：

```text
UNIQUE KEY (issue_code)
INDEX (market, data_type, start_date, end_date)
INDEX (status)
```

### data_quality_issue_detail

用途：记录问题明细，例如缺失股票。

字段：

```text
id
issue_id
trade_date
ts_code
issue_type
message
created_at
```

issue_type 示例：

```text
missing_daily
invalid_ohlc
missing_week
missing_month
abnormal_volume
```

索引：

```text
INDEX (issue_id)
INDEX (trade_date)
INDEX (ts_code)
```

### data_repair_job

用途：记录数据修复任务。

字段：

```text
id
issue_id
task_job_id
repair_mode
status
options_json
before_snapshot_json
after_snapshot_json
report_json
started_at
finished_at
created_at
```

repair_mode：

```text
repair_missing_only
reload_date
ignore
```

## 3. 任务系统

### task_job

用途：统一后台任务。

字段：

```text
id
task_type
status
priority
params_json
progress
message
created_by
created_at
started_at
finished_at
```

task_type：

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

status：

```text
pending
running
success
failed
canceled
```

索引：

```text
INDEX (status, priority, created_at)
INDEX (task_type)
```

### task_step

用途：记录任务步骤。

字段：

```text
id
job_id
step_order
step_name
status
message
started_at
finished_at
```

索引：

```text
INDEX (job_id, step_order)
```

## 4. 因子

### factor_def

用途：因子定义。

字段：

```text
id
factor_code
factor_name
category
description
params_json
enabled
created_at
updated_at
```

索引：

```text
UNIQUE KEY (factor_code)
```

### factor_value

用途：因子结果缓存。

字段：

```text
trade_date
ts_code
factor_code
value
created_at
```

索引：

```text
UNIQUE KEY (trade_date, ts_code, factor_code)
INDEX (factor_code, trade_date)
INDEX (ts_code, trade_date)
```

说明：

第一版可以不急着全量落 `factor_value`，可先按策略运行需要计算。

## 5. 策略

### strategy

用途：策略主表。

字段：

```text
id
name
strategy_type
description
enabled
created_at
updated_at
```

strategy_type：

```text
volume_breakout
ma_trend
macd_kdj_resonance
hk_trend
custom_combo
```

### strategy_version

用途：策略参数版本。

字段：

```text
id
strategy_id
version
params_json
buy_rules_json
sell_rules_json
remark
created_at
```

索引：

```text
INDEX (strategy_id, version)
```

### strategy_run

用途：策略运行记录。

字段：

```text
id
strategy_id
version_id
trade_date
status
signal_count
task_job_id
started_at
finished_at
message
```

索引：

```text
INDEX (strategy_id, trade_date)
INDEX (status)
```

## 6. 信号

### signal

用途：选股信号。

字段：

```text
id
trade_date
ts_code
name
market
strategy_id
strategy_version_id
strategy_run_id
score
reason_text
factor_snapshot_json
risk_snapshot_json
data_quality_status
status
created_at
```

status：

```text
new
watched
portfolio
ignored
```

索引：

```text
INDEX (trade_date)
INDEX (ts_code)
INDEX (strategy_id, trade_date)
INDEX (score)
```

## 7. 回测

### backtest_job

用途：回测主表。

字段：

```text
id
strategy_id
version_id
task_job_id
start_date
end_date
benchmark
status
params_json
metrics_json
created_at
started_at
finished_at
```

### backtest_nav

用途：每日净值。

字段：

```text
job_id
trade_date
nav
benchmark_nav
drawdown
```

索引：

```text
UNIQUE KEY (job_id, trade_date)
```

### backtest_position

用途：每日持仓。

字段：

```text
job_id
trade_date
ts_code
weight
market_value
close_price
```

索引：

```text
INDEX (job_id, trade_date)
```

### backtest_trade

用途：交易明细。

字段：

```text
id
job_id
trade_date
ts_code
side
price
quantity
amount
fee
reason
```

## 8. 观察池与模拟组合

### watchlist

用途：观察池。

字段：

```text
id
ts_code
name
market
source_signal_id
note
status
added_at
removed_at
```

### portfolio

用途：模拟组合。

字段：

```text
id
name
type
description
created_at
```

type：

```text
simulation
watch
custom
```

### portfolio_position

用途：模拟组合每日持仓。

字段：

```text
portfolio_id
trade_date
ts_code
weight
quantity
cost_price
close_price
market_value
```

### portfolio_nav

用途：模拟组合净值。

字段：

```text
portfolio_id
trade_date
nav
daily_return
drawdown
```

## 9. 系统配置

### system_config

用途：非敏感配置。

字段：

```text
config_key
config_value
description
updated_at
```

说明：

敏感信息，例如 Tushare Token、数据库密码、Webhook Key，优先放 `.env`，不要明文放数据库。

## 第一阶段必须表

建议第一阶段只新增：

```text
task_job
task_step
data_quality_issue
data_quality_issue_detail
data_repair_job
strategy
strategy_version
strategy_run
signal
backtest_job
backtest_nav
backtest_position
backtest_trade
```

因子和组合相关表可以第二阶段补。
