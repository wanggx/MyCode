# QT 量化平台 — 技术设计 V2

> **一期范围**：策略研究 + 回测中心（对标米筐 RiceQuant）
> **数据库**：MySQL `qt_dev`（新建库，同一 MySQL 地址）
> **回测引擎**：rqalpha 6.x（`/Users/gxwang/QT/rqalpha`）
> **参考实现**：QTrade（`/Users/gxwang/QT/QTrade`）

---

## 一、项目目标与范围

### 1.1 一期目标

构建一个可用的量化回测平台，用户可以：
1. 在 Web 界面编写、管理 Python 策略代码（版本控制）
2. 对策略发起回测，实时查看进度
3. 查看完整的回测结果：净值曲线、交易记录、持仓分析、风险指标、收益分布、执行日志

### 1.2 一期不做的

| 模块 | 状态 |
|------|------|
| 策略研究 + 回测中心 | ✅ 一期 |
| 数据中心（行情同步 + 数据源管理） | ✅ 一期（支撑回测） |
| 工作台仪表盘 | ✅ 一期 |
| 模拟交易（Paper Trading） | ❌ 二期 |
| 实盘交易（Live Trading） | ❌ 二期 |
| 因子研究增强（IC/分层） | ❌ 二期 |
| 组合管理 | ❌ 三期 |

### 1.3 技术约束

- 回测框架必须使用 rqalpha
- MySQL 地址不变，新建库 `qt_dev`
- 禁止 DDL 变更现有数据库
- 后端单文件 ≤1000 行，单函数 ≤150 行
- 后端启动必须使用 `backend/.venv` 虚拟环境

---

## 二、技术架构

### 2.1 整体架构

```
┌──────────────────────────────────────────────────────────┐
│                    前端 (Vue 3 + Element Plus)             │
│  Monaco Editor │ ECharts 6 │ Vuex 4 │ Vue Router 4       │
│  socket.io-client (WebSocket 回测进度推送)                 │
└──────────────────────┬───────────────────────────────────┘
                       │ HTTP REST + WebSocket
┌──────────────────────┴───────────────────────────────────┐
│                  后端 (Python Flask)                       │
│                                                          │
│  api/          services/        repositories/            │
│  (Controller)  (Business)       (Data Access)            │
│      │              │                 │                  │
│      │    ┌─────────┴───────┐         │                  │
│      │    │  BacktestEngine  │         │                  │
│      │    │  (rqalpha 封装)   │         │                  │
│      │    └─────────┬───────┘         │                  │
│      │              │                  │                  │
│  Flask-SocketIO   rqalpha.run_func()  pymysql / SQLAlchemy│
└──────────────────────┬───────────────────────────────────┘
                       │
┌──────────────────────┴───────────────────────────────────┐
│                  MySQL (qt_dev)                           │
│  17 张表：users, stock_basic, stock_daily,                 │
│  strategy, strategy_version,                              │
│  backtest_job/nav/trade/position/daily_metrics/risk,      │
│  data_source, data_sync_log, factor_def, factor_value,    │
│  task_job, task_step                                     │
│                                                          │
│  文件系统：logs/{strategy_key}/{backtest_id}.log           │
└──────────────────────────────────────────────────────────┘
```

### 2.2 后端分层

```
backend/
├── run.py                          # Flask 启动入口
├── worker.py                       # 后台 Worker：消费 task_job 队列
├── app/
│   ├── __init__.py                 # create_app() 工厂函数
│   ├── api/                        # 路由层（薄层，只做参数校验和响应）
│   │   ├── auth.py                 # /api/auth/*
│   │   ├── strategies.py           # /api/strategies/*
│   │   ├── backtests.py            # /api/backtests/*
│   │   ├── data.py                 # /api/data/*
│   │   ├── factors.py              # /api/factors/*
│   │   ├── tasks.py                # /api/tasks/*
│   │   └── system.py               # /api/health, /api/system/*
│   ├── services/                   # 服务层（业务编排）
│   │   ├── auth_service.py
│   │   ├── strategy_service.py     # 策略 CRUD + 版本管理
│   │   ├── backtest_service.py     # 回测生命周期管理
│   │   ├── backtest_engine.py      # ★ rqalpha 封装（核心）
│   │   ├── backtest_datasource.py  # ★ CustomDataSource（MySQL → rqalpha）
│   │   ├── data_service.py         # 行情数据同步
│   │   ├── factor_service.py
│   │   └── task_service.py
│   ├── repositories/               # 数据访问层（纯 SQL，无业务逻辑）
│   │   ├── user_repo.py            # users
│   │   ├── strategy_repo.py        # strategy + strategy_version
│   │   ├── backtest_repo.py        # backtest_* 全部 6 张表
│   │   ├── stock_repo.py           # stock_basic
│   │   ├── stock_daily_repo.py     # stock_daily
│   │   ├── data_source_repo.py     # data_source + data_sync_log
│   │   ├── factor_repo.py          # factor_def + factor_value
│   │   └── task_repo.py            # task_job + task_step
│   ├── core/                       # 基础设施
│   │   ├── config.py               # Settings (DB_NAME=qt_dev)
│   │   ├── database.py             # SQLAlchemy engine (QueuePool)
│   │   ├── security.py             # JWT + bcrypt 密码哈希
│   │   ├── response.py             # 统一响应格式
│   │   └── logger.py               # 日志配置
│   └── utils/
│       └── dateutil.py
└── tests/                          # 测试
    ├── test_strategy_api.py
    ├── test_backtest_api.py
    ├── test_backtest_engine.py
    └── test_datasource.py
```

**分层依赖规则（不变）：**
```
api/ → services/ → repositories/
                → analysis/
                → core/
                → utils/
```

### 2.3 rqalpha 集成方案

#### 架构思路

参考 QTrade 的方案，核心思路是 **CustomDataSource + monkey-patch**：

1. **数据适配层** — `QtDataSource` 继承 rqalpha 的 `BaseDataSource`，从 MySQL `stock_daily` 读取行情，转成 rqalpha 要求的 numpy 结构化数组格式
2. **策略执行** — 使用 `rqalpha.run_func(config, init=..., handle_bar=...)` API，在独立线程中运行
3. **进度推送** — 注入 `builtins._BT_PROGRESS_FN_` 回调函数，每个 bar 触发一次，通过 Flask-SocketIO 推送给前端
4. **结果提取** — 解析 `sys_analyser` mod 输出（summary / trades / positions / daily_nav / risk），写入 MySQL 结果表
5. **日志记录** — 配置 rqalpha 的 `log_file` 到 `logs/{strategy_key}/{backtest_id}.log`

#### CustomDataSource 设计

```python
# backend/app/services/backtest_datasource.py

import numpy as np
from rqalpha.data.base_data_source import BaseDataSource
from rqalpha.model.instrument import Instrument
from rqalpha.const import InstrumentType

# rqalpha 要求的 Bar 数据结构
BAR_DTYPE = np.dtype([
    ('datetime', 'uint64'),
    ('open', 'float64'),
    ('high', 'float64'),
    ('low', 'float64'),
    ('close', 'float64'),
    ('volume', 'float64'),
    ('total_turnover', 'float64'),
])

class QtDataSource(BaseDataSource):
    """
    从 MySQL stock_daily 读取行情，适配 rqalpha 数据接口

    关键方法：
    - get_bar(instrument, dt, frequency) → numpy array
    - history_bars(instrument, bar_count, frequency, fields, ...) → numpy array
    - get_instruments() → list[Instrument]
    - available_data_range(frequency) → (start_date, end_date)
    - get_trading_calendar() → numpy array of dates
    """

    def __init__(self, start_date, end_date, db_connection_pool):
        self._start_date = start_date
        self._end_date = end_date
        self._pool = db_connection_pool
        # 从 stock_basic 构建 Instrument 映射
        self._instruments = {}  # order_book_id → Instrument
        # 从 stock_daily 构建交易日历
        self._trading_calendar = None
        # 数据缓存：{order_book_id: numpy array of BAR_DTYPE}
        self._data_cache = {}
        self._init()

    def _init(self):
        """初始化：加载 Instrument 列表 + 交易日历 + 预加载行情数据"""
        # 1. 从 stock_basic 加载所有标的
        # 2. 从 stock_daily 的 DISTINCT trade_date 构建交易日历
        # 3. 按 order_book_id 批量预加载 [start_date, end_date] 的日线数据
        # 4. Instrument 编码规则：SZ000001 / SH600000
        #    - SZ** → exchange=SZSE, SZSE 代码以 000/001/002/300/301 开头
        #    - SH** → exchange=SSE，SSE 代码以 600/601/603/605/688 开头
        pass

    def get_bar(self, instrument, dt, frequency):
        """返回某一时间点的 Bar 数据"""
        pass

    def history_bars(self, instrument, bar_count, frequency, fields, skip_suspended=True,
                     include_now=False, adjust_type='pre', adjust_orig=None):
        """返回历史 N 个 Bar 的数据"""
        pass

    def get_instruments(self):
        """返回所有可用标的列表"""
        pass

    def available_data_range(self, frequency):
        """返回可用数据的时间范围"""
        pass

    def get_trading_calendar(self):
        """返回交易日历"""
        pass

    def get_yield_curve(self, start_date, end_date, tenor=None):
        """返回无风险利率曲线（简化：返回固定 3%）"""
        pass
```

#### 进度注入方式

```python
# 在 backtest_engine.py 中，执行回测前注入：

import builtins

def _setup_progress_hook(total_bars, socketio, backtest_id):
    """注入进度回调到 builtins，rqalpha 策略桥接代码可调用"""
    bar_counter = [0]

    def progress_fn(current_date_str):
        bar_counter[0] += 1
        progress = min(bar_counter[0] / total_bars * 100, 100)
        socketio.emit('backtest_progress', {
            'backtest_id': backtest_id,
            'progress': round(progress, 1),
            'current_date': current_date_str,
            'completed_bars': bar_counter[0],
            'total_bars': total_bars,
        })

    builtins._BT_PROGRESS_FN_ = progress_fn
    builtins._BT_TOTAL_BARS_ = total_bars
```

#### 取消回测机制

```python
# rqalpha 不原生支持中断，通过设置标志位 + 自定义 event_source 实现
# 在 Environment 中注入一个 threading.Event，event_source 每轮循环检查

def _make_cancellable_event_source(original_source, cancel_event):
    """包装 event_source，每个事件前检查是否被取消"""
    for event in original_source:
        if cancel_event.is_set():
            raise BacktestCancelledError("回测已被用户取消")
        yield event
```

### 2.4 前端架构

```
frontend/src/
├── main.js                          # Vue 应用入口
├── App.vue                          # 根组件
├── config/
│   ├── api.js                       # 后端地址配置
│   └── axios.js                     # Axios 实例（JWT 拦截器）
├── router/
│   └── index.js                     # 路由定义
├── store/
│   ├── index.js                     # Vuex 根模块
│   ├── modules/
│   │   ├── user.js                  # 用户认证状态
│   │   ├── strategy.js              # 策略列表 + 当前策略
│   │   └── backtest.js              # 回测列表 + 当前回测 + 运行状态
├── api/
│   ├── auth.js                      # 登录/注册 API
│   ├── strategy.js                  # 策略 CRUD API
│   ├── backtest.js                  # 回测 API
│   └── data.js                      # 数据 API
├── composables/
│   ├── useWebSocket.js              # WebSocket 连接管理
│   └── useECharts.js                # ECharts 实例管理
├── layouts/
│   └── MainLayout.vue               # 侧边栏 + 顶栏壳
├── views/
│   ├── LoginView.vue                # 登录页
│   ├── WorkspaceView.vue            # 工作台仪表盘
│   ├── StrategyResearch.vue         # 策略研究（列表 + 编辑器）
│   ├── BacktestCenter.vue           # 回测中心（列表 + 结果）
│   ├── DataCenter.vue               # 数据中心
│   └── SystemSettings.vue           # 系统设置
└── components/
    ├── CodeEditor.vue               # Monaco Editor 封装
    ├── StrategyCard.vue             # 策略列表卡片
    ├── BacktestCard.vue             # 回测列表卡片
    ├── BacktestProgress.vue         # 回测进度条
    ├── BacktestMetrics.vue          # 回测指标网格
    ├── NavChart.vue                 # 净值曲线图表
    ├── TradeTable.vue               # 交易记录表格
    ├── PositionChart.vue            # 持仓分析图表
    ├── RiskChart.vue                # 风险分析图表
    ├── DistributionChart.vue        # 收益分布图表
    ├── LogViewer.vue                # 日志查看器
    └── NewBacktestDialog.vue        # 新建回测弹窗
```

### 2.5 前端路由设计

| 路径 | 组件 | 说明 |
|------|------|------|
| `/login` | LoginView | 登录（公开） |
| `/workspace` | WorkspaceView | 工作台仪表盘 |
| `/strategies` | StrategyResearch | 策略研究（列表+编辑器） |
| `/strategies/:id` | StrategyResearch | 策略详情（锚定到指定策略） |
| `/backtest` | BacktestCenter | 回测中心 |
| `/backtest/:id` | BacktestCenter | 回测详情（锚定到指定回测） |
| `/data` | DataCenter | 数据中心 |
| `/settings` | SystemSettings | 系统设置 |
| `/` | — | 重定向到 `/workspace` |

### 2.6 Vuex Store 设计

```javascript
// store/modules/user.js
state: { token, user, isAuthenticated }
actions: { login, register, fetchUser, changePassword, logout }

// store/modules/strategy.js
state: { list, total, current, currentVersion, isLoading }
actions: { fetchList, fetchDetail, create, update, delete, createVersion, loadVersionCode }

// store/modules/backtest.js
state: { list, total, current, running, progress }
actions: { fetchList, fetchDetail, create, cancel, fetchNav, fetchTrades, fetchLogs }
mutations: { SET_PROGRESS, SET_RESULT, CLEAR_PROGRESS }
```

---

## 三、数据库设计

### 3.1 库名：`qt_dev`

### 3.2 完整 DDL（18 张表）

```sql
-- ============================================================
-- 1. users — 用户表
-- ============================================================
CREATE TABLE users (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    username    VARCHAR(64)  NOT NULL UNIQUE COMMENT '用户名',
    password    VARCHAR(256) NOT NULL COMMENT '密码（bcrypt hash）',
    email       VARCHAR(128) DEFAULT NULL COMMENT '邮箱',
    role        VARCHAR(32)  DEFAULT 'user' COMMENT '角色：admin/user',
    status      VARCHAR(16)  DEFAULT 'active' COMMENT '状态：active/disabled',
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='用户表';

-- ============================================================
-- 2. stock_basic — 股票基础信息
-- ============================================================
CREATE TABLE stock_basic (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    ts_code         VARCHAR(16)  NOT NULL UNIQUE COMMENT '代码（000001.SZ）',
    symbol          VARCHAR(8)   NOT NULL COMMENT '简写（000001）',
    name            VARCHAR(64)  NOT NULL COMMENT '名称（平安银行）',
    area            VARCHAR(32)  DEFAULT NULL COMMENT '地区',
    industry        VARCHAR(64)  DEFAULT NULL COMMENT '行业',
    market          VARCHAR(16)  NOT NULL COMMENT '市场（SZ/SE/HK）',
    list_date       DATE         DEFAULT NULL COMMENT '上市日期',
    delist_date     DATE         DEFAULT NULL COMMENT '退市日期',
    exchange        VARCHAR(16)  DEFAULT 'SZSE' COMMENT '交易所（SZSE/SSE）',
    board_type      VARCHAR(32)  DEFAULT 'MainBoard' COMMENT '板块（MainBoard/GEM/KSH）',
    status          VARCHAR(16)  DEFAULT 'active',
    created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_ts_code (ts_code),
    INDEX idx_market (market),
    INDEX idx_industry (industry)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='股票基础信息';

-- ============================================================
-- 3. stock_daily — 日线行情
-- ============================================================
CREATE TABLE stock_daily (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    ts_code     VARCHAR(16)  NOT NULL COMMENT '股票代码',
    trade_date  DATE         NOT NULL COMMENT '交易日期',
    open        DOUBLE       DEFAULT NULL,
    high        DOUBLE       DEFAULT NULL,
    low         DOUBLE       DEFAULT NULL,
    close       DOUBLE       DEFAULT NULL,
    pre_close   DOUBLE       DEFAULT NULL,
    change_pct  DOUBLE       DEFAULT NULL COMMENT '涨跌幅(%)',
    vol         DOUBLE       DEFAULT NULL COMMENT '成交量（手）',
    amount      DOUBLE       DEFAULT NULL COMMENT '成交额（千元）',
    turnover    DOUBLE       DEFAULT NULL COMMENT '换手率(%)',
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_code_date (ts_code, trade_date),
    INDEX idx_trade_date (trade_date),
    INDEX idx_ts_code (ts_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='A股日线行情';

-- ============================================================
-- 4. strategy — 策略主表
-- ============================================================
CREATE TABLE strategy (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT          NOT NULL COMMENT '创建用户',
    name            VARCHAR(128) NOT NULL COMMENT '策略名称',
    description     TEXT         DEFAULT NULL COMMENT '策略描述',
    strategy_type   VARCHAR(32)  DEFAULT 'stock' COMMENT '策略类型：stock/future/index',
    status          VARCHAR(16)  DEFAULT 'draft' COMMENT '状态：draft/active/archived',
    latest_version  INT          DEFAULT 0 COMMENT '最新版本号',
    default_config  JSON         DEFAULT NULL COMMENT '默认回测配置',
    tags            JSON         DEFAULT NULL COMMENT '标签',
    strategy_key    VARCHAR(64)  NOT NULL UNIQUE COMMENT '策略标识（用于日志目录等）',
    created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at      DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user (user_id),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='策略主表';

-- default_config JSON 示例：
-- {"start_date":"2024-01-01","end_date":"2024-12-31","initial_capital":100000,
--  "benchmark":"000300.XSHG","frequency":"1d","commission":0.0003,"slippage":0.01}

-- ============================================================
-- 5. strategy_version — 策略版本表
-- ============================================================
CREATE TABLE strategy_version (
    id              INT AUTO_INCREMENT PRIMARY KEY,
    strategy_id     INT          NOT NULL COMMENT '策略ID',
    version         INT          NOT NULL COMMENT '版本号（自增）',
    source_code     MEDIUMTEXT   NOT NULL COMMENT '策略源码（Python）',
    config          JSON         DEFAULT NULL COMMENT '该版本的配置快照',
    change_log      TEXT         DEFAULT NULL COMMENT '变更说明',
    status          VARCHAR(16)  DEFAULT 'active' COMMENT '状态：active/archived',
    created_at      DATETIME     DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_strategy_version (strategy_id, version),
    INDEX idx_strategy (strategy_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='策略版本表';

-- ============================================================
-- 6. backtest_job — 回测任务表
-- ============================================================
CREATE TABLE backtest_job (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    user_id             INT          NOT NULL COMMENT '用户ID',
    strategy_id         INT          NOT NULL COMMENT '策略ID',
    strategy_version    INT          NOT NULL COMMENT '策略版本号',
    strategy_name       VARCHAR(128) DEFAULT NULL COMMENT '策略名称（冗余）',
    strategy_key        VARCHAR(64)  DEFAULT NULL COMMENT '策略标识（冗余，用于日志路径）',
    status              VARCHAR(16)  DEFAULT 'pending' COMMENT 'pending/running/completed/failed/cancelled',
    config              JSON         NOT NULL COMMENT '回测配置快照',
    -- 进度
    progress            DOUBLE       DEFAULT 0 COMMENT '进度 0-100',
    current_date        DATE         DEFAULT NULL COMMENT '当前运行日期',
    -- 结果摘要
    total_return        DOUBLE       DEFAULT NULL COMMENT '总收益率',
    annualized_return   DOUBLE       DEFAULT NULL COMMENT '年化收益率',
    max_drawdown        DOUBLE       DEFAULT NULL COMMENT '最大回撤',
    sharpe_ratio        DOUBLE       DEFAULT NULL COMMENT '夏普比率',
    sortino_ratio       DOUBLE       DEFAULT NULL COMMENT '索提诺比率',
    win_rate            DOUBLE       DEFAULT NULL COMMENT '胜率',
    profit_loss_ratio   DOUBLE       DEFAULT NULL COMMENT '盈亏比',
    annual_volatility   DOUBLE       DEFAULT NULL COMMENT '年化波动率',
    alpha               DOUBLE       DEFAULT NULL COMMENT 'Alpha',
    beta                DOUBLE       DEFAULT NULL COMMENT 'Beta',
    final_value         DOUBLE       DEFAULT NULL COMMENT '最终资产总值',
    total_trades        INT          DEFAULT 0 COMMENT '总交易笔数',
    benchmark_return    DOUBLE       DEFAULT NULL COMMENT '基准收益率',
    excess_return       DOUBLE       DEFAULT NULL COMMENT '超额收益',
    -- 运行信息
    start_time          DATETIME     DEFAULT NULL COMMENT '开始时间',
    end_time            DATETIME     DEFAULT NULL COMMENT '结束时间',
    duration_ms         INT          DEFAULT NULL COMMENT '耗时（毫秒）',
    error_message       TEXT         DEFAULT NULL COMMENT '错误信息',
    -- 日志路径
    log_path            VARCHAR(256) DEFAULT NULL COMMENT '日志文件路径：logs/{strategy_key}/{backtest_id}.log',
    created_at          DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_user (user_id),
    INDEX idx_strategy (strategy_id),
    INDEX idx_status (status),
    INDEX idx_created (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='回测任务表';

-- ============================================================
-- 7. backtest_nav — 回测净值曲线（按日）
-- ============================================================
CREATE TABLE backtest_nav (
    id                BIGINT AUTO_INCREMENT PRIMARY KEY,
    backtest_id       INT     NOT NULL COMMENT '回测任务ID',
    trade_date        DATE    NOT NULL COMMENT '交易日期',
    unit_net_value    DOUBLE  NOT NULL COMMENT '单位净值',
    daily_return      DOUBLE  DEFAULT NULL COMMENT '日收益率',
    cumulative_return DOUBLE DEFAULT NULL COMMENT '累计收益率',
    benchmark_nav     DOUBLE  DEFAULT NULL COMMENT '基准净值',
    excess_return     DOUBLE  DEFAULT NULL COMMENT '超额收益',
    UNIQUE KEY uk_bt_date (backtest_id, trade_date),
    INDEX idx_backtest (backtest_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='回测净值曲线';

-- ============================================================
-- 8. backtest_trade — 回测交易记录（每笔完整交易）
-- ============================================================
CREATE TABLE backtest_trade (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    backtest_id     INT          NOT NULL COMMENT '回测任务ID',
    ts_code         VARCHAR(16)  NOT NULL COMMENT '股票代码',
    symbol          VARCHAR(8)   DEFAULT NULL COMMENT '股票简称',
    buy_date        DATE         NOT NULL COMMENT '买入日期',
    sell_date       DATE         DEFAULT NULL COMMENT '卖出日期',
    buy_price       DOUBLE       NOT NULL COMMENT '买入价',
    sell_price      DOUBLE       DEFAULT NULL COMMENT '卖出价',
    quantity        INT          NOT NULL COMMENT '交易数量（股）',
    buy_amount      DOUBLE       NOT NULL COMMENT '买入金额',
    sell_amount     DOUBLE       DEFAULT NULL COMMENT '卖出金额',
    pnl             DOUBLE       DEFAULT NULL COMMENT '盈亏金额',
    pnl_pct         DOUBLE       DEFAULT NULL COMMENT '盈亏百分比',
    holding_days    INT          DEFAULT NULL COMMENT '持仓天数',
    sell_reason     VARCHAR(64)  DEFAULT NULL COMMENT '卖出原因：signal/stop_loss/stop_profit/end',
    INDEX idx_backtest (backtest_id),
    INDEX idx_bt_code (backtest_id, ts_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='回测交易记录';

-- ============================================================
-- 9. backtest_position — 回测持仓快照（按日）
-- ============================================================
CREATE TABLE backtest_position (
    id              BIGINT AUTO_INCREMENT PRIMARY KEY,
    backtest_id     INT          NOT NULL COMMENT '回测任务ID',
    trade_date      DATE         NOT NULL COMMENT '交易日期',
    ts_code         VARCHAR(16)  NOT NULL COMMENT '股票代码',
    symbol          VARCHAR(8)   DEFAULT NULL COMMENT '股票简称',
    quantity        INT          NOT NULL COMMENT '持仓数量',
    market_value    DOUBLE       NOT NULL COMMENT '市值',
    weight          DOUBLE       NOT NULL COMMENT '权重(%)',
    cost            DOUBLE       NOT NULL COMMENT '成本价',
    current_price   DOUBLE       NOT NULL COMMENT '当前价',
    pnl             DOUBLE       DEFAULT NULL COMMENT '浮动盈亏',
    pnl_pct         DOUBLE       DEFAULT NULL COMMENT '浮动盈亏百分比',
    INDEX idx_backtest (backtest_id),
    INDEX idx_bt_date (backtest_id, trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='回测持仓快照';

-- ============================================================
-- 10. backtest_daily_metrics — 回测日度指标
-- ============================================================
CREATE TABLE backtest_daily_metrics (
    id                BIGINT AUTO_INCREMENT PRIMARY KEY,
    backtest_id       INT     NOT NULL COMMENT '回测任务ID',
    trade_date        DATE    NOT NULL COMMENT '交易日期',
    daily_return      DOUBLE  DEFAULT NULL COMMENT '当日收益率',
    cumulative_return DOUBLE DEFAULT NULL COMMENT '累计收益率',
    drawdown          DOUBLE  DEFAULT NULL COMMENT '当日回撤(%)',
    portfolio_value   DOUBLE  DEFAULT NULL COMMENT '当日组合总值',
    cash              DOUBLE  DEFAULT NULL COMMENT '当日现金',
    leverage          DOUBLE  DEFAULT NULL COMMENT '当日杠杆',
    turnover          DOUBLE  DEFAULT NULL COMMENT '当日换手率',
    UNIQUE KEY uk_bt_date (backtest_id, trade_date),
    INDEX idx_backtest (backtest_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='回测日度指标';

-- ============================================================
-- 11. backtest_risk_metrics — 回测风险指标（1:1 backtest_job）
-- ============================================================
CREATE TABLE backtest_risk_metrics (
    id                  INT AUTO_INCREMENT PRIMARY KEY,
    backtest_id         INT     NOT NULL UNIQUE COMMENT '回测任务ID',
    max_drawdown        DOUBLE  DEFAULT NULL COMMENT '最大回撤(%)',
    max_drawdown_start  DATE    DEFAULT NULL COMMENT '最大回撤开始日',
    max_drawdown_end    DATE    DEFAULT NULL COMMENT '最大回撤结束日',
    max_drawdown_recovery DATE  DEFAULT NULL COMMENT '最大回撤恢复日',
    max_drawdown_days   INT     DEFAULT NULL COMMENT '最大回撤持续天数',
    annual_volatility   DOUBLE  DEFAULT NULL COMMENT '年化波动率',
    downside_volatility DOUBLE  DEFAULT NULL COMMENT '下行波动率',
    var_95              DOUBLE  DEFAULT NULL COMMENT '95% VaR（日）',
    cvar_95             DOUBLE  DEFAULT NULL COMMENT '95% CVaR（日）',
    calmar_ratio        DOUBLE  DEFAULT NULL COMMENT 'Calmar比率',
    information_ratio   DOUBLE  DEFAULT NULL COMMENT '信息比率',
    tracking_error      DOUBLE  DEFAULT NULL COMMENT '跟踪误差',
    avg_holding_days    DOUBLE  DEFAULT NULL COMMENT '平均持仓天数',
    max_consecutive_win INT     DEFAULT NULL COMMENT '最大连续盈利次数',
    max_consecutive_lose INT    DEFAULT NULL COMMENT '最大连续亏损次数',
    INDEX idx_backtest (backtest_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='回测风险指标';

-- ============================================================
-- 12. data_source — 数据源配置
-- ============================================================
CREATE TABLE data_source (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    name        VARCHAR(32)  NOT NULL UNIQUE COMMENT '数据源名称',
    display_name VARCHAR(64) NOT NULL COMMENT '显示名称',
    status      VARCHAR(16)  DEFAULT 'active' COMMENT 'active/disabled',
    config      JSON         DEFAULT NULL COMMENT '配置（token等）',
    priority    INT          DEFAULT 0 COMMENT '优先级',
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    updated_at  DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据源配置';

-- ============================================================
-- 13. data_sync_log — 数据同步日志
-- ============================================================
CREATE TABLE data_sync_log (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    source      VARCHAR(32)  NOT NULL COMMENT '数据源',
    data_type   VARCHAR(32)  NOT NULL COMMENT '数据类型',
    trade_date  DATE         DEFAULT NULL COMMENT '同步日期',
    status      VARCHAR(16)  DEFAULT 'pending' COMMENT 'pending/running/completed/failed',
    total_count INT          DEFAULT 0,
    success_count INT        DEFAULT 0,
    fail_count  INT          DEFAULT 0,
    error_msg   TEXT         DEFAULT NULL,
    started_at  DATETIME     DEFAULT NULL,
    finished_at DATETIME     DEFAULT NULL,
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_source (source),
    INDEX idx_date (trade_date),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='数据同步日志';

-- ============================================================
-- 14. factor_def — 因子定义
-- ============================================================
CREATE TABLE factor_def (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    factor_code VARCHAR(64)  NOT NULL UNIQUE COMMENT '因子编码',
    factor_name VARCHAR(128) NOT NULL COMMENT '因子名称',
    category    VARCHAR(32)  DEFAULT NULL COMMENT '分类',
    description TEXT         DEFAULT NULL,
    params      JSON         DEFAULT NULL,
    status      VARCHAR(16)  DEFAULT 'active',
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='因子定义';

-- ============================================================
-- 15. factor_value — 因子值
-- ============================================================
CREATE TABLE factor_value (
    id          BIGINT AUTO_INCREMENT PRIMARY KEY,
    factor_code VARCHAR(64)  NOT NULL COMMENT '因子编码',
    ts_code     VARCHAR(16)  NOT NULL COMMENT '股票代码',
    trade_date  DATE         NOT NULL COMMENT '交易日期',
    value       DOUBLE       DEFAULT NULL COMMENT '因子值',
    UNIQUE KEY uk_factor_code_date (factor_code, ts_code, trade_date),
    INDEX idx_code (ts_code),
    INDEX idx_date (trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='因子值';

-- ============================================================
-- 16. task_job — 任务队列
-- ============================================================
CREATE TABLE task_job (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    task_type   VARCHAR(32)  NOT NULL COMMENT '任务类型',
    status      VARCHAR(16)  DEFAULT 'pending' COMMENT 'pending/running/completed/failed/cancelled',
    params      JSON         DEFAULT NULL COMMENT '任务参数',
    priority    INT          DEFAULT 0,
    progress    DOUBLE       DEFAULT 0 COMMENT '进度 0-100',
    result      JSON         DEFAULT NULL COMMENT '执行结果',
    error_msg   TEXT         DEFAULT NULL,
    created_at  DATETIME     DEFAULT CURRENT_TIMESTAMP,
    started_at  DATETIME     DEFAULT NULL,
    finished_at DATETIME     DEFAULT NULL,
    INDEX idx_status (status),
    INDEX idx_type (task_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='任务队列表';

-- ============================================================
-- 17. task_step — 任务步骤
-- ============================================================
CREATE TABLE task_step (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    job_id      INT          NOT NULL COMMENT '任务ID',
    step_name   VARCHAR(128) NOT NULL COMMENT '步骤名称',
    status      VARCHAR(16)  DEFAULT 'pending',
    started_at  DATETIME     DEFAULT NULL,
    finished_at DATETIME     DEFAULT NULL,
    error_msg   TEXT         DEFAULT NULL,
    INDEX idx_job (job_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='任务步骤表';

-- ============================================================
-- 18. rqalpha_config — rqalpha 配置（系统级别）
-- ============================================================
CREATE TABLE rqalpha_config (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    config_key  VARCHAR(64)  NOT NULL UNIQUE COMMENT '配置键',
    config_value JSON        NOT NULL COMMENT '配置值',
    description VARCHAR(256) DEFAULT NULL,
    updated_at  DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COMMENT='rqalpha 系统配置';
-- 存储默认的 commission、slippage、matching_type 等
```

### 3.3 ER 关系图

```
users ──1:N── strategy ──1:N── strategy_version
  │                  │
  │                  └── 1:N ── backtest_job ── 1:N ── backtest_nav
  │                                               ├── 1:N ── backtest_trade
  │                                               ├── 1:N ── backtest_position
  │                                               ├── 1:N ── backtest_daily_metrics
  │                                               └── 1:1 ── backtest_risk_metrics
  │
stock_basic ── 1:N ── stock_daily
stock_basic ── 1:N ── factor_value
factor_def  ── 1:N ── factor_value

文件系统: logs/{strategy_key}/{backtest_id}.log
```

### 3.4 数据初始化

库 `qt_dev` 创建后需要初始化：

1. **stock_basic** — 通过 Tushare `stock_basic` 接口全量同步一次
2. **stock_daily** — 通过 Tushare `daily` 接口按年/月批量下载（建议 2010-01 至今）
3. **data_source** — 插入 Tushare / AKShare 默认配置行
4. **rqalpha_config** — 插入默认配置（commission=0.0003, slippage=0.01, matching_type=current_bar, frequency=1d, 等）
5. **users** — 初始管理员账号

---

## 四、API 接口设计

### 4.1 统一响应格式

```json
// 成功
{ "code": 0, "data": {...}, "message": "ok" }

// 失败
{ "code": 40001, "data": null, "message": "策略不存在" }

// 分页
{ "code": 0, "data": { "items": [...], "total": 128, "page": 1, "page_size": 20 } }
```

### 4.2 接口总览

```
认证 (Auth)
  POST   /api/auth/login
  POST   /api/auth/register
  GET    /api/auth/me
  POST   /api/auth/change-password

策略管理 (Strategies)
  GET    /api/strategies                        列表（分页+筛选）
  POST   /api/strategies                        创建
  GET    /api/strategies/:id                    详情
  PUT    /api/strategies/:id                    更新信息
  PATCH  /api/strategies/:id/status             修改状态
  DELETE /api/strategies/:id                    删除
  GET    /api/strategies/:id/versions           版本列表
  POST   /api/strategies/:id/versions           创建版本（保存代码）
  GET    /api/strategies/:id/versions/:version  版本详情（含源码）

回测中心 (Backtests) ★
  POST   /api/backtests                         创建并启动回测
  GET    /api/backtests                         列表（分页+筛选）
  GET    /api/backtests/:id                     详情（含摘要指标）
  POST   /api/backtests/:id/cancel              取消运行中的回测
  DELETE /api/backtests/:id                     删除及关联数据
  GET    /api/backtests/:id/nav                 净值曲线
  GET    /api/backtests/:id/trades              交易记录（分页）
  GET    /api/backtests/:id/positions           持仓快照
  GET    /api/backtests/:id/daily-metrics       日度指标
  GET    /api/backtests/:id/risk-metrics        风险指标
  GET    /api/backtests/:id/logs                回测日志
  GET    /api/backtests/:id/report              完整报告（聚合）
  WS     /ws/backtest/:id                       实时进度 / 日志流

数据中心 (Data)
  GET    /api/data/stocks                       股票列表
  GET    /api/data/stocks/:code                 股票详情
  GET    /api/data/stocks/:code/daily           日线数据
  GET    /api/data/sources                      数据源列表
  POST   /api/data/sync                         触发数据同步
  GET    /api/data/sync-logs                    同步日志
  GET    /api/data/overview                     数据概览

任务队列 (Tasks)
  GET    /api/tasks                             任务列表
  GET    /api/tasks/:id                         任务详情
  POST   /api/tasks/:id/cancel                  取消
  POST   /api/tasks/:id/retry                   重试

系统 (System)
  GET    /api/health                            健康检查
  GET    /api/system/info                       系统信息
```

### 4.3 详细接口规格（核心）

#### 策略管理

**POST /api/strategies**
```json
// Request
{ "name": "双均线趋势跟踪", "description": "...", "strategy_type": "stock",
  "default_config": { "initial_capital": 100000, "benchmark": "000300.XSHG" } }
// Response 201
{ "code": 0, "data": { "id": 1, "strategy_key": "double_ma", "status": "draft", ... } }
```

**POST /api/strategies/:id/versions**
```json
// Request
{ "source_code": "def init(context):\n    ...", "change_log": "初始版本" }
// Response 201
{ "code": 0, "data": { "version": 1, ... } }
```

**GET /api/strategies/:id/versions/:version**
```json
// Response 200
{ "code": 0, "data": { "version": 3, "source_code": "...", "change_log": "...", ... } }
```

#### 回测中心 ★

**POST /api/backtests**
```json
// Request
{ "strategy_id": 1, "version": 3,
  "config": { "start_date": "2024-01-01", "end_date": "2024-12-31",
              "initial_capital": 100000, "benchmark": "000300.XSHG",
              "frequency": "1d", "commission": 0.0003, "slippage": 0.01 } }
// Response 202
{ "code": 0, "data": { "id": 128, "status": "pending", "message": "回测已创建" } }
```

**GET /api/backtests/:id**
```json
// Response 200 — 返回摘要指标（字段同 backtest_job.summary 相关列）
{ "code": 0, "data": {
    "id": 128, "status": "completed", "total_return": 0.325, "sharpe_ratio": 1.85, ...
  } }
```

**GET /api/backtests/:id/nav**
```
Query: ?format=full|compact  (compact 时采样到 ~300 点)
// Response 200
{ "code": 0, "data": {
    "dates": ["2024-01-02", ...],
    "nav": [1.0, 1.002, ...],
    "benchmark_nav": [1.0, 0.998, ...],
    "excess_return": [0.0, 0.004, ...]
  } }
```

**GET /api/backtests/:id/trades**
```
Query: ?page=1&page_size=50&sort_by=buy_date&order=asc
// Response 200
{ "code": 0, "data": {
    "items": [
      { "ts_code": "000001.SZ", "buy_date": "2024-01-15", "sell_date": "2024-03-22",
        "buy_price": 12.50, "sell_price": 15.20, "quantity": 8000,
        "pnl": 21600, "pnl_pct": 0.216, "holding_days": 67, "sell_reason": "signal" }
    ],
    "total": 47, "page": 1, "page_size": 50,
    "summary": { "total_trades": 47, "win_trades": 28, "lose_trades": 19,
                 "avg_profit": 4520, "avg_loss": -2150 }
  } }
```

**GET /api/backtests/:id/logs**
```
Query: ?mode=full|tail&lines=100
// Response 200
{ "code": 0, "data": {
    "log_path": "logs/double_ma/128.log",
    "size_bytes": 8452,
    "lines": [ "2026-06-19 14:32:00.123 │ [INFO ] QT Backtest Engine Starting", ... ]
  } }
```

**POST /api/backtests/:id/cancel**
```json
// Response 200
{ "code": 0, "data": { "status": "cancelled", "message": "回测已取消" } }
```

#### WebSocket — 回测实时进度

```
Client → Server:  connect to /ws/backtest/:id

Server → Client events:

event: backtest_progress
data: { "backtest_id": 128, "progress": 67.5, "current_date": "2024-08-15",
        "completed_bars": 163, "total_bars": 242,
        "elapsed_seconds": 8.5, "estimated_remaining_seconds": 4.1,
        "current_return": 0.12 }

event: backtest_completed
data: { "backtest_id": 128, "total_return": 0.325, "sharpe_ratio": 1.85, ... }

event: backtest_failed
data: { "backtest_id": 128, "error": "KeyError: 'close' — 2024-01-01 无数据" }

event: log_line  (可选：回测日志实时推送)
data: { "line": "14:32:00.825 │ [INFO ] [2024-01-15] SIGNAL: 金叉买入" }
```

---

## 五、实施计划

### 5.1 Phase 划分

| Phase | 内容 | 预估 |
|--------|------|------|
| **Phase 0** | 创建 `qt_dev` 库，执行 DDL，从旧 `stock` 库迁移数据（stock_basic 全量 + stock_daily 近半年 + users），配置 `.env` | 0.5天 |
| **Phase 1** | 数据中心：Tushare/AKShare 双数据源配置，增量同步补全历史行情 | 1天 |
| **Phase 2** | 策略管理：CRUD API + Monaco Editor 前端 + 版本管理（strategy + strategy_version） | 2天 |
| **Phase 3** | 回测引擎：QtDataSource + BacktestEngine + rqalpha.run_func 集成 | 2天 |
| **Phase 4** | 回测 API：create / list / detail / nav / trades / positions / risk / logs / cancel | 1.5天 |
| **Phase 5** | 回测中心前端：列表 + 进度条 + 6个Tab（净值/交易/持仓/风险/收益/日志）| 2天 |
| **Phase 6** | WebSocket 实时推送 + 工作台仪表盘 | 1天 |
| **Phase 7** | 测试（单元 + 集成 + E2E） + Bug 修复 | 1.5天 |
| **合计** | | **~11.5天** |

### 5.2 文件清单

**新建文件（后端）：**
- `backend/app/services/backtest_engine.py` — rqalpha 封装
- `backend/app/services/backtest_datasource.py` — CustomDataSource
- `backend/app/services/strategy_service.py` — 重写
- `backend/app/services/backtest_service.py` — 重写
- `backend/app/api/strategies.py` — 重写
- `backend/app/api/backtests.py` — 重写
- `backend/app/api/data.py` — 新增
- `backend/app/api/system.py` — 新增
- `backend/app/repositories/strategy_repo.py` — 重写
- `backend/app/repositories/backtest_repo.py` — 重写
- `backend/app/repositories/stock_repo.py` — 改造
- `backend/app/repositories/stock_daily_repo.py` — 改造

**新建文件（前端）：**
- `frontend/src/views/StrategyResearch.vue`
- `frontend/src/views/BacktestCenter.vue`
- `frontend/src/views/WorkspaceView.vue` — 重写
- `frontend/src/components/CodeEditor.vue`
- `frontend/src/components/BacktestProgress.vue`
- `frontend/src/components/BacktestMetrics.vue`
- `frontend/src/components/NavChart.vue`
- `frontend/src/components/TradeTable.vue`
- `frontend/src/components/LogViewer.vue`
- `frontend/src/components/NewBacktestDialog.vue`
- `frontend/src/api/strategy.js`
- `frontend/src/api/backtest.js`
- `frontend/src/composables/useWebSocket.js`
- `frontend/src/store/modules/strategy.js`
- `frontend/src/store/modules/backtest.js`

**修改文件：**
- `backend/.env` — DB_NAME=qt_dev
- `backend/app/__init__.py` — 注册新 Blueprint
- `backend/app/core/config.py` — DB_NAME 默认值
- `frontend/src/router/index.js` — 新路由
- `frontend/src/layouts/MainLayout.vue` — 新菜单

---

## 六、验证方案

### 6.1 单元测试

```
backend/tests/
├── test_backtest_engine.py       # BacktestEngine: run / cancel / 结果提取
├── test_datasource.py            # QtDataSource: get_bar / history_bars / 日历
├── test_strategy_service.py      # CRUD / 版本管理 / 代码存储
├── test_backtest_service.py      # 回测生命周期 / 结果写入
└── test_api/
    ├── test_strategy_api.py      # 策略 API 端点
    └── test_backtest_api.py      # 回测 API 端点
```

**关键测试用例：**

| 模块 | 用例 | 预期 |
|------|------|------|
| QtDataSource | 加载 2024 年 A 股数据，验证交易日历数量 | ~242 天 |
| QtDataSource | `history_bars("000001.XSHE", 20, "1d", "close")` | 返回 numpy array shape=(20,) |
| BacktestEngine | 执行简单 buy_and_hold 策略，验证返回结果非空 | summary.total_return ≠ None |
| BacktestEngine | 取消运行中的回测 | status=cancelled，数据库更新 |
| BacktestEngine | 日志写入 `logs/{key}/{id}.log` | 文件存在且包含完整日志 |
| Strategy Service | 创建策略 → 创建 v1,v2,v3 → 查询最新版本 | latest_version=3 |
| Strategy API | POST /api/strategies 缺 name | 返回 400 |
| Backtest API | POST /api/backtests 缺 strategy_id | 返回 400 |
| Backtest API | 回测完成后 GET /api/backtests/:id/nav | 返回净值序列 |

### 6.2 E2E 测试场景（关键路径）

**场景 1：新建策略并回测（核心流程）**
1. 登录 → 进入策略研究页
2. 点击「新建策略」→ 输入名称/描述 → 创建成功
3. 策略列表中选中该策略 → 点击「编辑代码」
4. 在 Monaco Editor 中输入策略代码 → Ctrl+S 保存
5. 点击「回测」→ 弹窗自动关联当前策略
6. 配置日期/资金/基准 → 点击「开始回测」
7. 跳转到回测中心 → 看到进度条推进
8. 净值曲线实时增长 → 指标实时跳动
9. 切换到日志 Tab → 看到流式日志
10. 回测完成 → 指标定格 → 净值曲线完整
11. 切换到交易记录 Tab → 查看交易明细
12. 点击「导出报告」

**场景 2：取消回测**
1. 在回测中心对一个策略发起回测
2. 进度条推进到 50%
3. 点击「取消」按钮 → 回测标记为 cancelled
4. 回测列表显示该记录为「已取消」

**场景 3：策略版本管理**
1. 对策略 A 创建 v1 → 创建 v2 → 创建 v3
2. 查看版本历史 → 看到 3 个版本
3. 对 v3 发起回测 → 完成后对比 v1 的回测结果

### 6.3 验收标准

| # | 标准 | 验证方式 |
|---|------|----------|
| 1 | 用户可创建策略并编写 Python 代码 | E2E |
| 2 | 策略代码可保存为多版本，版本间可切换 | E2E |
| 3 | 回测使用 rqalpha 真实执行（非 mock） | 单元测试 + 日志验证 |
| 4 | 回测结果包含完整的 12 项绩效指标 | API 返回验证 |
| 5 | 净值曲线数据 ≥ 回测交易日数量 | API 返回验证 |
| 6 | 交易记录与 rqalpha 输出一致 | 单元测试 |
| 7 | 回测运行中实时推送进度 | WebSocket 验证 |
| 8 | 回测可被取消，资源正确释放 | 单元测试 |
| 9 | 回测日志写入 `logs/{strategy_key}/{backtest_id}.log` | 文件系统验证 |
| 10 | 前端 6 个 Tab 均可正常展示数据 | E2E |
| 11 | Monaco Editor 可正常编辑 Python 代码并保存 | E2E |
| 12 | 数据库 qt_dev 所有表结构符合 DDL 定义 | 数据库对比 |

---

## 七、关键补充设计

### 7.1 策略执行线程模型

回测不在 HTTP 请求线程中执行，而是通过 Worker 异步消费：

```
POST /api/backtests
  → backtest_service.create_backtest()
    → backtest_repo.create_job(status='pending')  // 写入 DB
    → task_repo.create_job(task_type='backtest', params={backtest_id})
    → 返回 202 { id: 128, status: 'pending' }

worker.py (后台进程，独立于 Flask)
  → 轮询 task_job WHERE status='pending'
  → 认领任务 (SELECT ... FOR UPDATE)
  → backtest_engine.run(backtest_id, config, source_code, strategy_key)
    → 进度回调 → socketio.emit() → 前端实时更新
    → 结果写入 DB
    → 更新 task_job.status='completed'
```

**并发控制**：通过 `task_job` 的 `FOR UPDATE` 行锁实现，同一 backtest 不会被重复执行。Worker 单进程顺序消费，避免 rqalpha 并发问题。

### 7.2 strategy_key 生成规则

`strategy_key` 是策略的英文标识符，用于日志目录、文件命名。生成规则：

```python
# 创建策略时，从名称自动生成 key：
# "双均线趋势跟踪" → "double_ma"（首次创建时人工指定或拼音转换）
# 后续可通过 PUT /api/strategies/:id 修改

# 推荐使用 pinyin 库自动转换：
import pypinyin
def generate_strategy_key(name: str) -> str:
    """从中文策略名生成英文 key"""
    pinyin_list = pypinyin.lazy_pinyin(name, style=pypinyin.NORMAL)
    return '_'.join(pinyin_list).lower()
    # "双均线趋势跟踪" → "shuang_jun_xian_qu_shi_gen_zong"
```

用户可在创建时手动覆盖。key 在 `strategy` 表中 UNIQUE 约束。

### 7.3 级联删除规则

| 操作 | 行为 |
|------|------|
| DELETE /api/backtests/:id | 删除 backtest_job + 级联删除 nav/trade/position/daily_metrics/risk_metrics + 删除日志文件 |
| DELETE /api/strategies/:id | 如果存在关联回测，禁止删除并返回错误；需先删除所有回测记录 |

在 Repository 层实现：

```python
# backtest_repo.py
def delete_backtest_full(backtest_id):
    """级联删除回测及其所有关联数据"""
    tables = ['backtest_nav', 'backtest_trade', 'backtest_position',
              'backtest_daily_metrics', 'backtest_risk_metrics']
    for t in tables:
        execute_delete(f"DELETE FROM {t} WHERE backtest_id = %s", backtest_id)
    # 删除日志文件
    job = get_job(backtest_id)
    if job.log_path:
        os.remove(job.log_path)
    execute_delete("DELETE FROM backtest_job WHERE id = %s", backtest_id)
```

### 7.4 错误码规范

| 错误码 | 含义 | HTTP 状态码 |
|--------|------|------------|
| 0 | 成功 | 200/201 |
| 40001 | 参数校验失败 | 400 |
| 40100 | 未认证 | 401 |
| 40300 | 无权限 | 403 |
| 40400 | 资源不存在 | 404 |
| 40900 | 资源冲突（如策略下有回测记录不可删除） | 409 |
| 50001 | 回测执行失败 | 500 |
| 50002 | 数据源不可用 | 500 |
| 50003 | rqalpha 引擎异常 | 500 |

### 7.5 Monaco Editor 集成

```json
// frontend/package.json 新增依赖
{
  "monaco-editor": "^0.45.0",
  "monaco-editor-webpack-plugin": "^7.1.0"
}
```

```javascript
// frontend/vue.config.js 新增
const MonacoWebpackPlugin = require('monaco-editor-webpack-plugin');
module.exports = {
  configureWebpack: {
    plugins: [
      new MonacoWebpackPlugin({ languages: ['python'] })
    ]
  }
};
```

```vue
<!-- frontend/src/components/CodeEditor.vue 关键逻辑 -->
<template>
  <div ref="editorContainer" class="monaco-editor-wrap"></div>
</template>
<script setup>
import * as monaco from 'monaco-editor';
import { ref, onMounted, watch } from 'vue';

const props = defineProps({ modelValue: String, readOnly: Boolean });
const emit = defineEmits(['update:modelValue', 'save']);
const editorContainer = ref(null);
let editor = null;

onMounted(() => {
  editor = monaco.editor.create(editorContainer.value, {
    value: props.modelValue,
    language: 'python',
    theme: 'vs-dark',
    readOnly: props.readOnly,
    minimap: { enabled: true },
    automaticLayout: true,
    fontSize: 13,
    lineNumbers: 'on',
  });
  editor.onDidChangeModelContent(() => {
    emit('update:modelValue', editor.getValue());
  });
  editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
    emit('save', editor.getValue());
  });
});

watch(() => props.modelValue, (val) => {
  if (editor && val !== editor.getValue()) editor.setValue(val);
});
</script>
```

### 7.6 .env 配置变更

```env
# backend/.env — 关键变更项
DB_NAME=qt_dev                    # ← 从 stock 改为 qt_dev
PASSWORD_HASH=bcrypt              # ← 从 MD5 升级为 bcrypt
RQALPHA_PATH=/Users/gxwang/QT/rqalpha  # ← 新增
LOG_DIR=logs                      # ← 新增：回测日志根目录
MAX_CONCURRENT_BACKTESTS=3        # ← 新增：并发回测上限
DATA_SOURCE=Tushare               # ← 默认数据源
```

### 7.7 前端组件通信

```
StrategyResearch.vue
  ├── StrategyCard.vue (左侧列表，v-for 渲染)
  │     @click → emit('select', strategy)
  ├── CodeEditor.vue (右侧，v-model 绑定源码)
  │     @save → store.dispatch('strategy/createVersion')
  │     @quick-backtest → emit('backtest', strategy)
  └── NewBacktestDialog.vue (弹窗)
        props: { strategy: Object }
        @start → store.dispatch('backtest/create')

BacktestCenter.vue
  ├── BacktestCard.vue (左侧列表)
  │     @click → emit('select', backtest)
  ├── BacktestProgress.vue (顶部进度条，运行中显示)
  │     props: { progress, currentDate, completedBars, totalBars }
  │     @cancel → emit('cancel')
  ├── BacktestMetrics.vue (12 个指标网格)
  │     props: { metrics: Object }
  ├── NavChart.vue (净值曲线)
  │     props: { navData, benchData, dates }
  ├── TradeTable.vue (交易记录)
  │     props: { trades, summary }
  ├── LogViewer.vue (日志查看器)
  │     props: { logPath, lines, isStreaming }
  └── (PositionChart / RiskChart / DistributionChart — 可合并到 Tab 渲染)
```

### 7.8 OpenSpec 规格（需创建）

按 CLAUDE.md 中的 OpenSpec 规范，需在 `openspec/changes/qt-platform-redesign/specs/` 下创建：

```
specs/
├── backtest-center/
│   └── spec.md        # 回测中心行为规范（Requirements + Scenarios）
└── strategy-management/
    └── spec.md        # 策略管理行为规范
```

---

## 八、已确认决策

| # | 问题 | 决策 |
|---|------|------|
| 1 | 策略代码安全性 | Phase 1 不做沙箱，Phase 2 引入 Docker 隔离 |
| 2 | 数据源 | Tushare + AKShare 双数据源，Tushare 为主 |
| 3 | 回测并发上限 | 3 个/用户，Worker 单进程串行消费 task_job |
| 4 | 历史数据迁移 | 从旧 `stock` 库迁移到 `qt_dev`：`stock_basic` 全量 + `stock_daily` 近半年行情 |
| 5 | 前端主题 | 浅色主题（Element Plus 默认，原型当前风格） |

---

## 九、数据迁移方案

### 9.1 源库 → 目标库

```
源：stock.stock_basic         →  qt_dev.stock_basic          (全量，~5300 条)
源：stock.stock_daily         →  qt_dev.stock_daily          (近 6 个月，约 60 万条)
    stock.users               →  qt_dev.users                (全量)
    stock.factor_def          →  qt_dev.factor_def           (结构复用)
    stock.factor_value        →  qt_dev.factor_value         (结构复用)
    stock.task_job            →  qt_dev.task_job             (结构复用)
    stock.task_step           →  qt_dev.task_step             (结构复用)
```

### 9.2 迁移脚本（伪代码）

```sql
-- 1. 全量迁移 stock_basic
INSERT INTO qt_dev.stock_basic SELECT * FROM stock.stock_basic;

-- 2. 迁移近 6 个月行情
INSERT INTO qt_dev.stock_daily
SELECT * FROM stock.stock_daily WHERE trade_date >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH);

-- 3. 迁移用户
INSERT INTO qt_dev.users SELECT * FROM stock.users;

-- 4. 创建新表（strategy / backtest_* / data_source / data_sync_log / rqalpha_config）
-- 使用文档第三部分的 DDL
```

---

## 十、开始编码
