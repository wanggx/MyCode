"""下单 REST API"""
from fastapi import APIRouter, HTTPException

from server.xtquant.wrapper import get_provider
from server.models import OrderRequest, OrderResponse, CancelRequest

router = APIRouter(prefix="/api/bridge", tags=["order"])


@router.post("/order", response_model=OrderResponse)
async def submit_order(req: OrderRequest):
    """提交订单"""
    if req.direction not in ("buy", "sell"):
        raise HTTPException(400, "direction 仅支持 buy / sell")
    if req.order_type not in ("limit", "market"):
        raise HTTPException(400, "order_type 仅支持 limit / market")

    try:
        provider = get_provider()
        result = provider.submit_order(
            symbol=req.symbol, direction=req.direction,
            price=req.price, quantity=req.quantity,
            order_type=req.order_type,
        )
        return OrderResponse(**result)
    except Exception as e:
        raise HTTPException(500, f"下单失败: {e}")


@router.delete("/order/{order_id}")
async def cancel_order(order_id: str):
    """撤销订单"""
    try:
        provider = get_provider()
        ok = provider.cancel_order(order_id)
        if not ok:
            raise HTTPException(404, "订单不存在或无法撤销")
        return {"success": True, "message": "订单已撤销"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, f"撤单失败: {e}")
