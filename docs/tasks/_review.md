# Review: P1-T1

## 问题列表

### 1. [BUG] task_repo.py create_job: cursor 生命周期错误
**文件**: `backend/app/repositories/task_repo.py` 第27行
**问题**: `cursor.lastrowid` 在 `with conn.cursor()` 块外部访问，此时 cursor 已关闭，会抛异常。
**修复**: 在 `with` 块内部保存 `job_id = cursor.lastrowid`，然后在 `return job_id`。

### 2. [结构] task_repo.py 缺少 init_tables()
**文件**: `backend/app/repositories/task_repo.py`
**问题**: 任务文件要求 repo 提供 `init_tables()` 方法，但实际没有实现。导致 worker.py 只能自己内联建表SQL。
**修复**: 在 task_repo.py 中添加 `init_tables()` 函数（包含 task_job 和 task_step 的 CREATE TABLE），然后 worker.py 的 `_ensure_tables()` 改为调用 `task_repo.init_tables()`，消除 DDL 重复。

### 3. [BUG] worker.py 日期计算 month boundary bug
**文件**: `backend/worker.py` 第111行
**问题**: `today.replace(day=today.day - 1)` 在每月1号会抛出 `ValueError`（day=0 非法）。例如 6月1日 → day=0 出错。
**修复**: 使用 `from datetime import timedelta; yesterday = today - timedelta(days=1)`。

### 4. [样式] worker.py DDL 重复
**问题**: worker.py 的 `_ensure_tables()` 包含完整的 CREATE TABLE SQL，与 task_repo.py 应提供的函数重复。修复问题2后自动消除。

### 5. [日志] worker.py 缺少 setup_logger
**文件**: `backend/worker.py`
**问题**: worker.py 直接使用 `logging.basicConfig()` 而不是项目统一的 `app.core.logger.setup_logger()`，导致日志格式与其他进程不一致。
**修复**: 使用 `from app.core.logger import setup_logger` 并在 `__name__ == "__main__"` 中调用。

## 修改清单
- `backend/app/repositories/task_repo.py`: 修复 cursor 生命周期 + 添加 init_tables()
- `backend/worker.py`: 修复日期计算 + 消除 DDL 重复 + 改用统一日志配置

完成后自测：启动后端 + 启动 worker，确保两者都能正常启动。
