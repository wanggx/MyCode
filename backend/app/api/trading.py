# -*- coding: utf-8 -*-
"""
交易中心 API 路由
"""

from flask import Blueprint, request

from app.services.trading_service import trading_service
from app.core.response import success, error

trading_bp = Blueprint("trading", __name__)


# ========== 大盘指数 ==========

@trading_bp.route("/api/market/indices", methods=["GET"])
def market_indices():
    """获取大盘指数实时行情"""
    result = trading_service.get_market_indices()
    return success(result)


# ========== 实盘运行 ==========

@trading_bp.route("/api/trading/live-runs", methods=["GET"])
def live_runs():
    """获取策略运行列表（支持 mode 过滤）"""
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)
    mode = request.args.get("mode")
    result = trading_service.get_live_runs(page, page_size, mode)
    return success(result)


@trading_bp.route("/api/trading/live-runs/<int:run_id>", methods=["GET"])
def live_run_detail(run_id):
    """获取单个实盘运行详情"""
    detail = trading_service.get_live_run_overview(run_id)
    if not detail:
        return error("实盘运行不存在", 404)
    return success(detail)


@trading_bp.route("/api/trading/live-runs/<int:run_id>/trades", methods=["GET"])
def live_run_trades(run_id):
    """获取实盘交易记录"""
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)
    result = trading_service.get_live_run_trades(run_id, page, page_size)
    return success(result)


@trading_bp.route("/api/trading/live-runs/<int:run_id>/positions", methods=["GET"])
def live_run_positions(run_id):
    """获取当前持仓"""
    result = trading_service.get_live_run_positions(run_id)
    return success(result)


@trading_bp.route("/api/trading/live-runs/<int:run_id>/logs", methods=["GET"])
def live_run_logs(run_id):
    """获取运行日志"""
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 50, type=int)
    result = trading_service.get_live_run_logs(run_id, page, page_size)
    return success(result)


@trading_bp.route("/api/trading/live-runs/<int:run_id>/metrics", methods=["GET"])
def live_run_metrics(run_id):
    """获取风控指标"""
    result = trading_service.get_live_run_metrics(run_id)
    if not result:
        return error("实盘运行不存在", 404)
    return success(result)


# ========== 模拟盘运行管理 ==========

@trading_bp.route("/api/trading/paper-runs", methods=["POST"])
def create_paper_run():
    """创建模拟盘运行（从回测策略部署）"""
    body = request.get_json(silent=True) or {}
    strategy_id = body.get("strategy_id")
    initial_capital = body.get("initial_capital", 100000)
    auto_start = body.get("auto_start", True)

    if not strategy_id:
        return error("strategy_id 不能为空", 400)

    run_id = trading_service.create_paper_run(strategy_id, initial_capital, auto_start)
    if not run_id:
        return error("创建失败", 500)
    return success({"id": run_id}, message="模拟盘运行已创建")


@trading_bp.route("/api/trading/paper-runs/<int:run_id>/start", methods=["POST"])
def start_paper_run(run_id):
    """启动模拟盘运行"""
    ok = trading_service.start_paper_run(run_id)
    if not ok:
        return error("启动失败", 500)
    return success(message="模拟盘已启动")


@trading_bp.route("/api/trading/paper-runs/<int:run_id>/stop", methods=["POST"])
def stop_paper_run(run_id):
    """停止模拟盘运行"""
    ok = trading_service.stop_paper_run(run_id)
    if not ok:
        return error("停止失败", 500)
    return success(message="模拟盘已停止")


@trading_bp.route("/api/trading/paper-runs/<int:run_id>", methods=["DELETE"])
def delete_paper_run(run_id):
    """删除模拟盘运行"""
    ok = trading_service.delete_paper_run(run_id)
    if not ok:
        return error("删除失败", 500)
    return success(message="模拟盘已删除")


@trading_bp.route("/api/trading/paper-runs/<int:run_id>/promote", methods=["POST"])
def promote_to_live(run_id):
    """模拟盘升级为实盘"""
    body = request.get_json(silent=True) or {}
    broker = body.get("broker", "国金证券 miniQMT")
    capital = body.get("capital")

    ok = trading_service.promote_to_live(run_id, broker, capital)
    if not ok:
        return error("升级失败", 500)
    return success(message="已升级为实盘交易")


# ========== 交易信号 ==========

@trading_bp.route("/api/trading/signals", methods=["GET"])
def trading_signals():
    """获取实盘交易信号列表"""
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)
    mode = request.args.get("mode", "live")
    result = trading_service.get_trading_signals(page, page_size)
    return success(result)


# ========== 风控概览 ==========

@trading_bp.route("/api/trading/risk-overview", methods=["GET"])
def risk_overview():
    """获取全局风控概览"""
    result = trading_service.get_risk_overview()
    return success(result)
