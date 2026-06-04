# -*- coding: utf-8 -*-
"""
策略数据访问层：strategy / strategy_version / strategy_run 的 CRUD
"""

import json
import logging
from datetime import datetime

from app.core.database import get_db_connection
from app.repositories.base import paginate_sql

logger = logging.getLogger(__name__)


def init_tables():
    """确保 strategy、strategy_version、strategy_run 三张表存在"""
    conn = get_db_connection()
    if not conn:
        logger.error("数据库连接失败，无法初始化策略表")
        return False
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS strategy (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(50) NOT NULL,
                    strategy_type VARCHAR(30) NOT NULL COMMENT 'volume_breakout/ma_trend/macd_kdj_resonance/hk_trend/custom_combo',
                    description TEXT,
                    enabled TINYINT(1) DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS strategy_version (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    strategy_id INT NOT NULL,
                    version VARCHAR(20) NOT NULL,
                    params_json JSON COMMENT '策略参数',
                    buy_rules_json JSON COMMENT '买入规则',
                    sell_rules_json JSON COMMENT '卖出规则',
                    remark TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    INDEX idx_strategy_version (strategy_id, version)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS strategy_run (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    strategy_id INT NOT NULL,
                    version_id INT NOT NULL,
                    trade_date VARCHAR(8) NOT NULL,
                    status VARCHAR(20) DEFAULT 'pending' COMMENT 'pending/running/success/failed',
                    signal_count INT DEFAULT 0,
                    task_job_id INT NULL,
                    started_at DATETIME NULL,
                    finished_at DATETIME NULL,
                    message TEXT,
                    INDEX idx_strategy_date (strategy_id, trade_date),
                    INDEX idx_status (status)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
        conn.commit()
        logger.info("策略表已就绪")
        return True
    finally:
        conn.close()


def create_strategy(data: dict) -> int:
    """创建策略，返回 strategy_id"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO strategy (name, strategy_type, description, enabled)
                VALUES (%s, %s, %s, %s)
            """
            cursor.execute(sql, [
                data.get("name"),
                data.get("strategy_type"),
                data.get("description"),
                data.get("enabled", 1),
            ])
            strategy_id = cursor.lastrowid
        conn.commit()
        return strategy_id
    finally:
        conn.close()


def get_strategy(strategy_id: int) -> dict:
    """获取单个策略"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM strategy WHERE id = %s", [strategy_id])
            return cursor.fetchone()
    finally:
        conn.close()


def get_strategies(enabled_only=False, page=1, page_size=20) -> dict:
    """分页查询策略列表，按 created_at DESC"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            conditions = []
            params = []
            if enabled_only:
                conditions.append("enabled = 1")
            where = (" WHERE " + " AND ".join(conditions)) if conditions else ""

            base_sql = f"SELECT * FROM strategy{where} ORDER BY created_at DESC"
            count_sql = f"SELECT COUNT(*) AS total FROM strategy{where}"
            return paginate_sql(base_sql, count_sql, params, page, page_size, cursor)
    finally:
        conn.close()


def update_strategy(strategy_id: int, data: dict) -> bool:
    """更新策略"""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            allowed = {"name", "strategy_type", "description", "enabled"}
            sets = []
            params = []
            for key, value in data.items():
                if key in allowed:
                    sets.append(f"{key} = %s")
                    params.append(value)
            if not sets:
                return False
            params.append(strategy_id)
            sql = f"UPDATE strategy SET {', '.join(sets)} WHERE id = %s"
            cursor.execute(sql, params)
            affected = cursor.rowcount
        conn.commit()
        return affected > 0
    finally:
        conn.close()


def create_version(data: dict) -> int:
    """创建策略版本，返回 version_id"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            params_json = data.get("params_json")
            if isinstance(params_json, (dict, list)):
                params_json = json.dumps(params_json, ensure_ascii=False)
            buy_rules_json = data.get("buy_rules_json")
            if isinstance(buy_rules_json, (dict, list)):
                buy_rules_json = json.dumps(buy_rules_json, ensure_ascii=False)
            sell_rules_json = data.get("sell_rules_json")
            if isinstance(sell_rules_json, (dict, list)):
                sell_rules_json = json.dumps(sell_rules_json, ensure_ascii=False)

            sql = """
                INSERT INTO strategy_version (strategy_id, version, params_json, buy_rules_json, sell_rules_json, remark)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, [
                data.get("strategy_id"),
                data.get("version"),
                params_json,
                buy_rules_json,
                sell_rules_json,
                data.get("remark"),
            ])
            version_id = cursor.lastrowid
        conn.commit()
        return version_id
    finally:
        conn.close()


def get_versions(strategy_id: int) -> list:
    """获取策略的所有版本，按 version DESC 排序"""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM strategy_version WHERE strategy_id = %s ORDER BY version DESC",
                [strategy_id],
            )
            return cursor.fetchall()
    finally:
        conn.close()


def get_latest_version(strategy_id: int) -> dict:
    """获取策略最新版本"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM strategy_version WHERE strategy_id = %s ORDER BY version DESC LIMIT 1",
                [strategy_id],
            )
            return cursor.fetchone()
    finally:
        conn.close()


def create_run(data: dict) -> int:
    """创建策略运行记录，返回 run_id"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO strategy_run (strategy_id, version_id, trade_date, status, signal_count, task_job_id)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, [
                data.get("strategy_id"),
                data.get("version_id"),
                data.get("trade_date"),
                data.get("status", "pending"),
                data.get("signal_count", 0),
                data.get("task_job_id"),
            ])
            run_id = cursor.lastrowid
        conn.commit()
        return run_id
    finally:
        conn.close()


def get_runs(strategy_id: int, page=1, page_size=20) -> dict:
    """分页查询策略运行记录"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            base_sql = "SELECT * FROM strategy_run WHERE strategy_id = %s ORDER BY trade_date DESC"
            count_sql = "SELECT COUNT(*) AS total FROM strategy_run WHERE strategy_id = %s"
            return paginate_sql(base_sql, count_sql, [strategy_id], page, page_size, cursor)
    finally:
        conn.close()


def update_run(run_id: int, data: dict) -> bool:
    """更新策略运行记录"""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            allowed = {"status", "signal_count", "task_job_id", "message", "started_at", "finished_at"}
            sets = []
            params = []
            for key, value in data.items():
                if key in allowed:
                    sets.append(f"{key} = %s")
                    params.append(value)
            if not sets:
                return False

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            status = data.get("status")
            if status == "running" and "started_at" not in data:
                sets.append("started_at = %s")
                params.append(now)
            elif status in ("success", "failed") and "finished_at" not in data:
                sets.append("finished_at = %s")
                params.append(now)

            params.append(run_id)
            sql = f"UPDATE strategy_run SET {', '.join(sets)} WHERE id = %s"
            cursor.execute(sql, params)
            affected = cursor.rowcount
        conn.commit()
        return affected > 0
    finally:
        conn.close()
