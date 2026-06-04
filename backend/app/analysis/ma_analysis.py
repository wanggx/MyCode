# -*- coding: utf-8 -*-
"""
均线分析：MA3/MA5 计算和趋势判断
纯函数，仅依赖 pandas
"""

import pandas as pd


def ma(df):
    """计算单只股票的 MA3/MA5，检查最近 N 天 MA3 > MA5"""
    if df is None or len(df) == 0:
        return None
    try:
        df = df.copy()
        df.sort_values(by=["trade_date"], inplace=True, ascending=True)
        df["ma3"] = df["close"].rolling(3).mean()
        df["ma5"] = df["close"].rolling(5).mean()

        def check_last_n_days(n):
            last_n = df.tail(n)
            return (last_n["ma3"] > last_n["ma5"]).all()

        return pd.Series(
            {
                "ma35_3": check_last_n_days(3),
                "ma35_5": check_last_n_days(5),
                "ma3": df.tail(1)["ma3"].values[0],
                "ma5": df.tail(1)["ma5"].values[0],
            }
        )
    except Exception as e:
        print(f"计算ma异常: {e}")
        return None


def process_ma(df):
    """批量处理多只股票的均线"""
    if df is None or len(df) == 0:
        return None
    return df.groupby(["ts_code"]).apply(ma, include_groups=False).reset_index()


def select_ma_by_daily(stock_daily_df, date_str):
    """
    按日线筛选均线金叉
    stock_daily_df: 包含 ts_code, trade_date, close 列的 DataFrame
    date_str: YYYYMMDD
    """
    close_ma_df = (
        stock_daily_df[["ts_code", "trade_date", "high", "open", "close", "low"]]
        .groupby(["ts_code"])
        .tail(60)
    )
    filter_df = close_ma_df.groupby(["ts_code"]).filter(
        lambda x: x["trade_date"].max() == date_str
    )
    stock_ma_df = process_ma(filter_df)
    if stock_ma_df is None or len(stock_ma_df) == 0:
        return None
    stock_ma_df = stock_ma_df[
        stock_ma_df["ma35_3"] & stock_ma_df["ma35_5"]
    ]
    stock_ma_df.insert(0, "select_date", date_str)
    return stock_ma_df[["select_date", "ts_code", "ma35_3", "ma35_5", "ma3", "ma5"]].round(
        3
    )


def select_ma_by_week(date_str, n, get_week_data_fn):
    """
    按周线筛选均线金叉
    get_week_data_fn: (ts_code, start, end) -> DataFrame
    """
    from datetime import datetime, timedelta

    end_date = datetime.strptime(date_str, "%Y%m%d")
    start_date = end_date - timedelta(days=n - 1)
    stock_week_df = get_week_data_fn(None, start_date.strftime("%Y%m%d"), date_str)

    close_ma_df = (
        stock_week_df[["ts_code", "trade_date", "high", "open", "close", "low"]]
        .groupby(["ts_code"])
        .tail(60)
    )
    filter_df = close_ma_df.groupby(["ts_code"]).filter(
        lambda x: x["trade_date"].max() == date_str
    )
    stock_ma_df = process_ma(filter_df)
    if stock_ma_df is None or len(stock_ma_df) == 0:
        return pd.DataFrame(
            {
                "select_date": pd.Series([], dtype="str"),
                "ts_code": pd.Series([], dtype="str"),
                "ma35_3": pd.Series([], dtype="float64"),
                "ma35_5": pd.Series([], dtype="float64"),
                "ma3": pd.Series([], dtype="float64"),
                "ma5": pd.Series([], dtype="float64"),
            }
        )
    stock_ma_df = stock_ma_df[stock_ma_df["ma35_3"]]
    stock_ma_df.insert(0, "select_date", date_str)
    return stock_ma_df[["select_date", "ts_code", "ma35_3", "ma35_5", "ma3", "ma5"]].round(
        3
    )
