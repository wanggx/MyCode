# -*- coding: utf-8 -*-
"""数据中心 API"""
from flask import Blueprint, request
from app.core.response import success, error
from app.core.security import require_auth
from app.services.data_service import (
    get_stock_list, get_stock_detail, get_stock_daily,
    get_data_sources, trigger_sync, get_sync_logs, get_data_overview
)

data_bp = Blueprint("data", __name__)


@data_bp.route("/api/data/stocks", methods=["GET"])
@require_auth
def list_stocks():
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)
    keyword = request.args.get("keyword", "")
    area = request.args.get("area", "")
    industry = request.args.get("industry", "")
    market = request.args.get("market", "")
    result, err = get_stock_list(page, page_size, keyword, area, industry, market)
    if err:
        return error(err, code=50001)
    return success(result)


@data_bp.route("/api/data/stocks/<ts_code>", methods=["GET"])
@require_auth
def stock_detail(ts_code):
    row = get_stock_detail(ts_code)
    if not row:
        return error("股票不存在", code=40400)
    return success({
        "ts_code": row["ts_code"], "symbol": row["symbol"], "name": row["name"],
        "area": row.get("area", ""), "industry": row.get("industry", ""),
        "market": row.get("market", ""), "exchange": row.get("exchange", ""),
        "board_type": row.get("board_type", ""),
        "list_date": str(row.get("list_date")) if row.get("list_date") else "",
    })


@data_bp.route("/api/data/stocks/<ts_code>/daily", methods=["GET"])
@require_auth
def stock_daily_data(ts_code):
    start_date = request.args.get("start_date", "")
    end_date = request.args.get("end_date", "")
    if not start_date or not end_date:
        return error("缺少 start_date 或 end_date 参数", code=40001)
    result, err = get_stock_daily(ts_code, start_date, end_date)
    if err:
        return error(err, code=50001)
    return success(result)


@data_bp.route("/api/data/sources", methods=["GET"])
@require_auth
def list_sources():
    rows = get_data_sources()
    return success([{
        "name": r["name"], "display_name": r["display_name"],
        "status": r["status"], "config": r.get("config"), "priority": r["priority"]
    } for r in rows])


@data_bp.route("/api/data/sync", methods=["POST"])
@require_auth
def sync_data():
    body = request.get_json(silent=True) or {}
    source = body.get("source", "tushare")
    data_type = body.get("data_type", "daily")
    trade_date = body.get("trade_date", "")
    result = trigger_sync(source, data_type, trade_date)
    return success(result, message="同步任务已创建")


@data_bp.route("/api/data/sync-logs", methods=["GET"])
@require_auth
def list_sync_logs():
    page = request.args.get("page", 1, type=int)
    page_size = request.args.get("page_size", 20, type=int)
    source = request.args.get("source", None)
    result, err = get_sync_logs(page, page_size, source)
    if err:
        return error(err, code=50001)
    return success(result)


@data_bp.route("/api/data/overview", methods=["GET"])
@require_auth
def data_overview():
    result = get_data_overview()
    return success(result)
