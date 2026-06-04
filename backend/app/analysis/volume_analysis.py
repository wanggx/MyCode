# -*- coding: utf-8 -*-
"""
成交量分析：斜率、放量、长下影线
纯函数，仅依赖 numpy/pandas
"""

import numpy as np
import pandas as pd
from datetime import datetime


def polyline(df, n):
    """计算收盘价的多项式斜率"""
    dailys = df.tail(n)
    x = np.arange(len(dailys))
    y = dailys.values
    slope, _ = np.polyfit(x, y, 1)
    return slope


def volmagnify(vol_series):
    """计算成交量放大倍数"""
    size = len(vol_series)
    prev = vol_series.values[0 : size - 1]
    mean = prev.mean()
    max_val = prev.max()
    latest = vol_series.values[size - 1]
    latest_prev = vol_series.values[size - 2]
    if mean == 0:
        return 0
    if latest > mean * 1.5 and latest > latest_prev * 1.5 and latest > max_val:
        return latest / mean
    return 0


def has_low_shadow(df):
    """判断是否存在长下影线（翻红且最低价跌幅 >= 5%）"""
    t_df = df.copy()
    t_df["drop_pct"] = (t_df["low"] - t_df["pre_close"]) / t_df["pre_close"] * 100
    t_df["low_shadow"] = (t_df["close"] > t_df["open"]) & (t_df["drop_pct"] <= -5.0)
    return t_df["low_shadow"].values[0]


def polylineslope(df):
    """
    计算单只股票的多项式斜率和成交量放大倍数
    返回包含 slope3/5/10/20/30/60、vol_magnify、low_shadow、out_date、sun 的 Series
    """
    if df is None or len(df) == 0:
        return None
    try:
        df = df.copy()
        df.sort_values(by=["trade_date"], inplace=True, ascending=True)

        result = pd.Series(
            {
                "slope3": polyline(df["close"], 3),
                "slope5": polyline(df["close"], 5),
                "slope10": polyline(df["close"], 10),
                "slope20": polyline(df["close"], 20),
                "slope30": polyline(df["close"], 30),
                "slope60": polyline(df["close"], 60),
                "low_shadow": has_low_shadow(df.tail(1)),
                "vol_magnify": df["vol"].tail(20).agg(volmagnify),
                "out_date": False,
                "sun": df.tail(1)["open"].values[0] < df.tail(1)["close"].values[0],
            }
        )

        # 判断是否过期
        lastday = df.tail(1)
        latest_trade_date = lastday["trade_date"].values[0]
        result["out_date"] = latest_trade_date != datetime.now().strftime("%Y%m%d")

        return result
    except Exception as e:
        print(f"polylineslope异常: {e}")
        return None
