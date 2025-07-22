import logging
from datetime import datetime
from moduledir.stockutil import *
from backend.data.select_daily import selectVolMagnify
from backend.data.select_daily import selectLowTrendLowShadow

logger = logging.getLogger('myapp')

def download_daily():
    # 获取当前日期并格式化为 %Y%m%d
    current_date = datetime.now().strftime("%Y%m%d")
    stock_pd = getStockList()
    logger.info(len(stock_pd))
    logger.info(("begin " + current_date))
    savePdStockData(stock_pd, current_date)
    mergeDailyData()
    logger.info(("end " + current_date))

    selectVolMagnify(current_date, 100)
    selectLowTrendLowShadow(current_date, 100)
