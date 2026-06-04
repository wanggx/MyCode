# -*- coding: utf-8 -*-
"""
数据校验数据访问
"""

from app.core.database import get_db_connection


def query_daily_count_by_date(start_date, end_date, page, page_size):
    """按交易日分组统计日线数据条数（分页）"""
    conn = get_db_connection()
    if not conn:
        return None, "数据库连接失败"
    try:
        with conn.cursor() as cursor:
            sql = "SELECT trade_date, COUNT(1) as cnt FROM stock_daily WHERE 1=1"
            params = []
            if start_date:
                sql += " AND trade_date >= %s"
                params.append(start_date)
            if end_date:
                sql += " AND trade_date <= %s"
                params.append(end_date)
            sql += " GROUP BY trade_date ORDER BY trade_date DESC"

            count_sql = f"SELECT COUNT(*) as total FROM ({sql}) t"
            cursor.execute(count_sql, params)
            total = cursor.fetchone()["total"] or 0

            offset = (page - 1) * page_size
            data_sql = sql + " LIMIT %s OFFSET %s"
            cursor.execute(data_sql, params + [page_size, offset])
            rows = cursor.fetchall()

            result = [
                {"trade_date": str(r["trade_date"]), "cnt": r["cnt"]}
                if isinstance(r, dict)
                else {"trade_date": r[0], "cnt": r[1]}
                for r in rows
            ]

            return {"list": result, "total": total}, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()
