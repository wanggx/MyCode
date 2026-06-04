# P1-T1: 任务中心 — DB + 后端

## 目标

创建任务中心的数据库表、后端服务和 API，以及 Worker 进程。这是所有后台任务的基础设施。

## 参考文档

- 数据库设计: `docs/quant-platform/database-draft.md` 第3节
- 功能模块: `docs/quant-platform/modules.md` 第8节
- 架构方案: `docs/quant-platform/architecture.md` 进程模型和API设计原则
- 原型: `prototype/quant-prototype-v2.html` 任务中心页面（id="tasks"）

## 数据表

### task_job

```sql
CREATE TABLE IF NOT EXISTS task_job (
    id INT AUTO_INCREMENT PRIMARY KEY,
    task_type VARCHAR(50) NOT NULL COMMENT '任务类型',
    status VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT 'pending/running/success/failed/canceled',
    priority INT NOT NULL DEFAULT 0 COMMENT '优先级（越大越优先）',
    params_json JSON COMMENT '任务参数JSON',
    progress INT DEFAULT 0 COMMENT '进度0-100',
    message TEXT COMMENT '状态消息/错误信息',
    created_by VARCHAR(50) DEFAULT 'system' COMMENT '创建者',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    started_at DATETIME NULL,
    finished_at DATETIME NULL,
    INDEX idx_status_priority (status, priority, created_at),
    INDEX idx_task_type (task_type)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

task_type 枚举值:
- `sync_daily_data` — 同步日线数据
- `repair_missing_data` — 补录缺失数据
- `aggregate_week_month` — 聚合周线/月线
- `quality_scan` — 数据质量扫描
- `run_strategy` — 运行策略
- `run_backtest` — 运行回测
- `update_portfolio` — 更新模拟组合

### task_step

```sql
CREATE TABLE IF NOT EXISTS task_step (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL COMMENT '关联任务ID',
    step_order INT NOT NULL COMMENT '步骤序号',
    step_name VARCHAR(100) NOT NULL COMMENT '步骤名',
    status VARCHAR(20) DEFAULT 'pending' COMMENT 'pending/running/success/failed',
    message TEXT COMMENT '步骤消息',
    started_at DATETIME NULL,
    finished_at DATETIME NULL,
    INDEX idx_job_id (job_id, step_order)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

## 需要创建的文件

### 1. backend/app/repositories/task_repo.py

数据访问层，实现 task_job 和 task_step 的 CRUD。

方法:
- `create_job(task_type, priority, params_json, created_by) -> job_id`
- `get_job(job_id) -> dict`
- `get_jobs(status=None, task_type=None, page=1, page_size=20) -> paginated dict`
- `update_job_status(job_id, status, message=None, progress=None)`
- `claim_pending_job() -> dict|None` (原子性地将一条 pending 任务设为 running)
- `create_step(job_id, step_order, step_name) -> step_id`
- `update_step_status(step_id, status, message=None)`
- `get_steps(job_id) -> list[dict]`

### 2. backend/app/services/task_service.py

业务逻辑层，封装任务操作。

方法:
- `create_task(task_type, priority=0, params=None, created_by='system') -> dict`
- `get_task(job_id) -> dict`
- `get_tasks(status=None, task_type=None, page=1, page_size=20) -> dict`
- `retry_task(job_id) -> dict` (创建新任务，复制原参数)
- `cancel_task(job_id) -> bool`
- `get_task_steps(job_id) -> list[dict]`

### 3. backend/app/api/tasks.py

API 路由层。

接口：

```python
GET /api/tasks?status=&task_type=&page=&page_size=
    返回: {"success":true, "data": {items, total, page, page_size, total_pages}}

GET /api/tasks/<id>
    返回: {"success":true, "data": {任务详情 + steps 列表}}

POST /api/tasks/<id>/retry
    返回: {"success":true, "data": {新任务}}

POST /api/tasks/<id>/cancel
    返回: {"success":true, "data": {任务}}
```

使用 `from app.core.response import success, error` 统一响应格式。

### 4. backend/worker.py

独立进程，扫描 pending 任务并执行。

```python
"""
Worker 进程入口
用法: python backend/worker.py
"""
```

核心逻辑：

```python
import time
from app.services.task_service import TaskService
from app.repositories.task_repo import TaskRepo

task_repo = TaskRepo()
task_service = TaskService(task_repo)

def execute_task(job):
    """根据 task_type 分发执行"""
    pass  # 后续各阶段逐步填充

def main_loop():
    """每隔 5 秒扫描一次 pending 任务"""
    while True:
        job = task_repo.claim_pending_job()
        if job:
            execute_task(job)
        time.sleep(5)

if __name__ == '__main__':
    main_loop()
```

Worker 目前只需支持 `sync_daily_data` 的桩实现（调用现有 `download_daily_data`），其他任务类型后续填充。

Worker 中执行任务时必须：
1. 创建步骤日志
2. 捕获异常写入 job.message
3. 更新 job 状态为 success/failed

### 5. 修改 backend/app/__init__.py

注册 tasks 蓝图：

```python
from app.api.tasks import tasks_bp
app.register_blueprint(tasks_bp)
```

### 6. 修改 backend/run.py

不需要修改（Worker 独立启动）。

## 现有代码参考

现有响应格式（`app/core/response.py`）：
- `success(data=None, message="success")` — 返回成功响应
- `error(message, status_code=400)` — 返回错误响应

现有分页工具（`app/repositories/base.py`）：
- `paginate_sql(base_sql, count_sql, params, page, page_size, cursor)` — 执行分页查询

数据库连接（`app/core/database.py`）：
- `get_db_connection()` — 获取 pymysql 连接

## 自测步骤

1. 启动后端：`cd backend && .venv\Scripts\python run.py`（确保不报错）
2. 验证数据库表创建成功（连接 MySQL 检查 task_job 和 task_step 表是否存在）
3. 创建任务：`POST /api/tasks` 手动测试（用 curl 或 Postman）
4. Worker 能否正常启动：`cd backend && .venv\Scripts\python worker.py`
5. Worker 能扫描到 pending 任务并更新状态
