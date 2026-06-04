# P3-T1: 策略参数化与信号解释 — DB + 后端

## 目标

将现有选股逻辑升级为参数化策略系统，包含策略配置、版本管理、运行记录和可解释信号。

## 前提

P1-T1 已完成（任务中心可用）。

## 参考文档

- 功能模块: `docs/quant-platform/modules.md` 第4节（策略工作台）和第6节（选股信号）
- 数据库设计: `docs/quant-platform/database-draft.md` 第5节（策略）和第6节（信号）
- 原型: `prototype/quant-prototype-v2.html` 策略页面（id="strategy"）和信号页面（id="signals"）

## 数据表

### strategy

```sql
CREATE TABLE IF NOT EXISTS strategy (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    strategy_type VARCHAR(30) NOT NULL COMMENT 'volume_breakout/ma_trend/macd_kdj_resonance/hk_trend/custom_combo',
    description TEXT,
    enabled TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### strategy_version

```sql
CREATE TABLE IF NOT EXISTS strategy_version (
    id INT AUTO_INCREMENT PRIMARY KEY,
    strategy_id INT NOT NULL,
    version VARCHAR(20) NOT NULL,
    params_json JSON COMMENT '策略参数',
    buy_rules_json JSON COMMENT '买入规则',
    sell_rules_json JSON COMMENT '卖出规则',
    remark TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_strategy_version (strategy_id, version)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### strategy_run

```sql
CREATE TABLE IF NOT EXISTS strategy_run (
    id INT AUTO_INCREMENT PRIMARY KEY,
    strategy_id INT NOT NULL,
    version_id INT NOT NULL,
    trade_date VARCHAR(8) NOT NULL,
    status VARCHAR(20) DEFAULT 'pending' COMMENT 'pending/running/success/failed',
    signal_count INT DEFAULT 0,
    task_job_id INT NULL,
    started_at DATETIME NULL,
    finished_at DATETIME NULL,
    message TEXT,
    INDEX idx_strategy_date (strategy_id, trade_date),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### signal

```sql
CREATE TABLE IF NOT EXISTS signal (
    id INT AUTO_INCREMENT PRIMARY KEY,
    trade_date VARCHAR(8) NOT NULL,
    ts_code VARCHAR(20) NOT NULL,
    name VARCHAR(50),
    market VARCHAR(10),
    strategy_id INT NOT NULL,
    strategy_version_id INT NOT NULL,
    strategy_run_id INT NOT NULL,
    score DECIMAL(6,2) DEFAULT 0 COMMENT '信号分',
    reason_text TEXT COMMENT '入选原因',
    factor_snapshot_json JSON COMMENT '因子快照',
    risk_snapshot_json JSON COMMENT '风险快照',
    data_quality_status VARCHAR(20) DEFAULT 'unknown',
    status VARCHAR(20) DEFAULT 'new' COMMENT 'new/watched/portfolio/ignored',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_trade_date (trade_date),
    INDEX idx_ts_code (ts_code),
    INDEX idx_strategy_date (strategy_id, trade_date),
    INDEX idx_score (score)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## 需要创建的文件

### 1. backend/app/repositories/strategy_repo.py

方法:
- `create_strategy(data) -> strategy_id`
- `get_strategy(strategy_id) -> dict`
- `get_strategies(enabled_only=False, page=1, page_size=20) -> paginated dict`
- `update_strategy(strategy_id, data)`
- `create_version(data) -> version_id`
- `get_versions(strategy_id) -> list[dict]`
- `get_latest_version(strategy_id) -> dict`
- `create_run(data) -> run_id`
- `get_runs(strategy_id, page=1, page_size=20) -> paginated dict`
- `update_run(run_id, data)`

### 2. backend/app/repositories/signal_repo.py

方法:
- `create_signals(signals: list[dict]) -> int` (批量插入，返回插入数)
- `get_signal(signal_id) -> dict`
- `get_signals(trade_date=None, strategy_id=None, market=None, min_score=0, page=1, page_size=20) -> paginated dict`
- `update_signal_status(signal_id, status)`

### 3. backend/app/services/strategy_service.py

策略服务，负责策略 CRUD 和策略运行调度。

```python
class StrategyService:
    def __init__(self, strategy_repo, signal_repo, task_service):
        ...

    def create_strategy(self, data) -> dict: ...
    def get_strategies(self, enabled_only=False, page=1, page_size=20) -> dict: ...
    def get_strategy_detail(self, strategy_id) -> dict: ...
    def update_strategy(self, strategy_id, data) -> dict: ...
    def create_version(self, strategy_id, data) -> dict: ...
    def get_versions(self, strategy_id) -> list[dict]: ...

    def run_strategy(self, strategy_id, version_id=None) -> dict:
        """
        提交策略运行任务。
        1. 获取策略最新版本
        2. 创建 strategy_run
        3. 通过 task_service.create_task 创建 run_strategy 任务
        4. 返回任务信息
        """
        ...

    def execute_run(self, run_id):
        """
        实际执行策略运行（由 Worker 调用）。
        1. 获取 strategy_run 和 params
        2. 根据 strategy_type 分发到对应分析逻辑
        3. 生成 signal 列表
        4. 批量写入 signal 表
        5. 更新 strategy_run 状态和 signal_count
        """
        ...

    def get_runs(self, strategy_id, page=1, page_size=20) -> dict: ...
```

### 4. backend/app/services/signal_service.py

信号服务。

```python
class SignalService:
    def __init__(self, signal_repo):
        ...

    def get_signals(self, trade_date=None, strategy_id=None, market=None, min_score=0, page=1, page_size=20) -> dict: ...
    def get_signal_detail(self, signal_id) -> dict: ...
    def update_status(self, signal_id, status) -> dict: ...

    def generate_signals(self, strategy_run, candidates: list[dict]) -> list[dict]:
        """
        生成信号列表。
        每个候选股票包含:
        - ts_code, name, market
        - score (信号分)
        - reason_text (入选原因)
        - factor_snapshot (因子快照)
        - risk_snapshot (风险快照)
        """
        ...
```

### 5. backend/app/api/strategies.py

```python
GET /api/strategies?enabled_only=&page=&page_size=
GET /api/strategies/<id>
POST /api/strategies
    参数: {"name", "strategy_type", "description"}
PUT /api/strategies/<id>
POST /api/strategies/<id>/versions
    参数: {"version", "params", "buy_rules", "sell_rules", "remark"}
POST /api/strategies/<id>/run
    参数: {"version_id"} (可选，默认最新版)
GET /api/strategies/<id>/runs?page=&page_size=
```

### 6. backend/app/api/signals.py

```python
GET /api/signals?trade_date=&strategy_id=&market=&min_score=&page=&page_size=
GET /api/signals/<id>
POST /api/signals/<id>/status
    参数: {"status": "watched|portfolio|ignored"}
```

### 7. 修改 backend/app/__init__.py

注册 strategies 和 signals 蓝图。

### 8. 修改 backend/worker.py

在 `execute_task` 中添加 `run_strategy` 的处理：调用 `StrategyService.execute_run()`。

## 现有代码参考

现有选股逻辑（`app/services/select_service.py`、`app/analysis/` 目录下的分析函数）应被复用：

- `app/analysis/volume_analysis.py` — 放量分析
- `app/analysis/ma_analysis.py` — 均线分析
- `app/analysis/indicators.py` — MACD/KDJ 指标
- `app/services/select_service.py` — 选股服务

策略运行在第一个版本中可以直接调用这些现有的分析函数，不要求立即重写。

## 自测步骤

1. 启动后端，检查新表是否创建成功
2. `POST /api/strategies` 创建策略
3. `POST /api/strategies/{id}/versions` 创建版本
4. `POST /api/strategies/{id}/run` 提交运行任务
5. Worker 执行策略并生成信号
6. `GET /api/signals` 查看信号
7. `GET /api/signals/{id}` 查看信号详情
