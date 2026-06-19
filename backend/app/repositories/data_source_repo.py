# -*- coding: utf-8 -*-
"""数据源配置 & 同步日志数据访问"""
from app.core.database import get_db_connection


def get_sources():
    conn = get_db_connection()
    if not conn: return []
    try:
        with conn.cursor() as c:
            c.execute("SELECT id, name, display_name, status, config, priority FROM data_source ORDER BY priority DESC")
            return list(c.fetchall())
    finally:
        conn.close()


def get_source_by_name(name):
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor() as c:
            c.execute("SELECT * FROM data_source WHERE name = %s", (name,))
            return c.fetchone()
    finally:
        conn.close()


def create_sync_log(source, data_type, trade_date):
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor() as c:
            c.execute(
                "INSERT INTO data_sync_log (source, data_type, trade_date, status, created_at) VALUES (%s,%s,%s,'pending',NOW())",
                (source, data_type, trade_date)
            )
            conn.commit()
            return c.lastrowid
    finally:
        conn.close()


def update_sync_log(log_id, status, total=0, success=0, fail=0, error_msg=None):
    conn = get_db_connection()
    if not conn: return
    try:
        with conn.cursor() as c:
            c.execute(
                "UPDATE data_sync_log SET status=%s, total_count=%s, success_count=%s, fail_count=%s, error_msg=%s, finished_at=NOW() WHERE id=%s",
                (status, total, success, fail, error_msg, log_id)
            )
            conn.commit()
    finally:
        conn.close()


def query_sync_logs(page=1, page_size=20, source=None):
    conn = get_db_connection()
    if not conn: return None, "DB error"
    try:
        with conn.cursor() as c:
            where, params = "", []
            if source:
                where = "WHERE source = %s"
                params.append(source)
            c.execute(f"SELECT COUNT(*) as total FROM data_sync_log {where}", params)
            total = c.fetchone()["total"] or 0
            off = (page - 1) * page_size
            c.execute(f"SELECT * FROM data_sync_log {where} ORDER BY created_at DESC LIMIT %s OFFSET %s", params + [page_size, off])
            return {"items": list(c.fetchall()), "total": total, "page": page, "page_size": page_size}, None
    finally:
        conn.close()
