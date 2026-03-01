import logging
from dataclasses import replace

import akshare as ak
import pandas as pd
from db.db import getDbEngine
from sqlalchemy import text
from sqlalchemy.dialects.mssql.information_schema import columns

logger = logging.getLogger('myapp')

def saveHKStockList():
    stockdf = ak.stock_hk_spot()
    engine = getDbEngine()
    stockdf.rename(columns={'日期时间': 'date', '代码': 'ts_code', '中文名称': 'cn_name',
                            '英文名称':'en_name', '交易类型': 'type', '最新价': 'price',
                            '涨跌幅': 'change', '涨跌额': 'change_amount', '成交量': 'volume'}, inplace=True)
    stockdf.to_sql('hk_stock', con=engine, if_exists='replace', index=False)


def saveHKDaily(dailydf):
    engine = getDbEngine()
    dailydf.to_sql('hk_stock_daily_temp', con=engine, if_exists='replace', index=False)

def mergeHKDailyData():
    engine = getDbEngine()
    sql = text("insert into hk_stock_daily select t.* from hk_stock_daily_temp t left join hk_stock_daily d on" +
               " t.ts_code = d.ts_code and t.trade_date = d.trade_date where d.ts_code is null")
    with engine.connect() as conn:
        conn.execute(sql)
        conn.commit()

def getHkStockList():
    engine = getDbEngine()
    stock_df = pd.read_sql_table('hk_stock', con=engine)
    stock_df.rename(columns={'cn_name': 'name'}, inplace = True)
    return stock_df



def getHkStockData(ts_code, start_date, end_date):
    engine = getDbEngine()
    if ts_code is not None:
        stock_sql = "select * from hk_stock_daily  where ts_code = \'" + ts_code + "\'"
        if start_date is not None and end_date is not None:
            stock_sql = stock_sql + " and trade_date >= \'" + start_date + "\' and trade_date <= \'" + end_date + "\'"
    else:
        stock_sql = ('select * from hk_stock_daily')
        if start_date is not None and end_date is not None:
            stock_sql = stock_sql + " where trade_date >= \'" + start_date + "\' and trade_date <= \'" + end_date + "\'"
    logger.info("取数SQL:" + stock_sql)
    stock_df = pd.read_sql(stock_sql, con=engine)
    return stock_df
