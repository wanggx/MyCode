# -*- coding: utf-8 -*-
"""
因子数据访问层：factor_def / factor_value 表的 CRUD
"""

import json
import logging

from app.core.database import get_db_connection
from app.repositories.base import paginate_sql

logger = logging.getLogger(__name__)


def init_tables():
    """创建 factor_def 和 factor_value 表"""
    conn = get_db_connection()
    if not conn:
        logger.error("数据库连接失败，无法初始化因子表")
        return False
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS factor_def (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    factor_code VARCHAR(30) NOT NULL,
                    factor_name VARCHAR(50) NOT NULL,
                    category VARCHAR(20) COMMENT '技术/价量/风险',
                    description TEXT,
                    params_json JSON COMMENT '计算参数',
                    enabled TINYINT(1) DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
                    UNIQUE KEY uk_factor_code (factor_code)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS factor_value (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    trade_date VARCHAR(8) NOT NULL,
                    ts_code VARCHAR(20) NOT NULL,
                    factor_code VARCHAR(30) NOT NULL,
                    value DECIMAL(12,4) NULL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY uk_date_code_factor (trade_date, ts_code, factor_code),
                    INDEX idx_factor_date (factor_code, trade_date),
                    INDEX idx_ts_date (ts_code, trade_date)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
        conn.commit()
        logger.info("因子表已就绪")
        return True
    finally:
        conn.close()


def get_factor_defs(category=None) -> list:
    """获取因子定义列表，可选按 category 过滤"""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            if category:
                cursor.execute(
                    "SELECT * FROM factor_def WHERE category = %s ORDER BY id",
                    [category],
                )
            else:
                cursor.execute("SELECT * FROM factor_def ORDER BY id")
            return cursor.fetchall()
    finally:
        conn.close()


def get_factor_def(factor_code: str) -> dict:
    """获取单个因子定义"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM factor_def WHERE factor_code = %s",
                [factor_code],
            )
            return cursor.fetchone()
    finally:
        conn.close()


def create_factor_def(data: dict) -> int:
    """创建因子定义，返回插入行 id"""
    conn = get_db_connection()
    if not conn:
        return 0
    try:
        with conn.cursor() as cursor:
            params_json = data.get("params_json") or data.get("params")
            if isinstance(params_json, (dict, list)):
                params_json = json.dumps(params_json, ensure_ascii=False)
            sql = """
                INSERT INTO factor_def (factor_code, factor_name, category, description, params_json, enabled)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, [
                data.get("factor_code"),
                data.get("factor_name"),
                data.get("category"),
                data.get("description"),
                params_json,
                data.get("enabled", 1),
            ])
            inserted_id = cursor.lastrowid
        conn.commit()
        return inserted_id
    finally:
        conn.close()


def get_enabled_factors() -> list:
    """获取所有启用的因子定义"""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM factor_def WHERE enabled = 1 ORDER BY id"
            )
            return cursor.fetchall()
    finally:
        conn.close()


def batch_insert_values(items: list) -> int:
    """批量插入因子值（INSERT IGNORE），返回插入数"""
    if not items:
        return 0
    conn = get_db_connection()
    if not conn:
        return 0
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT IGNORE INTO factor_value (trade_date, ts_code, factor_code, value)
                VALUES (%s, %s, %s, %s)
            """
            rows = [
                (item.get("trade_date"), item.get("ts_code"),
                 item.get("factor_code"), item.get("value"))
                for item in items
            ]
            cursor.executemany(sql, rows)
            affected = cursor.rowcount
        conn.commit()
        return affected
    finally:
        conn.close()


def get_values(factor_code: str, trade_date: str = None, limit=500) -> list:
    """获取因子值列表"""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            if trade_date:
                cursor.execute(
                    "SELECT * FROM factor_value WHERE factor_code = %s AND trade_date = %s ORDER BY ts_code LIMIT %s",
                    [factor_code, trade_date, limit],
                )
            else:
                cursor.execute(
                    "SELECT * FROM factor_value WHERE factor_code = %s ORDER BY trade_date DESC, ts_code LIMIT %s",
                    [factor_code, limit],
                )
            return cursor.fetchall()
    finally:
        conn.close()


def get_coverage(factor_code: str, trade_date: str = None) -> dict:
    """获取因子覆盖率：覆盖数 / 总股票数"""
    conn = get_db_connection()
    if not conn:
        return {"covered": 0, "total": 0, "ratio": 0}
    try:
        with conn.cursor() as cursor:
            if trade_date:
                cursor.execute(
                    "SELECT COUNT(*) AS covered FROM factor_value WHERE factor_code = %s AND trade_date = %s",
                    [factor_code, trade_date],
                )
            else:
                cursor.execute(
                    "SELECT COUNT(*) AS covered FROM factor_value WHERE factor_code = %s",
                    [factor_code],
                )
            row = cursor.fetchone()
            covered = row["covered"] if row else 0

            if trade_date:
                cursor.execute(
                    "SELECT COUNT(DISTINCT ts_code) AS total FROM factor_value WHERE trade_date = %s",
                    [trade_date],
                )
            else:
                cursor.execute(
                    "SELECT COUNT(DISTINCT ts_code) AS total FROM factor_value"
                )
            total_row = cursor.fetchone()
            total = total_row["total"] if total_row else 0
            if total == 0:
                total = 3500
            ratio = round(covered / total, 4) if total > 0 else 0
            return {"covered": covered, "total": total, "ratio": ratio}
    finally:
        conn.close()


def get_factor_ic(factor_code: str, start_date: str, end_date: str) -> list:
    """因子 IC 计算（第一版返回空列表）"""
    return []
