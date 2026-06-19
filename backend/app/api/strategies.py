# -*- coding: utf-8 -*-
"""策略管理 API"""
from flask import Blueprint, request
from app.core.response import success, error
from app.core.security import require_auth
from app.services.strategy_service import (
    get_strategies, get_strategy_detail, create_strategy_svc,
    update_strategy_svc, change_strategy_status, delete_strategy_svc,
    get_versions, get_version_detail, create_version_svc
)

strategies_bp = Blueprint("strategies", __name__)


@strategies_bp.route("/api/strategies", methods=["GET"])
@require_auth
def list_strategies_route():
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)
    status = request.args.get("status")
    keyword = request.args.get("keyword")
    user_id = request.user.get("user_id")
    result, err = get_strategies(page, page_size, status, keyword, user_id)
    if err: return error(err, code=50001)
    return success(result)


@strategies_bp.route("/api/strategies", methods=["POST"])
@require_auth
def create_strategy_route():
    body = request.get_json(silent=True) or {}
    name = body.get("name", "").strip()
    if not name: return error("策略名称不能为空", code=40001)
    result, err = create_strategy_svc(
        name, body.get("description", ""), body.get("strategy_type", "stock"),
        request.user["user_id"], body.get("default_config")
    )
    if err: return error(err, code=40001)
    return success(result, message="策略创建成功")


@strategies_bp.route("/api/strategies/<int:sid>", methods=["GET"])
@require_auth
def get_strategy_route(sid):
    data = get_strategy_detail(sid)
    if not data: return error("策略不存在", code=40400)
    return success(data)


@strategies_bp.route("/api/strategies/<int:sid>", methods=["PUT"])
@require_auth
def update_strategy_route(sid):
    body = request.get_json(silent=True) or {}
    allowed = {"name", "description", "strategy_type", "default_config", "tags", "strategy_key"}
    updates = {k: v for k, v in body.items() if k in allowed}
    if not updates: return error("无有效更新字段", code=40001)
    if not update_strategy_svc(sid, **updates):
        return error("更新失败", code=50001)
    return success(None, message="更新成功")


@strategies_bp.route("/api/strategies/<int:sid>/status", methods=["PATCH"])
@require_auth
def patch_strategy_status(sid):
    body = request.get_json(silent=True) or {}
    status = body.get("status", "").strip()
    ok, err = change_strategy_status(sid, status)
    if not ok: return error(err, code=40001)
    return success(None, message="状态已更新")


@strategies_bp.route("/api/strategies/<int:sid>", methods=["DELETE"])
@require_auth
def delete_strategy_route(sid):
    ok, err = delete_strategy_svc(sid)
    if not ok: return error(err, code=40900)
    return success(None, message="删除成功")


# === Versions ===

@strategies_bp.route("/api/strategies/<int:sid>/versions", methods=["GET"])
@require_auth
def list_versions_route(sid):
    return success(get_versions(sid))


@strategies_bp.route("/api/strategies/<int:sid>/versions", methods=["POST"])
@require_auth
def create_version_route(sid):
    body = request.get_json(silent=True) or {}
    source_code = body.get("source_code", "")
    change_log = body.get("change_log", "")
    config = body.get("config")
    result, err = create_version_svc(sid, source_code, change_log, config)
    if err: return error(err, code=40001)
    return success(result, message="版本创建成功")


@strategies_bp.route("/api/strategies/<int:sid>/versions/<int:version>", methods=["GET"])
@require_auth
def get_version_route(sid, version):
    data = get_version_detail(sid, version)
    if not data: return error("版本不存在", code=40400)
    return success(data)
