"""模拟行情生成器 — 非 Windows 环境开发使用"""
import random
import time
from datetime import datetime, timedelta
from typing import List

from server.models import KlineBar, Position, AccountInfo


class MockDataProvider:
    """生成模拟行情和账户数据"""

    @staticmethod
    def get_kline(symbol: str, period: str, count: int = 100) -> List[KlineBar]:
        """生成模拟 K 线数据"""
        base_price = MockDataProvider._base_price(symbol)
        now = datetime.now()
        bars = []
        close = base_price * (0.9 + random.random() * 0.2)

        for i in range(count - 1, -1, -1):
            if period == "1m":
                t = now - timedelta(minutes=i)
                time_str = t.strftime("%H:%M:%S")
                volatility = base_price * 0.001  # 0.1% per minute
            else:  # 1d
                t = now - timedelta(days=i)
                while t.weekday() >= 5:
                    t -= timedelta(days=1)
                time_str = t.strftime("%Y-%m-%d")
                volatility = base_price * 0.02  # 2% per day

            open_p = close + (random.random() - 0.5) * volatility * 0.5
            close = open_p + (random.random() - 0.48) * volatility
            high = max(open_p, close) + random.random() * volatility * 0.5
            low = min(open_p, close) - random.random() * volatility * 0.5
            volume = random.randint(10000, 500000)

            bars.append(KlineBar(
                time=time_str, open=round(open_p, 2), high=round(high, 2),
                low=round(low, 2), close=round(close, 2),
                volume=volume, amount=round(volume * close, 2),
            ))
        return bars

    @staticmethod
    def get_current_quote(symbol: str) -> KlineBar:
        """获取当前最新行情（用于 WebSocket 推送）"""
        bars = MockDataProvider.get_kline(symbol, "1m", 2)
        return bars[-1]

    @staticmethod
    def get_account() -> AccountInfo:
        """生成模拟账户数据"""
        positions = [
            Position(symbol="000001.SZ", name="平安银行", quantity=3000,
                     cost_price=11.80, current_price=12.50,
                     market_value=37500.0, pnl=2100.0, pnl_pct=5.93),
            Position(symbol="600036.SH", name="招商银行", quantity=500,
                     cost_price=40.30, current_price=42.80,
                     market_value=21400.0, pnl=1250.0, pnl_pct=6.20),
        ]
        mv = sum(p.market_value for p in positions)
        pnl = sum(p.pnl for p in positions)
        return AccountInfo(
            account_id="MOCK-ACCOUNT-001", total_asset=100000 + pnl,
            available_cash=100000 - mv, frozen_cash=0,
            market_value=mv, total_pnl=pnl,
            total_pnl_pct=round(pnl / 100000 * 100, 2),
            positions=positions,
        )

    @staticmethod
    def submit_order(symbol: str, direction: str, price: float,
                     quantity: int, order_type: str) -> dict:
        """模拟下单"""
        order_id = f"MOCK-{int(time.time() * 1000)}"
        return {"order_id": order_id, "symbol": symbol, "direction": direction,
                "price": price, "quantity": quantity, "status": "filled",
                "message": "模拟成交"}

    @staticmethod
    def cancel_order(order_id: str) -> bool:
        """模拟撤单"""
        return True

    @staticmethod
    def _base_price(symbol: str) -> float:
        """各股票基准价"""
        prices = {"000001.SZ": 12.50, "000002.SZ": 8.30, "600036.SH": 42.80,
                  "600519.SH": 1685.0, "300750.SZ": 198.50, "000858.SZ": 152.0}
        return prices.get(symbol, 50.0)


# 全局单例
mock_provider = MockDataProvider()
