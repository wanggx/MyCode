# -*- coding: utf-8 -*-
"""
数据健康中心 API 路由
"""

from flask import Blueprint, request

from app.services import data_quality_service
from app.services import data_repair_service
from app.core.response import success, error

data_quality_bp = Blueprint("data_quality", __name__)


@data_quality_bp.route("/api/data/quality-summary", methods=["GET"])
def get_quality_summary():
    result = data_quality_service.get_quality_summary()
    return success(result)


@data_quality_bp.route("/api/data/issues", methods=["GET"])
def list_issues():
    market = request.args.get("market")
    severity = request.args.get("severity")
    status = request.args.get("status")
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 20))

    result = data_quality_service.quality_repo.get_issues(
        market, severity, status, page, page_size
    )
    return success(result)


@data_quality_bp.route("/api/data/issues/<int:issue_id>", methods=["GET"])
def get_issue_detail(issue_id):
    detail = data_quality_service.get_issue_detail(issue_id)
    if not detail:
        return error("问题不存在", 404)
    return success(detail)


@data_quality_bp.route("/api/data/issues/<int:issue_id>/repair", methods=["POST"])
def create_repair(issue_id):
    body = request.get_json(silent=True) or {}
    repair_mode = body.get("repair_mode")
    options = body.get("options", {})

    job = data_repair_service.create_repair(issue_id, repair_mode, options)
    if not job:
        return error("创建修复任务失败", 400)
    return success(job, message="修复任务已创建")


@data_quality_bp.route("/api/data/quality-scan", methods=["POST"])
def quality_scan():
    body = request.get_json(silent=True) or {}
    market = body.get("market", "A股")
    start_date = body.get("start_date")
    end_date = body.get("end_date")

    if not start_date or not end_date:
        return error("start_date 和 end_date 不能为空", 400)

    issues = data_quality_service.scan_date_range(market, start_date, end_date)
    return success(issues, message="扫描完成")
