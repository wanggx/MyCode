# P2-T1: 数据健康中心 — DB + 后端

## 目标

创建数据质量诊断与修复闭环的数据库表、服务和 API。能检查数据完整性、发现缺口、生成 issue，以及执行修复。

## 前提

P1-T1 已完成（任务中心 Worker 可用）。

## 参考文档

- 数据健康方案: `docs/quant-platform/data-health.md`
- 数据库设计: `docs/quant-platform/database-draft.md` 第2节
- 功能模块: `docs/quant-platform/modules.md` 第2节

## 数据表

### data_quality_issue

```sql
CREATE TABLE IF NOT EXISTS data_quality_issue (
    id INT AUTO_INCREMENT PRIMARY KEY,
    issue_code VARCHAR(50) NOT NULL COMMENT 'issue编号 DQ-YYYYMMDD-NNN',
    market VARCHAR(10) NOT NULL COMMENT 'A股/港股',
    data_type VARCHAR(20) NOT NULL COMMENT 'daily/weekly/monthly',
    start_date VARCHAR(8) NOT NULL,
    end_date VARCHAR(8) NOT NULL,
    expected_count INT DEFAULT 0,
    actual_count INT DEFAULT 0,
    missing_count INT DEFAULT 0,
    severity VARCHAR(10) DEFAULT 'medium' COMMENT 'low/medium/high',
    status VARCHAR(20) DEFAULT 'open' COMMENT 'open/repairing/resolved/ignored/failed',
    impact_summary_json JSON COMMENT '影响范围摘要',
    discovered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    resolved_at DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_issue_code (issue_code),
    INDEX idx_market_date (market, data_type, start_date, end_date),
    INDEX idx_status (status)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

severity 规则:
- low: missing_count <= 5
- medium: missing_count > 5 或影响至少一个启用策略
- high: 整个市场某日缺失或影响信号生成

### data_quality_issue_detail

```sql
CREATE TABLE IF NOT EXISTS data_quality_issue_detail (
    id INT AUTO_INCREMENT PRIMARY KEY,
    issue_id INT NOT NULL,
    trade_date VARCHAR(8) NOT NULL,
    ts_code VARCHAR(20) NOT NULL,
    issue_type VARCHAR(30) NOT NULL COMMENT 'missing_daily/invalid_ohlc/missing_week/missing_month',
    message TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_issue_id (issue_id),
    INDEX idx_trade_date (trade_date),
    INDEX idx_ts_code (ts_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### data_repair_job

```sql
CREATE TABLE IF NOT EXISTS data_repair_job (
    id INT AUTO_INCREMENT PRIMARY KEY,
    issue_id INT NOT NULL,
    task_job_id INT NULL COMMENT '关联任务中心的task_job',
    repair_mode VARCHAR(30) NOT NULL COMMENT 'repair_missing_only/reload_date/ignore',
    status VARCHAR(20) DEFAULT 'pending' COMMENT 'pending/running/success/failed',
    options_json JSON COMMENT '用户修复选项',
    before_snapshot_json JSON COMMENT '修复前快照',
    after_snapshot_json JSON COMMENT '修复后快照',
    report_json JSON COMMENT '修复报告',
    started_at DATETIME NULL,
    finished_at DATETIME NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_issue_id (issue_id),
    INDEX idx_task_job_id (task_job_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## 需要创建的文件

### 1. backend/app/repositories/data_quality_repo.py

方法:
- `create_issue(data) -> issue_id`
- `get_issue(issue_id) -> dict`
- `get_issues(market=None, severity=None, status=None, page=1, page_size=20) -> paginated dict`
- `update_issue(issue_id, data)`
- `get_issue_details(issue_id) -> list[dict]`
- `add_issue_details(issue_id, details: list[dict])`
- `get_quality_summary() -> dict` (统计各市场/各状态的 issue 数量)
- `create_repair_job(data) -> repair_job_id`
- `get_repair_job(repair_job_id) -> dict`
- `update_repair_job(repair_job_id, data)`

### 2. backend/app/services/data_quality_service.py

核心检查逻辑。

```python
class DataQualityService:
    def __init__(self, quality_repo, stock_repo, daily_repo, task_service):
        ...

    def scan_daily_completeness(self, market, trade_date) -> int:
        """
        检查某个交易日的数据完整率。
        1. 查询 stock_basic 获取该市场应有股票数
        2. 查询 stock_daily/hk_stock_daily 获取实际记录数
        3. 如果缺失 > 0，创建 data_quality_issue + details
        4. 返回创建的 issue_id (0=无问题)
        """
        ...

    def scan_ohlc_validity(self, market, trade_date) -> int:
        """
        检查 OHLC 异常：
        - open/high/low/close 为空或 0
        - high < low
        """
        ...

    def get_issue_detail(self, issue_id) -> dict:
        """获取 issue 详情（含明细列表）"""
        ...

    def get_impact(self, issue_id) -> dict:
        """
        评估影响范围：
        - 影响哪些因子
        - 影响哪些策略
        - 影响信号生成
        - 影响组合更新
        第一版使用静态规则映射。
        """
        ...

    def get_quality_summary(self) -> dict:
        """
        质量总览摘要：
        - 今日完整率
        - 缺口问题数
        - 异常问题数
        - 最近修复结果
        """
        ...

    def scan_date_range(self, market, start_date, end_date) -> list[dict]:
        """
        扫描日期范围内的所有问题，返回创建的 issue 列表。
        遍历每个交易日，分别检查完整性和 OHLC 有效性。
        """
        ...
```

### 3. backend/app/services/data_repair_service.py

修复逻辑。

```python
class DataRepairService:
    def __init__(self, quality_repo, daily_repo, task_service, data_provider):
        ...

    def create_repair(self, issue_id, repair_mode, options) -> dict:
        """
        创建修复任务（包含创建 task_job 和 data_repair_job）。
        """
        ...

    def execute_repair(self, repair_job_id):
        """
        执行修复（由 Worker 调用）。
        1. 从 issue 加载缺失清单
        2. 调用数据源补录
        3. 合并到正式表
        4. 重聚合周线/月线
        5. 自动复检
        6. 生成修复报告
        """
        ...

    def auto_recheck(self, issue_id) -> bool:
        """修复后复检同一范围，返回是否全部修复"""
        ...
```

### 4. backend/app/api/data_quality.py

API 路由。

```python
GET /api/data/quality-summary
    返回质量总览

GET /api/data/issues?market=&severity=&status=&page=&page_size=
    返回 issue 列表

GET /api/data/issues/<id>
    返回 issue 详情 + details + 影响范围

POST /api/data/issues/<id>/repair
    创建修复任务
    参数: {"repair_mode": "repair_missing_only", "options": {...}}

POST /api/data/quality-scan
    手动触发扫描
    参数: {"market": "A股", "start_date": "20260601", "end_date": "20260604"}
```

### 5. 修改 backend/app/__init__.py

注册 data_quality 蓝图。

### 6. 修改 backend/worker.py

在 `execute_task` 中添加对 `quality_scan` 和 `repair_missing_data` 的处理。

## 与现有代码的衔接

现有数据服务（`app/services/data_service.py`）中有 `download_daily_data` 方法，修复服务应复用它。

现有 `app/repositories/stock_daily_repo.py` 和 `app/repositories/stock_repo.py` 可用于查询股票基础信息和日线数据。

## 自测步骤

1. 启动后端，检查新表是否创建成功
2. `POST /api/data/quality-scan` 触发扫描某日数据
3. `GET /api/data/issues` 查看创建的 issue
4. `GET /api/data/issues/{id}` 查看 issue 详情
5. `POST /api/data/issues/{id}/repair` 创建修复任务
6. Worker 能执行修复任务并更新状态
7. `GET /api/data/quality-summary` 返回摘要
