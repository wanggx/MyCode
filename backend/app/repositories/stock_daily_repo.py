# -*- coding: utf-8 -*-
"""
日线/周线/月线数据访问
"""

from app.core.database import get_db_connection, get_engine
from sqlalchemy import text




TABLE_MAP = {"d": "stock_daily", "w": "stock_week", "m": "stock_month"}


def query_daily_data(ts_code, start_date, end_date, page, page_size, data_type="d"):
    """查询日线/周线/月线数据（分页）"""
    table = TABLE_MAP.get(data_type, "stock_daily")
    conn = get_db_connection()
    if not conn:
        return None, "数据库连接失败"
    try:
        with conn.cursor() as cursor:
            count_sql = f"""
                SELECT COUNT(*) as total FROM {table}
                WHERE ts_code = %s AND trade_date BETWEEN %s AND %s
            """
            cursor.execute(count_sql, (ts_code, start_date, end_date))
            total = cursor.fetchone()["total"] or 0

            offset = (page - 1) * page_size
            sql = f"""
                SELECT ts_code, trade_date, open, high, low, close,
                       pre_close, `change`, pct_chg, vol
                FROM {table}
                WHERE ts_code = %s AND trade_date BETWEEN %s AND %s
                ORDER BY trade_date DESC
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql, (ts_code, start_date, end_date, page_size, offset))
            rows = cursor.fetchall()

            return {
                "items": rows,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size if total > 0 else 0,
            }, None
    except Exception as e:
        return None, f"查询失败: {str(e)}"
    finally:
        conn.close()


def query_stock_data_df(ts_code, start_date, end_date):
    """查询日线数据 DataFrame（用于分析算法）"""
    engine = get_engine()
    import pandas as pd

    if ts_code:
        sql = f"SELECT * FROM stock_daily WHERE ts_code = '{ts_code}'"
    else:
        sql = (
            "SELECT * FROM stock_daily WHERE ts_code IN ("
            "SELECT ts_code FROM stock WHERE ts_code NOT LIKE '688%%' AND ts_code NOT LIKE '%%BJ' AND name NOT LIKE '%%ST%%')"
        )
    if start_date and end_date:
        sql += f" AND trade_date >= '{start_date}' AND trade_date <= '{end_date}'"

    return pd.read_sql(sql, con=engine)


def query_stock_week_data_df(ts_code, start_date, end_date):
    """查询周线数据 DataFrame"""
    engine = get_engine()
    import pandas as pd

    if ts_code:
        sql = f"SELECT * FROM stock_week WHERE ts_code = '{ts_code}'"
    else:
        sql = (
            "SELECT * FROM stock_week WHERE ts_code IN ("
            "SELECT ts_code FROM stock WHERE ts_code NOT LIKE '688%%' AND ts_code NOT LIKE '%%BJ' AND name NOT LIKE '%%ST%%')"
        )
    if start_date and end_date:
        sql += f" AND trade_date >= '{start_date}' AND trade_date <= '{end_date}'"

    return pd.read_sql(sql, con=engine)


def save_stock_daily_batch(ts_codes, daily_date, replace):
    """批量保存日线数据到临时表"""
    import tushare as ts

    ts.set_token(settings.TUSHARE_TOKEN)
    pro = ts.pro_api()
    df = pro.daily(ts_code=ts_codes, trade_date=daily_date)
    engine = get_engine()
    df.to_sql("stock_daily_temp", con=engine, if_exists="replace" if replace else "append", index=False)


def merge_daily_data():
    """合并临时表到正式表"""
    engine = get_engine()
    sql = text(
        "INSERT INTO stock_daily SELECT t.* FROM stock_daily_temp t "
        "LEFT JOIN stock_daily d ON t.ts_code = d.ts_code AND t.trade_date = d.trade_date "
        "WHERE d.ts_code IS NULL"
    )
    with engine.connect() as conn:
        conn.execute(sql)
        conn.commit()


def save_week_data(week_df):
    """保存周线数据（先删重复再追加）"""
    import pandas as pd

    engine = get_engine()
    week_df.to_sql("stock_week_temp", con=engine, if_exists="replace", index=False)
    with engine.connect() as conn:
        conn.execute(
            text(
                "DELETE w FROM stock_week w JOIN stock_week_temp t "
                "ON w.ts_code = t.ts_code AND w.trade_date = t.trade_date"
            )
        )
        conn.commit()
    week_df.to_sql("stock_week", con=engine, if_exists="append", index=False)


def delete_week_data(start_date, end_date):
    """删除指定范围的周线数据"""
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(
            text(
                "DELETE FROM stock_week WHERE trade_date >= :start AND trade_date <= :end"
            ),
            {"start": start_date, "end": end_date},
        )
        conn.commit()


def save_month_data(month_df):
    """保存月线数据"""
    import pandas as pd

    engine = get_engine()
    month_df.to_sql("stock_month_temp", con=engine, if_exists="replace", index=False)
    with engine.connect() as conn:
        conn.execute(
            text(
                "DELETE m FROM stock_month m JOIN stock_month_temp t "
                "ON m.ts_code = t.ts_code AND m.trade_date = t.trade_date"
            )
        )
        conn.commit()
    month_df.to_sql("stock_month", con=engine, if_exists="append", index=False)


def delete_month_data(start_date, end_date):
    """删除指定范围的月线数据"""
    engine = get_engine()
    with engine.connect() as conn:
        conn.execute(
            text(
                "DELETE FROM stock_month WHERE trade_date >= :start AND trade_date <= :end"
            ),
            {"start": start_date, "end": end_date},
        )
        conn.commit()
