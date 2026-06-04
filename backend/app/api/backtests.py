# -*- coding: utf-8 -*-
"""
回测 API 路由
"""

from flask import Blueprint, request

from app.services import backtest_service
from app.core.response import success, error

backtests_bp = Blueprint("backtests", __name__)


@backtests_bp.route("", methods=["POST"])
def create_backtest():
    """创建回测任务"""
    body = request.get_json(silent=True) or {}
    strategy_id = body.get("strategy_id")
    version_id = body.get("version_id")
    start_date = body.get("start_date")
    end_date = body.get("end_date")
    params = body.get("params")

    if not strategy_id or not version_id or not start_date or not end_date:
        return error("缺少必要参数: strategy_id, version_id, start_date, end_date", 400)

    result = backtest_service.create_backtest(strategy_id, version_id, start_date, end_date, params)
    if not result:
        return error("创建回测任务失败", 400)
    return success(result, message="回测任务已创建", status_code=201)


@backtests_bp.route("", methods=["GET"])
def list_backtests():
    """分页查询"""
    strategy_id = request.args.get("strategy_id", type=int)
    status = request.args.get("status")
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 20))

    result = backtest_service.get_backtests(strategy_id, status, page, page_size)
    if result is None:
        return error("查询失败", 500)
    return success(result)


@backtests_bp.route("/<int:backtest_id>", methods=["GET"])
def get_backtest(backtest_id):
    """回测详情"""
    detail = backtest_service.get_backtest_detail(backtest_id)
    if not detail:
        return error("回测任务不存在", 404)
    return success(detail)


@backtests_bp.route("/<int:backtest_id>/nav", methods=["GET"])
def get_nav(backtest_id):
    """净值列表"""
    nav = backtest_service.get_nav(backtest_id)
    return success(nav)


@backtests_bp.route("/<int:backtest_id>/positions", methods=["GET"])
def get_positions(backtest_id):
    """持仓列表"""
    trade_date = request.args.get("trade_date")
    positions = backtest_service.get_positions(backtest_id, trade_date)
    return success(positions)


@backtests_bp.route("/<int:backtest_id>/trades", methods=["GET"])
def get_trades(backtest_id):
    """交易明细"""
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 20))

    result = backtest_service.get_trades(backtest_id, page, page_size)
    if result is None:
        return error("查询失败", 500)
    return success(result)
