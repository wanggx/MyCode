import logging
import talib
import numpy as np
from datetime import datetime, timedelta
from moduledir.stockutil import getStockData, getStockWeekData

logger = logging.getLogger('myapp')

def calc_macd_and_kdj(df):
    stock_pd = df
    stock_pd['dif'], stock_pd['dea'], _ = talib.MACD(stock_pd['close'], fastperiod=12, slowperiod=26, signalperiod=9)
    stock_pd['macd'] = (stock_pd['dif'] - stock_pd['dea']) * 2
    stock_pd['macd_gloden'] = (stock_pd['macd'] > 0) & (stock_pd['macd'].shift(1) < 0)

    stock_pd['k'], stock_pd['d'] = talib.STOCH(stock_pd['high'], stock_pd['low'], stock_pd['close'],9, 5, slowk_matype=1, slowd_period=5, slowd_matype=1)
    stock_pd['j'] = 3 * stock_pd['k'] - 2 * stock_pd['d']

    # 判断金叉和死叉
    stock_pd['kdj_gloden'] = np.where((stock_pd['k'].shift(1) < stock_pd['d'].shift(1)) & (stock_pd['k'] > stock_pd['d']), True, False)
    # stock_pd['kdj_gloden'] = np.where((stock_pd['k'].shift(1) > stock_pd['d'].shift(1)) & (stock_pd['k'] < stock_pd['d']), 'Dead Cross', stock_pd['kdj_gloden'])
    return stock_pd.tail(1)


def process_macd_and_kdj(stock_df):
    if stock_df is None or len(stock_df) == 0:
        return None
    final_df = stock_df.groupby('ts_code').apply(calc_macd_and_kdj, include_groups=False).reset_index()

    return final_df[['ts_code', 'trade_date', 'macd_gloden', 'dif', 'dea', 'macd', 'kdj_gloden', 'k', 'd', 'j', ]].round(2)


def selectMacdAndKdjByDaily(date_str, n):
    end_date = datetime.strptime(date_str, '%Y%m%d')
    start_date = end_date - timedelta(days=n - 1)
    start_str = start_date.strftime('%Y%m%d')
    stock_daily_df = getStockData(None, start_str, date_str)
    if stock_daily_df is None or len(stock_daily_df) == 0:
        return None
    final_df = stock_daily_df.groupby('ts_code').filter(lambda x: x['trade_date'].max() == date_str)

    return process_macd_and_kdj(final_df)

def selectMacdAndKdjByWeek(date_str, n):
    end_date = datetime.strptime(date_str, '%Y%m%d')
    start_date = end_date - timedelta(days=n - 1)
    start_str = start_date.strftime('%Y%m%d')
    stock_daily_df = getStockWeekData(None, start_str, date_str)
    if stock_daily_df is None or len(stock_daily_df) == 0:
        return None
    final_df = stock_daily_df.groupby('ts_code').filter(lambda x: x['trade_date'].max() == date_str)

    return process_macd_and_kdj(final_df)
