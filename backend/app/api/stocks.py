# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify

from app.services.stock_service import (
    get_stock_list,
    get_areas,
    get_industries,
    get_stock_daily,
    sync_stocks,
)
from app.core.security import require_auth

stocks_bp = Blueprint("stocks", __name__)


@stocks_bp.route("/api/stocks", methods=["GET"])
@require_auth
def stocks_list():
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))
    keyword = request.args.get("keyword", "")
    area = request.args.get("area", "")
    industry = request.args.get("industry", "")

    result, error = get_stock_list(page, page_size, keyword, area, industry)
    if error:
        return jsonify({"error": error}), 500
    return jsonify({"message": "获取成功", "data": result}), 200


@stocks_bp.route("/api/stocks/areas", methods=["GET"])
@require_auth
def areas_list():
    areas = get_areas()
    return jsonify({"message": "获取成功", "data": areas}), 200


@stocks_bp.route("/api/stocks/industries", methods=["GET"])
@require_auth
def industries_list():
    industries = get_industries()
    return jsonify({"message": "获取成功", "data": industries}), 200


@stocks_bp.route("/api/stocks/sync", methods=["POST"])
@require_auth
def sync_stocks_route():
    result = sync_stocks()
    status = 200 if result.get("success") else 500
    return jsonify(result), status


@stocks_bp.route("/api/stock/data", methods=["GET"])
@require_auth
def stock_daily_data():
    ts_code = request.args.get("ts_code")
    start_date = request.args.get("startDate")
    end_date = request.args.get("endDate")
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))
    data_type = request.args.get("type", "d")

    if not ts_code or not start_date or not end_date:
        return jsonify({"error": "参数缺失(ts_code, startDate, endDate)"}), 400

    result, error = get_stock_daily(
        ts_code, start_date, end_date, page, page_size, data_type
    )
    if error:
        return jsonify({"error": error}), 500
    return jsonify({"message": "获取成功", "data": result}), 200
