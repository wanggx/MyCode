"""miniQMT xtquant SDK 封装（Windows 真实环境）"""


class XtQuantWrapper:
    """封装 xtquant SDK，提供与 MockDataProvider 相同接口"""

    def __init__(self, miniqmt_path: str, account: str):
        self.path = miniqmt_path
        self.account = account
        self._connected = False
        self._xtdata = None
        self._xttrade = None

    def connect(self) -> bool:
        """连接 miniQMT"""
        try:
            from xtquant import xtdata, xttrade
            self._xtdata = xtdata
            self._xttrade = xttrade
            self._connected = True
            return True
        except ImportError:
            raise RuntimeError(
                "xtquant SDK 未安装。请在 Windows 环境下运行：\n"
                "pip install xtquant  # 或从 miniQMT 安装目录复制"
            )
        except Exception as e:
            raise RuntimeError(f"连接 miniQMT 失败: {e}")

    # ---- 行情 ----
    def get_kline(self, symbol: str, period: str, count: int = 100):
        if not self._connected:
            raise RuntimeError("未连接 miniQMT")
        # period: "1m" → xtdata 使用 "1min"
        xt_period = {"1m": "1min", "1d": "1day"}.get(period, period)
        data = self._xtdata.get_market_data_ex(
            [], [symbol], period=xt_period, count=count
        )
        # 转换为标准格式
        bars = []
        if data and symbol in data:
            df = data[symbol]
            for i in range(len(df)):
                bars.append({
                    "time": str(df.index[i]),
                    "open": float(df['open'].iloc[i]),
                    "high": float(df['high'].iloc[i]),
                    "low": float(df['low'].iloc[i]),
                    "close": float(df['close'].iloc[i]),
                    "volume": int(df['volume'].iloc[i]),
                    "amount": float(df.get('amount', 0).iloc[i]),
                })
        return bars

    def subscribe_quote(self, symbols: list, callback):
        """订阅实时行情"""
        if not self._connected:
            raise RuntimeError("未连接 miniQMT")
        for symbol in symbols:
            self._xtdata.subscribe_quote(symbol, period="1m", callback=callback)

    # ---- 交易 ----
    def submit_order(self, symbol: str, direction: str, price: float,
                     quantity: int, order_type: str) -> dict:
        if not self._connected:
            raise RuntimeError("未连接 miniQMT")
        # direction: buy/sell → xttrade 常量
        # TODO: 根据实际 xttrade API 完成下单逻辑
        return {"order_id": "XT-xxx", "status": "pending"}

    def cancel_order(self, order_id: str) -> bool:
        if not self._connected:
            raise RuntimeError("未连接 miniQMT")
        # TODO: 调用 xttrade 撤单
        return True

    def get_account(self) -> dict:
        if not self._connected:
            raise RuntimeError("未连接 miniQMT")
        # TODO: 调用 xttrade 查询账户
        return {"account_id": self.account, "total_asset": 0}

    def get_positions(self) -> list:
        if not self._connected:
            raise RuntimeError("未连接 miniQMT")
        # TODO: 调用 xttrade 查询持仓
        return []

    @property
    def connected(self) -> bool:
        return self._connected


# 全局单例（在 server 启动时初始化）
xtquant_wrapper: XtQuantWrapper = None


def get_provider():
    """根据配置返回真实 wrapper 或 mock provider"""
    from server.config import MOCK_MODE
    if MOCK_MODE:
        from server.xtquant.mock import mock_provider
        return mock_provider
    else:
        if xtquant_wrapper is None:
            raise RuntimeError("xtquant 未初始化")
        return xtquant_wrapper
