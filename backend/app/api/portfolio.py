# -*- coding: utf-8 -*-
"""
组合 API 路由
"""

from flask import Blueprint, request

from app.services import portfolio_service
from app.core.response import success, error

portfolio_bp = Blueprint("portfolio", __name__)


@portfolio_bp.route("", methods=["GET"])
def list_portfolios():
    result = portfolio_service.get_portfolios()
    if result is None:
        return error("查询失败", 500)
    return success(result)


@portfolio_bp.route("/<int:portfolio_id>/nav", methods=["GET"])
def get_portfolio_nav(portfolio_id):
    result = portfolio_service.get_portfolio_nav(portfolio_id)
    if result is None:
        return error("查询失败", 500)
    return success(result)


@portfolio_bp.route("/<int:portfolio_id>/positions", methods=["GET"])
def get_portfolio_positions(portfolio_id):
    trade_date = request.args.get("trade_date")
    result = portfolio_service.get_portfolio_positions(portfolio_id)
    if result is None:
        return error("查询失败", 500)
    return success(result)


@portfolio_bp.route("/<int:portfolio_id>/risk", methods=["GET"])
def get_portfolio_risk(portfolio_id):
    result = portfolio_service.get_portfolio_risk(portfolio_id)
    if not result:
        return success({
            "portfolio_id": portfolio_id,
            "max_drawdown": 0.0,
            "industry_concentration": 0.0,
            "max_single_weight": 0.0,
            "position_count": 0,
        })
    return success(result)
