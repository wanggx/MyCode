import logging
from datetime import datetime
from moduledir.stockutil import *
from backend.data.select_daily import selectVolMagnify
from backend.data.select_daily import selectLowTrendLowShadow
from backend.data.select import select
from moduledir.dateutil import get_current_saturday_and_month_start
from backend.data.wm import iterate_weeks, iterate_months

logger = logging.getLogger('myapp')

def download_daily():
    # 获取当前日期并格式化为 %Y%m%d
    current_date = datetime.now()
    current_date_str = current_date.strftime("%Y%m%d")
    stock_pd = getStockList()
    logger.info(len(stock_pd))
    logger.info(("begin " + current_date_str))
    savePdStockData(stock_pd, current_date_str)
    mergeDailyData()
    logger.info(("end " + current_date_str))

    selectVolMagnify(current_date_str, 100)
    selectLowTrendLowShadow(current_date_str, 100)
    select(current_date_str)

    saturday, month_start = get_current_saturday_and_month_start(current_date)

    iterate_weeks(saturday, current_date_str)
    iterate_months(month_start, current_date_str)

