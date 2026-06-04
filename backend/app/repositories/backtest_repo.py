# -*- coding: utf-8 -*-
"""
回测数据访问层：backtest_job / backtest_nav / backtest_position / backtest_trade 的 CRUD
"""

import json
import logging
from datetime import datetime

from app.core.database import get_db_connection
from app.repositories.base import paginate_sql

logger = logging.getLogger(__name__)


def init_tables():
    """确保回测相关 4 张表存在"""
    conn = get_db_connection()
    if not conn:
        logger.error("数据库连接失败，无法初始化回测表")
        return False
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS backtest_job (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    strategy_id INT NOT NULL,
                    version_id INT NOT NULL,
                    task_job_id INT NULL,
                    start_date VARCHAR(8) NOT NULL,
                    end_date VARCHAR(8) NOT NULL,
                    benchmark VARCHAR(10) DEFAULT '000300.SH',
                    status VARCHAR(20) DEFAULT 'pending' COMMENT 'pending/running/success/failed',
                    params_json JSON COMMENT '回测参数(手续费/滑点/最大持仓等)',
                    metrics_json JSON COMMENT '风险指标(年化收益/夏普/最大回撤等)',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    started_at DATETIME NULL,
                    finished_at DATETIME NULL
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS backtest_nav (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    job_id INT NOT NULL,
                    trade_date VARCHAR(8) NOT NULL,
                    nav DECIMAL(12,4) NOT NULL,
                    benchmark_nav DECIMAL(12,4) DEFAULT NULL,
                    drawdown DECIMAL(8,4) DEFAULT 0,
                    UNIQUE KEY uk_job_date (job_id, trade_date)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS backtest_position (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    job_id INT NOT NULL,
                    trade_date VARCHAR(8) NOT NULL,
                    ts_code VARCHAR(20) NOT NULL,
                    weight DECIMAL(8,4) DEFAULT 0,
                    market_value DECIMAL(16,2) DEFAULT 0,
                    close_price DECIMAL(12,4) DEFAULT 0,
                    INDEX idx_job_date (job_id, trade_date)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS backtest_trade (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    job_id INT NOT NULL,
                    trade_date VARCHAR(8) NOT NULL,
                    ts_code VARCHAR(20) NOT NULL,
                    side VARCHAR(4) NOT NULL COMMENT 'buy/sell',
                    price DECIMAL(12,4) NOT NULL,
                    quantity INT NOT NULL,
                    amount DECIMAL(16,2) NOT NULL,
                    fee DECIMAL(10,4) DEFAULT 0,
                    reason VARCHAR(200) COMMENT '交易原因'
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
        conn.commit()
        logger.info("回测表已就绪")
        return True
    finally:
        conn.close()


def create_job(data: dict) -> int:
    """创建回测任务，返回 job_id"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            params_str = json.dumps(data.get("params_json"), ensure_ascii=False) if data.get("params_json") else None
            sql = """
                INSERT INTO backtest_job (strategy_id, version_id, task_job_id, start_date, end_date,
                    benchmark, status, params_json, metrics_json)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(sql, [
                data.get("strategy_id"),
                data.get("version_id"),
                data.get("task_job_id"),
                data.get("start_date"),
                data.get("end_date"),
                data.get("benchmark", "000300.SH"),
                data.get("status", "pending"),
                params_str,
                data.get("metrics_json"),
            ])
            job_id = cursor.lastrowid
        conn.commit()
        return job_id
    finally:
        conn.close()


def get_job(job_id: int) -> dict:
    """获取单个回测任务"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM backtest_job WHERE id = %s", [job_id])
            return cursor.fetchone()
    finally:
        conn.close()


def get_jobs(strategy_id=None, status=None, page=1, page_size=20) -> dict:
    """分页查询回测任务列表，按 created_at DESC"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            conditions = []
            params = []
            if strategy_id:
                conditions.append("strategy_id = %s")
                params.append(strategy_id)
            if status:
                conditions.append("status = %s")
                params.append(status)
            where = (" WHERE " + " AND ".join(conditions)) if conditions else ""

            base_sql = f"SELECT * FROM backtest_job{where} ORDER BY created_at DESC"
            count_sql = f"SELECT COUNT(*) AS total FROM backtest_job{where}"
            return paginate_sql(base_sql, count_sql, params, page, page_size, cursor)
    finally:
        conn.close()


def update_job(job_id: int, data: dict) -> bool:
    """更新回测任务"""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            allowed = {"task_job_id", "status", "params_json", "metrics_json", "started_at", "finished_at"}
            sets = []
            params = []
            for key, value in data.items():
                if key in allowed:
                    if key in ("params_json", "metrics_json") and isinstance(value, (dict, list)):
                        value = json.dumps(value, ensure_ascii=False)
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

            params.append(job_id)
            sql = f"UPDATE backtest_job SET {', '.join(sets)} WHERE id = %s"
            cursor.execute(sql, params)
            affected = cursor.rowcount
        conn.commit()
        return affected > 0
    finally:
        conn.close()


def claim_pending_job() -> dict:
    """原子性地抢占一条 pending 回测任务"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM backtest_job WHERE status = 'pending' "
                "ORDER BY created_at ASC LIMIT 1 FOR UPDATE"
            )
            job = cursor.fetchone()
            if not job:
                return None
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "UPDATE backtest_job SET status = 'running', started_at = %s WHERE id = %s",
                [now, job["id"]],
            )
        conn.commit()
        job["status"] = "running"
        job["started_at"] = now
        return job
    finally:
        conn.close()


def batch_insert_nav(items: list) -> int:
    """INSERT IGNORE 批量写入净值数据"""
    if not items:
        return 0
    conn = get_db_connection()
    if not conn:
        return 0
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT IGNORE INTO backtest_nav (job_id, trade_date, nav, benchmark_nav, drawdown)
                VALUES (%s, %s, %s, %s, %s)
            """
            rows = [(i["job_id"], i["trade_date"], i["nav"], i.get("benchmark_nav"), i.get("drawdown", 0)) for i in items]
            cursor.executemany(sql, rows)
            affected = cursor.rowcount
        conn.commit()
        return affected
    finally:
        conn.close()


def get_navs(job_id: int) -> list:
    """获取净值列表"""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM backtest_nav WHERE job_id = %s ORDER BY trade_date",
                [job_id],
            )
            return cursor.fetchall()
    finally:
        conn.close()


def batch_insert_positions(items: list) -> int:
    """先按 job_id 删除再批量插入持仓"""
    if not items:
        return 0
    conn = get_db_connection()
    if not conn:
        return 0
    try:
        with conn.cursor() as cursor:
            job_id = items[0]["job_id"]
            cursor.execute("DELETE FROM backtest_position WHERE job_id = %s", [job_id])
            sql = """
                INSERT INTO backtest_position (job_id, trade_date, ts_code, weight, market_value, close_price)
                VALUES (%s, %s, %s, %s, %s, %s)
            """
            rows = [(i["job_id"], i["trade_date"], i["ts_code"], i.get("weight", 0), i.get("market_value", 0), i.get("close_price", 0)) for i in items]
            cursor.executemany(sql, rows)
            affected = cursor.rowcount
        conn.commit()
        return affected
    finally:
        conn.close()


def get_positions(job_id: int, trade_date: str = None) -> list:
    """获取持仓列表"""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            if trade_date:
                cursor.execute(
                    "SELECT * FROM backtest_position WHERE job_id = %s AND trade_date = %s ORDER BY ts_code",
                    [job_id, trade_date],
                )
            else:
                cursor.execute(
                    "SELECT * FROM backtest_position WHERE job_id = %s ORDER BY trade_date, ts_code",
                    [job_id],
                )
            return cursor.fetchall()
    finally:
        conn.close()


def batch_insert_trades(items: list) -> int:
    """批量插入交易记录"""
    if not items:
        return 0
    conn = get_db_connection()
    if not conn:
        return 0
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO backtest_trade (job_id, trade_date, ts_code, side, price, quantity, amount, fee, reason)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            rows = [(i["job_id"], i["trade_date"], i["ts_code"], i["side"], i["price"], i["quantity"], i["amount"], i.get("fee", 0), i.get("reason")) for i in items]
            cursor.executemany(sql, rows)
            affected = cursor.rowcount
        conn.commit()
        return affected
    finally:
        conn.close()


def get_trades(job_id: int, page=1, page_size=20) -> dict:
    """获取交易明细（分页）"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            base_sql = "SELECT * FROM backtest_trade WHERE job_id = %s ORDER BY trade_date, id"
            count_sql = "SELECT COUNT(*) AS total FROM backtest_trade WHERE job_id = %s"
            return paginate_sql(base_sql, count_sql, [job_id], page, page_size, cursor)
    finally:
        conn.close()
