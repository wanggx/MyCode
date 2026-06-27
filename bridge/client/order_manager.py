"""订单管理器 — 订单提交、状态跟踪、成交回调"""
import logging
from datetime import datetime
from typing import Callable, Optional

from bridge.client.bridge_client import BridgeClient

logger = logging.getLogger(__name__)

# 订单状态常量
ORDER_PENDING = "pending"
ORDER_FILLED = "filled"
ORDER_CANCELLED = "cancelled"
ORDER_REJECTED = "rejected"


class Order:
    """订单对象"""
    def __init__(self, order_id: str, symbol: str, direction: str,
                 price: float, quantity: int, order_type: str = "limit"):
        self.order_id = order_id
        self.symbol = symbol
        self.direction = direction
        self.price = price
        self.quantity = quantity
        self.order_type = order_type
        self.status = ORDER_PENDING
        self.filled_quantity = 0
        self.filled_price = 0.0
        self.created_at = datetime.now()
        self.filled_at: Optional[datetime] = None
        self.message = ""

    def to_dict(self) -> dict:
        return {
            "order_id": self.order_id, "symbol": self.symbol,
            "direction": self.direction, "price": self.price,
            "quantity": self.quantity, "order_type": self.order_type,
            "status": self.status, "filled_quantity": self.filled_quantity,
            "filled_price": self.filled_price,
            "created_at": str(self.created_at)[:19],
            "filled_at": str(self.filled_at)[:19] if self.filled_at else "",
            "message": self.message,
        }


class OrderManager:
    """订单生命周期管理"""

    def __init__(self, client: BridgeClient):
        self.client = client
        self._orders: dict[str, Order] = {}
        self._on_fill: Optional[Callable] = None

    @property
    def pending_orders(self) -> list[Order]:
        return [o for o in self._orders.values() if o.status == ORDER_PENDING]

    @property
    def filled_orders(self) -> list[Order]:
        return [o for o in self._orders.values() if o.status == ORDER_FILLED]

    def on_order_filled(self, callback: Callable):
        """成交回调: callback(order)"""
        self._on_fill = callback

    def submit(self, symbol: str, direction: str, price: float,
               quantity: int, order_type: str = "limit") -> Order:
        """提交订单"""
        result = self.client.submit_order(
            symbol=symbol, direction=direction, price=price,
            quantity=quantity, order_type=order_type,
        )
        order = Order(
            order_id=result.get("order_id", ""),
            symbol=symbol, direction=direction,
            price=price, quantity=quantity,
            order_type=order_type,
        )
        order.status = result.get("status", ORDER_PENDING)
        order.message = result.get("message", "")
        if order.status == ORDER_FILLED:
            order.filled_quantity = quantity
            order.filled_price = price
            order.filled_at = datetime.now()
        self._orders[order.order_id] = order

        if order.status == ORDER_FILLED and self._on_fill:
            self._on_fill(order)

        logger.info(f"订单已提交: {order.order_id} {direction} {symbol} "
                    f"{quantity}@{price} status={order.status}")
        return order

    def cancel(self, order_id: str) -> bool:
        """撤销订单"""
        ok = self.client.cancel_order(order_id)
        if ok and order_id in self._orders:
            self._orders[order_id].status = ORDER_CANCELLED
        return ok

    def get_order(self, order_id: str) -> Optional[Order]:
        return self._orders.get(order_id)

    def get_orders_by_symbol(self, symbol: str) -> list[Order]:
        return [o for o in self._orders.values() if o.symbol == symbol]

    def get_all_orders(self) -> list[Order]:
        return sorted(self._orders.values(), key=lambda o: o.created_at, reverse=True)
