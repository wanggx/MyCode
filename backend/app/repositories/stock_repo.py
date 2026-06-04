# -*- coding: utf-8 -*-
"""
A 股基本数据访问
"""

from app.core.database import get_db_connection
from app.core.config import settings
from sqlalchemy import create_engine, text


def query_stocks(page=1, page_size=10, keyword="", area="", industry=""):
    """查询股票列表（分页 + 筛选）"""
    conn = get_db_connection()
    if not conn:
        return None, "数据库连接失败"

    try:
        with conn.cursor() as cursor:
            where_conditions = []
            params = []

            if keyword:
                where_conditions.append(
                    "(ts_code LIKE %s OR symbol LIKE %s OR name LIKE %s)"
                )
                kw = f"%{keyword}%"
                params.extend([kw, kw, kw])

            if area:
                where_conditions.append("area = %s")
                params.append(area)

            if industry:
                where_conditions.append("industry = %s")
                params.append(industry)

            where_clause = ""
            if where_conditions:
                where_clause = "WHERE " + " AND ".join(where_conditions)

            count_sql = f"SELECT COUNT(*) as total FROM stock {where_clause}"
            cursor.execute(count_sql, params)
            total = cursor.fetchone()["total"] or 0

            offset = (page - 1) * page_size
            sql = f"""
                SELECT ts_code, symbol, name, area, industry, cnspell,
                       market, list_date, act_name, act_ent_type
                FROM stock {where_clause}
                ORDER BY ts_code
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql, params + [page_size, offset])
            rows = cursor.fetchall()

            stocks = []
            for r in rows:
                stocks.append({
                    "ts_code": r["ts_code"],
                    "symbol": str(r["symbol"]) if r["symbol"] else "",
                    "name": r["name"],
                    "area": r["area"],
                    "industry": r["industry"],
                    "cnspell": r["cnspell"],
                    "market": r["market"],
                    "list_date": str(r["list_date"]) if r["list_date"] else "",
                    "act_name": r["act_name"],
                    "act_ent_type": r["act_ent_type"],
                })

            return {
                "stocks": stocks,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size,
            }, None
    except Exception as e:
        return None, f"查询失败: {str(e)}"
    finally:
        conn.close()


def query_areas():
    """查询所有地域列表"""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT DISTINCT area FROM stock WHERE area IS NOT NULL AND area != '' ORDER BY area"
            )
            return [r["area"] for r in cursor.fetchall()]
    finally:
        conn.close()


def query_industries():
    """查询所有行业列表"""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT DISTINCT industry FROM stock WHERE industry IS NOT NULL AND industry != '' ORDER BY industry"
            )
            return [r["industry"] for r in cursor.fetchall()]
    finally:
        conn.close()


def query_stock_list_df():
    """获取股票列表 DataFrame（排除科创板/北交所/ST）"""
    engine = create_engine(
        f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )
    import pandas as pd

    stock_df = pd.read_sql_table("stock", con=engine)
    return stock_df[
        (stock_df["ts_code"].str.startswith("68") == False)
        & (stock_df["ts_code"].str.endswith("BJ") == False)
        & (stock_df["name"].str.contains("ST") == False)
    ]


def refresh_stock_list_from_tushare():
    """从 Tushare 刷新股票列表（替换式）"""
    import tushare as ts

    ts.set_token(settings.TUSHARE_TOKEN)
    pro = ts.pro_api()
    data = pro.stock_basic(exchange="", list_status="L")
    engine = create_engine(
        f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )
    data.to_sql("stock", con=engine, if_exists="replace", index=False)
