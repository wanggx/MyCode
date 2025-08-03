
import pandas as pd
from moduledir.stockutil import getStockList
from backend.data.talib_metric import selectMacdAndKdjByDaily, selectMacdAndKdjByWeek
from backend.data.select_ma import selectMaByDaily, selectMaByWeek
from moduledir.chatutil import sendMsg, sendGroupFile


def select(date_str):
    """
        date_str: 结束日期（字符串，格式如'20250710'）
        n: 向前推的天数
        """
    ma_df_daily = selectMaByDaily(date_str, 200)
    ma_df_week = selectMaByWeek(date_str, 360)
    ta_df_daily = selectMacdAndKdjByDaily(date_str, 200)
    ta_df_week = selectMacdAndKdjByWeek(date_str, 360)

    stock_df = getStockList()
    select_df = (pd.merge(ma_df_daily, ma_df_week, on='ts_code', how='left', suffixes=('_d', '_w'))
                 .merge(ta_df_daily, on='ts_code', how='left', suffixes=('_d', '_w'))
                 .merge(ta_df_week, on='ts_code', how='left', suffixes=('_d', '_w')))

    select_df = select_df[select_df['macd_gloden_d'] | select_df['kdj_gloden_d']
                          | select_df['macd_gloden_w'] | select_df['kdj_gloden_w']]

    print(len(select_df))

    join_df = pd.merge(select_df, stock_df[['ts_code', 'name']], on='ts_code', how='left')
    join_df = join_df[['select_date_d', 'ts_code', 'name',
                       'ma35_3_d', 'ma35_5_d','ma3_d', 'ma5_d',
                       'macd_gloden_d', 'dif_d', 'dea_d', 'macd_d',
                       'kdj_gloden_d', 'k_d', 'd_d', 'j_d',
                       'ma35_3_w', 'ma35_5_w', 'ma3_w', 'ma5_w',
                       'macd_gloden_w', 'dif_w', 'dea_w', 'macd_w',
                       'kdj_gloden_w', 'k_w', 'd_w', 'j_w']].round(2)

    file_name = date_str + '_select.csv'
    join_df.to_csv(file_name, index=True)
    sendGroupFile(file_name)