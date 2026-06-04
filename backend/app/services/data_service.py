# -*- coding: utf-8 -*-
"""
数据服务：日线下载、周月聚合、港股同步
"""

import logging
import time
import threading
from datetime import datetime, timedelta
import calendar

from app.repositories.stock_daily_repo import (
    query_stock_data_df,
    save_stock_daily_batch,
    merge_daily_data,
    save_week_data,
    save_month_data,
    delete_week_data,
    delete_month_data,
)
from app.repositories.stock_repo import query_stock_list_df
from app.repositories.hk_stock_repo import (
    save_hk_daily,
    merge_hk_daily_data,
)
from app.analysis.aggregation import process_week_df, process_month_df
from app.utils.dateutil import calculate_date, saturday

logger = logging.getLogger("myapp")


def download_daily_data(start_date, end_date):
    """
    下载日线数据并合并
    start_date, end_date: YYYYMMDD
    """
    try:
        start_dt = datetime.strptime(start_date, "%Y%m%d")
        end_dt = datetime.strptime(end_date, "%Y%m%d")
        if start_dt > end_dt:
            raise ValueError("开始日期不能大于结束日期")

        stock_pd = query_stock_list_df()
        logger.info(f"开始下载数据 {start_date}~{end_date}, 股票数: {len(stock_pd)}")

        current = start_dt
        while current <= end_dt:
            date_str = current.strftime("%Y%m%d")
            logger.info(f"下载数据: {date_str}")

            idx, ts_codes, replace = 0, "", True
            for _, stock in stock_pd.iterrows():
                if idx % 500 == 0:
                    if ts_codes:
                        save_stock_daily_batch(ts_codes, date_str, replace)
                        replace = False
                    ts_codes = stock["ts_code"]
                else:
                    ts_codes += "," + stock["ts_code"]
                idx += 1
            if ts_codes:
                save_stock_daily_batch(ts_codes, date_str, replace)

            merge_daily_data()
            logger.info(f"下载完成: {date_str}")
            time.sleep(2)
            current += timedelta(days=1)

        _download_hk_daily()
    except Exception as e:
        logger.error(f"下载数据时发生错误: {e}")


def _download_hk_daily():
    """同步港股日线数据"""
    try:
        from hk.hk_daily import saveHKStockDaily
        saveHKStockDaily("")
        merge_hk_daily_data()
    except Exception as e:
        logger.error(f"获取港股数据异常: {e}")


def iterate_weeks(start_date_str, end_date_str):
    """遍历周区间，聚合周线"""
    start = datetime.strptime(start_date_str, "%Y%m%d").date()
    end = datetime.strptime(end_date_str, "%Y%m%d").date()
    current_start = saturday(start)

    if current_start > end:
        return

    while current_start <= end:
        current_end = current_start + timedelta(days=6)
        if current_start <= end and current_end >= start:
            actual_start = max(current_start, start)
            actual_end = min(current_end, end)
            logger.info(f"处理周数据: {actual_start.strftime('%Y%m%d')}~{actual_end.strftime('%Y%m%d')}")
            pre_start = calculate_date(actual_start, 0)
            delete_week_data(pre_start.strftime("%Y%m%d"), actual_end.strftime("%Y%m%d"))
            stock_df = query_stock_data_df(
                None, pre_start.strftime("%Y%m%d"), actual_end.strftime("%Y%m%d")
            )
            week_df = process_week_df(stock_df)
            if week_df is not None:
                save_week_data(week_df)
        current_start += timedelta(days=7)


def iterate_months(start_date_str, end_date_str):
    """遍历月区间，聚合月线"""
    start = datetime.strptime(start_date_str, "%Y%m%d").date()
    end = datetime.strptime(end_date_str, "%Y%m%d").date()
    year, month = start.year, start.month

    while True:
        month_start = datetime.date(year, month, 1)
        _, last_day_num = calendar.monthrange(year, month)
        month_end = datetime.date(year, month, last_day_num)

        if month_start > end:
            break
        if month_end >= start:
            actual_start = max(month_start, start)
            actual_end = min(month_end, end)
            logger.info(f"处理月数据: {actual_start.strftime('%Y%m%d')}~{actual_end.strftime('%Y%m%d')}")
            pre_start = calculate_date(actual_start, 0)
            delete_month_data(pre_start.strftime("%Y%m%d"), actual_end.strftime("%Y%m%d"))
            stock_df = query_stock_data_df(
                None, pre_start.strftime("%Y%m%d"), actual_end.strftime("%Y%m%d")
            )
            month_df = process_month_df(stock_df)
            if month_df is not None:
                save_month_data(month_df)

        if month == 12:
            year += 1
            month = 1
        else:
            month += 1
