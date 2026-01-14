import logging
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from moduledir.chatutil import *
from moduledir.dateutil import date_equal
from moduledir.stockutil import getStockData, getStockList, saveStockSelect

logger = logging.getLogger('myapp')

def polyline(df, n):
    dailys = df.tail(n)
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

def has_low_shadow(df):
    t_df = df.copy()
    t_df.loc[:, "drop_pct"] = (df['low'] - df['pre_close']) / df['pre_close'] * 100
    # 筛选符合条件的行：翻红且最低价跌幅 >= 5%
    t_df.loc[:, 'low_shadow'] = (df['close'] > df['open']) & (t_df['drop_pct'] <= -5.0)
    return t_df['low_shadow'].values[0]

def polylineslope(df):
    if df is None or len(df) == 0:
        print('polylineslope: 输入df为空')
        return None
    try:
        df.sort_values(by=['trade_date'], inplace=True, ascending=True)
        slope_series = df['close'].agg({
            'slope3': lambda x: polyline(x, 3),
            'slope5': lambda x: polyline(x, 5),
            'slope10': lambda x: polyline(x, 10),
            'slope20': lambda x: polyline(x, 20),
            'slope30': lambda x: polyline(x, 30),
            'slope60': lambda x: polyline(x, 60),
        })

        slope_series['low_shadow'] = has_low_shadow(df.tail(1))

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
    except Exception as e:
        print(f'polylineslope异常: {e}')
        return None

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

    close_polyline_df = stock_daily_df[['ts_code', 'trade_date', 'high', 'open', 'close', 'pre_close', 'low', 'vol']].groupby(['ts_code']).tail(60)
    stock_polyline_df = (close_polyline_df.groupby(['ts_code'])
                         .filter(lambda x: x['trade_date'].max() == date_str)
                         .groupby(['ts_code'])
                         .apply(polylineslope, include_groups=False).reset_index())
    if stock_polyline_df is None or len(stock_polyline_df) == 0:
        return None
    print(stock_polyline_df.head(2))
    select_df = stock_polyline_df[(stock_polyline_df['vol_magnify'] > 0)
                                #   & (stock_polyline_df['out_date'] == False)
                                #  & (stock_polyline_df['sun'])
                                #  & (stock_polyline_df['slope60'] > 0)
                                #  & (stock_polyline_df['slope30'] > 0)
                                #  & (stock_polyline_df['slope20'] > 0)
                                ]
    print(select_df.columns)
    select_df.insert(0, 'select_date', date_str)
    select_df.rename(columns={'slope3': 'trend3',
                              'slope5': 'trend5',
                              'slope10': 'trend10',
                              'slope20': 'trend20',
                              'slope30': 'trend30',
                              'vol_magnify': 'vol'}, inplace=True)
    stock_df = getStockList()
    join_df = pd.merge(select_df, stock_df[['ts_code', 'name']], on='ts_code', how='left')
    final_df = join_df[['select_date', 'ts_code', 'name', 'vol', 'trend3', 'trend5', 'trend10', 'trend20', 'trend30']].round(3)

    filename = date_str + '_vol.csv'
    final_df.to_csv(filename, index=True)
    saveStockSelect(final_df)
    sendGroupFile(filename)



def selectLowTrendLowShadow(date_str, n):
    """
    date_str: 结束日期（字符串，格式如'20250710'）
    n: 向前推的天数
    """
    # 计算startDate
    end_date = datetime.strptime(date_str, '%Y%m%d')
    start_date = end_date - timedelta(days=n-1)
    start_str = start_date.strftime('%Y%m%d')
    stock_daily_df = getStockData(None, start_str, date_str)

    close_polyline_df = stock_daily_df[['ts_code', 'trade_date', 'high', 'open', 'pre_close', 'close', 'low', 'vol']].groupby(['ts_code']).tail(60)
    stock_polyline_df = (close_polyline_df.groupby(['ts_code'])
                         .filter(lambda x: x['trade_date'].max() == date_str)
                         .groupby(['ts_code'])
                         .apply(polylineslope, include_groups=False).reset_index())
    if stock_polyline_df is None or len(stock_polyline_df) == 0:
        return None
    print(stock_polyline_df.head(2))
    select_df = stock_polyline_df[(stock_polyline_df['low_shadow'])]

    filename = date_str + '_lowshadow.csv'
    select_df.round(3).to_csv(filename, index=True)
    sendGroupFile(filename)


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

def mockSelect(ts_code, date_str, n):
    """
    ts_code: 股票代码，仅处理该股票
    date_str: 结束日期（字符串，格式如'20250710'）
    n: 向前推的天数
    返回：最终DataFrame
    """
    from datetime import datetime, timedelta
    end_date = datetime.strptime(date_str, '%Y%m%d')
    start_date = end_date - timedelta(days=n-1)
    start_str = start_date.strftime('%Y%m%d')
    stock_daily_df = getStockData(ts_code, start_str, date_str)
    if stock_daily_df is None or len(stock_daily_df) == 0:
        return None
    close_polyline_df = stock_daily_df[['ts_code', 'trade_date', 'high', 'open', 'close', 'pre_close', 'low', 'vol']].groupby(['ts_code']).tail(60)
    stock_polyline_df = (close_polyline_df.groupby(['ts_code'])
                         .filter(lambda x: x['trade_date'].max() == date_str)
                         .groupby(['ts_code'])
                         .apply(polylineslope, include_groups=False).reset_index())
    if stock_polyline_df is None or len(stock_polyline_df) == 0:
        return None
    select_df = stock_polyline_df
    select_df.insert(0, 'select_date', date_str)
    from moduledir.stockutil import getStockList
    stock_df = getStockList()
    join_df = pd.merge(select_df, stock_df[['ts_code', 'name']], on='ts_code', how='left')
    final_df = join_df.round(3)
    return final_df






