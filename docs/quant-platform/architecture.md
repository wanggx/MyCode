# 总体架构方案

## 目标

建设一个个人使用的轻量量化投研平台，核心能力包括：

- 数据获取与补录
- 数据质量诊断与修复
- 因子和技术指标研究
- 策略参数化运行
- 日频回测
- 选股信号解释
- 模拟交易与策略验证（模拟盘）
- 实盘交易（miniQMT，需 Windows 桥接）
- 任务调度与运行日志

## 设计原则

1. 单体优先：不拆微服务。
2. 数据可靠优先：先保证数据可信，再扩展复杂策略。
3. 任务可追踪：所有长任务都必须有任务记录和步骤日志。
4. 计算轻量：日频为主，分钟级仅用于实盘行情推送。
5. 可恢复：失败任务可查看原因并手动重试。
6. 可追溯：策略、回测、信号都能追溯到参数版本和数据日期。
7. 跨平台桥接：Windows 端轻量网关，Linux 端集中管理。

---

## 部署形态

### 总体拓扑

```
┌────────────────────────────────────────────────────────────┐
│                      用户浏览器                              │
│                 http://linux-server:5100                     │
└────────────────────────┬───────────────────────────────────┘
                         │
┌────────────────────────┴───────────────────────────────────┐
│                  Linux Server（主平台）                       │
│                                                             │
│  Nginx / Vue Dev Server (port 5100)                        │
│    └─ 托管前端静态文件 + 反向代理 /api → Flask              │
│                                                             │
│  Flask API 进程 (port 5000)                                  │
│    ├─ 策略 / 回测 / 因子 / 任务 API                         │
│    ├─ 模拟交易 / 实盘交易 API                                │
│    └─ QuantBridge Client（连接 Windows 桥接器）              │
│         ├─ HTTP REST：查询行情、提交订单                    │
│         └─ WebSocket：接收实时行情推送                      │
│                                                             │
│  Worker 进程                                                 │
│    ├─ 扫描 MySQL 任务表                                      │
│    ├─ 数据同步 / 补录 / 质量检查                             │
│    ├─ 日频回测                                               │
│    └─ 策略信号生成                                           │
│                                                             │
│  MySQL                                                       │
│    ├─ 行情数据（日线 / 分钟线）                              │
│    ├─ 策略 / 版本 / 回测 / 信号                             │
│    ├─ 模拟盘 / 实盘运行记录                                  │
│    └─ 任务日志                                               │
└────────────────────────────────────────────────────────────┘
                         │
                         │ LAN (HTTP + WebSocket)
                         │
┌────────────────────────┴───────────────────────────────────┐
│              Windows PC（miniQMT 桥接器）                     │
│                                                             │
│  QuantBridge Server (Python, Flask + Flask-Sock)            │
│    ├─ REST API: GET /api/bridge/quote/{symbol}?period=1m   │
│    ├─ REST API: POST /api/bridge/order (下单)              │
│    ├─ REST API: GET /api/bridge/account (账户查询)         │
│    └─ WebSocket: ws://windows:5101/ws/quote (实时推送)      │
│                                                             │
│  miniQMT (xtquant SDK)                                       │
│    ├─ 行情：1m K线 / 1d K线 / 实时 Tick                     │
│    ├─ 交易：买入 / 卖出 / 撤单 / 持仓查询                   │
│    └─ 账户：资金 / 持仓 / 当日委托                          │
└────────────────────────────────────────────────────────────┘
```

### 跨平台数据流

```
策略信号生成（Linux Worker）
  → 写入 signal 表
  → 模拟盘 / 实盘运行服务读取信号
  → 实盘信号通过 QuantBridge Client → HTTP → Windows QuantBridge Server
  → Windows miniQMT 执行下单
  → 成交回报通过 WebSocket → Linux Flask → 更新持仓 / 订单状态
```

```
实时行情（Windows miniQMT）
  → xtquant 订阅行情
  → QuantBridge Server WebSocket 推送
  → Linux QuantBridge Client 接收
  → 落库 MySQL 分钟线表
  → 策略引擎消费行情数据
```

---

## 进程模型

```text
Linux:
  1. Web 进程:       python backend/run.py
  2. Worker 进程:     python backend/worker.py
  3. Bridge Client:  python backend/quant_bridge_client.py（Web 进程内嵌或独立）

Windows:
  4. Bridge Server:  python bridge/server.py
  5. miniQMT:         xtquant (国金证券官方客户端)
```

- Web 进程：处理 API 请求 + 内嵌 QuantBridge Client（连接 Windows）
- Worker 进程：定时任务、回测、信号生成
- Bridge Client：与 Windows Bridge Server 通信，获取行情、提交订单
- Bridge Server：Windows 端轻量网关，封装 miniQMT API

---

## 核心分层

```text
API Layer
  app/api/*
    ├── trading.py          # 模拟盘 / 实盘 管理
    ├── strategies.py       # 策略 CRUD
    ├── backtests.py        # 回测管理
    ├── signals.py          # 信号查询
    └── ...

Service Layer
  app/services/*
    ├── trading_service.py  # 交易聚合服务
    ├── bridge_client.py    # QuantBridge 客户端（→ Windows）
    └── ...

Repository Layer
  app/repositories/*
    └── ...

Bridge Layer（Windows）
  bridge/
    ├── server.py           # Flask 网关服务
    ├── xtquant_wrapper.py  # miniQMT SDK 封装
    └── config.yaml         # 券商配置
```

---

## 实盘交易架构详解

### 模拟盘 vs 实盘对比

| | 模拟盘 | 实盘 |
|---|---|---|
| 运行环境 | Linux 本地 | Linux + Windows 桥接 |
| 行情来源 | MySQL 历史数据 / Tushare | miniQMT 实时行情 |
| 撮合方式 | 模拟撮合引擎 | 券商真实撮合 |
| 资金 | 虚拟资金 | 券商账户真实资金 |
| 延迟 | 无要求 | 1m 级别，秒级延迟可接受 |
| 风控 | 软限制 | 硬限制（仓位/止损/日内亏损） |

### 策略运行生命周期

```
回测完成（BacktestCenter）
  ↓
部署到模拟盘（PaperTrading）── 零风险验证
  ├── 启停控制
  ├── 查看持仓 / 交易记录 / 日志
  └── 满足条件 → 升级实盘
       ↓
实盘运行（TradingCenter）
  ├── 信号 → QuantBridge Client → Windows → miniQMT → 券商
  ├── 行情 ← Windows miniQMT ← 券商
  ├── 实时监控：持仓 / 订单 / 风控
  └── 可降级回模拟盘（停止实盘，保留模拟盘）
```

### QuantBridge 通信协议

**REST API（请求-响应）：**
```
GET  /api/bridge/quote/{symbol}?period=1m&count=100   → K线数据
GET  /api/bridge/quote/{symbol}?period=1d&count=250
POST /api/bridge/order       → 下单（{symbol, direction, price, quantity, order_type}）
DELETE /api/bridge/order/{id} → 撤单
GET  /api/bridge/account     → 账户信息（资金、持仓、委托）
GET  /api/bridge/positions   → 当前持仓
```

**WebSocket（实时推送）：**
```
ws://windows:5101/ws/quote
  → 订阅: {action: "subscribe", symbols: ["000001.SZ", "600036.SH"]}
  ← 推送: {symbol: "000001.SZ", time: "09:35:00", open: 12.50, high: 12.60, low: 12.45, close: 12.55, volume: 125000}
```

### 数据存储

```
stock_daily        — 日线行情（已有，Tushare/AKShare 同步）
stock_minute       — 分钟线行情（新增，miniQMT 实时写入）
  ├── ts_code, trade_time, open, high, low, close, volume, amount
paper_run          — 模拟盘运行（使用 task_job 表，mode=paper）
live_run           — 实盘运行（使用 task_job 表，mode=live）
  ├── strategy_id, broker, initial_capital, status, params(JSON)
signal             — 策略信号（已有）
trade_order        — 交易订单（新增，记录所有下单）
  ├── run_id, symbol, direction, price, quantity, status, order_type
  ├── created_at, filled_at, pnl, broker_order_id
```

---

## 数据流

### 每日自动流程

```text
定时触发
  → 创建 sync_daily_data 任务
  → 下载 A 股日线
  → 下载港股日线
  → 合并临时数据到正式表
  → 聚合周线/月线
  → 执行数据质量扫描
  → 如果数据健康，运行启用策略
  → 生成信号
  → 更新模拟组合
  → 发送通知
```

### 实盘行情流

```text
Windows miniQMT 接收行情
  → QuantBridge Server WebSocket 推送到 Linux
  → Linux Bridge Client 接收
  → 写入 stock_minute 表（异步批量）
  → 策略引擎检查信号条件
  → 触发买卖信号
  → 信号写入 signal 表
  → 实盘运行服务读取信号
  → 通过 Bridge Client 发送订单到 Windows
  → miniQMT 执行下单
  → 成交回报回传 → 更新持仓
```

### 回测流程

```text
用户提交回测
  → 创建 backtest_job + task_job
  → Worker 执行日频回测
  → 保存净值、持仓、交易明细、指标
  → 前端查询结果并展示
```

---

## API 设计原则

1. 所有长任务 API 只创建任务并返回 `job_id`。
2. 前端通过任务中心或轮询查询任务状态。
3. 查询类 API 必须分页。
4. 大结果不直接实时计算，优先读取已落库结果。
5. 接口返回结构统一：`{ "success": true, "data": {}, "message": "" }`
6. Bridge API 超时设置 5s（行情）/ 10s（下单），失败重试 1 次。

---

## 不做的事情（现阶段）

- Redis / Celery / Kafka / Airflow
- Kubernetes / 分布式任务
- Tick 级回测
- 多账户管理
- 在线代码 IDE

---

## 资源控制

- 后台任务串行执行。
- 回测默认限制区间（默认 3 年，最大 8 年）。
- 单次数据补录限制日期范围。
- 大表查询必须分页。
- 日线、周线、月线、分钟线表必须建复合索引。
- 日志和历史任务支持清理。

---

## Windows 桥接器部署要求

- **OS**: Windows 10/11 或 Windows Server
- **Python**: 3.10+（xtquant 官方支持版本）
- **网络**: 与 Linux 服务器在同一局域网（延迟 <5ms）
- **启动**: 开机自启 QuantBridge Server + miniQMT 客户端
- **安全**: 仅监听内网地址，不做公网暴露
- **高可用**: Bridge Client 自动重连，断开期间使用缓存行情
