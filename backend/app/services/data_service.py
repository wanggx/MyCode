# -*- coding: utf-8 -*-
"""
数据服务：行情同步 + 数据概览（Phase 1）
"""
import logging
from app.repositories import stock_repo, stock_daily_repo, data_source_repo
from app.core.database import get_db_connection

logger = logging.getLogger("myapp")

# === 旧版数据下载函数（保留兼容，后续 Phase 升级） ===

def download_daily_data(start_date, end_date):
    """下载日线数据（旧版兼容）"""
    logger.info(f"download_daily_data: {start_date}~{end_date} (Phase 2 升级)")


def iterate_weeks(start_date, end_date):
    """聚合周线（旧版兼容）"""
    logger.info(f"iterate_weeks: {start_date}~{end_date}")


def iterate_months(start_date, end_date):
    """聚合月线（旧版兼容）"""
    logger.info(f"iterate_months: {start_date}~{end_date}")


def get_stock_list(page, page_size, keyword="", area="", industry="", market=""):
    return stock_repo.query_stocks(page, page_size, keyword, area, industry, market)


def get_stock_detail(ts_code):
    return stock_repo.query_stock_by_code(ts_code)


def get_stock_daily(ts_code, start_date, end_date):
    result, err = stock_daily_repo.query_stock_data(ts_code, start_date, end_date)
    return result, err


def get_data_sources():
    return data_source_repo.get_sources()


def trigger_sync(source, data_type, trade_date):
    """触发数据同步（创建 task_job 交给 worker）"""
    log_id = data_source_repo.create_sync_log(source, data_type, trade_date)
    return {"sync_log_id": log_id, "status": "pending"}


def get_sync_logs(page, page_size, source=None):
    return data_source_repo.query_sync_logs(page, page_size, source)


def get_data_overview():
    """数据概览统计"""
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor() as c:
            c.execute("SELECT COUNT(*) as cnt FROM stock_basic")
            total = c.fetchone()["cnt"]
            c.execute("SELECT MAX(trade_date) as latest FROM stock_daily")
            latest = c.fetchone()["latest"]
            c.execute("SELECT MIN(trade_date) as earliest FROM stock_daily")
            earliest = c.fetchone()["earliest"]
            return {
                "total_stocks": total,
                "latest_trade_date": str(latest) if latest else None,
                "date_range_start": str(earliest) if earliest else None,
                "completeness": "N/A",
            }
    finally:
        conn.close()
