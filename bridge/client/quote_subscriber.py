"""行情订阅管理器 — 管理多标的订阅与数据落库"""
import logging
from collections import defaultdict
from typing import Callable, Optional

from bridge.client.bridge_client import BridgeClient

logger = logging.getLogger(__name__)


class QuoteSubscriber:
    """行情订阅管理"""

    def __init__(self, client: BridgeClient):
        self.client = client
        self._symbols: set[str] = set()
        self._on_quote: Optional[Callable] = None
        self._quote_buffer: dict[str, list[dict]] = defaultdict(list)
        self._max_buffer_size = 100

    @property
    def subscribed_symbols(self) -> list[str]:
        return sorted(self._symbols)

    def on_quote(self, callback: Callable):
        """设置行情推送回调 callback(symbol, bar)"""
        self._on_quote = callback

        def ws_callback(data: dict):
            symbol = data.get("symbol", "")
            self._quote_buffer[symbol].append(data)
            if len(self._quote_buffer[symbol]) > self._max_buffer_size:
                self._quote_buffer[symbol] = self._quote_buffer[symbol][-self._max_buffer_size:]
            if self._on_quote:
                self._on_quote(symbol, data)

        # 注册到 client
        for symbol in self._symbols:
            self.client.subscribe(symbol, ws_callback)

    def add_symbols(self, symbols: list[str]):
        """新增订阅标的"""
        new_symbols = [s for s in symbols if s not in self._symbols]
        if not new_symbols:
            return
        self._symbols.update(new_symbols)
        logger.info(f"新增行情订阅: {new_symbols}")

    def remove_symbols(self, symbols: list[str]):
        """取消订阅"""
        for s in symbols:
            self._symbols.discard(s)
            self.client.unsubscribe(s)
            self._quote_buffer.pop(s, None)

    def get_recent_bars(self, symbol: str, count: int = 10) -> list[dict]:
        """获取缓存中的最近 N 根 K 线"""
        return self._quote_buffer.get(symbol, [])[-count:]

    def flush_buffer(self, symbol: str = None):
        """清空缓存"""
        if symbol:
            self._quote_buffer.pop(symbol, None)
        else:
            self._quote_buffer.clear()
