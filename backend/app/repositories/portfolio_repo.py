# -*- coding: utf-8 -*-
"""
组合风控数据访问层：watchlist, portfolio, portfolio_position, portfolio_nav 表的 CRUD
"""

import logging
from datetime import datetime

from app.core.database import get_db_connection

logger = logging.getLogger(__name__)


def init_tables():
    conn = get_db_connection()
    if not conn:
        logger.error("数据库连接失败，无法初始化组合风控表")
        return False
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS watchlist (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    ts_code VARCHAR(20) NOT NULL,
                    name VARCHAR(50),
                    market VARCHAR(10),
                    source_signal_id INT NULL,
                    note TEXT,
                    status VARCHAR(20) DEFAULT 'active' COMMENT 'active/removed',
                    added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    removed_at DATETIME NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolio (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(50) NOT NULL,
                    type VARCHAR(20) DEFAULT 'simulation' COMMENT 'simulation/watch/custom',
                    description TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolio_position (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    portfolio_id INT NOT NULL,
                    trade_date VARCHAR(8) NOT NULL,
                    ts_code VARCHAR(20) NOT NULL,
                    weight DECIMAL(8,4) DEFAULT 0,
                    quantity INT DEFAULT 0,
                    cost_price DECIMAL(12,4) DEFAULT 0,
                    close_price DECIMAL(12,4) DEFAULT 0,
                    market_value DECIMAL(16,2) DEFAULT 0,
                    INDEX idx_portfolio_date (portfolio_id, trade_date)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS portfolio_nav (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    portfolio_id INT NOT NULL,
                    trade_date VARCHAR(8) NOT NULL,
                    nav DECIMAL(12,4) NOT NULL,
                    daily_return DECIMAL(8,4) DEFAULT 0,
                    drawdown DECIMAL(8,4) DEFAULT 0,
                    INDEX idx_portfolio_date (portfolio_id, trade_date)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
        conn.commit()
        logger.info("组合风控表已就绪")
        return True
    finally:
        conn.close()


def get_watchlist(status='active'):
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM watchlist WHERE status = %s ORDER BY added_at DESC",
                [status],
            )
            return cursor.fetchall() or []
    finally:
        conn.close()


def add_to_watchlist(data: dict) -> int:
    conn = get_db_connection()
    if not conn:
        return 0
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """INSERT INTO watchlist (ts_code, name, market, source_signal_id, note, status)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                [
                    data.get("ts_code"),
                    data.get("name"),
                    data.get("market"),
                    data.get("source_signal_id"),
                    data.get("note"),
                    data.get("status", "active"),
                ],
            )
            inserted_id = cursor.lastrowid
        conn.commit()
        return inserted_id
    finally:
        conn.close()


def remove_from_watchlist(watchlist_id: int) -> bool:
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE watchlist SET status = 'removed', removed_at = %s WHERE id = %s",
                [datetime.now(), watchlist_id],
            )
            affected = cursor.rowcount
        conn.commit()
        return affected > 0
    finally:
        conn.close()


def create_portfolio(data: dict) -> int:
    conn = get_db_connection()
    if not conn:
        return 0
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """INSERT INTO portfolio (name, type, description)
                   VALUES (%s, %s, %s)""",
                [data.get("name"), data.get("type", "simulation"), data.get("description")],
            )
            inserted_id = cursor.lastrowid
        conn.commit()
        return inserted_id
    finally:
        conn.close()


def get_portfolios() -> list:
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM portfolio ORDER BY created_at DESC")
            return cursor.fetchall() or []
    finally:
        conn.close()


def get_portfolio(portfolio_id: int) -> dict:
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM portfolio WHERE id = %s", [portfolio_id])
            return cursor.fetchone()
    finally:
        conn.close()


def batch_replace_positions(portfolio_id: int, items: list) -> int:
    if not items:
        return 0
    conn = get_db_connection()
    if not conn:
        return 0
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "DELETE FROM portfolio_position WHERE portfolio_id = %s",
                [portfolio_id],
            )
            sql = """INSERT INTO portfolio_position
                     (portfolio_id, trade_date, ts_code, weight, quantity, cost_price, close_price, market_value)
                     VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"""
            rows = [
                (
                    portfolio_id,
                    item.get("trade_date"),
                    item.get("ts_code"),
                    item.get("weight", 0),
                    item.get("quantity", 0),
                    item.get("cost_price", 0),
                    item.get("close_price", 0),
                    item.get("market_value", 0),
                )
                for item in items
            ]
            cursor.executemany(sql, rows)
            affected = cursor.rowcount
        conn.commit()
        return affected
    finally:
        conn.close()


def get_positions(portfolio_id: int, trade_date: str = None) -> list:
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            if trade_date:
                cursor.execute(
                    "SELECT * FROM portfolio_position WHERE portfolio_id = %s AND trade_date = %s",
                    [portfolio_id, trade_date],
                )
            else:
                cursor.execute(
                    "SELECT * FROM portfolio_position WHERE portfolio_id = %s",
                    [portfolio_id],
                )
            return cursor.fetchall() or []
    finally:
        conn.close()


def batch_insert_nav(items: list) -> int:
    if not items:
        return 0
    conn = get_db_connection()
    if not conn:
        return 0
    try:
        with conn.cursor() as cursor:
            sql = """INSERT INTO portfolio_nav (portfolio_id, trade_date, nav, daily_return, drawdown)
                     VALUES (%s, %s, %s, %s, %s)"""
            rows = [
                (
                    item.get("portfolio_id"),
                    item.get("trade_date"),
                    item.get("nav"),
                    item.get("daily_return", 0),
                    item.get("drawdown", 0),
                )
                for item in items
            ]
            cursor.executemany(sql, rows)
            affected = cursor.rowcount
        conn.commit()
        return affected
    finally:
        conn.close()


def get_navs(portfolio_id: int) -> list:
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM portfolio_nav WHERE portfolio_id = %s ORDER BY trade_date",
                [portfolio_id],
            )
            return cursor.fetchall() or []
    finally:
        conn.close()
