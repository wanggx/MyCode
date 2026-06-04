# -*- coding: utf-8 -*-
"""
因子实验室 API 路由
"""

from flask import Blueprint, request

from app.services import factor_service
from app.core.response import success, error

factors_bp = Blueprint("factors", __name__)


@factors_bp.route("", methods=["GET"])
def list_factors():
    """GET /api/factors?category="""
    category = request.args.get("category")
    result = factor_service.get_factors(category)
    return success(result)


@factors_bp.route("", methods=["POST"])
def register_factor():
    """POST /api/factors  body: {factor_code, factor_name, category, description, params}"""
    body = request.get_json(silent=True) or {}
    factor_code = body.get("factor_code")
    factor_name = body.get("factor_name")
    category = body.get("category")
    if not factor_code or not factor_name or not category:
        return error("factor_code, factor_name, category 不能为空", 400)
    result = factor_service.register_factor(
        factor_code, factor_name, category,
        body.get("description"), body.get("params"),
    )
    if not result:
        return error("注册因子失败", 500)
    return success(result, status_code=201)


@factors_bp.route("/analyze", methods=["POST"])
def analyze():
    """POST /api/factors/analyze  body: {factor_code, start_date, end_date, groups}"""
    body = request.get_json(silent=True) or {}
    factor_code = body.get("factor_code")
    start_date = body.get("start_date")
    end_date = body.get("end_date")
    if not factor_code or not start_date or not end_date:
        return error("factor_code, start_date, end_date 不能为空", 400)
    groups = int(body.get("groups", 5))
    result = factor_service.analyze_factor(factor_code, start_date, end_date, groups)
    return success(result)


@factors_bp.route("/<factor_code>/coverage", methods=["GET"])
def get_coverage(factor_code):
    """GET /api/factors/<code>/coverage?trade_date="""
    trade_date = request.args.get("trade_date")
    result = factor_service.get_coverage(factor_code, trade_date)
    return success(result)


@factors_bp.route("/<factor_code>/ic", methods=["GET"])
def get_ic(factor_code):
    """GET /api/factors/<code>/ic?start_date=&end_date="""
    start_date = request.args.get("start_date")
    end_date = request.args.get("end_date")
    if not start_date or not end_date:
        return error("start_date 和 end_date 不能为空", 400)
    result = factor_service.get_ic(factor_code, start_date, end_date)
    return success(result)


@factors_bp.route("/<factor_code>/group-return", methods=["GET"])
def get_group_return(factor_code):
    """GET /api/factors/<code>/group-return?trade_date=&groups="""
    trade_date = request.args.get("trade_date")
    groups = int(request.args.get("groups", 5))
    result = factor_service.get_group_return(factor_code, trade_date, groups)
    return success(result)
