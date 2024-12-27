

import pandas as pd
import tushare as ts
from sqlalchemy import create_engine, text

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

def mergeDailyData():
    engine = create_engine('mysql+pymysql://' + mysql_user + ':' + mysql_pass + '@' + mysql_url + '/' + mysql_db)
    sql = text("insert into stock_daily select t.* from stock_daily_temp t left join stock_daily d on" +
               " t.ts_code = d.ts_code and t.trade_date = d.trade_date where d.ts_code is null")
    with engine.connect() as conn:
        conn.execute(sql)

def downloadStockList():
    engine = create_engine('mysql+pymysql://' + mysql_user + ':' + mysql_pass + '@' + mysql_url + '/' + mysql_db)
    stock_df = pd.read_sql_table('stock', con = engine)
    stock_df.to_csv('stock.csv')


def getStockData(ts_code, start_date, end_date):
    engine = create_engine('mysql+pymysql://' + mysql_user + ':' + mysql_pass + '@' + mysql_url + '/' + mysql_db)
    if ts_code is not None:
        stock_sql = "select * from stock_daily  where ts_code = \'" + ts_code + "\'"
    else:
        stock_sql = ('select * from stock_daily where ts_code in ' +
                     '(select ts_code from stock where ts_code not like \'688%%\' and ts_code not like \'30%%\' and ts_code not like \'%%BJ\' and name not like \'%%ST%%\')')
    stock_df = pd.read_sql(stock_sql, con=engine)
    return stock_df

def getStockTestData(ts_code, start_date, end_date):
    engine = create_engine('mysql+pymysql://' + mysql_user + ':' + mysql_pass + '@' + mysql_url + '/' + mysql_db)
    if ts_code is not None:
        stock_sql = "select * from stock_daily_test  where ts_code = \'" + ts_code + "\'"
    else:
        stock_sql = ('select * from stock_daily_test where ts_code in ' +
                     '(select ts_code from stock where ts_code not like \'688%%\' and ts_code not like \'30%%\')')
    stock_df = pd.read_sql(stock_sql, con=engine)
    return stock_df
