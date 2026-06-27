#!/usr/bin/env python3
"""QuantBridge Server 自测脚本 — 验证所有 API 和 WebSocket"""
import asyncio
import json
import sys
import requests
import websockets

BASE_URL = "http://localhost:5101"
WS_URL = "ws://localhost:5101/ws/quote"


def test_health():
    """测试健康检查"""
    r = requests.get(f"{BASE_URL}/health")
    assert r.status_code == 200, f"health failed: {r.status_code}"
    data = r.json()
    assert data["status"] == "ok"
    print("✓ Health check")


def test_quote_1m():
    """测试 1m K线"""
    r = requests.get(f"{BASE_URL}/api/bridge/quote/000001.SZ?period=1m&count=10")
    assert r.status_code == 200, f"quote failed: {r.status_code}"
    data = r.json()
    assert len(data["bars"]) == 10
    assert data["symbol"] == "000001.SZ"
    assert data["period"] == "1m"
    print(f"✓ 1m K线: {len(data['bars'])} bars, last close={data['bars'][-1]['close']}")


def test_quote_1d():
    """测试日K线"""
    r = requests.get(f"{BASE_URL}/api/bridge/quote/600036.SH?period=1d&count=20")
    assert r.status_code == 200
    data = r.json()
    assert len(data["bars"]) == 20
    print(f"✓ 日K线: {len(data['bars'])} bars")


def test_order():
    """测试下单"""
    payload = {"symbol": "000001.SZ", "direction": "buy", "price": 12.50,
               "quantity": 1000, "order_type": "limit"}
    r = requests.post(f"{BASE_URL}/api/bridge/order", json=payload)
    assert r.status_code == 200, f"order failed: {r.status_code}"
    data = r.json()
    assert data["order_id"].startswith("MOCK-")
    assert data["status"] == "filled"
    print(f"✓ 下单: order_id={data['order_id']}")


def test_cancel_order():
    """测试撤单"""
    # 先下单
    payload = {"symbol": "000001.SZ", "direction": "buy", "price": 12.50,
               "quantity": 500, "order_type": "limit"}
    r = requests.post(f"{BASE_URL}/api/bridge/order", json=payload)
    order_id = r.json()["order_id"]

    # 再撤单
    r = requests.delete(f"{BASE_URL}/api/bridge/order/{order_id}")
    assert r.status_code == 200
    print(f"✓ 撤单: {order_id}")


def test_account():
    """测试账户查询"""
    r = requests.get(f"{BASE_URL}/api/bridge/account")
    assert r.status_code == 200
    data = r.json()
    assert data["account_id"] == "MOCK-ACCOUNT-001"
    assert data["total_asset"] > 0
    assert len(data["positions"]) == 2
    print(f"✓ 账户: total_asset={data['total_asset']}, positions={len(data['positions'])}")


def test_positions():
    """测试持仓查询"""
    r = requests.get(f"{BASE_URL}/api/bridge/positions")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 2
    print(f"✓ 持仓: {len(data)} positions")


async def test_websocket():
    """测试 WebSocket"""
    async with websockets.connect(WS_URL) as ws:
        # 订阅
        await ws.send(json.dumps({"action": "subscribe", "symbols": ["000001.SZ"]}))
        sub_resp = await asyncio.wait_for(ws.recv(), timeout=5)
        sub_data = json.loads(sub_resp)
        assert sub_data["type"] == "subscribed"
        print(f"✓ WS 订阅: {sub_data['symbols']}")

        # 接收行情推送
        quote_resp = await asyncio.wait_for(ws.recv(), timeout=10)
        quote_data = json.loads(quote_resp)
        assert quote_data["type"] == "quote"
        assert quote_data["data"]["symbol"] == "000001.SZ"
        print(f"✓ WS 行情: {quote_data['data']['symbol']} close={quote_data['data']['close']}")


async def main():
    print("=== QuantBridge Server 自测 ===\n")

    # REST API 测试
    test_health()
    test_quote_1m()
    test_quote_1d()
    test_order()
    test_cancel_order()
    test_account()
    test_positions()
    print()

    # WebSocket 测试
    try:
        await test_websocket()
    except Exception as e:
        print(f"✗ WebSocket 测试失败: {e}")
        sys.exit(1)

    print("\n✅ 全部测试通过！")


if __name__ == "__main__":
    asyncio.run(main())
