# -*- coding: utf-8 -*-
"""回测中心 API"""
from flask import Blueprint, request
from app.core.response import success, error
from app.core.security import require_auth
from app.services.backtest_service import (
    create_backtest, get_backtests, get_backtest_detail,
    cancel_backtest, delete_backtest,
    get_backtest_nav, get_backtest_trades, get_backtest_positions,
    get_backtest_daily_metrics, get_backtest_risk_metrics,
    get_backtest_logs, get_backtest_report,
)

backtests_bp = Blueprint("backtests", __name__)


@backtests_bp.route("/api/backtests", methods=["POST"])
@require_auth
def create_backtest_route():
    body = request.get_json(silent=True) or {}
    sid = body.get("strategy_id")
    ver = body.get("version")
    cfg = body.get("config", {})
    if not sid: return error("缺少 strategy_id", code=40001)
    if not cfg.get("start_date") or not cfg.get("end_date"):
        return error("缺少 start_date / end_date", code=40001)
    result, err = create_backtest(request.user["user_id"], int(sid), ver, cfg)
    if err: return error(err, code=40001 if "不存在" in err or "没有" in err else 40900 if "上限" in err else 50001)
    return success(result, message="回测已创建")


@backtests_bp.route("/api/backtests", methods=["GET"])
@require_auth
def list_backtests_route():
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)
    sid = request.args.get("strategy_id", type=int)
    status = request.args.get("status")
    result, err = get_backtests(page, page_size, sid, status, request.user.get("user_id"))
    if err: return error(err, code=50001)
    return success(result)


@backtests_bp.route("/api/backtests/<int:bid>", methods=["GET"])
@require_auth
def get_backtest_route(bid):
    data = get_backtest_detail(bid)
    if not data: return error("回测不存在", code=40400)
    return success(data)


@backtests_bp.route("/api/backtests/<int:bid>/cancel", methods=["POST"])
@require_auth
def cancel_backtest_route(bid):
    ok, err = cancel_backtest(bid)
    if not ok: return error(err, code=40001)
    return success(None, message="回测已取消")


@backtests_bp.route("/api/backtests/<int:bid>", methods=["DELETE"])
@require_auth
def delete_backtest_route(bid):
    ok, err = delete_backtest(bid)
    if not ok: return error(err, code=40001)
    return success(None, message="删除成功")


@backtests_bp.route("/api/backtests/<int:bid>/nav", methods=["GET"])
@require_auth
def nav_route(bid):
    data = get_backtest_nav(bid)
    return success(data)


@backtests_bp.route("/api/backtests/<int:bid>/trades", methods=["GET"])
@require_auth
def trades_route(bid):
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 50, type=int)
    result, err = get_backtest_trades(bid, page, page_size)
    if err: return error(err, code=50001)
    return success(result)


@backtests_bp.route("/api/backtests/<int:bid>/positions", methods=["GET"])
@require_auth
def positions_route(bid):
    trade_date = request.args.get("trade_date")
    return success(get_backtest_positions(bid, trade_date))


@backtests_bp.route("/api/backtests/<int:bid>/daily-metrics", methods=["GET"])
@require_auth
def daily_metrics_route(bid):
    return success(get_backtest_daily_metrics(bid))


@backtests_bp.route("/api/backtests/<int:bid>/risk-metrics", methods=["GET"])
@require_auth
def risk_metrics_route(bid):
    data = get_backtest_risk_metrics(bid)
    return success(data)


@backtests_bp.route("/api/backtests/<int:bid>/logs", methods=["GET"])
@require_auth
def logs_route(bid):
    mode = request.args.get("mode", "full")
    lines = request.args.get("lines", 100, type=int)
    result, err = get_backtest_logs(bid, mode, lines)
    if err: return error(err, code=40400)
    return success(result)


@backtests_bp.route("/api/backtests/<int:bid>/report", methods=["GET"])
@require_auth
def report_route(bid):
    data = get_backtest_report(bid)
    if not data: return error("回测不存在", code=40400)
    return success(data)
