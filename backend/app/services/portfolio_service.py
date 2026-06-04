# -*- coding: utf-8 -*-
"""
组合风控业务逻辑层：组合查询、风险指标、净值、持仓
"""

import logging
from datetime import datetime

from app.repositories import portfolio_repo

logger = logging.getLogger("myapp")


def _serialize(row):
    if not row:
        return None
    result = dict(row)
    for key in ("created_at", "added_at", "removed_at"):
        if result.get(key) and hasattr(result[key], "isoformat"):
            result[key] = result[key].isoformat()
    return result


def get_portfolios() -> list:
    try:
        rows = portfolio_repo.get_portfolios()
        return [_serialize(r) for r in rows]
    except Exception as e:
        logger.error("get_portfolios failed: %s", e)
        return []


def get_portfolio_risk(portfolio_id: int) -> dict:
    try:
        positions = portfolio_repo.get_positions(portfolio_id)
        if not positions:
            return None
        max_weight = max((float(p.get("weight", 0)) for p in positions), default=0)
        return {
            "portfolio_id": portfolio_id,
            "max_drawdown": 0.0,
            "industry_concentration": 0.0,
            "max_single_weight": max_weight,
            "position_count": len(positions),
        }
    except Exception as e:
        logger.error("get_portfolio_risk failed: %s", e)
        return None


def get_portfolio_nav(portfolio_id: int) -> list:
    try:
        rows = portfolio_repo.get_navs(portfolio_id)
        return [_serialize(r) for r in rows]
    except Exception as e:
        logger.error("get_portfolio_nav failed: %s", e)
        return []


def get_portfolio_positions(portfolio_id: int) -> list:
    try:
        rows = portfolio_repo.get_positions(portfolio_id)
        return [_serialize(r) for r in rows]
    except Exception as e:
        logger.error("get_portfolio_positions failed: %s", e)
        return []


def add_to_portfolio(signal_id: int, portfolio_id: int) -> dict:
    try:
        return {
            "signal_id": signal_id,
            "portfolio_id": portfolio_id,
            "status": "added",
            "message": "mock: 信号已添加到组合",
        }
    except Exception as e:
        logger.error("add_to_portfolio failed: %s", e)
        return None


def update_portfolio_nav(portfolio_id: int):
    try:
        logger.info("update_portfolio_nav mock: portfolio_id=%s", portfolio_id)
    except Exception as e:
        logger.error("update_portfolio_nav failed: %s", e)
