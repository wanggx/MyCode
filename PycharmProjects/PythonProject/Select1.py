from datetime import datetime

import numpy as np
import pandas as pd

from moduledir.stockutil import getStockData
print(datetime.now())
stock_daily_df = getStockData(None, None, None)
print(datetime.now())

def polyline(dailys):
    size = len(dailys)
    prev = dailys.values[0:size-1]
    mean = prev.mean()
    latest = dailys.values[size-1]
    latest_pre = dailys.values[size-2]
    if (latest > mean * 2 and latest > latest_pre * 2):
        return 1
    return 0


close_polyline_df = stock_daily_df[['ts_code', 'vol']].groupby(['ts_code']).tail(20)
stock_polyline_df = close_polyline_df.groupby(['ts_code']).agg(polyline)

print(datetime.now())
stock_polyline_df[stock_polyline_df['vol'] > 0].to_csv(str(20) + "vol.csv")