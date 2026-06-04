# P5-T1: 组合风控 — DB + 后端 + 前端

## 目标

创建观察池和模拟组合功能，跟踪信号表现和组合风险。

## 前提

P3-T1 已完成（信号系统可用）。

## 参考文档

- 功能模块: `docs/quant-platform/modules.md` 第7节
- 数据库设计: `docs/quant-platform/database-draft.md` 第8节
- 原型: `prototype/quant-prototype-v2.html` 组合风控页面（id="portfolio"）

## 数据表

### watchlist

```sql
CREATE TABLE IF NOT EXISTS watchlist (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ts_code VARCHAR(20) NOT NULL,
    name VARCHAR(50),
    market VARCHAR(10),
    source_signal_id INT NULL,
    note TEXT,
    status VARCHAR(20) DEFAULT 'active' COMMENT 'active/removed',
    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    removed_at DATETIME NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### portfolio

```sql
CREATE TABLE IF NOT EXISTS portfolio (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    type VARCHAR(20) DEFAULT 'simulation' COMMENT 'simulation/watch/custom',
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### portfolio_position

```sql
CREATE TABLE IF NOT EXISTS portfolio_position (
    id INT AUTO_INCREMENT PRIMARY KEY,
    portfolio_id INT NOT NULL,
    trade_date VARCHAR(8) NOT NULL,
    ts_code VARCHAR(20) NOT NULL,
    weight DECIMAL(8,4) DEFAULT 0,
    quantity INT DEFAULT 0,
    cost_price DECIMAL(12,4) DEFAULT 0,
    close_price DECIMAL(12,4) DEFAULT 0,
    market_value DECIMAL(16,2) DEFAULT 0,
    INDEX idx_portfolio_date (portfolio_id, trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### portfolio_nav

```sql
CREATE TABLE IF NOT EXISTS portfolio_nav (
    id INT AUTO_INCREMENT PRIMARY KEY,
    portfolio_id INT NOT NULL,
    trade_date VARCHAR(8) NOT NULL,
    nav DECIMAL(12,4) NOT NULL,
    daily_return DECIMAL(8,4) DEFAULT 0,
    drawdown DECIMAL(8,4) DEFAULT 0,
    INDEX idx_portfolio_date (portfolio_id, trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## 需要创建/修改的文件

### 1. backend/app/repositories/portfolio_repo.py

CRUD for watchlist, portfolio, portfolio_position, portfolio_nav.

### 2. backend/app/services/portfolio_service.py

```python
class PortfolioService:
    def __init__(self, repo, daily_repo, signal_repo, task_service):
        ...

    def get_portfolios(self) -> list[dict]: ...
    def get_portfolio_risk(self, portfolio_id) -> dict:
        """计算风险指标（最大回撤、行业集中度、单票权重等）"""
        ...

    def get_portfolio_nav(self, portfolio_id) -> list[dict]: ...
    def get_portfolio_positions(self, portfolio_id) -> list[dict]: ...
    def add_to_portfolio(self, signal_id, portfolio_id) -> dict: ...

    def update_portfolio_nav(self, portfolio_id):
        """每日用收盘价更新净值"""
        ...
```

### 3. backend/app/services/watchlist_service.py

```python
class WatchlistService:
    def __init__(self, repo, signal_repo):
        ...

    def get_watchlist(self) -> list[dict]: ...
    def add_to_watchlist(self, ts_code, name, market, source_signal_id, note) -> dict: ...
    def remove_from_watchlist(self, watchlist_id) -> dict: ...
```

### 4. backend/app/api/portfolio.py

```python
GET /api/portfolio
    返回组合列表

GET /api/portfolio/<id>/nav
    返回净值数据

GET /api/portfolio/<id>/positions
    返回持仓数据

GET /api/portfolio/<id>/risk
    返回风险指标
```

### 5. backend/app/api/watchlist.py

```python
GET /api/watchlist
POST /api/watchlist
    参数: {ts_code, name, market, source_signal_id, note}
DELETE /api/watchlist/<id>
```

### 6. 重写 frontend/src/views/PortfolioRiskView.vue

对应原型组合风控页面。

包含：
- Tab 切换（模拟组合A / 观察池 / 自定义组合）
- 组合净值曲线 ECharts 图
- 持仓明细表格
- 风险预警卡片（行业集中、单股过重、选股质量）
- 行业分布环形图

### 7. 修改 backend/worker.py

添加 `update_portfolio` 任务处理。

## 自测步骤

1. `POST /api/watchlist` 添加股票到观察池
2. `GET /api/watchlist` 返回观察池列表
3. 组合相关 API 正常工作
4. 前端页面展示组合数据和风险指标
