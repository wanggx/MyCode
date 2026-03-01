from datetime import datetime, timedelta

import pandas as pd

from moduledir.chatutil import sendMsg, sendGroupFile
from moduledir.stockutil import getStockData, getStockList, getStockWeekData


def ma(df):
    if df is None or len(df) == 0:
        print('计算ma均线: 输入df为空')
        return None
    try:
        df.sort_values(by=['trade_date'], inplace=True, ascending=True)
        df['ma3'] = df['close'].rolling(3).mean()
        df['ma5'] = df['close'].rolling(5).mean()

        # 创建一个辅助函数来处理整个DataFrame
        def check_last_n_days(n):
            last_n_days = df.tail(n)
            return (last_n_days['ma3'] > last_n_days['ma5']).all()

        # 使用 agg 进行多列聚合
        result = pd.Series({
            'ma35_3': check_last_n_days(3),
            'ma35_5': check_last_n_days(5),
            'ma3': df.tail(1)['ma3'].values[0],
            'ma5': df.tail(1)['ma5'].values[0]
        })

        return result
    except Exception as e:
        print(f'计算ma异常: {e}')
        return None


def processMa(df):
    if df is None or len(df) == 0:
        return None
    return df.groupby(['ts_code']).apply(ma, include_groups=False).reset_index()

def selectMaByWeek(date_str, n):
    """
        date_str: 结束日期（字符串，格式如'20250710'）
        n: 向前推的天数
        """
    # 计算startDate
    end_date = datetime.strptime(date_str, '%Y%m%d')
    start_date = end_date - timedelta(days=n - 1)
    start_str = start_date.strftime('%Y%m%d')
    stock_daily_df = getStockWeekData(None, start_str, date_str)

    close_ma_df = (stock_daily_df[['ts_code', 'trade_date', 'high', 'open', 'close', 'low']]
                   .groupby(['ts_code']).tail(60))
    filter_df = close_ma_df.groupby(['ts_code']).filter(lambda x: x['trade_date'].max() == date_str)
    stock_ma_df = processMa(filter_df)
    if stock_ma_df is None or len(stock_ma_df) == 0:
        return pd.DataFrame({
            'select_date': pd.Series([], dtype='str'),
            'ts_code': pd.Series([], dtype='str'),
            'ma35_3': pd.Series([], dtype='float64'),
            'ma35_5': pd.Series([], dtype='float64'),
            'ma3': pd.Series([], dtype='float64'),
            'ma5': pd.Series([], dtype='float64')
        })
    stock_ma_df = stock_ma_df[stock_ma_df['ma35_3']]
    stock_ma_df.insert(0, 'select_date', date_str)
    return stock_ma_df[['select_date', 'ts_code', 'ma35_3', 'ma35_5', 'ma3', 'ma5']].round(3)

def selectMaByDaily(stock_daily_df, date_str):
    """
    date_str: 结束日期（字符串，格式如'20250710'）
    """

    close_ma_df = stock_daily_df[['ts_code', 'trade_date', 'high', 'open', 'close', 'low']].groupby(['ts_code']).tail(60)
    filter_df = close_ma_df.groupby(['ts_code']).filter(lambda x: x['trade_date'].max() == date_str)
    stock_ma_df = processMa(filter_df)
    if stock_ma_df is None or len(stock_ma_df) == 0:
        sendMsg(f"{date_str}没有选中任何股票")
        return None
    stock_ma_df = stock_ma_df[stock_ma_df['ma35_3'] & stock_ma_df['ma35_5']]
    stock_ma_df.insert(0, 'select_date', date_str)
    return stock_ma_df[['select_date', 'ts_code', 'ma35_3', 'ma35_5', 'ma3', 'ma5']].round(3)
