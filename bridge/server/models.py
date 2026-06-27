"""Pydantic 数据模型"""
from typing import Optional, List
from pydantic import BaseModel, Field


# ---- 行情 ----

class KlineBar(BaseModel):
    """单根 K 线"""
    time: str = Field(..., description="时间 (HH:MM:SS 或 YYYY-MM-DD)")
    open: float
    high: float
    low: float
    close: float
    volume: int
    amount: float = 0.0


class QuoteResponse(BaseModel):
    """行情查询响应"""
    symbol: str
    period: str  # "1m" | "1d"
    count: int
    bars: List[KlineBar]


# ---- 订单 ----

class OrderRequest(BaseModel):
    """下单请求"""
    symbol: str = Field(..., description="股票代码，如 000001.SZ")
    direction: str = Field(..., description="buy | sell")
    price: float = Field(..., description="委托价格（市价单填 0）")
    quantity: int = Field(..., gt=0, description="委托数量（股）")
    order_type: str = Field(default="limit", description="limit | market")


class OrderResponse(BaseModel):
    """下单响应"""
    order_id: str
    symbol: str
    direction: str
    price: float
    quantity: int
    status: str = "pending"
    message: str = ""


class CancelRequest(BaseModel):
    """撤单请求"""
    order_id: str


# ---- 账户 ----

class Position(BaseModel):
    """持仓"""
    symbol: str
    name: str = ""
    quantity: int
    cost_price: float
    current_price: float
    market_value: float
    pnl: float
    pnl_pct: float


class AccountInfo(BaseModel):
    """账户信息"""
    account_id: str
    total_asset: float
    available_cash: float
    frozen_cash: float
    market_value: float
    total_pnl: float
    total_pnl_pct: float
    positions: List[Position] = []


# ---- WebSocket ----

class WSMessage(BaseModel):
    """WebSocket 消息"""
    type: str  # "quote" | "order_update" | "error"
    data: dict


class SubscribeRequest(BaseModel):
    """行情订阅请求"""
    action: str  # "subscribe" | "unsubscribe"
    symbols: List[str]
