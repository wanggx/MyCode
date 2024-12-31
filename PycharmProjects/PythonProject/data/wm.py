
import datetime
import pandas as pd
from moduledir.stockutil import *
from moduledir.dateutil import *


date = pd.to_datetime('20241116').date()
print(friday(date))
print(last_day_of_monday(date))

stock_pd = getStockTestData(None, None, None)

def fridayline(datestr):
    date = pd.to_datetime(datestr).date()
    return friday(date).strftime('%Y%m%d')


def lastday(datestr):
    date = pd.to_datetime(datestr).date()
    return last_day_of_monday(date).strftime('%Y%m%d')

def aggweekline(week):
    first_day = week.head(1).reset_index(drop=False)
    last_day = week.tail(1).reset_index(drop=False)
    high = week['open'].max()
    low = week['close'].min()
    vol = week['vol'].sum()
    amount = week['amount'].sum()
    open = first_day.at[0, 'open']
    close = last_day.at[0, 'close']
    change = close - open

    return pd.Series({'close': close, 'open': open, 'high': high, 'low': low , 'change': change, 'vol': vol, 'amount': amount})

def processWeekDf(stock_df):
    stock_df['week'] = stock_df['trade_date'].transform(fridayline)
    week_df = stock_df.groupby(['ts_code', 'week']).apply(aggweekline, include_groups=False)
    week_df['pre_close'] = week_df['close'].shift(1)
    week_df['change'] = week_df['close'] - week_df['pre_close']
    week_df['pct_chg'] = (week_df['close'] - week_df['pre_close']) / week_df['pre_close']
    week_df.reset_index(inplace=True)
    week_df.rename(columns={'week':'trade_date'},  inplace=True)
    week_df = week_df.reindex(columns=['ts_code', 'trade_date', 'close', 'open', 'high', 'low', 'pre_close', 'change' , 'pct_chg', 'vol', 'amount'])
    saveWeekData(week_df)

def processMonthDf(stock_df):
    stock_df['month'] = stock_df['trade_date'].transform(lastday)
    month_df = stock_df.groupby(['ts_code', 'month']).apply(aggweekline, include_groups=False)
    month_df['pre_close'] = month_df['close'].shift(1)
    month_df['change'] = month_df['close'] - month_df['pre_close']
    month_df['pct_chg'] = (month_df['close'] - month_df['pre_close']) / month_df['pre_close']
    month_df.reset_index(inplace=True)
    month_df.rename(columns={'month': 'trade_date'}, inplace=True)
    month_df = month_df.reindex(columns=['ts_code', 'trade_date', 'close', 'open', 'high', 'low', 'pre_close', 'change' , 'pct_chg', 'vol', 'amount'])
    saveMonthData(month_df)

processWeekDf(stock_pd)
# processMonthDf(stock_pd)
