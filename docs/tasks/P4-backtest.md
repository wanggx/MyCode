# P4-T1: 回测中心 — DB + 后端 + 前端

## 目标

创建日频回测系统，支持提交回测任务、查看净值曲线、风险指标、持仓和交易明细。

## 前提

P1-T1 已完成（任务中心和 Worker 可用），P3-T1 已完成（策略系统可用）。

## 参考文档

- 功能模块: `docs/quant-platform/modules.md` 第5节
- 数据库设计: `docs/quant-platform/database-draft.md` 第7节
- 原型: `prototype/quant-prototype-v2.html` 回测页面（id="backtest"）

## 数据表

### backtest_job

```sql
CREATE TABLE IF NOT EXISTS backtest_job (
    id INT AUTO_INCREMENT PRIMARY KEY,
    strategy_id INT NOT NULL,
    version_id INT NOT NULL,
    task_job_id INT NULL,
    start_date VARCHAR(8) NOT NULL,
    end_date VARCHAR(8) NOT NULL,
    benchmark VARCHAR(10) DEFAULT '000300.SH',
    status VARCHAR(20) DEFAULT 'pending' COMMENT 'pending/running/success/failed',
    params_json JSON COMMENT '回测参数(手续费/滑点/最大持仓等)',
    metrics_json JSON COMMENT '风险指标(年化收益/夏普/最大回撤等)',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME NULL,
    finished_at DATETIME NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### backtest_nav

```sql
CREATE TABLE IF NOT EXISTS backtest_nav (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    trade_date VARCHAR(8) NOT NULL,
    nav DECIMAL(12,4) NOT NULL,
    benchmark_nav DECIMAL(12,4) DEFAULT NULL,
    drawdown DECIMAL(8,4) DEFAULT 0,
    UNIQUE KEY uk_job_date (job_id, trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### backtest_position

```sql
CREATE TABLE IF NOT EXISTS backtest_position (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    trade_date VARCHAR(8) NOT NULL,
    ts_code VARCHAR(20) NOT NULL,
    weight DECIMAL(8,4) DEFAULT 0,
    market_value DECIMAL(16,2) DEFAULT 0,
    close_price DECIMAL(12,4) DEFAULT 0,
    INDEX idx_job_date (job_id, trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### backtest_trade

```sql
CREATE TABLE IF NOT EXISTS backtest_trade (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    trade_date VARCHAR(8) NOT NULL,
    ts_code VARCHAR(20) NOT NULL,
    side VARCHAR(4) NOT NULL COMMENT 'buy/sell',
    price DECIMAL(12,4) NOT NULL,
    quantity INT NOT NULL,
    amount DECIMAL(16,2) NOT NULL,
    fee DECIMAL(10,4) DEFAULT 0,
    reason VARCHAR(200) COMMENT '交易原因'
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## 需要创建的/修改的文件

### 1. backend/app/repositories/backtest_repo.py

CRUD for backtest_job, backtest_nav, backtest_position, backtest_trade.

### 2. backend/app/services/backtest_service.py

```python
class BacktestService:
    def __init__(self, backtest_repo, strategy_repo, daily_repo, task_service):
        ...

    def create_backtest(self, strategy_id, version_id, start_date, end_date, params) -> dict:
        """创建回测任务（包含 task_job）"""
        ...

    def execute_backtest(self, backtest_job_id):
        """
        执行日频回测：
        1. 加载策略参数和信号
        2. 遍历每日：
           - 获取当日信号
           - 按规则调仓
           - 记录持仓和交易
           - 计算净值
        3. 计算风险指标
        4. 保存 nav/position/trade/metrics
        """
        ...

    def get_nav(self, backtest_job_id) -> list[dict]: ...
    def get_positions(self, backtest_job_id) -> list[dict]: ...
    def get_trades(self, backtest_job_id) -> list[dict]: ...
```

第一版回测规则：
- 日频，收盘后调仓
- 等权或按信号分加权
- 固定手续费（默认 0.03%）
- 固定滑点（默认 0.02%）
- 最大持仓数（默认 20）
- 单票权重上限（默认 10%）
- 简单止损（回撤超 8% 卖出）
- 基准对比沪深300

资源限制：
- 默认回测 3 年
- 最大回测 8 年
- 一次只运行一个回测

### 3. backend/app/api/backtests.py

```python
POST /api/backtests
    参数: {"strategy_id", "version_id", "start_date", "end_date", "params"}
    返回: {"success":true, "data": {backtest_job}}

GET /api/backtests?page=&page_size=
    返回: {"success":true, "data": {回测任务列表}}

GET /api/backtests/<id>
    返回: {"success":true, "data": {回测详情+风险指标}}

GET /api/backtests/<id>/nav
    返回: {"success":true, "data": {净值列表}}

GET /api/backtests/<id>/positions?trade_date=
    返回: {"success":true, "data": {持仓列表}}

GET /api/backtests/<id>/trades?page=&page_size=
    返回: {"success":true, "data": {交易明细}}
```

### 4. 修改 backend/app/__init__.py

注册 backtests 蓝图。

### 5. 修改 backend/worker.py

添加 `run_backtest` 处理。

### 6. 重写 frontend/src/views/BacktestCenterView.vue

对应原型回测中心页面。

包含：
- Tab 切换（回测任务 / 回测报告库）
- 过滤器（日期范围、股票池、状态）
- 回测任务表格（策略名、区间、状态、年化收益、夏普、最大回撤、操作）
- 新建回测按钮弹出对话框
- 净值曲线 ECharts 图
- 风险指标卡片（年化收益、年化波动、夏普、卡玛比率、胜率、最大回撤）

## 自测步骤

1. `POST /api/backtests` 创建回测
2. Worker 执行回测
3. `GET /api/backtests/{id}/nav` 返回净值数据
4. 前端展示净值曲线和风险指标
