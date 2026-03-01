import logging
import pandas as pd
from datetime import datetime, timedelta
from moduledir.stockutil import getStockList, saveStockTrendSelect
from backend.data.talib_metric import selectMacdAndKdjByDaily, selectMacdAndKdjByWeek
from backend.data.select_ma import selectMaByDaily, selectMaByWeek
from moduledir.chatutil import sendMsg, sendGroupFile

from hk.hkutil import getHkStockData, getHkStockList

from moduledir.stockutil import getStockData

logger = logging.getLogger('myapp')

def select(date_str):
    """
        date_str: 结束日期（字符串，格式如'20250710'）
        n: 向前推的天数
        """

    # 计算startDate
    end_date = datetime.strptime(date_str, '%Y%m%d')
    start_date = end_date - timedelta(days=200)
    start_str = start_date.strftime('%Y%m%d')
    stock_daily_df = getStockData(None, start_str, date_str)

    ma_df_daily = selectMaByDaily(stock_daily_df, date_str)
    ma_df_week = selectMaByWeek(date_str, 360)
    ta_df_daily = selectMacdAndKdjByDaily(stock_daily_df, date_str)
    ta_df_week = selectMacdAndKdjByWeek(date_str, 1200)

    select_df = ma_df_daily 

    if ma_df_daily is None or len(ma_df_daily) == 0:
        logger.warning('日均线数据不存在')
        sendMsg('日均线数据不存在')
        return

    select_df = pd.merge(select_df, ma_df_week, on='ts_code', how='left', suffixes=('_d', '_w'))
    select_df = pd.merge(select_df, ta_df_daily, on='ts_code', how='left', suffixes=('_d', '_w'))
    select_df = pd.merge(select_df, ta_df_week, on='ts_code', how='left', suffixes=('_d', '_w'))
    select_df = select_df[select_df['macd_gloden_w'] | select_df['kdj_gloden_w'] | select_df['macd_gloden_d'] | select_df['kdj_gloden_d']]

    stock_df = getStockList()
    join_df = pd.merge(select_df, stock_df[['ts_code', 'name']], on='ts_code', how='left')
    join_df = join_df[['select_date_d', 'ts_code', 'name',
                       'ma35_3_d', 'ma35_5_d','ma3_d', 'ma5_d',
                       'macd_gloden_d', 'dif_d', 'dea_d', 'macd_d',
                       'kdj_gloden_d', 'k_d', 'd_d', 'j_d',
                       'ma35_3_w', 'ma35_5_w', 'ma3_w', 'ma5_w',
                       'macd_gloden_w', 'dif_w', 'dea_w', 'macd_w',
                       'kdj_gloden_w', 'k_w', 'd_w', 'j_w']].round(2)

    join_df.rename(columns={'select_date_d': 'select_date'}, inplace=True)

    saveStockTrendSelect(join_df)

    file_name = date_str + '_select.csv'
    join_df.to_csv(file_name, index=True)
    sendGroupFile(file_name)

def selectHk(date_str):
    """
        date_str: 结束日期（字符串，格式如'20250710'）
        n: 向前推的天数
        """

    # 计算startDate
    end_date = datetime.strptime(date_str, '%Y%m%d')
    start_date = end_date - timedelta(days=200 - 1)
    start_str = start_date.strftime('%Y%m%d')
    stock_daily_df = getHkStockData(None, start_str, date_str)

    ma_df_daily = selectMaByDaily(stock_daily_df, date_str)
    ta_df_daily = selectMacdAndKdjByDaily(stock_daily_df, date_str)

    select_df = ma_df_daily

    if ma_df_daily is None or len(ma_df_daily) == 0:
        logger.warning('日均线数据不存在')
        sendMsg('日均线数据不存在')
        return

    select_df = pd.merge(select_df, ta_df_daily, on='ts_code', how='left', suffixes=('_d', '_d'))
    select_df = select_df[select_df['macd_gloden'] | select_df['kdj_gloden']]

    stock_df = getHkStockList()
    join_df = pd.merge(select_df, stock_df[['ts_code', 'name']], on='ts_code', how='left')
    join_df = join_df[['select_date', 'ts_code', 'name',
                       'ma35_3', 'ma35_5','ma3', 'ma5',
                       'macd_gloden', 'dif', 'dea', 'macd',
                       'kdj_gloden', 'k', 'd', 'j']].round(2)

    # saveStockTrendSelect(join_df)

    file_name = date_str + '_hk_select.csv'
    join_df.to_csv(file_name, index=True)
    sendGroupFile(file_name)