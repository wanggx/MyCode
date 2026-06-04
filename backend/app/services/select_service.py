# -*- coding: utf-8 -*-
"""
选股服务：查询、异步触发、mock
"""

import threading
from app.repositories.stock_select_repo import (
    query_stock_select,
    delete_stock_select,
    save_select_result_to_db,
    query_vol_line_data,
)
from app.repositories.stock_daily_repo import query_stock_data_df
from app.repositories.hk_stock_repo import get_hk_stock_data, get_hk_stock_list
from app.repositories.stock_repo import query_stock_list_df
from app.analysis.volume_analysis import polylineslope
from app.analysis.indicators import select_macd_kdj_by_daily, select_macd_kdj_by_week
from app.analysis.ma_analysis import select_ma_by_daily, select_ma_by_week
from app.repositories.stock_daily_repo import query_stock_week_data_df
from app.utils.notify import sendMsg, sendGroupFile

import pandas as pd
from datetime import datetime, timedelta

_running_select_tasks = set()
_running_tasks_lock = threading.Lock()


def get_select_results(page=1, page_size=10, select_date=None):
    """查询选股结果"""
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 10
    return query_stock_select(page, page_size, select_date)


def remove_select_results(select_date):
    """删除指定日期的选股结果"""
    return delete_stock_select(select_date)


def _async_select(date_str):
    """异步执行选股（内部函数）"""
    task_key = date_str
    with _running_tasks_lock:
        if task_key in _running_select_tasks:
            return
        _running_select_tasks.add(task_key)
    try:
        _run_select_volume(date_str)
        _run_select_trend(date_str)
        _run_hk_select_volume(date_str)
        _run_hk_select_trend(date_str)
    finally:
        with _running_tasks_lock:
            _running_select_tasks.discard(task_key)


def trigger_async_select(select_date_str):
    """触发异步选股"""
    task_key = select_date_str
    with _running_tasks_lock:
        if task_key in _running_select_tasks:
            return False, "选股任务已在执行中"
    threading.Thread(target=_async_select, args=(select_date_str,), daemon=True).start()
    return True, "选股任务已启动"


def is_task_running(select_date_str):
    """检查选股任务是否正在运行"""
    with _running_tasks_lock:
        return select_date_str in _running_select_tasks


def get_vol_line_data(start_date, end_date):
    """获取成交量线数据"""
    if not start_date or not end_date:
        return None, "startDate and endDate parameters are required"
    return query_vol_line_data(start_date, end_date)


def _run_select_volume(date_str):
    """执行放量选股（A股）"""
    end = datetime.strptime(date_str, "%Y%m%d")
    start = end - timedelta(days=100)
    stock_df = query_stock_data_df(None, start.strftime("%Y%m%d"), date_str)
    if stock_df is None or len(stock_df) == 0:
        return

    close_polyline = (
        stock_df[["ts_code", "trade_date", "high", "open", "close", "pre_close", "low", "vol"]]
        .groupby(["ts_code"])
        .tail(60)
    )
    result = (
        close_polyline.groupby(["ts_code"])
        .filter(lambda x: x["trade_date"].max() == date_str)
        .groupby(["ts_code"])
        .apply(polylineslope, include_groups=False)
        .reset_index()
    )
    if result is None or len(result) == 0:
        return

    selected = result[result["vol_magnify"] > 0].copy()
    if len(selected) == 0:
        return

    selected.insert(0, "select_date", date_str)
    selected.rename(
        columns={
            "slope3": "trend3", "slope5": "trend5", "slope10": "trend10",
            "slope20": "trend20", "slope30": "trend30", "vol_magnify": "vol",
        },
        inplace=True,
    )
    stock_names = query_stock_list_df()
    joined = pd.merge(
        selected, stock_names[["ts_code", "name"]], on="ts_code", how="left"
    )
    final_df = joined[
        ["select_date", "ts_code", "name", "vol", "trend3", "trend5", "trend10", "trend20", "trend30"]
    ].round(3)
    save_select_result_to_db(final_df)

    filename = f"{date_str}_vol.csv"
    final_df.to_csv(filename, index=True)
    sendGroupFile(filename)


def _run_hk_select_volume(date_str):
    """执行放量选股（港股）"""
    end = datetime.strptime(date_str, "%Y%m%d")
    start = end - timedelta(days=100)
    stock_df = get_hk_stock_data(None, start.strftime("%Y%m%d"), date_str)
    if stock_df is None or len(stock_df) == 0:
        return

    close_polyline = (
        stock_df[["ts_code", "trade_date", "high", "open", "close", "pre_close", "low", "vol"]]
        .groupby(["ts_code"])
        .tail(60)
    )
    result = (
        close_polyline.groupby(["ts_code"])
        .filter(lambda x: x["trade_date"].max() == date_str)
        .groupby(["ts_code"])
        .apply(polylineslope, include_groups=False)
        .reset_index()
    )
    if result is None or len(result) == 0:
        return

    selected = result[result["vol_magnify"] > 0].copy()
    if len(selected) == 0:
        return

    selected.insert(0, "select_date", date_str)
    selected.rename(
        columns={
            "slope3": "trend3", "slope5": "trend5", "slope10": "trend10",
            "slope20": "trend20", "slope30": "trend30", "vol_magnify": "vol",
        },
        inplace=True,
    )
    stock_names = get_hk_stock_list()
    joined = pd.merge(
        selected, stock_names[["ts_code", "name"]], on="ts_code", how="left"
    )
    final_df = joined[
        ["select_date", "ts_code", "name", "vol", "trend3", "trend5", "trend10", "trend20", "trend30"]
    ].round(3)
    save_select_result_to_db(final_df)

    filename = f"{date_str}_hk_vol.csv"
    final_df.to_csv(filename, index=True)
    sendGroupFile(filename)


def _run_select_trend(date_str):
    """执行趋势选股（A股）"""
    end = datetime.strptime(date_str, "%Y%m%d")
    start = end - timedelta(days=200)
    stock_df = query_stock_data_df(None, start.strftime("%Y%m%d"), date_str)

    ma_daily = select_ma_by_daily(stock_df, date_str)
    ma_week = select_ma_by_week(date_str, 360, query_stock_week_data_df)
    ta_daily = select_macd_kdj_by_daily(stock_df, date_str)
    ta_week = select_macd_kdj_by_week(date_str, 1200, query_stock_week_data_df)

    if ma_daily is None or len(ma_daily) == 0:
        sendMsg(f"{date_str}日均线数据不存在")
        return

    merged = pd.merge(ma_daily, ma_week, on="ts_code", how="left", suffixes=("_d", "_w"))
    merged = pd.merge(merged, ta_daily, on="ts_code", how="left", suffixes=("_d", "_w"))
    merged = pd.merge(merged, ta_week, on="ts_code", how="left", suffixes=("_d", "_w"))
    merged = merged[
        merged["macd_gloden_w"] | merged["kdj_gloden_w"] | merged["macd_gloden_d"] | merged["kdj_gloden_d"]
    ]

    stock_names = query_stock_list_df()
    joined = pd.merge(merged, stock_names[["ts_code", "name"]], on="ts_code", how="left")
    cols = [
        "select_date_d", "ts_code", "name",
        "ma35_3_d", "ma35_5_d", "ma3_d", "ma5_d",
        "macd_gloden_d", "dif_d", "dea_d", "macd_d",
        "kdj_gloden_d", "k_d", "d_d", "j_d",
        "ma35_3_w", "ma35_5_w", "ma3_w", "ma5_w",
        "macd_gloden_w", "dif_w", "dea_w", "macd_w",
        "kdj_gloden_w", "k_w", "d_w", "j_w",
    ]
    joined = joined[cols].round(2)
    joined.rename(columns={"select_date_d": "select_date"}, inplace=True)

    save_select_result_to_db(joined)
    filename = f"{date_str}_select.csv"
    joined.to_csv(filename, index=True)
    sendGroupFile(filename)


def _run_hk_select_trend(date_str):
    """执行趋势选股（港股）"""
    end = datetime.strptime(date_str, "%Y%m%d")
    start = end - timedelta(days=200)
    stock_df = get_hk_stock_data(None, start.strftime("%Y%m%d"), date_str)

    ma_daily = select_ma_by_daily(stock_df, date_str)
    ta_daily = select_macd_kdj_by_daily(stock_df, date_str)

    if ma_daily is None or len(ma_daily) == 0:
        sendMsg(f"{date_str}港股日均线数据不存在")
        return

    merged = pd.merge(ma_daily, ta_daily, on="ts_code", how="left", suffixes=("_d", "_d"))
    merged = merged[
        merged["macd_gloden"] | (merged["macd"] > 0) | merged["kdj_gloden"] | (merged["k"] > merged["d"])
    ]

    stock_names = get_hk_stock_list()
    joined = pd.merge(merged, stock_names[["ts_code", "name"]], on="ts_code", how="left")
    cols = [
        "select_date", "ts_code", "name",
        "ma35_3", "ma35_5", "ma3", "ma5",
        "macd_gloden", "dif", "dea", "macd",
        "kdj_gloden", "k", "d", "j",
    ]
    joined = joined[cols].round(2)

    filename = f"{date_str}_hk_select.csv"
    joined.to_csv(filename, index=True)
    sendGroupFile(filename)


def mock_select(ts_code, date_str, n):
    """Mock 选股：单只股票详细分析"""
    end = datetime.strptime(date_str, "%Y%m%d")
    start = end - timedelta(days=n - 1)
    stock_df = query_stock_data_df(ts_code, start.strftime("%Y%m%d"), date_str)
    if stock_df is None or len(stock_df) == 0:
        return None

    close_polyline = (
        stock_df[["ts_code", "trade_date", "high", "open", "close", "pre_close", "low", "vol"]]
        .groupby(["ts_code"])
        .tail(60)
    )
    result = (
        close_polyline.groupby(["ts_code"])
        .filter(lambda x: x["trade_date"].max() == date_str)
        .groupby(["ts_code"])
        .apply(polylineslope, include_groups=False)
        .reset_index()
    )
    if result is None or len(result) == 0:
        return None

    result.insert(0, "select_date", date_str)
    stock_names = query_stock_list_df()
    joined = pd.merge(result, stock_names[["ts_code", "name"]], on="ts_code", how="left")
    return joined.round(3)
