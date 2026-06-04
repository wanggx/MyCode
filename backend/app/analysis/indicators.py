# -*- coding: utf-8 -*-
"""
技术指标计算：MACD、KDJ
纯函数，仅依赖 talib、pandas、numpy
"""

import talib
import pandas as pd
import numpy as np


def calc_macd_and_kdj(df):
    """计算单只股票的 MACD 和 KDJ 指标，返回最后一行"""
    stock_pd = df.copy()
    stock_pd["dif"], stock_pd["dea"], _ = talib.MACD(
        stock_pd["close"], fastperiod=12, slowperiod=26, signalperiod=9
    )
    stock_pd["macd"] = (stock_pd["dif"] - stock_pd["dea"]) * 2
    stock_pd["macd_gloden"] = (stock_pd["macd"] > 0) & (
        stock_pd["macd"].shift(1) < 0
    )

    stock_pd["k"], stock_pd["d"] = talib.STOCH(
        stock_pd["high"],
        stock_pd["low"],
        stock_pd["close"],
        9,
        5,
        slowk_matype=1,
        slowd_period=5,
        slowd_matype=1,
    )
    stock_pd["j"] = 3 * stock_pd["k"] - 2 * stock_pd["d"]

    # 金叉/死叉
    stock_pd["kdj_gloden"] = np.where(
        (stock_pd["k"].shift(1) < stock_pd["d"].shift(1))
        & (stock_pd["k"] > stock_pd["d"]),
        True,
        False,
    )
    return stock_pd.tail(1)


def process_macd_and_kdj(stock_df):
    """批量处理多只股票的 MACD/KDI，返回结果 DataFrame"""
    if stock_df is None or len(stock_df) == 0:
        return pd.DataFrame(
            {
                "ts_code": pd.Series([], dtype="str"),
                "trade_date": pd.Series([], dtype="str"),
                "macd_gloden": pd.Series([], dtype="bool"),
                "dif": pd.Series([], dtype="float64"),
                "dea": pd.Series([], dtype="float64"),
                "macd": pd.Series([], dtype="float64"),
                "kdj_gloden": pd.Series([], dtype="bool"),
                "k": pd.Series([], dtype="float64"),
                "d": pd.Series([], dtype="float64"),
                "j": pd.Series([], dtype="float64"),
            }
        )
    final_df = (
        stock_df.groupby("ts_code")
        .apply(calc_macd_and_kdj, include_groups=False)
        .reset_index()
    )
    return final_df[
        ["ts_code", "trade_date", "macd_gloden", "dif", "dea", "macd", "kdj_gloden", "k", "d", "j"]
    ].round(2)


def filter_by_latest_date(stock_daily_df, date_str):
    """筛选出最新交易日期为 date_str 的股票"""
    return stock_daily_df.groupby("ts_code").filter(
        lambda x: x["trade_date"].max() == date_str
    )


def select_macd_kdj_by_daily(stock_daily_df, date_str):
    """按日线筛选 MACD/KDI"""
    final_df = filter_by_latest_date(stock_daily_df, date_str)
    return process_macd_and_kdj(final_df)


def select_macd_kdj_by_week(date_str, n, get_week_data_fn):
    """
    按周线筛选 MACD/KDI
    get_week_data_fn: 外部传入的数据获取函数 (start_date, end_date) -> DataFrame
    """
    from datetime import datetime, timedelta

    end_date = datetime.strptime(date_str, "%Y%m%d")
    start_date = end_date - timedelta(days=n - 1)
    stock_week_df = get_week_data_fn(None, start_date.strftime("%Y%m%d"), date_str)
    if stock_week_df is None or len(stock_week_df) == 0:
        return pd.DataFrame(
            {
                "ts_code": pd.Series([], dtype="str"),
                "trade_date": pd.Series([], dtype="str"),
                "macd_gloden": pd.Series([], dtype="float64"),
                "dif": pd.Series([], dtype="float64"),
                "dea": pd.Series([], dtype="float64"),
                "macd": pd.Series([], dtype="float64"),
                "kdj_gloden": pd.Series([], dtype="float64"),
                "k": pd.Series([], dtype="float64"),
                "d": pd.Series([], dtype="float64"),
                "j": pd.Series([], dtype="float64"),
            }
        )
    final_df = filter_by_latest_date(stock_week_df, date_str)
    return process_macd_and_kdj(final_df)
