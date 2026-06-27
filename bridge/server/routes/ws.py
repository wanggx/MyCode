"""WebSocket 实时行情推送"""
import asyncio
import json
import logging
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from server.config import MOCK_PUSH_INTERVAL, DEFAULT_SYMBOLS
from server.xtquant.mock import mock_provider

logger = logging.getLogger(__name__)
router = APIRouter()

# 已连接的客户端
_connected_clients: dict[str, WebSocket] = {}


@router.websocket("/ws/quote")
async def websocket_quote(websocket: WebSocket):
    """WebSocket 实时行情推送"""
    await websocket.accept()
    client_id = f"{websocket.client.host}:{websocket.client.port}"
    _connected_clients[client_id] = websocket
    logger.info(f"WebSocket 客户端连接: {client_id}")

    subscribed_symbols = list(DEFAULT_SYMBOLS)

    try:
        while True:
            # 接收客户端消息（订阅/取消订阅）
            try:
                raw = await asyncio.wait_for(websocket.receive_text(), timeout=1.0)
                msg = json.loads(raw)
                action = msg.get("action")
                if action == "subscribe":
                    subscribed_symbols = msg.get("symbols", subscribed_symbols)
                    await websocket.send_json({
                        "type": "subscribed", "symbols": subscribed_symbols,
                    })
                elif action == "unsubscribe":
                    remove = set(msg.get("symbols", []))
                    subscribed_symbols = [s for s in subscribed_symbols if s not in remove]
            except asyncio.TimeoutError:
                pass  # 无消息，继续推送

            # 推送模拟行情（每 MOCK_PUSH_INTERVAL 秒一次）
            for symbol in subscribed_symbols:
                bar = mock_provider.get_current_quote(symbol)
                await websocket.send_json({
                    "type": "quote",
                    "data": {
                        "symbol": symbol,
                        "time": bar.time, "open": bar.open,
                        "high": bar.high, "low": bar.low,
                        "close": bar.close, "volume": bar.volume,
                    },
                })
            await asyncio.sleep(MOCK_PUSH_INTERVAL)

    except WebSocketDisconnect:
        logger.info(f"WebSocket 客户端断开: {client_id}")
    except Exception as e:
        logger.error(f"WebSocket 异常: {e}")
    finally:
        _connected_clients.pop(client_id, None)
