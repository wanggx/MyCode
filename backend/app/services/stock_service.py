# -*- coding: utf-8 -*-
"""
股票数据服务：查询、同步
"""

from app.repositories.stock_repo import (
    query_stocks,
    query_areas,
    query_industries,
    refresh_stock_list_from_tushare,
)
from app.repositories.stock_daily_repo import query_daily_data


def get_stock_list(page=1, page_size=10, keyword="", area="", industry=""):
    """获取股票列表"""
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 10
    return query_stocks(page, page_size, keyword, area, industry)


def get_areas():
    """获取所有地域"""
    return query_areas()


def get_industries():
    """获取所有行业"""
    return query_industries()


def get_stock_daily(ts_code, start_date, end_date, page=1, page_size=10, data_type="d"):
    """获取日线/周线/月线数据"""
    if not ts_code or not start_date or not end_date:
        return None, "参数缺失(ts_code, startDate, endDate)"
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 10
    return query_daily_data(ts_code, start_date, end_date, page, page_size, data_type)


def sync_stocks():
    """从 Tushare 同步股票列表"""
    try:
        refresh_stock_list_from_tushare()
        return {"success": True, "message": "同步成功"}
    except Exception as e:
        return {"success": False, "message": f"同步失败: {str(e)}"}
