# -*- coding: utf-8 -*-
"""
因子业务逻辑层：因子查询、注册、分析
"""

import json
import logging
import random
from datetime import datetime, timedelta

from app.repositories import factor_repo

logger = logging.getLogger(__name__)

_MOCK_FACTORS = [
    {"factor_code": "MA5", "factor_name": "5日均线", "category": "技术",
     "description": "5日移动平均线因子", "enabled": 1},
    {"factor_code": "MA10", "factor_name": "10日均线", "category": "技术",
     "description": "10日移动平均线因子", "enabled": 1},
    {"factor_code": "MA20", "factor_name": "20日均线", "category": "技术",
     "description": "20日移动平均线因子", "enabled": 1},
    {"factor_code": "MACD", "factor_name": "MACD因子", "category": "技术",
     "description": "MACD指标因子", "enabled": 1},
    {"factor_code": "Volume_Slope", "factor_name": "成交量斜率", "category": "价量",
     "description": "成交量趋势斜率因子", "enabled": 1},
    {"factor_code": "Volatility", "factor_name": "波动率", "category": "风险",
     "description": "历史波动率因子", "enabled": 1},
]


def _serialize(row):
    if not row:
        return None
    result = dict(row)
    for key in ("created_at", "updated_at"):
        if result.get(key) and hasattr(result[key], "isoformat"):
            result[key] = result[key].isoformat()
    val = result.get("params_json")
    if isinstance(val, str):
        try:
            result["params_json"] = json.loads(val)
        except (json.JSONDecodeError, TypeError):
            pass
    return result


def get_factors(category=None) -> list:
    """获取因子定义列表，category 过滤"""
    try:
        rows = factor_repo.get_factor_defs(category)
        if not rows:
            result = _MOCK_FACTORS[:]
            if category:
                result = [f for f in result if f["category"] == category]
            return result
        return [_serialize(r) for r in rows]
    except Exception as e:
        logger.error("get_factors failed: %s", e)
        result = _MOCK_FACTORS[:]
        if category:
            result = [f for f in result if f["category"] == category]
        return result


def register_factor(factor_code, factor_name, category, description=None, params=None) -> dict:
    """注册新因子"""
    try:
        data = {
            "factor_code": factor_code,
            "factor_name": factor_name,
            "category": category,
            "description": description,
            "params_json": params,
            "enabled": 1,
        }
        inserted_id = factor_repo.create_factor_def(data)
        if inserted_id:
            data["id"] = inserted_id
            return data
        return None
    except Exception as e:
        logger.error("register_factor failed: %s", e)
        return None


def get_coverage(factor_code, trade_date=None) -> dict:
    """因子覆盖率"""
    try:
        return factor_repo.get_coverage(factor_code, trade_date)
    except Exception as e:
        logger.error("get_coverage failed: %s", e)
        return {"covered": 0, "total": 0, "ratio": 0}


def get_ic(factor_code, start_date, end_date) -> list:
    """IC 曲线（第一版 mock 实现）"""
    try:
        result = factor_repo.get_factor_ic(factor_code, start_date, end_date)
        if result:
            return result
        start = datetime.strptime(start_date, "%Y%m%d")
        end = datetime.strptime(end_date, "%Y%m%d")
        points = []
        current = start
        while current <= end and len(points) < 30:
            points.append({
                "trade_date": current.strftime("%Y-%m-%d"),
                "ic": round(random.uniform(-0.15, 0.25), 4),
            })
            current += timedelta(days=7)
        return points
    except Exception as e:
        logger.error("get_ic failed: %s", e)
        return []


def get_group_return(factor_code, trade_date, groups=5) -> list:
    """分层收益（第一版 mock 实现）"""
    try:
        result = []
        for i in range(1, groups + 1):
            ret = round(random.uniform(-0.02, 0.05), 4)
            result.append({"group": f"Q{i}", "return": ret})
        return result
    except Exception as e:
        logger.error("get_group_return failed: %s", e)
        return []


def analyze_factor(factor_code, start_date, end_date, groups=5) -> dict:
    """综合分析：返回 ic_curve, group_return, coverage"""
    try:
        ic_curve = get_ic(factor_code, start_date, end_date)
        trade_date = end_date if end_date else None
        group_return = get_group_return(factor_code, trade_date, groups)
        coverage = get_coverage(factor_code, trade_date)
        if coverage.get("total", 0) == 0:
            coverage = {"covered": 2800, "total": 3500, "ratio": 0.8}
        return {
            "ic_curve": ic_curve,
            "group_return": group_return,
            "coverage": coverage,
        }
    except Exception as e:
        logger.error("analyze_factor failed: %s", e)
        return {
            "ic_curve": [],
            "group_return": [],
            "coverage": {"covered": 0, "total": 0, "ratio": 0},
        }
