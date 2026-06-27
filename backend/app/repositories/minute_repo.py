"""分钟线数据访问层"""
import logging
from datetime import datetime
from app.core.database import get_db_connection
from app.repositories.base import paginate_sql

logger = logging.getLogger(__name__)


def init_tables():
    """创建 stock_minute 表"""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS stock_minute (
                    id BIGINT AUTO_INCREMENT PRIMARY KEY,
                    ts_code VARCHAR(20) NOT NULL COMMENT '股票代码',
                    trade_time DATETIME NOT NULL COMMENT '交易时间',
                    open DECIMAL(10,3) NOT NULL,
                    high DECIMAL(10,3) NOT NULL,
                    low DECIMAL(10,3) NOT NULL,
                    close DECIMAL(10,3) NOT NULL,
                    volume BIGINT NOT NULL DEFAULT 0,
                    amount DECIMAL(16,2) NOT NULL DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE KEY uk_code_time (ts_code, trade_time),
                    INDEX idx_ts_code (ts_code),
                    INDEX idx_trade_time (trade_time)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
        conn.commit()
        logger.info("stock_minute 表已就绪")
        return True
    except Exception as e:
        logger.error(f"stock_minute 表初始化失败: {e}")
        return False
    finally:
        conn.close()


def batch_insert(bars: list[dict]) -> int:
    """批量插入分钟线数据（ON DUPLICATE KEY UPDATE）"""
    if not bars:
        return 0
    conn = get_db_connection()
    if not conn:
        return 0
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO stock_minute (ts_code, trade_time, open, high, low, close, volume, amount)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    open = VALUES(open), high = VALUES(high), low = VALUES(low),
                    close = VALUES(close), volume = VALUES(volume), amount = VALUES(amount)
            """
            rows = []
            for bar in bars:
                rows.append((
                    bar.get("symbol") or bar.get("ts_code", ""),
                    bar.get("trade_time") or bar.get("time", ""),
                    bar.get("open", 0), bar.get("high", 0),
                    bar.get("low", 0), bar.get("close", 0),
                    bar.get("volume", 0), bar.get("amount", 0),
                ))
            cursor.executemany(sql, rows)
            count = cursor.rowcount
        conn.commit()
        return count
    except Exception as e:
        logger.error(f"批量插入分钟线失败: {e}")
        return 0
    finally:
        conn.close()


def get_minute_bars(ts_code: str, trade_date: str = None,
                    page: int = 1, page_size: int = 240) -> dict:
    """查询分钟线"""
    conn = get_db_connection()
    if not conn:
        return {"items": [], "total": 0}
    try:
        with conn.cursor() as cursor:
            conditions = ["ts_code = %s"]
            params = [ts_code]
            if trade_date:
                conditions.append("DATE(trade_time) = %s")
                params.append(trade_date)
            where = " WHERE " + " AND ".join(conditions)
            base_sql = f"SELECT * FROM stock_minute{where} ORDER BY trade_time ASC"
            count_sql = f"SELECT COUNT(*) AS total FROM stock_minute{where}"
            return paginate_sql(base_sql, count_sql, params, page, page_size, cursor)
    finally:
        conn.close()


def get_latest_minute(ts_code: str) -> dict:
    """获取某股票最新一条分钟线"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM stock_minute WHERE ts_code = %s "
                "ORDER BY trade_time DESC LIMIT 1", [ts_code]
            )
            return cursor.fetchone()
    finally:
        conn.close()
