

import pandas as pd
import tushare as ts
from sqlalchemy import create_engine

ts.set_token('3252a9af155128787f44d053c563d6b156f03e80f0254899e8668ecc')

pro = ts.pro_api()

mysql_user = 'wgx_mysql'
mysql_pass = '8Dm4PQU2pp6!C3y'
mysql_url = 'rm-bp1eqw5j01245gr6jao.mysql.rds.aliyuncs.com:3306'
mysql_db = 'stock'

def saveStockDailyData(ts_codes, replace, daily_date):

    df = pro.daily(ts_code=ts_codes, trade_date=daily_date)
    engine = create_engine('mysql+pymysql://' + mysql_user + ':' + mysql_pass + '@' + mysql_url + '/' + mysql_db)

    if replace:
        df.to_sql('stock_daily_temp', con=engine, if_exists='replace', index=False)
    else:
        df.to_sql('stock_daily_temp', con=engine, if_exists='append', index=False)

def savePdStockData(stock_pd, daily_date):
    idx = 0
    ts_codes = ''
    replace = True
    for index, stock in stock_pd.iterrows():
        if idx % 500 == 0:
            if ts_codes != '':
                saveStockDailyData(ts_codes, replace, daily_date)
                replace = False
            ts_codes = stock['ts_code']
        else:
            ts_codes = ts_codes + "," + stock['ts_code']
        idx = idx + 1

    if ts_codes != '':
        saveStockDailyData(ts_codes, replace, daily_date)