# -*- coding: utf-8 -*-
"""
任务业务逻辑层
"""

import json
import logging

from app.repositories import task_repo

logger = logging.getLogger("myapp")


def _serialize_job(job):
    """将数据库行转换为可序列化字典"""
    if not job:
        return None
    result = dict(job)
    if result.get("params_json") and isinstance(result["params_json"], str):
        try:
            result["params_json"] = json.loads(result["params_json"])
        except (json.JSONDecodeError, TypeError):
            pass
    for key in ("created_at", "started_at", "finished_at"):
        if result.get(key) and hasattr(result[key], "isoformat"):
            result[key] = result[key].isoformat()
    return result


def create_task(task_type, priority=0, params=None, created_by="system"):
    """创建任务"""
    job_id = task_repo.create_job(task_type, priority, params, created_by)
    if job_id is None:
        return None
    job = task_repo.get_job(job_id)
    return _serialize_job(job)


def get_task(job_id):
    """获取任务详情"""
    job = task_repo.get_job(job_id)
    if not job:
        return None
    result = _serialize_job(job)
    steps = task_repo.get_steps(job_id)
    result["steps"] = [dict(s) for s in steps]
    for step in result["steps"]:
        for key in ("started_at", "finished_at"):
            if step.get(key) and hasattr(step[key], "isoformat"):
                step[key] = step[key].isoformat()
    return result


def get_tasks(status=None, task_type=None, page=1, page_size=20):
    """分页查询任务"""
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 20
    result = task_repo.get_jobs(status, task_type, page, page_size)
    if result is None:
        return None
    result["items"] = [_serialize_job(item) for item in result.get("items", [])]
    return result


def retry_task(job_id):
    """重试任务：基于原任务创建新任务"""
    original = task_repo.get_job(job_id)
    if not original:
        return None
    params = original.get("params_json")
    if isinstance(params, str):
        try:
            params = json.loads(params)
        except (json.JSONDecodeError, TypeError):
            params = None
    return create_task(
        task_type=original["task_type"],
        priority=original.get("priority", 0),
        params=params,
        created_by=original.get("created_by", "system"),
    )


def cancel_task(job_id):
    """取消任务（仅 pending 状态可取消）"""
    job = task_repo.get_job(job_id)
    if not job:
        return False
    if job["status"] != "pending":
        return False
    return task_repo.update_job_status(job_id, "canceled", message="用户取消")


def get_task_steps(job_id):
    """获取任务步骤列表"""
    steps = task_repo.get_steps(job_id)
    result = []
    for s in steps:
        item = dict(s)
        for key in ("started_at", "finished_at"):
            if item.get(key) and hasattr(item[key], "isoformat"):
                item[key] = item[key].isoformat()
        result.append(item)
    return result
