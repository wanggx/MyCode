"""行情 REST API"""
from fastapi import APIRouter, Query, HTTPException

from server.xtquant.wrapper import get_provider
from server.models import KlineBar, QuoteResponse

router = APIRouter(prefix="/api/bridge", tags=["quote"])


@router.get("/quote/{symbol}", response_model=QuoteResponse)
async def get_quote(
    symbol: str,
    period: str = Query("1m", description="K线周期: 1m / 1d"),
    count: int = Query(100, ge=1, le=500, description="K线数量"),
):
    """获取 K 线数据"""
    if period not in ("1m", "1d"):
        raise HTTPException(400, "period 仅支持 1m / 1d")

    try:
        provider = get_provider()
        bars = provider.get_kline(symbol, period, count)
        return QuoteResponse(symbol=symbol, period=period, count=len(bars), bars=bars)
    except Exception as e:
        raise HTTPException(500, f"获取行情失败: {e}")
