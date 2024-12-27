from datetime import datetime

import numpy as np
import pandas as pd
from sqlalchemy import false

from moduledir.stockutil import getStockData
from moduledir.stockutil import getStockTestData
print(datetime.now())
stock_daily_df = getStockData(None, None, None)
print(datetime.now())

def polyline3(df):
    dailys = df.tail(3)
    x = np.arange(len(dailys))
    y = dailys.values
    slope, _ = np.polyfit(x, y, 1)
    return slope

def polyline5(df):
    dailys = df.tail(5)
    x = np.arange(len(dailys))
    y = dailys.values
    slope, _ = np.polyfit(x, y, 1)
    return slope

def polyline10(df):
    dailys = df.tail(10)
    x = np.arange(len(dailys))
    y = dailys.values
    slope, _ = np.polyfit(x, y, 1)
    return slope

def polyline20(df):
    dailys = df.tail(20)
    x = np.arange(len(dailys))
    y = dailys.values
    slope, _ = np.polyfit(x, y, 1)
    return slope

def polyline30(df):
    dailys = df.tail(30)
    x = np.arange(len(dailys))
    y = dailys.values
    slope, _ = np.polyfit(x, y, 1)
    return slope

def polyline60(df):
    dailys = df.tail(60)
    x = np.arange(len(dailys))
    y = dailys.values
    slope, _ = np.polyfit(x, y, 1)
    return slope

def volmagnify(df):
    size = len(df)
    prev = df.values[0:size-1]
    mean = prev.mean()
    latest = df.values[size-1]
    latest_prev = df.values[size-2]
    if (latest > mean * 2 and latest > latest_prev * 2):
        return latest / mean
    return 0

def polylineslope(df):
    df.sort_values(by=['trade_date'], inplace=True, ascending=True)
    slope_series = df['close'].agg({
        'slope3': polyline3,
        'slope5': polyline5,
        'slope10': polyline10,
        'slope20': polyline20,
        'slope30': polyline30,
        'slope60': polyline60,
    })
    vol_magnify = df['vol'].tail(20).agg(volmagnify)
    slope_series['vol_magnify'] = vol_magnify
    return slope_series


close_polyline_df = stock_daily_df[['ts_code', 'trade_date', 'close', 'vol']].groupby(['ts_code']).tail(60)
stock_polyline_df = close_polyline_df.groupby(['ts_code']).apply(polylineslope, include_groups=False)

select_df = stock_polyline_df[(stock_polyline_df['vol_magnify'] > 0)
                              & (stock_polyline_df['slope60'] > 0)
                              & (stock_polyline_df['slope30'] > 0)
                              & (stock_polyline_df['slope20'] > 0)]


print(select_df.head(10))
select_df.to_csv('merge.csv', index=True)




