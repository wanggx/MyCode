#!/usr/bin/env python3
"""QuantBridge Client 自测 — 验证 HTTP + WebSocket 通信"""
import asyncio
import sys
import time

from bridge.client.bridge_client import BridgeClient, BridgeConfig
from bridge.client.quote_subscriber import QuoteSubscriber
from bridge.client.order_manager import OrderManager


def test_health(client):
    assert client.health_check(), "health check failed"
    print("✓ Health check")


def test_quote(client):
    bars = client.get_quote("000001.SZ", "1m", 10)
    assert len(bars) == 10
    assert "close" in bars[0]
    print(f"✓ Quote 1m: {len(bars)} bars, close={bars[-1]['close']}")


def test_order(client):
    om = OrderManager(client)
    order = om.submit("000001.SZ", "buy", 12.50, 1000, "limit")
    assert order.status == "filled"
    assert order.order_id.startswith("MOCK-")
    print(f"✓ Order: {order.order_id} status={order.status}")


def test_account(client):
    account = client.get_account()
    assert account["total_asset"] > 0
    print(f"✓ Account: total_asset={account['total_asset']}")


async def test_websocket(client):
    """测试 WebSocket 连接和行情推送"""
    received = []

    def on_quote(symbol, bar):
        received.append((symbol, bar))

    sub = QuoteSubscriber(client)
    sub.add_symbols(["000001.SZ", "600036.SH"])
    sub.on_quote(on_quote)

    # 启动 WebSocket
    task = asyncio.create_task(client.connect_ws(sub.subscribed_symbols))

    # 等待至少收到 2 条行情
    for _ in range(15):
        await asyncio.sleep(0.5)
        if len(received) >= 2:
            break

    await client.stop()
    task.cancel()

    assert len(received) >= 1, f"No quotes received, got {len(received)}"
    print(f"✓ WebSocket: received {len(received)} quotes, "
          f"symbols={set(s for s, _ in received)}")


async def main():
    config = BridgeConfig(host="localhost", port=5101)
    client = BridgeClient(config)

    print("=== QuantBridge Client 自测 ===\n")

    # REST API
    test_health(client)
    test_quote(client)
    test_order(client)
    test_account(client)
    print()

    # WebSocket
    await test_websocket(client)

    print("\n✅ Client 全部测试通过！")


if __name__ == "__main__":
    asyncio.run(main())
