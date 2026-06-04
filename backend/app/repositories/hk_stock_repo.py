# -*- coding: utf-8 -*-
"""
港股数据访问
"""

import logging

import akshare as ak
import pandas as pd
from sqlalchemy import text

from app.core.database import get_engine

logger = logging.getLogger("myapp")




def save_hk_stock_list():
    """保存港股列表（替换式）"""
    stockdf = ak.stock_hk_spot()
    engine = get_engine()
    stockdf.rename(
        columns={
            "日期时间": "date",
            "代码": "ts_code",
            "中文名称": "cn_name",
            "英文名称": "en_name",
            "交易类型": "type",
            "最新价": "price",
            "涨跌幅": "change",
            "涨跌额": "change_amount",
            "成交量": "volume",
        },
        inplace=True,
    )
    stockdf.to_sql("hk_stock", con=engine, if_exists="replace", index=False)


def save_hk_daily(dailydf):
    """保存港股日线数据到临时表"""
    engine = get_engine()
    dailydf.to_sql("hk_stock_daily_temp", con=engine, if_exists="replace", index=False)


def merge_hk_daily_data():
    """合并港股日线临时表到正式表"""
    engine = get_engine()
    sql = text(
        "INSERT INTO hk_stock_daily SELECT t.* FROM hk_stock_daily_temp t "
        "LEFT JOIN hk_stock_daily d ON t.ts_code = d.ts_code AND t.trade_date = d.trade_date "
        "WHERE d.ts_code IS NULL"
    )
    with engine.connect() as conn:
        conn.execute(sql)
        conn.commit()


def get_hk_stock_list():
    """获取港股列表 DataFrame"""
    engine = get_engine()
    stock_df = pd.read_sql_table("hk_stock", con=engine)
    stock_df.rename(columns={"cn_name": "name"}, inplace=True)
    return stock_df


def get_hk_stock_data(ts_code, start_date, end_date):
    """获取港股日线数据 DataFrame"""
    engine = get_engine()
    if ts_code:
        sql = f"SELECT * FROM hk_stock_daily WHERE ts_code = '{ts_code}'"
    else:
        sql = "SELECT * FROM hk_stock_daily"
    if start_date and end_date:
        if "WHERE" in sql.upper():
            sql += f" AND trade_date >= '{start_date}' AND trade_date <= '{end_date}'"
        else:
            sql += f" WHERE trade_date >= '{start_date}' AND trade_date <= '{end_date}'"
    logger.info(f"取数SQL: {sql}")
    return pd.read_sql(sql, con=engine)
