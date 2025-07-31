import logging
import calendar
import pandas as pd
import datetime
from moduledir.stockutil import *
from moduledir.dateutil import *
from moduledir.dateutil import saturday

from moduledir.stockutil import getStockData

from moduledir.dateutil import calculate_date

logger = logging.getLogger('myapp')

def fridayline(datestr):
    date = pd.to_datetime(datestr).date()
    return friday(date).strftime('%Y%m%d')


def lastday(datestr):
    date = pd.to_datetime(datestr).date()
    return last_day_of_monday(date).strftime('%Y%m%d')

def aggline(week):
    week.sort_values(by=['trade_date'], inplace=True, ascending=True)
    first_day = week.head(1).reset_index(drop=False)
    last_day = week.tail(1).reset_index(drop=False)
    high = week['high'].max()
    low = week['low'].min()
    vol = week['vol'].sum()
    amount = week['amount'].sum()
    open = first_day.at[0, 'open']
    close = last_day.at[0, 'close']
    change = close - open

    return pd.Series({'close': close, 'open': open, 'high': high, 'low': low , 'change': change, 'vol': vol, 'amount': amount})

def processWeekDf(stock_df):
    stock_df['week'] = stock_df['trade_date'].transform(fridayline)
    week_df = stock_df.groupby(['ts_code', 'week']).apply(aggline, include_groups=False)
    week_df['pre_close'] = week_df['close'].shift(1)
    # 过滤掉 pre_close 为 NaN 的行
    week_df = week_df.dropna(subset=['pre_close'])
    week_df['change'] = week_df['close'] - week_df['pre_close']
    week_df['pct_chg'] = (week_df['close'] - week_df['pre_close']) / week_df['pre_close']
    week_df.reset_index(inplace=True)
    week_df.rename(columns={'week':'trade_date'},  inplace=True)
    week_df = week_df.reindex(columns=['ts_code', 'trade_date', 'close', 'open', 'high', 'low', 'pre_close', 'change' , 'pct_chg', 'vol', 'amount'])
    saveWeekData(week_df.round(3))

def processMonthDf(stock_df):
    stock_df['month'] = stock_df['trade_date'].transform(lastday)
    month_df = stock_df.groupby(['ts_code', 'month']).apply(aggline, include_groups=False)
    month_df['pre_close'] = month_df['close'].shift(1)
    # 过滤掉 pre_close 为 NaN 的行
    month_df = month_df.dropna(subset=['pre_close'])
    month_df['change'] = month_df['close'] - month_df['pre_close']
    month_df['pct_chg'] = (month_df['close'] - month_df['pre_close']) / month_df['pre_close']
    month_df.reset_index(inplace=True)
    month_df.rename(columns={'month': 'trade_date'}, inplace=True)
    month_df = month_df.reindex(columns=['ts_code', 'trade_date', 'close', 'open', 'high', 'low', 'pre_close', 'change' , 'pct_chg', 'vol', 'amount'])
    saveMonthData(month_df.round(3))


def iterate_weeks(start_date_str, end_date_str):
    """
    给定一个开始时间和结束时间，遍历时间区间内的所有周。
    每周定义为周六到下周五。

    参数:
        start_date_str (str): 开始日期，格式为 'YYYYMMDD'
        end_date_str (str): 结束日期，格式为 'YYYYMMDD'

    返回:
        list: 包含所有周的开始和结束日期的元组列表，每个元组格式为 (周六, 周五)
    """
    # 将字符串转换为日期对象
    start_date = datetime.datetime.strptime(start_date_str, '%Y%m%d').date()
    end_date = datetime.datetime.strptime(end_date_str, '%Y%m%d').date()

    # 找到开始日期所在周的周六
    current_week_start = saturday(start_date)

    # 如果当前周的周六在结束日期之后，则没有完整的周
    if current_week_start > end_date:
        return

    # 遍历所有周
    while current_week_start <= end_date:
        # 计算该周的结束日期（下周五）
        current_week_end = current_week_start + datetime.timedelta(days=6)

        # 如果周的结束日期在指定范围内，则添加这一周
        if current_week_start <= end_date and current_week_end >= start_date:
            # 调整周的开始和结束日期，使其不超出指定范围
            actual_start = max(current_week_start, start_date)
            actual_end = min(current_week_end, end_date)
            logger.info(f"开始处理周数据，开始日期：{actual_start.strftime('%Y%m%d')}, 结束日期：{actual_end.strftime('%Y%m%d')}")
            pre_start_date = calculate_date(actual_start, -1)
            stock_pd = getStockData('000001.SZ', pre_start_date.strftime('%Y%m%d'), actual_end.strftime('%Y%m%d'))
            processWeekDf(stock_pd)
        # 移动到下一周的周六
        current_week_start += datetime.timedelta(days=7)


def iterate_months(start_date_str, end_date_str):
    """
    给定一个开始时间和结束时间，遍历时间区间内的所有月份。

    参数:
        start_date_str (str): 开始日期，格式为 'YYYYMMDD'
        end_date_str (str): 结束日期，格式为 'YYYYMMDD'

    返回:
        list: 包含所有月份的开始和结束日期的元组列表，每个元组格式为 (月初, 月末)
    """
    # 将字符串转换为日期对象
    start_date = datetime.datetime.strptime(start_date_str, '%Y%m%d').date()
    end_date = datetime.datetime.strptime(end_date_str, '%Y%m%d').date()

    # 从开始日期的月份开始
    current_year = start_date.year
    current_month = start_date.month

    while True:
        # 计算当前月份的第一天
        month_start = datetime.date(current_year, current_month, 1)

        # 计算当前月份的最后一天
        _, last_day_num = calendar.monthrange(current_year, current_month)
        month_end = datetime.date(current_year, current_month, last_day_num)

        # 如果月份的开始日期超过了结束日期，则退出循环
        if month_start > end_date:
            break

        # 如果月份的结束日期在开始日期之后，则添加这个月份
        if month_end >= start_date:
            # 调整月份的开始和结束日期，使其不超出指定范围
            actual_start = max(month_start, start_date)
            actual_end = min(month_end, end_date)
            logger.info(f"开始处理月数据，开始日期：{actual_start.strftime('%Y%m%d')}, 结束日期：{actual_end.strftime('%Y%m%d')}")
            pre_start_date = calculate_date(actual_start, -1)
            stock_pd = getStockData(None, pre_start_date.strftime('%Y%m%d'), actual_end.strftime('%Y%m%d'))
            processMonthDf(stock_pd)

        # 移动到下一个月
        if current_month == 12:
            current_year += 1
            current_month = 1
        else:
            current_month += 1

