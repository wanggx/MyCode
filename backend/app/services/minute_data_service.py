"""分钟线数据服务 — 接收行情推送并批量落库"""
import logging
import threading
import time
from datetime import datetime

from app.repositories import minute_repo

logger = logging.getLogger(__name__)


class MinuteDataService:
    """分钟线行情接收与落库"""

    def __init__(self):
        self._buffer: list[dict] = []
        self._lock = threading.Lock()
        self._flush_interval = 30  # 每 30 秒批量写入一次
        self._running = False
        self._thread: threading.Thread = None
        self._flush_count = 0

    # ---- Bridge Client 回调 ----

    def on_quote(self, symbol: str, bar: dict):
        """接收 Bridge WebSocket 推送的行情数据"""
        record = {
            "ts_code": symbol,
            "trade_time": self._format_time(bar.get("time", "")),
            "open": bar.get("open", 0),
            "high": bar.get("high", 0),
            "low": bar.get("low", 0),
            "close": bar.get("close", 0),
            "volume": bar.get("volume", 0),
            "amount": bar.get("amount", 0),
        }
        with self._lock:
            self._buffer.append(record)

    # ---- 批量写入 ----

    def start_flush_thread(self):
        """启动后台定时写入线程"""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._flush_loop, daemon=True)
        self._thread.start()
        logger.info(f"分钟线写入线程已启动（间隔 {self._flush_interval}s）")

    def stop_flush_thread(self):
        """停止写入线程并 flush 剩余数据"""
        self._running = False
        if self._thread:
            self._thread.join(timeout=5)
        self._flush()

    def _flush_loop(self):
        """定时 flush 循环"""
        while self._running:
            time.sleep(self._flush_interval)
            self._flush()

    def _flush(self):
        """将缓冲区的数据批量写入数据库"""
        with self._lock:
            if not self._buffer:
                return
            bars = self._buffer[:]
            self._buffer.clear()

        if bars:
            count = minute_repo.batch_insert(bars)
            self._flush_count += count
            logger.info(f"分钟线批量写入: {count} 条 (累计 {self._flush_count})")

    # ---- 查询 ----

    def get_bars(self, ts_code: str, trade_date: str = None,
                 page: int = 1, page_size: int = 240) -> dict:
        return minute_repo.get_minute_bars(ts_code, trade_date, page, page_size)

    def get_latest(self, ts_code: str) -> dict:
        return minute_repo.get_latest(ts_code)

    # ----

    @staticmethod
    def _format_time(time_str: str) -> str:
        """将 HH:MM:SS 格式的时间字符串补全为完整 datetime"""
        today = datetime.now().strftime("%Y-%m-%d")
        if ":" in time_str and len(time_str) <= 8:
            return f"{today} {time_str}"
        return time_str[:19] if time_str else ""


# 全局单例
minute_data_service = MinuteDataService()
