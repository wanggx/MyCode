import time
from moduledir.stockutil import *

# ts.set_token('3252a9af155128787f44d053c563d6b156f03e80f0254899e8668ecc')
#
# pro = ts.pro_api()

# downloadStockList()

stock_pd = getStockList()

print(len(stock_pd))

# ret = stock_pd[(stock_pd['ts_code'].str.startswith('300') == False) & (stock_pd['name'].str.contains('ST') == False)]
#
# print(ret)

# print(stock_pd[(stock_pd['ts_code'].str.startswith('300') == False) & (stock_pd['ts_code'].str.endswith('BJ') == False)])


# for date in pd.date_range('12/23/2024', periods=1):
#     date_str = date.strftime('%Y%m%d')
#     print("begin " + date_str)
#     savePdStockData(stock_pd, date_str)
#     mergeDailyData()
#     time.sleep(2)
#     print("end " + date_str)

