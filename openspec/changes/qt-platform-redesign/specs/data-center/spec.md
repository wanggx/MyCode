# Specification (Delta): Data Center — 数据中心

## ADDED Requirements

### Requirement: 股票列表查询

系统 SHALL 支持从 stock_basic 表分页查询股票列表。

#### Scenario: 查询 A 股列表
- **GIVEN** stock_basic 表中有 5,286 条记录
- **WHEN** 客户端发送 GET `/api/data/stocks?page=1&page_size=20&market=SZ`
- **THEN** 系统 SHALL 响应 HTTP 200
- **AND** 返回的每项含 `ts_code, symbol, name, area, industry, market, list_date, board_type`

#### Scenario: 模糊搜索
- **WHEN** 客户端发送 GET `/api/data/stocks?keyword=平安`
- **THEN** 系统 SHALL 返回 name 或 ts_code 包含"平安"的股票

### Requirement: 股票日线数据

系统 SHALL 返回指定股票的日线行情数据。

#### Scenario: 查询日线
- **WHEN** 客户端发送 GET `/api/data/stocks/000001.SZ/daily?start_date=2024-01-01&end_date=2024-01-31`
- **THEN** 系统 SHALL 响应 HTTP 200
- **AND** 每条记录含 `trade_date, open, high, low, close, vol, amount`

#### Scenario: 日期范围超限
- **WHEN** 客户端请求超过 365 天的日线数据
- **THEN** 系统 SHALL 响应 HTTP 400，提示缩小日期范围

### Requirement: 数据源管理

系统 SHALL 支持查看和管理数据源配置。

#### Scenario: 查询数据源列表
- **WHEN** 客户端发送 GET `/api/data/sources`
- **THEN** 系统 SHALL 响应 HTTP 200
- **AND** 返回每个数据源的 `name, display_name, status, priority`

#### Scenario: Tushare 同步触发
- **WHEN** 客户端发送 POST `/api/data/sync`，body 含 `source="tushare", data_type="daily", trade_date="2026-06-19"`
- **THEN** 系统 SHALL 创建 data_sync_log 记录（status=pending）
- **AND** 系统 SHALL 创建 task_job（task_type=data_sync）
- **AND** 系统 SHALL 响应 HTTP 200 含 `data.sync_log_id`

### Requirement: 数据同步日志

系统 SHALL 记录每次数据同步的执行日志。

#### Scenario: 查询同步日志
- **WHEN** 客户端发送 GET `/api/data/sync-logs?source=tushare&page=1&page_size=20`
- **THEN** 系统 SHALL 返回分页同步日志，每项含 `source, data_type, trade_date, status, total_count, success_count, fail_count, error_msg`

### Requirement: 数据概览

系统 SHALL 返回数据中心的总览统计。

#### Scenario: 查询数据概览
- **WHEN** 客户端发送 GET `/api/data/overview`
- **THEN** 系统 SHALL 响应 HTTP 200
- **AND** body 含 `data.total_stocks`（股票总数）、`data.latest_trade_date`（最新行情日期）、`data.completeness`（数据完整度百分比）、`data.date_range_start`（数据起始日期）
