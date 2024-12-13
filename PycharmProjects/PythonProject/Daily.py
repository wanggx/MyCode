import pandas as pd
import tushare as ts
import numpy as np
from sqlalchemy import create_engine

ts.set_token('3252a9af155128787f44d053c563d6b156f03e80f0254899e8668ecc')

pro = ts.pro_api()

stock_pd = pd.read_csv('stock.csv', header=0, index_col=0)



engine = create_engine('mysql+pymysql://wgx_mysql:8Dm4PQU2pp6!C3y@rm-bp1eqw5j01245gr6jao.mysql.rds.aliyuncs.com:3306/stock')

stock_pd.to_sql('stock', engine, if_exists='replace', index=False)

# def saveStockDailyData(ts_codes, replace, daily_date):
#
#     df = pro.daily(ts_code=ts_codes, trade_date=daily_date)
#
#     engine = create_engine('mysql+pymysql://wgx_mysql:8Dm4PQU2pp6!C3y@rm-bp1eqw5j01245gr6jao.mysql.rds.aliyuncs.com:3306/stock')
#
#     if replace:
#         df.to_sql('stock_daily_temp', engine, if_exists='replace', index=False)
#     else:
#         df.to_sql('stock_daily_temp', con=engine, if_exists='append', index=False)
#
# idx = 0
# ts_codes = ''
# replace = True
# for index, stock in stock_pd.iterrows():
#     if idx % 500 == 0:
#         if ts_codes != '':
#             saveStockDailyData(ts_codes, replace, '20241213')
#             replace = False
#         ts_codes = stock['ts_code']
#     else:
#         ts_codes = ts_codes + "," + stock['ts_code']
#     idx = idx + 1
#
# if ts_codes != '':
#     saveStockDailyData(ts_codes, replace, '20241213')

