
import pandas as pd
from moduledir.stockutil import *
from moduledir.dateutil import *


date = pd.to_datetime('20241116').date()
print(friday(date))
print(last_day_of_monday(date))

# stock_pd = pd.read_csv('stock.csv', header=0, index_col=0)
#
# for date in pd.date_range('12/13/2024', periods=2, freq='W'):
#
#     print(date.week)
#     print(date.month)

    # print(date)
    # date_str = date.strftime('%Y%m%d')
    # print("begin " + date_str)
    # savePdStockWeekMonthData(stock_pd, date_str)
    # # mergeDailyData()
    # time.sleep(2)
    # print("end " + date_str)