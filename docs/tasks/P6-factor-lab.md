# P6-T1: 因子实验室 — DB + 后端 + 前端

## 目标

创建因子定义和因子值缓存系统，提供因子覆盖率、IC 曲线、分层收益和相关性分析能力。

## 前提

其他阶段都已完成或至少数据质量系统可用。

## 参考文档

- 功能模块: `docs/quant-platform/modules.md` 第3节
- 数据库设计: `docs/quant-platform/database-draft.md` 第4节
- 原型: `prototype/quant-prototype-v2.html` 因子实验室页面（id="factor"）

## 数据表

### factor_def

```sql
CREATE TABLE IF NOT EXISTS factor_def (
    id INT AUTO_INCREMENT PRIMARY KEY,
    factor_code VARCHAR(30) NOT NULL,
    factor_name VARCHAR(50) NOT NULL,
    category VARCHAR(20) COMMENT '技术/价量/风险',
    description TEXT,
    params_json JSON COMMENT '计算参数',
    enabled TINYINT(1) DEFAULT 1,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uk_factor_code (factor_code)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### factor_value

```sql
CREATE TABLE IF NOT EXISTS factor_value (
    id INT AUTO_INCREMENT PRIMARY KEY,
    trade_date VARCHAR(8) NOT NULL,
    ts_code VARCHAR(20) NOT NULL,
    factor_code VARCHAR(30) NOT NULL,
    value DECIMAL(12,4) NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    UNIQUE KEY uk_date_code_factor (trade_date, ts_code, factor_code),
    INDEX idx_factor_date (factor_code, trade_date),
    INDEX idx_ts_date (ts_code, trade_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## 需要创建/修改的文件

### 1. backend/app/repositories/factor_repo.py

CRUD for factor_def and factor_value.

### 2. backend/app/services/factor_service.py

```python
class FactorService:
    def __init__(self, factor_repo, daily_repo):
        ...

    def get_factors(self, category=None) -> list[dict]: ...
    def register_factor(self, factor_code, factor_name, category, description, params) -> dict: ...

    def compute_factor(self, factor_code, trade_date):
        """计算指定因子在指定日期的值"""
        ...

    def get_coverage(self, factor_code, trade_date) -> dict:
        """因子覆盖率（覆盖股票数/应有股票数）"""
        ...

    def get_ic(self, factor_code, start_date, end_date) -> list[dict]:
        """
        IC 曲线数据。
        计算每个交易日因子值和次日收益的相关系数。
        """
        ...

    def get_group_return(self, factor_code, trade_date, groups=5) -> list[dict]:
        """
        分层收益数据。
        按因子值分 N 组，计算每组平均收益。
        """
        ...

    def compute_all_factors(self, trade_date):
        """批量计算当日所有已启用的因子"""
        ...
```

第一版因子列表：
- MA3, MA5, MA10, MA20（均线）
- MACD
- KDJ
- 成交量斜率
- 涨跌幅
- 波动率

第一版计算方式：按需计算，结果写入 factor_value 缓存。

### 3. backend/app/api/factors.py

```python
GET /api/factors?category=
    返回因子定义列表

POST /api/factors/analyze
    参数: {"factor_code", "start_date", "end_date", "groups"}
    返回: {ic_curve, group_return, coverage}

GET /api/factors/<code>/coverage?trade_date=
    返回覆盖率

GET /api/factors/<code>/ic?start_date=&end_date=
    返回 IC 曲线

GET /api/factors/<code>/group-return?trade_date=&groups=
    返回分层收益
```

### 4. 修改 backend/app/__init__.py

注册 factors 蓝图。

### 5. 重写 frontend/src/views/FactorLabView.vue

对应原型因子实验室页面。

包含：
- 因子分类侧边栏（技术类、价量类、风险类）
- 因子选择和时间范围过滤器
- IC 曲线 ECharts 图
- 分层收益柱状图
- 相关性热力图
- 因子覆盖率表格（因子名、覆盖股票数、覆盖率、IC均值、IR、多空年化、信息比率）
- "分析"按钮触发计算

## 自测步骤

1. `GET /api/factors` 返回因子定义
2. `POST /api/factors/analyze` 返回分析结果
3. 前端页面展示 IC 曲线和分层收益
4. 因子覆盖率表格显示数据
