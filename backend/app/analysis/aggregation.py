# -*- coding: utf-8 -*-
"""
周线/月线聚合计算
纯函数，仅依赖 pandas/datetime
"""

import pandas as pd
import datetime
import calendar


def fridayline(datestr):
    """计算日期所在周的周五 YYYYMMDD"""
    date = pd.to_datetime(datestr).date()
    # adjust_date + friday
    current_date = datetime.date.today()
    input_date = date
    adjusted = current_date if input_date > current_date else input_date
    days_since_monday = adjusted.weekday() % 7
    fri = adjusted - datetime.timedelta(days=days_since_monday) + datetime.timedelta(4)
    return fri.strftime("%Y%m%d")


def lastday(datestr):
    """计算日期所在月的最后一天 YYYYMMDD"""
    date = pd.to_datetime(datestr).date()
    current_date = datetime.date.today()
    adjusted = current_date if date > current_date else date
    _, last_day_num = calendar.monthrange(adjusted.year, adjusted.month)
    return datetime.date(adjusted.year, adjusted.month, last_day_num).strftime("%Y%m%d")


def aggline(week):
    """聚合周/月线：对一组日线计算 OHLC/vol/amount"""
    week = week.sort_values(by=["trade_date"], ascending=True)
    first = week.head(1)
    last = week.tail(1)
    return pd.Series(
        {
            "close": last["close"].values[0],
            "open": first["open"].values[0],
            "high": week["high"].max(),
            "low": week["low"].min(),
            "change": last["close"].values[0] - first["open"].values[0],
            "vol": week["vol"].sum(),
            "amount": week["amount"].sum(),
        }
    )


def process_week_df(stock_df):
    """将日线聚合成周线"""
    if stock_df is None or len(stock_df) == 0:
        return None
    df = stock_df.copy()
    df["week"] = df["trade_date"].transform(fridayline)
    week_df = df.groupby(["ts_code", "week"]).apply(aggline, include_groups=False)
    week_df["pre_close"] = 0
    week_df["change"] = 0
    week_df["pct_chg"] = 0
    week_df.reset_index(inplace=True)
    week_df.rename(columns={"week": "trade_date"}, inplace=True)
    week_df = week_df.reindex(
        columns=["ts_code", "trade_date", "close", "open", "high", "low", "pre_close", "change", "pct_chg", "vol", "amount"]
    )
    return week_df.round(3)


def process_month_df(stock_df):
    """将日线聚合成月线"""
    if stock_df is None or len(stock_df) == 0:
        return None
    df = stock_df.copy()
    df["month"] = df["trade_date"].transform(lastday)
    month_df = df.groupby(["ts_code", "month"]).apply(aggline, include_groups=False)
    month_df["pre_close"] = 0
    month_df["change"] = 0
    month_df["pct_chg"] = 0
    month_df.reset_index(inplace=True)
    month_df.rename(columns={"month": "trade_date"}, inplace=True)
    month_df = month_df.reindex(
        columns=["ts_code", "trade_date", "close", "open", "high", "low", "pre_close", "change", "pct_chg", "vol", "amount"]
    )
    return month_df.round(3)
