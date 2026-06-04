# -*- coding: utf-8 -*-
"""
数据质量数据访问层：data_quality_issue / data_quality_issue_detail / data_repair_job 的 CRUD
"""

import json
import logging

from app.core.database import get_db_connection
from app.repositories.base import paginate_sql

logger = logging.getLogger(__name__)


def init_tables():
    conn = get_db_connection()
    if not conn:
        logger.error("数据库连接失败，无法初始化数据质量表")
        return False
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_quality_issue (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    issue_code VARCHAR(50) NOT NULL COMMENT 'issue编号 DQ-YYYYMMDD-NNN',
                    market VARCHAR(10) NOT NULL COMMENT 'A股/港股',
                    data_type VARCHAR(20) NOT NULL COMMENT 'daily/weekly/monthly',
                    start_date VARCHAR(8) NOT NULL,
                    end_date VARCHAR(8) NOT NULL,
                    expected_count INT DEFAULT 0,
                    actual_count INT DEFAULT 0,
                    missing_count INT DEFAULT 0,
                    severity VARCHAR(10) DEFAULT 'medium' COMMENT 'low/medium/high',
                    status VARCHAR(20) DEFAULT 'open' COMMENT 'open/repairing/resolved/ignored/failed',
                    impact_summary_json JSON COMMENT '影响范围摘要',
                    discovered_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    resolved_at DATETIME NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE KEY uk_issue_code (issue_code),
                    INDEX idx_market_date (market, data_type, start_date, end_date),
                    INDEX idx_status (status)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_quality_issue_detail (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    issue_id INT NOT NULL,
                    trade_date VARCHAR(8) NOT NULL,
                    ts_code VARCHAR(20) NOT NULL,
                    issue_type VARCHAR(30) NOT NULL COMMENT 'missing_daily/invalid_ohlc/missing_week/missing_month',
                    message TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_issue_id (issue_id),
                    INDEX idx_trade_date (trade_date),
                    INDEX idx_ts_code (ts_code)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS data_repair_job (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    issue_id INT NOT NULL,
                    task_job_id INT NULL COMMENT '关联任务中心的task_job',
                    repair_mode VARCHAR(30) NOT NULL COMMENT 'repair_missing_only/reload_date/ignore',
                    status VARCHAR(20) DEFAULT 'pending' COMMENT 'pending/running/success/failed',
                    options_json JSON COMMENT '用户修复选项',
                    before_snapshot_json JSON COMMENT '修复前快照',
                    after_snapshot_json JSON COMMENT '修复后快照',
                    report_json JSON COMMENT '修复报告',
                    started_at DATETIME NULL,
                    finished_at DATETIME NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_issue_id (issue_id),
                    INDEX idx_task_job_id (task_job_id)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
        conn.commit()
        logger.info("数据质量表已就绪")
        return True
    finally:
        conn.close()


def create_issue(data: dict) -> int:
    conn = get_db_connection()
    if not conn:
        return 0
    try:
        with conn.cursor() as cursor:
            cols = ", ".join(data.keys())
            placeholders = ", ".join(["%s"] * len(data))
            sql = f"INSERT INTO data_quality_issue ({cols}) VALUES ({placeholders})"
            cursor.execute(sql, list(data.values()))
            issue_id = cursor.lastrowid
        conn.commit()
        return issue_id
    finally:
        conn.close()


def get_issue(issue_id: int) -> dict:
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM data_quality_issue WHERE id = %s", [issue_id])
            return cursor.fetchone()
    finally:
        conn.close()


def get_issues(market=None, severity=None, status=None, page=1, page_size=20) -> dict:
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            conditions = []
            params = []
            if market:
                conditions.append("market = %s")
                params.append(market)
            if severity:
                conditions.append("severity = %s")
                params.append(severity)
            if status:
                conditions.append("status = %s")
                params.append(status)
            where = (" WHERE " + " AND ".join(conditions)) if conditions else ""
            base_sql = f"SELECT * FROM data_quality_issue{where} ORDER BY created_at DESC"
            count_sql = f"SELECT COUNT(*) AS total FROM data_quality_issue{where}"
            return paginate_sql(base_sql, count_sql, params, page, page_size, cursor)
    finally:
        conn.close()


def update_issue(issue_id: int, data: dict) -> bool:
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            sets = []
            params = []
            for k, v in data.items():
                if k == "id":
                    continue
                sets.append(f"{k} = %s")
                params.append(v)
            if not sets:
                return False
            params.append(issue_id)
            sql = f"UPDATE data_quality_issue SET {', '.join(sets)} WHERE id = %s"
            cursor.execute(sql, params)
            affected = cursor.rowcount
        conn.commit()
        return affected > 0
    finally:
        conn.close()


def get_issue_details(issue_id: int) -> list:
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM data_quality_issue_detail WHERE issue_id = %s ORDER BY trade_date, ts_code",
                [issue_id],
            )
            return cursor.fetchall()
    finally:
        conn.close()


def add_issue_details(issue_id: int, details: list):
    if not details:
        return
    conn = get_db_connection()
    if not conn:
        return
    try:
        with conn.cursor() as cursor:
            for d in details:
                d["issue_id"] = issue_id
                cols = ", ".join(d.keys())
                placeholders = ", ".join(["%s"] * len(d))
                sql = f"INSERT INTO data_quality_issue_detail ({cols}) VALUES ({placeholders})"
                cursor.execute(sql, list(d.values()))
        conn.commit()
    finally:
        conn.close()


def get_quality_summary() -> dict:
    conn = get_db_connection()
    if not conn:
        return {}
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT market, status, COUNT(*) AS count FROM data_quality_issue GROUP BY market, status"
            )
            rows = cursor.fetchall()
        summary = {}
        for row in rows:
            m = row["market"]
            s = row["status"]
            if m not in summary:
                summary[m] = {}
            summary[m][s] = row["count"]
        return summary
    finally:
        conn.close()


def create_repair_job(data: dict) -> int:
    conn = get_db_connection()
    if not conn:
        return 0
    try:
        with conn.cursor() as cursor:
            cols = ", ".join(data.keys())
            placeholders = ", ".join(["%s"] * len(data))
            sql = f"INSERT INTO data_repair_job ({cols}) VALUES ({placeholders})"
            cursor.execute(sql, list(data.values()))
            job_id = cursor.lastrowid
        conn.commit()
        return job_id
    finally:
        conn.close()


def get_repair_job(repair_job_id: int) -> dict:
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM data_repair_job WHERE id = %s", [repair_job_id])
            return cursor.fetchone()
    finally:
        conn.close()


def update_repair_job(repair_job_id: int, data: dict) -> bool:
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            sets = []
            params = []
            for k, v in data.items():
                if k == "id":
                    continue
                sets.append(f"{k} = %s")
                params.append(v)
            if not sets:
                return False
            params.append(repair_job_id)
            sql = f"UPDATE data_repair_job SET {', '.join(sets)} WHERE id = %s"
            cursor.execute(sql, params)
            affected = cursor.rowcount
        conn.commit()
        return affected > 0
    finally:
        conn.close()
