# -*- coding: utf-8 -*-
"""
数据质量服务：完整性扫描、OHLC 校验、质量总览
"""

import json
import logging
from datetime import datetime

from app.core.database import get_db_connection
from app.repositories import data_quality_repo as quality_repo
from app.repositories import stock_repo
from app.repositories import stock_daily_repo
from app.repositories import hk_stock_repo

logger = logging.getLogger("myapp")


def _count_daily_by_date(trade_date: str) -> int:
    conn = get_db_connection()
    if not conn:
        return 0
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) AS cnt FROM stock_daily WHERE trade_date = %s",
                [trade_date],
            )
            return cursor.fetchone()["cnt"]
    finally:
        conn.close()


def _count_hk_daily_by_date(trade_date: str) -> int:
    conn = get_db_connection()
    if not conn:
        return 0
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) AS cnt FROM hk_stock_daily WHERE trade_date = %s",
                [trade_date],
            )
            return cursor.fetchone()["cnt"]
    finally:
        conn.close()


def _determine_severity(missing_count: int, market: str) -> str:
    if missing_count <= 5:
        return "low"
    if missing_count > 5:
        return "medium"
    return "medium"


def _generate_issue_code(trade_date: str, market: str) -> str:
    conn = get_db_connection()
    if not conn:
        return f"DQ-{trade_date}-{market}-1"
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT COUNT(*) AS cnt FROM data_quality_issue WHERE issue_code LIKE %s",
                [f"DQ-{trade_date}-{market}-%"],
            )
            seq = cursor.fetchone()["cnt"] + 1
        return f"DQ-{trade_date}-{market}-{seq}"
    finally:
        conn.close()


def scan_daily_completeness(market: str, trade_date: str) -> int:
    try:
        if market == "A股":
            attention_df = stock_repo.query_stock_list_df()
            expected = len(attention_df) if attention_df is not None else 0
            actual = _count_daily_by_date(trade_date)
        else:
            hk_list = hk_stock_repo.get_hk_stock_list()
            expected = len(hk_list) if hk_list is not None else 0
            actual = _count_hk_daily_by_date(trade_date)

        missing_count = expected - actual
        if missing_count <= 0:
            return 0

        severity = _determine_severity(missing_count, market)
        issue_code = _generate_issue_code(trade_date, market)
        issue_id = quality_repo.create_issue({
            "issue_code": issue_code,
            "market": market,
            "data_type": "daily",
            "start_date": trade_date,
            "end_date": trade_date,
            "expected_count": expected,
            "actual_count": actual,
            "missing_count": missing_count,
            "severity": severity,
            "status": "open",
        })

        details = _build_missing_details(market, trade_date)
        if details:
            quality_repo.add_issue_details(issue_id, details)

        return issue_id
    except Exception as e:
        logger.error(f"scan_daily_completeness error: {e}")
        return 0


def _build_missing_details(market: str, trade_date: str) -> list:
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            if market == "A股":
                cursor.execute(
                    "SELECT s.ts_code FROM stock s "
                    "LEFT JOIN stock_daily d ON s.ts_code = d.ts_code AND d.trade_date = %s "
                    "WHERE d.ts_code IS NULL AND s.ts_code NOT LIKE '688%%' "
                    "AND s.ts_code NOT LIKE '%%BJ' AND s.name NOT LIKE '%%ST%%'",
                    [trade_date],
                )
            else:
                cursor.execute(
                    "SELECT h.ts_code FROM hk_stock h "
                    "LEFT JOIN hk_stock_daily d ON h.ts_code = d.ts_code AND d.trade_date = %s "
                    "WHERE d.ts_code IS NULL",
                    [trade_date],
                )
            rows = cursor.fetchall()
        return [
            {"trade_date": trade_date, "ts_code": r["ts_code"], "issue_type": "missing_daily", "message": "日线数据缺失"}
            for r in rows
        ]
    except Exception as e:
        logger.error(f"_build_missing_details error: {e}")
        return []
    finally:
        conn.close()


def scan_ohlc_validity(market: str, trade_date: str) -> int:
    try:
        table = "stock_daily" if market == "A股" else "hk_stock_daily"
        conn = get_db_connection()
        if not conn:
            return 0
        try:
            with conn.cursor() as cursor:
                cursor.execute(
                    f"SELECT ts_code, trade_date, open, high, low, close FROM {table} "
                    f"WHERE trade_date = %s AND (open IS NULL OR open = 0 "
                    f"OR high IS NULL OR high = 0 OR low IS NULL OR low = 0 "
                    f"OR close IS NULL OR close = 0 OR high < low)",
                    [trade_date],
                )
                invalid_rows = cursor.fetchall()
        finally:
            conn.close()

        if not invalid_rows:
            return 0

        severity = "high" if len(invalid_rows) > 10 else "medium"
        issue_code = _generate_issue_code(trade_date, market)
        issue_id = quality_repo.create_issue({
            "issue_code": issue_code,
            "market": market,
            "data_type": "daily",
            "start_date": trade_date,
            "end_date": trade_date,
            "expected_count": 0,
            "actual_count": 0,
            "missing_count": len(invalid_rows),
            "severity": severity,
            "status": "open",
        })

        details = []
        for r in invalid_rows:
            msg_parts = []
            if r["open"] is None or r["open"] == 0:
                msg_parts.append("open异常")
            if r["high"] is None or r["high"] == 0:
                msg_parts.append("high异常")
            if r["low"] is None or r["low"] == 0:
                msg_parts.append("low异常")
            if r["close"] is None or r["close"] == 0:
                msg_parts.append("close异常")
            if r["high"] is not None and r["low"] is not None and r["high"] < r["low"]:
                msg_parts.append("high<low")
            details.append({
                "trade_date": trade_date,
                "ts_code": r["ts_code"],
                "issue_type": "invalid_ohlc",
                "message": "; ".join(msg_parts),
            })
        quality_repo.add_issue_details(issue_id, details)

        return issue_id
    except Exception as e:
        logger.error(f"scan_ohlc_validity error: {e}")
        return 0


def get_issue_detail(issue_id: int) -> dict:
    try:
        issue = quality_repo.get_issue(issue_id)
        if not issue:
            return {}
        details = quality_repo.get_issue_details(issue_id)
        result = dict(issue)
        result["details"] = [dict(d) for d in details]
        result["impact"] = _assess_impact(issue)
        return result
    except Exception as e:
        logger.error(f"get_issue_detail error: {e}")
        return {}


def _assess_impact(issue: dict) -> dict:
    missing_count = issue.get("missing_count", 0)
    severity = issue.get("severity", "medium")
    impact = {"factors": [], "strategies": [], "signal_generation": False, "portfolio_update": False}
    if severity == "high" or missing_count > 20:
        impact["factors"] = ["量价因子", "动量因子"]
        impact["strategies"] = ["趋势跟踪", "均值回归"]
        impact["signal_generation"] = True
        impact["portfolio_update"] = True
    elif severity == "medium":
        impact["factors"] = ["量价因子"]
        impact["strategies"] = ["趋势跟踪"]
        impact["signal_generation"] = missing_count > 10
    return impact


def get_quality_summary() -> dict:
    try:
        summary = quality_repo.get_quality_summary()
        today = datetime.now().strftime("%Y%m%d")
        a_count = _count_daily_by_date(today)
        hk_count = _count_hk_daily_by_date(today)
        summary["today_completeness"] = {"A股": a_count, "港股": hk_count}
        return summary
    except Exception as e:
        logger.error(f"get_quality_summary error: {e}")
        return {}


def scan_date_range(market: str, start_date: str, end_date: str) -> list:
    try:
        conn = get_db_connection()
        if not conn:
            return []
        trade_dates = []
        try:
            with conn.cursor() as cursor:
                table = "stock_daily" if market == "A股" else "hk_stock_daily"
                cursor.execute(
                    f"SELECT DISTINCT trade_date FROM {table} "
                    f"WHERE trade_date >= %s AND trade_date <= %s ORDER BY trade_date",
                    [start_date, end_date],
                )
                trade_dates = [r["trade_date"] for r in cursor.fetchall()]
        finally:
            conn.close()

        if not trade_dates:
            trade_dates = [start_date]

        issues = []
        for td in trade_dates:
            iid1 = scan_daily_completeness(market, td)
            if iid1 > 0:
                issues.append({"issue_id": iid1, "trade_date": td, "issue_type": "completeness"})
            iid2 = scan_ohlc_validity(market, td)
            if iid2 > 0:
                issues.append({"issue_id": iid2, "trade_date": td, "issue_type": "ohlc_validity"})
        return issues
    except Exception as e:
        logger.error(f"scan_date_range error: {e}")
        return []
