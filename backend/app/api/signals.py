# -*- coding: utf-8 -*-
"""
信号 API 路由
"""

from flask import Blueprint, request

from app.services import signal_service
from app.core.response import success, error

signals_bp = Blueprint("signals", __name__)


@signals_bp.route("/api/signals", methods=["GET"])
def list_signals():
    trade_date = request.args.get("trade_date")
    strategy_id = request.args.get("strategy_id", type=int)
    market = request.args.get("market")
    min_score = float(request.args.get("min_score", 0))
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 20))

    result = signal_service.get_signals(
        trade_date, strategy_id, market, min_score, page, page_size,
    )
    if result is None:
        return error("查询失败", 500)
    return success(result)


@signals_bp.route("/api/signals/<int:signal_id>", methods=["GET"])
def get_signal(signal_id):
    detail = signal_service.get_signal_detail(signal_id)
    if not detail:
        return error("信号不存在", 404)
    return success(detail)


@signals_bp.route("/api/signals/<int:signal_id>/status", methods=["POST"])
def update_status(signal_id):
    body = request.get_json(silent=True) or {}
    status = body.get("status")
    if not status:
        return error("status 不能为空", 400)

    signal = signal_service.update_status(signal_id, status)
    if not signal:
        return error("状态更新失败，信号不存在或状态无效", 400)
    return success(signal, message="状态已更新")
