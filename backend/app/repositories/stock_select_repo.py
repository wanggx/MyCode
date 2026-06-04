# -*- coding: utf-8 -*-
"""
选股结果数据访问
"""

from app.core.database import get_db_connection
from app.core.config import settings
from sqlalchemy import create_engine


def query_stock_select(page=1, page_size=10, select_date=None):
    """查询选股结果（分页）"""
    conn = get_db_connection()
    if not conn:
        return None, "数据库连接失败"
    try:
        with conn.cursor() as cursor:
            where, params = [], []
            if select_date:
                where.append("select_date = %s")
                params.append(select_date)

            where_clause = "WHERE " + " AND ".join(where) if where else ""

            cursor.execute(
                f"SELECT COUNT(*) as total FROM stock_select {where_clause}", params
            )
            total = cursor.fetchone()["total"] or 0

            offset = (page - 1) * page_size
            sql = f"""
                SELECT select_date, ts_code, name, vol,
                       trend3, trend5, trend10, trend20, trend30
                FROM stock_select {where_clause}
                ORDER BY select_date DESC, ts_code
                LIMIT %s OFFSET %s
            """
            cursor.execute(sql, params + [page_size, offset])
            rows = cursor.fetchall()

            items = []
            for r in rows:
                items.append({
                    "select_date": str(r["select_date"]),
                    "ts_code": r["ts_code"],
                    "name": r["name"],
                    "vol": r["vol"],
                    "trend3": r["trend3"],
                    "trend5": r["trend5"],
                    "trend10": r["trend10"],
                    "trend20": r["trend20"],
                    "trend30": r["trend30"],
                })

            return {
                "items": items,
                "total": total,
                "page": page,
                "page_size": page_size,
                "total_pages": (total + page_size - 1) // page_size if total > 0 else 0,
            }, None
    except Exception as e:
        return None, f"查询失败: {str(e)}"
    finally:
        conn.close()


def delete_stock_select(select_date):
    """删除指定日期的选股记录"""
    conn = get_db_connection()
    if not conn:
        return None, "数据库连接失败"
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM stock_select WHERE select_date = %s", (select_date,)
            )
            conn.commit()
            return cursor.rowcount, None
    except Exception as e:
        return None, f"删除失败: {str(e)}"
    finally:
        conn.close()


def save_select_result_to_db(df):
    """保存选股结果到 stock_select 表"""
    engine = create_engine(
        f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )
    df.to_sql("stock_select", con=engine, if_exists="append", index=False)


def query_vol_line_data(start_date, end_date):
    """查询选股成交量线数据（按日期分组计数）"""
    conn = get_db_connection()
    if not conn:
        return None, "数据库连接失败"
    try:
        with conn.cursor() as cursor:
            sql = """
                SELECT select_date, COUNT(1) as count
                FROM stock_select
                WHERE select_date >= %s AND select_date <= %s
                GROUP BY select_date
                ORDER BY select_date
            """
            cursor.execute(sql, (start_date, end_date))
            rows = cursor.fetchall()
            result = [
                {"select_date": str(r["select_date"]), "count": r["count"]}
                for r in rows
            ]
            return result, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()


def save_trend_select_to_db(df):
    """保存趋势选股结果到 stock_trend_select 表"""
    engine = create_engine(
        f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    )
    df.to_sql("stock_trend_select", con=engine, if_exists="append", index=False)
