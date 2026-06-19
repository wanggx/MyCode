# -*- coding: utf-8 -*-
"""
A 股基础数据访问（qt_dev.stock_basic + stock_daily）
"""
from app.core.database import get_db_connection


def query_stocks(page=1, page_size=10, keyword="", area="", industry="", market=""):
    """查询股票列表（分页 + 筛选）"""
    conn = get_db_connection()
    if not conn:
        return None, "数据库连接失败"
    try:
        with conn.cursor() as cursor:
            where = []
            params = []
            if keyword:
                where.append("(ts_code LIKE %s OR symbol LIKE %s OR name LIKE %s)")
                kw = f"%{keyword}%"
                params.extend([kw, kw, kw])
            if area:
                where.append("area = %s")
                params.append(area)
            if industry:
                where.append("industry = %s")
                params.append(industry)
            if market:
                where.append("market = %s")
                params.append(market)
            wc = ("WHERE " + " AND ".join(where)) if where else ""

            cursor.execute(f"SELECT COUNT(*) as total FROM stock_basic {wc}", params)
            total = cursor.fetchone()["total"] or 0

            offset = (page - 1) * page_size
            cursor.execute(
                f"SELECT ts_code, symbol, name, area, industry, market, list_date, exchange, board_type "
                f"FROM stock_basic {wc} ORDER BY ts_code LIMIT %s OFFSET %s",
                params + [page_size, offset]
            )
            items = []
            for r in cursor.fetchall():
                items.append({
                    "ts_code": r["ts_code"], "symbol": r["symbol"], "name": r["name"],
                    "area": r["area"] or "", "industry": r["industry"] or "",
                    "market": r["market"] or "", "exchange": r["exchange"] or "",
                    "board_type": r["board_type"] or "",
                    "list_date": str(r["list_date"]) if r["list_date"] else "",
                })
            return {
                "stocks": items, "total": total,
                "page": page, "page_size": page_size,
                "total_pages": max((total + page_size - 1) // page_size, 1),
            }, None
    except Exception as e:
        return None, f"查询失败: {str(e)}"
    finally:
        conn.close()


def query_areas():
    conn = get_db_connection()
    if not conn: return []
    try:
        with conn.cursor() as c:
            c.execute("SELECT DISTINCT area FROM stock_basic WHERE area IS NOT NULL AND area != '' ORDER BY area")
            return [r["area"] for r in c.fetchall()]
    finally:
        conn.close()


def query_industries():
    conn = get_db_connection()
    if not conn: return []
    try:
        with conn.cursor() as c:
            c.execute("SELECT DISTINCT industry FROM stock_basic WHERE industry IS NOT NULL AND industry != '' ORDER BY industry")
            return [r["industry"] for r in c.fetchall()]
    finally:
        conn.close()


def query_stock_by_code(ts_code):
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor() as c:
            c.execute("SELECT * FROM stock_basic WHERE ts_code = %s", (ts_code,))
            return c.fetchone()
    finally:
        conn.close()


def query_stock_list_df():
    """获取股票列表 DataFrame（排除科创板/北交所/ST）"""
    from app.core.config import settings
    from sqlalchemy import create_engine
    import pandas as pd
    engine = create_engine(
        f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )
    df = pd.read_sql_table("stock_basic", con=engine)
    return df[
        (~df["ts_code"].str.startswith("68"))
        & (~df["ts_code"].str.endswith("BJ"))
        & (~df["name"].str.contains("ST"))
    ]
