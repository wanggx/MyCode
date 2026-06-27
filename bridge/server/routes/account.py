"""账户查询 REST API"""
from fastapi import APIRouter, HTTPException

from server.xtquant.wrapper import get_provider
from server.models import AccountInfo

router = APIRouter(prefix="/api/bridge", tags=["account"])


@router.get("/account", response_model=AccountInfo)
async def get_account():
    """查询账户信息（资金、持仓）"""
    try:
        provider = get_provider()
        return provider.get_account()
    except Exception as e:
        raise HTTPException(500, f"查询账户失败: {e}")


@router.get("/positions")
async def get_positions():
    """查询当前持仓"""
    try:
        provider = get_provider()
        if hasattr(provider, "get_positions"):
            return provider.get_positions()
        # Mock provider: 返回 account 中的 positions
        account = provider.get_account()
        return account.positions if hasattr(account, "positions") else []
    except Exception as e:
        raise HTTPException(500, f"查询持仓失败: {e}")
