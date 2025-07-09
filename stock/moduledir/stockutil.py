

import pandas as pd
import tushare as ts
from sqlalchemy import create_engine, text
from sqlalchemy.dialects.mysql import insert

ts.set_token('3252a9af155128787f44d053c563d6b156f03e80f0254899e8668ecc')

pro = ts.pro_api()

mysql_user = 'root'
mysql_pass = '8Dm4PQU2pp6!C3y'
mysql_url = 'rm-bp160jkc22y874i30to.mysql.rds.aliyuncs.com:3306'
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

def getStockList():
    engine = create_engine('mysql+pymysql://' + mysql_user + ':' + mysql_pass + '@' + mysql_url + '/' + mysql_db)
    stock_df = pd.read_sql_table('stock', con=engine)
    return stock_df[(stock_df['ts_code'].str.startswith('30') == False) &
                    (stock_df['ts_code'].str.startswith('68') == False) &
                    (stock_df['ts_code'].str.endswith('BJ') == False) &
                    (stock_df['name'].str.contains('ST') == False)]

def getStockData(ts_code, start_date, end_date):
    engine = create_engine('mysql+pymysql://' + mysql_user + ':' + mysql_pass + '@' + mysql_url + '/' + mysql_db)
    if ts_code is not None:
        stock_sql = "select * from stock_daily  where ts_code = \'" + ts_code + "\'"
        if start_date is not None and end_date is not None:
            stock_sql = stock_sql + " and trade_date >= \'" + start_date + "\' and trade_date <= \'" + end_date + "\'"
    else:
        stock_sql = ('select * from stock_daily where ts_code in ' +
                     '(select ts_code from stock where ts_code not like \'688%%\' and ts_code not like \'30%%\' and ts_code not like \'%%BJ\' and name not like \'%%ST%%\')')
        if start_date is not None and end_date is not None:
            stock_sql = stock_sql + " and trade_date >= \'" + start_date + "\' and trade_date <= \'" + end_date + "\'"
    stock_df = pd.read_sql(stock_sql, con=engine)
    return stock_df

def getStockTestData(ts_code, start_date, end_date):
    engine = create_engine('mysql+pymysql://' + mysql_user + ':' + mysql_pass + '@' + mysql_url + '/' + mysql_db)
    if ts_code is not None:
        stock_sql = "select * from stock_daily_test  where ts_code = \'" + ts_code + "\'"
        if start_date is not None and end_date is not None:
            stock_sql = stock_sql + " and trade_date >= \'" + start_date + "\' and trade_date <= \'" + end_date + "\'"
    else:
        stock_sql = ('select * from stock_daily_test where ts_code in ' +
                     '(select ts_code from stock where ts_code not like \'688%%\' and ts_code not like \'30%%\')')
        if start_date is not None and end_date is not None:
            stock_sql = stock_sql + " and trade_date >= \'" + start_date + "\' and trade_date <= \'" + end_date + "\'"
    stock_df = pd.read_sql(stock_sql, con=engine)
    return stock_df

def saveWeekData(week_df):
    engine = create_engine('mysql+pymysql://' + mysql_user + ':' + mysql_pass + '@' + mysql_url + '/' + mysql_db)
    week_df.to_sql('stock_week_temp', con=engine, if_exists='replace', index=False)
    sql = text("delete w from stock_week w join stock_week_temp t on w.ts_code = t.ts_code and w.trade_date = t.trade_date")
    with engine.connect() as conn:
        conn.execute(sql)
    week_df.to_sql('stock_week', con=engine, if_exists='append', index=False)

def saveMonthData(month_df):
    engine = create_engine('mysql+pymysql://' + mysql_user + ':' + mysql_pass + '@' + mysql_url + '/' + mysql_db)
    month_df.to_sql('stock_month_temp', con=engine, if_exists='replace', index=False)
    sql = text(
        "delete m from stock_month m join stock_month_temp t on m.ts_code = t.ts_code and m.trade_date = t.trade_date")
    with engine.connect() as conn:
        conn.execute(sql)
    month_df.to_sql('stock_month', con=engine, if_exists='append', index=False)

