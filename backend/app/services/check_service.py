# -*- coding: utf-8 -*-
"""
数据校验服务：数据覆盖检查、补录
"""

import re
import threading
from datetime import datetime

from app.repositories.check_repo import query_daily_count_by_date
from app.services.data_service import download_daily_data, iterate_weeks, iterate_months


def check_daily_coverage(start_date, end_date, page=1, page_size=10):
    """检查日线数据覆盖情况"""
    if page < 1:
        page = 1
    if page_size < 1:
        page_size = 10
    return query_daily_count_by_date(start_date, end_date, page, page_size)


def trigger_daily_add(start_date, end_date, data_type="d"):
    """触发数据补录（参数校验 + 异步执行）"""
    date_pattern = re.compile(r"^\d{8}$")
    if not start_date or not end_date:
        return False, "start_date和end_date必填"
    if not date_pattern.match(start_date) or not date_pattern.match(end_date):
        return False, "日期格式应为yyyyMMdd"

    try:
        start_dt = datetime.strptime(start_date, "%Y%m%d")
        end_dt = datetime.strptime(end_date, "%Y%m%d")
        if start_dt > end_dt:
            return False, "开始日期不能大于结束日期"
        if (end_dt - start_dt).days > 30 and data_type == "d":
            return False, "补录区间不能超过一个月"
    except ValueError:
        return False, "日期格式错误"

    def _async_download():
        if data_type == "d":
            download_daily_data(start_date, end_date)
        elif data_type == "w":
            iterate_weeks(start_date, end_date)
        elif data_type == "m":
            iterate_months(start_date, end_date)

    threading.Thread(target=_async_download, daemon=True).start()
    return True, "补录任务已提交，正在后台处理"
