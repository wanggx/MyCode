"""QuantBridge Client — Linux 端连接 Windows FastAPI Server"""
import asyncio
import json
import logging
import time
from typing import Optional, Callable
from dataclasses import dataclass, field

import requests
import websockets

logger = logging.getLogger(__name__)


@dataclass
class BridgeConfig:
    """连接配置"""
    host: str = "localhost"
    port: int = 5101
    ws_path: str = "/ws/quote"
    max_retries: int = 3
    retry_delay: float = 2.0
    request_timeout: float = 10.0

    @property
    def base_url(self) -> str:
        return f"http://{self.host}:{self.port}"

    @property
    def ws_url(self) -> str:
        return f"ws://{self.host}:{self.port}{self.ws_path}"


class BridgeClient:
    """QuantBridge HTTP + WebSocket 客户端"""

    def __init__(self, config: BridgeConfig = None):
        self.config = config or BridgeConfig()
        self._ws: Optional[websockets.WebSocketClientProtocol] = None
        self._ws_task: Optional[asyncio.Task] = None
        self._running = False
        self._subscribers: dict[str, list[Callable]] = {}  # symbol → [callbacks]
        self._on_reconnect: Optional[Callable] = None

    # ==================== REST API ====================

    def get_quote(self, symbol: str, period: str = "1m", count: int = 100) -> list[dict]:
        """获取K线数据"""
        url = f"{self.config.base_url}/api/bridge/quote/{symbol}"
        resp = requests.get(url, params={"period": period, "count": count},
                            timeout=self.config.request_timeout)
        resp.raise_for_status()
        return resp.json().get("bars", [])

    def submit_order(self, symbol: str, direction: str, price: float,
                     quantity: int, order_type: str = "limit") -> dict:
        """提交订单"""
        url = f"{self.config.base_url}/api/bridge/order"
        payload = {"symbol": symbol, "direction": direction, "price": price,
                   "quantity": quantity, "order_type": order_type}
        resp = requests.post(url, json=payload, timeout=self.config.request_timeout)
        resp.raise_for_status()
        return resp.json()

    def cancel_order(self, order_id: str) -> bool:
        """撤销订单"""
        url = f"{self.config.base_url}/api/bridge/order/{order_id}"
        resp = requests.delete(url, timeout=self.config.request_timeout)
        return resp.status_code == 200

    def get_account(self) -> dict:
        """查询账户"""
        url = f"{self.config.base_url}/api/bridge/account"
        resp = requests.get(url, timeout=self.config.request_timeout)
        resp.raise_for_status()
        return resp.json()

    def get_positions(self) -> list[dict]:
        """查询持仓"""
        url = f"{self.config.base_url}/api/bridge/positions"
        resp = requests.get(url, timeout=self.config.request_timeout)
        resp.raise_for_status()
        return resp.json()

    def health_check(self) -> bool:
        """检查服务是否可达"""
        try:
            resp = requests.get(f"{self.config.base_url}/health", timeout=3)
            return resp.status_code == 200
        except Exception:
            return False

    # ==================== WebSocket ====================

    async def connect_ws(self, symbols: list[str] = None):
        """连接 WebSocket 并开始接收行情"""
        self._running = True
        retries = 0

        while self._running:
            try:
                self._ws = await websockets.connect(self.config.ws_url)
                logger.info(f"WebSocket 已连接: {self.config.ws_url}")

                # 订阅行情
                if symbols:
                    await self._subscribe_ws(symbols)

                # 接收消息循环
                async for message in self._ws:
                    try:
                        data = json.loads(message)
                        await self._handle_ws_message(data)
                    except Exception as e:
                        logger.error(f"WebSocket 消息处理失败: {e}")

            except (websockets.ConnectionClosed, OSError) as e:
                logger.warning(f"WebSocket 断开: {e}")
            except Exception as e:
                logger.error(f"WebSocket 异常: {e}")

            if self._running:
                retries += 1
                delay = min(self.config.retry_delay * retries, 30)
                logger.info(f"{delay}s 后重连 (第 {retries} 次)...")
                await asyncio.sleep(delay)
                if self._on_reconnect:
                    try:
                        self._on_reconnect()
                    except Exception:
                        pass
            retries = 0  # reset on successful connection

    async def disconnect_ws(self):
        """断开 WebSocket"""
        self._running = False
        if self._ws:
            await self._ws.close()
            self._ws = None

    def on_reconnect(self, callback: Callable):
        """注册重连回调"""
        self._on_reconnect = callback

    def subscribe(self, symbol: str, callback: Callable):
        """订阅某只股票的行情推送"""
        if symbol not in self._subscribers:
            self._subscribers[symbol] = []
        self._subscribers[symbol].append(callback)

    def unsubscribe(self, symbol: str, callback: Callable = None):
        """取消订阅"""
        if callback:
            self._subscribers.get(symbol, []).remove(callback)
        else:
            self._subscribers.pop(symbol, None)

    async def _subscribe_ws(self, symbols: list[str]):
        """通过 WebSocket 发送订阅请求"""
        if self._ws:
            await self._ws.send(json.dumps({"action": "subscribe", "symbols": symbols}))

    async def _handle_ws_message(self, data: dict):
        """处理 WebSocket 消息并分发给订阅者"""
        msg_type = data.get("type")
        if msg_type == "quote":
            quote_data = data.get("data", {})
            symbol = quote_data.get("symbol", "")
            for cb in self._subscribers.get(symbol, []):
                try:
                    cb(quote_data)
                except Exception as e:
                    logger.error(f"行情回调失败 [{symbol}]: {e}")
        elif msg_type == "subscribed":
            logger.info(f"已订阅: {data.get('symbols', [])}")

    # ==================== 启动/停止 ====================

    def start_ws_background(self, symbols: list[str] = None):
        """在后台事件循环中启动 WebSocket"""
        try:
            loop = asyncio.get_running_loop()
            self._ws_task = loop.create_task(self.connect_ws(symbols))
        except RuntimeError:
            # 没有运行中的事件循环，创建新的
            loop = asyncio.new_event_loop()
            self._ws_task = loop.create_task(self.connect_ws(symbols))
            import threading
            t = threading.Thread(target=loop.run_forever, daemon=True)
            t.start()

    async def stop(self):
        """停止客户端"""
        self._running = False
        await self.disconnect_ws()
        if self._ws_task:
            self._ws_task.cancel()


# 全局单例（在主 Flask app 中使用）
bridge_client = BridgeClient()
