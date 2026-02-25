

from db.db import getDbEngine
from sqlalchemy import text


def saveHKStockList(stockdf):
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
