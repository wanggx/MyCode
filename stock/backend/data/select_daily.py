import logging
from datetime import datetime, timedelta
from moduledir.chatutil import *
import numpy as np
import pandas as pd
from sqlalchemy import false

from moduledir.dateutil import date_equal
from moduledir.stockutil import getStockData

logger = logging.getLogger('myapp')

def polyline3(df):
    try:
        dailys = df.tail(3)
        x = np.arange(len(dailys))
        y = dailys.values
        slope, _ = np.polyfit(x, y, 1)
        return slope
    except AttributeError as e:
        print(df)

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
    max = prev.max()
    latest = df.values[size-1]
    latest_prev = df.values[size-2]
    if (latest > mean * 2 and latest > latest_prev * 2 and latest > max):
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

    slope_series['out_date'] = False

    lastday = df.tail(1).reset_index(drop=False)
    sun = lastday.at[0, 'open'] < lastday.at[0, 'close']
    latest_trade_date = lastday.at[0, 'trade_date']
    if not date_equal(latest_trade_date, datetime.now()):
        slope_series['out_date'] = True

    slope_series['sun'] = sun

    return slope_series

def selectVolMagnify(date_str, n):
    """
    date_str: 结束日期（字符串，格式如'20250710'）
    n: 向前推的天数
    """
    # 计算startDate
    end_date = datetime.strptime(date_str, '%Y%m%d')
    start_date = end_date - timedelta(days=n-1)
    start_str = start_date.strftime('%Y%m%d')
    stock_daily_df = getStockData(None, start_str, date_str)

    close_polyline_df = stock_daily_df[['ts_code', 'trade_date', 'high', 'open', 'close', 'low', 'vol']].groupby(['ts_code']).tail(60)
    stock_polyline_df = close_polyline_df.groupby(['ts_code']).apply(polylineslope, include_groups=False)

    select_df = stock_polyline_df[(stock_polyline_df['vol_magnify'] > 0)
                                  & (stock_polyline_df['out_date'] == False)
                                  & (stock_polyline_df['sun'])
                                  & (stock_polyline_df['slope60'] > 0)
                                  & (stock_polyline_df['slope30'] > 0)
                                  & (stock_polyline_df['slope20'] > 0)]

    print(select_df.head(10))
    select_df.drop(columns=['out_date']).to_csv('vol.csv', index=True)
    sendGroupFile('vol.csv')

def selectTrend():
    stock_daily_df = getStockData(None, '20250501', '20250710')
    close_polyline_df = stock_daily_df[['ts_code', 'trade_date', 'high', 'open', 'close', 'low', 'vol']].groupby(
        ['ts_code']).tail(60)
    stock_polyline_df = close_polyline_df.groupby(['ts_code']).apply(polylineslope, include_groups=False)

    select_df = stock_polyline_df[((stock_polyline_df['out_date'] == False)
                                  & stock_polyline_df['slope60'] > 0)
                                  & (stock_polyline_df['slope30'] > 0)
                                  & (stock_polyline_df['slope20'] > 0)
                                  & (stock_polyline_df['slope10'] > 0)
                                  & (stock_polyline_df['slope5'] < 0)
                                  & (stock_polyline_df['slope3'] < 0)]

    print(select_df.head(10))
    select_df.to_csv('trend.csv', index=True)

    sendGroupFile('trend.csv')

def litterSun():
    stock_daily_df = getStockData(None, '20250501', '20250710')
    close_polyline_df = stock_daily_df[['ts_code', 'trade_date', 'high', 'open', 'close', 'low', 'vol']].groupby(
        ['ts_code']).tail(60)
    close_polyline_df[['ts_code', 'trade_date', 'close']].to_csv('close.csv', index=False)
    stock_polyline_df = close_polyline_df.groupby(['ts_code']).apply(polylineslope, include_groups=False)

    select_df = stock_polyline_df[((stock_polyline_df['out_date'] == False)
                                   & stock_polyline_df['slope60'] > 0)
                                  & (stock_polyline_df['slope30'] > 0)
                                  & (stock_polyline_df['slope20'] > 0)
                                  & (stock_polyline_df['slope10'] > 0)]

    print(select_df.head(10))
    select_df.to_csv('litter.csv', index=True)

    sendGroupFile('litter.csv')






