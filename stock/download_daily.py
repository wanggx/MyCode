
from datetime import datetime
from moduledir.stockutil import *

def download_daily():
    # 获取当前日期并格式化为 %Y%m%d
    current_date = datetime.now().strftime("%Y%m%d")
    stock_pd = getStockList()
    print(len(stock_pd))
    print("begin " + current_date)
    savePdStockData(stock_pd, current_date)
    mergeDailyData()
    print("end " + current_date)