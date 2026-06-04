# -*- coding: utf-8 -*-
"""
关注列表 API 路由
"""

from flask import Blueprint, request

from app.services import watchlist_service
from app.core.response import success, error

watchlist_bp = Blueprint("watchlist", __name__)


@watchlist_bp.route("", methods=["GET"])
def list_watchlist():
    result = watchlist_service.get_watchlist()
    if result is None:
        return error("查询失败", 500)
    return success(result)


@watchlist_bp.route("", methods=["POST"])
def add_watchlist():
    body = request.get_json(silent=True) or {}
    ts_code = body.get("ts_code")
    name = body.get("name")
    market = body.get("market")
    if not ts_code or not name or not market:
        return error("缺少必要参数: ts_code, name, market", 400)

    result = watchlist_service.add_to_watchlist(
        ts_code, name, market,
        source_signal_id=body.get("source_signal_id"),
        note=body.get("note"),
    )
    if not result:
        return error("添加失败", 400)
    return success(result, message="已添加到关注列表", status_code=201)


@watchlist_bp.route("/<int:watchlist_id>", methods=["DELETE"])
def remove_watchlist(watchlist_id):
    result = watchlist_service.remove_from_watchlist(watchlist_id)
    if not result:
        return error("移除失败，记录不存在", 404)
    return success(result, message="已从关注列表移除")
