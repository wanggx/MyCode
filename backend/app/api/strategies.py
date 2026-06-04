# -*- coding: utf-8 -*-
"""
策略 API 路由
"""

from flask import Blueprint, request

from app.services import strategy_service
from app.core.response import success, error

strategies_bp = Blueprint("strategies", __name__)


@strategies_bp.route("/api/strategies", methods=["GET"])
def list_strategies():
    enabled_only = request.args.get("enabled_only", "").lower() in ("true", "1")
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 20))

    result = strategy_service.get_strategies(enabled_only, page, page_size)
    if result is None:
        return error("查询失败", 500)
    return success(result)


@strategies_bp.route("/api/strategies/<int:strategy_id>", methods=["GET"])
def get_strategy(strategy_id):
    detail = strategy_service.get_strategy_detail(strategy_id)
    if not detail:
        return error("策略不存在", 404)
    return success(detail)


@strategies_bp.route("/api/strategies", methods=["POST"])
def create_strategy():
    body = request.get_json(silent=True) or {}
    strategy = strategy_service.create_strategy(body)
    if not strategy:
        return error("创建策略失败", 400)
    return success(strategy, message="策略已创建", status_code=201)


@strategies_bp.route("/api/strategies/<int:strategy_id>", methods=["PUT"])
def update_strategy(strategy_id):
    body = request.get_json(silent=True) or {}
    strategy = strategy_service.update_strategy(strategy_id, body)
    if not strategy:
        return error("策略不存在或更新失败", 400)
    return success(strategy, message="策略已更新")


@strategies_bp.route("/api/strategies/<int:strategy_id>/versions", methods=["POST"])
def create_version(strategy_id):
    body = request.get_json(silent=True) or {}
    version = strategy_service.create_version(strategy_id, body)
    if not version:
        return error("版本创建失败", 400)
    return success(version, message="版本已创建", status_code=201)


@strategies_bp.route("/api/strategies/<int:strategy_id>/run", methods=["POST"])
def run_strategy(strategy_id):
    body = request.get_json(silent=True) or {}
    version_id = body.get("version_id")
    result = strategy_service.run_strategy(strategy_id, version_id)
    if not result:
        return error("策略运行失败", 400)
    return success(result, message="策略运行任务已提交")


@strategies_bp.route("/api/strategies/<int:strategy_id>/runs", methods=["GET"])
def list_runs(strategy_id):
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 20))

    result = strategy_service.get_runs(strategy_id, page, page_size)
    if result is None:
        return error("查询失败", 500)
    return success(result)
