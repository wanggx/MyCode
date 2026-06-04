# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify

from app.services.check_service import check_daily_coverage, trigger_daily_add
from app.core.security import require_auth

check_bp = Blueprint("stock_check", __name__)


@check_bp.route("/api/stock/check", methods=["GET"])
@require_auth
def stock_check():
    start_date = request.args.get("startDate")
    end_date = request.args.get("endDate")
    page = int(request.args.get("page", 1))
    page_size = int(request.args.get("page_size", 10))

    result, error = check_daily_coverage(start_date, end_date, page, page_size)
    if error:
        return jsonify({"code": 1, "message": error})
    return jsonify({"code": 0, "data": result})


@check_bp.route("/api/stock/daily/add", methods=["POST"])
@require_auth
def stock_daily_add():
    data = request.get_json() or {}
    start_date = data.get("start_date")
    end_date = data.get("end_date")
    data_type = data.get("type", "d")

    success, message = trigger_daily_add(start_date, end_date, data_type)
    if success:
        return jsonify({"success": True, "message": message})
    return jsonify({"success": False, "message": message}), 400
