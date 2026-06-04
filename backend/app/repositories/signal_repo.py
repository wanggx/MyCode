# -*- coding: utf-8 -*-
"""
信号数据访问层：signal 表的 CRUD
"""

import json
import logging

from app.core.database import get_db_connection
from app.repositories.base import paginate_sql

logger = logging.getLogger(__name__)


def init_tables():
    """确保 signal 表存在"""
    conn = get_db_connection()
    if not conn:
        logger.error("数据库连接失败，无法初始化信号表")
        return False
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS `signal` (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    trade_date VARCHAR(8) NOT NULL,
                    ts_code VARCHAR(20) NOT NULL,
                    name VARCHAR(50),
                    market VARCHAR(10),
                    strategy_id INT NOT NULL,
                    strategy_version_id INT NOT NULL,
                    strategy_run_id INT NOT NULL,
                    score DECIMAL(6,2) DEFAULT 0 COMMENT '信号分',
                    reason_text TEXT COMMENT '入选原因',
                    factor_snapshot_json JSON COMMENT '因子快照',
                    risk_snapshot_json JSON COMMENT '风险快照',
                    data_quality_status VARCHAR(20) DEFAULT 'unknown',
                    status VARCHAR(20) DEFAULT 'new' COMMENT 'new/watched/portfolio/ignored',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_trade_date (trade_date),
                    INDEX idx_ts_code (ts_code),
                    INDEX idx_strategy_date (strategy_id, trade_date),
                    INDEX idx_score (score)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
        conn.commit()
        logger.info("信号表已就绪")
        return True
    finally:
        conn.close()


def create_signals(signals: list) -> int:
    """批量插入信号，返回插入数"""
    if not signals:
        return 0
    conn = get_db_connection()
    if not conn:
        return 0
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO `signal` (
                    trade_date, ts_code, name, market,
                    strategy_id, strategy_version_id, strategy_run_id,
                    score, reason_text, factor_snapshot_json, risk_snapshot_json,
                    data_quality_status, status
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            rows = []
            for s in signals:
                factor_json = s.get("factor_snapshot_json")
                if isinstance(factor_json, (dict, list)):
                    factor_json = json.dumps(factor_json, ensure_ascii=False)
                risk_json = s.get("risk_snapshot_json")
                if isinstance(risk_json, (dict, list)):
                    risk_json = json.dumps(risk_json, ensure_ascii=False)
                rows.append((
                    s.get("trade_date"),
                    s.get("ts_code"),
                    s.get("name"),
                    s.get("market"),
                    s.get("strategy_id"),
                    s.get("strategy_version_id"),
                    s.get("strategy_run_id"),
                    s.get("score", 0),
                    s.get("reason_text"),
                    factor_json,
                    risk_json,
                    s.get("data_quality_status", "unknown"),
                    s.get("status", "new"),
                ))
            cursor.executemany(sql, rows)
            affected = cursor.rowcount
        conn.commit()
        return affected
    finally:
        conn.close()


def get_signal(signal_id: int) -> dict:
    """获取单个信号"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM `signal` WHERE id = %s", [signal_id])
            return cursor.fetchone()
    finally:
        conn.close()


def get_signals(trade_date=None, strategy_id=None, market=None, min_score=0,
                page=1, page_size=20) -> dict:
    """分页查询信号列表"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            conditions = []
            params = []
            if trade_date:
                conditions.append("trade_date = %s")
                params.append(trade_date)
            if strategy_id:
                conditions.append("strategy_id = %s")
                params.append(strategy_id)
            if market:
                conditions.append("market = %s")
                params.append(market)
            if min_score and min_score > 0:
                conditions.append("score >= %s")
                params.append(min_score)
            where = (" WHERE " + " AND ".join(conditions)) if conditions else ""

            base_sql = f"SELECT * FROM `signal`{where} ORDER BY score DESC, created_at DESC"
            count_sql = f"SELECT COUNT(*) AS total FROM `signal`{where}"
            return paginate_sql(base_sql, count_sql, params, page, page_size, cursor)
    finally:
        conn.close()


def update_signal_status(signal_id: int, status: str) -> bool:
    """更新信号状态"""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            sql = "UPDATE `signal` SET status = %s WHERE id = %s"
            cursor.execute(sql, [status, signal_id])
            affected = cursor.rowcount
        conn.commit()
        return affected > 0
    finally:
        conn.close()
