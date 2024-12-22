from datetime import datetime

import numpy as np
import pandas as pd

from moduledir.stockutil import getStockData
from moduledir.stockutil import getStockTestData
print(datetime.now())
stock_daily_df = getStockData(None, None, None)
print(datetime.now())

def polyline(dailys):
    x = np.arange(len(dailys))
    y = dailys.values
    slope, _ = np.polyfit(x, y, 1)
    return slope

for day in (5, 10, 20, 30, 54):
    close_polyline_df = stock_daily_df[['ts_code', 'close']].groupby(['ts_code']).tail(day)
    stock_polyline_df = close_polyline_df.groupby(['ts_code']).agg(polyline)

    print(datetime.now())
    stock_polyline_df.to_csv(str(day) + ".csv")

# print(stock_polyline_df.head(10))

