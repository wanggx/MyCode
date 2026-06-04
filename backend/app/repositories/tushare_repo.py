# -*- coding: utf-8 -*-
"""
Tushare 外部数据源封装
"""

from app.core.config import settings
import tushare as ts
import pandas as pd


def get_pro_api():
    """获取 Tushare pro API 实例"""
    ts.set_token(settings.TUSHARE_TOKEN)
    return ts.pro_api()


def fetch_daily_data(ts_code, trade_date):
    """获取单日单只股票日线数据"""
    pro = get_pro_api()
    return pro.daily(ts_code=ts_code, trade_date=trade_date)


def fetch_stock_basic():
    """获取股票基础信息列表"""
    pro = get_pro_api()
    return pro.stock_basic(exchange="", list_status="L")
