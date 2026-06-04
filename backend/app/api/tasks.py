# -*- coding: utf-8 -*-
"""
任务 API 路由
"""

from flask import Blueprint, request

from app.services import task_service
from app.core.response import success, error

tasks_bp = Blueprint("tasks", __name__)


@tasks_bp.route("/api/tasks", methods=["GET"])
def list_tasks():
    status = request.args.get("status")
    task_type = request.args.get("task_type")
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 20))

    result = task_service.get_tasks(status, task_type, page, page_size)
    if result is None:
        return error("查询失败", 500)
    return success(result)


@tasks_bp.route("/api/tasks/<int:job_id>", methods=["GET"])
def get_task(job_id):
    result = task_service.get_task(job_id)
    if not result:
        return error("任务不存在", 404)
    return success(result)


@tasks_bp.route("/api/tasks/<int:job_id>/retry", methods=["POST"])
def retry_task(job_id):
    result = task_service.retry_task(job_id)
    if not result:
        return error("重试失败，原任务不存在", 404)
    return success(result, message="已创建重试任务")


@tasks_bp.route("/api/tasks/<int:job_id>/cancel", methods=["POST"])
def cancel_task(job_id):
    ok = task_service.cancel_task(job_id)
    if not ok:
        return error("取消失败，任务不存在或非 pending 状态", 400)
    job = task_service.get_task(job_id)
    return success(job, message="任务已取消")
