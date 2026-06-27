# QuantBridge 开发验证计划

## 概述

QuantBridge 是连接 Linux 主平台与 Windows miniQMT 的桥接层：
- **Server**：Windows 端 FastAPI 服务，封装 miniQMT SDK
- **Client**：Linux 端 Python 库，内嵌 Flask，连接 Server
- **Mock 模式**：在非 Windows 环境开发时使用模拟行情数据

## 目录结构

```
bridge/
├── PLAN.md                  # 本文件 — 开发计划
├── requirements.txt         # FastAPI 依赖
├── server/                  # Windows 端 FastAPI 服务
│   ├── main.py              # FastAPI 入口
│   ├── config.py            # 配置（端口、券商、mock模式）
│   ├── routes/
│   │   ├── quote.py         # 行情 REST API
│   │   ├── order.py         # 下单 REST API
│   │   ├── account.py       # 账户查询 REST API
│   │   └── ws.py            # WebSocket 实时推送
│   ├── xtquant/
│   │   ├── wrapper.py       # miniQMT SDK 封装（真实）
│   │   └── mock.py          # 模拟行情生成器（开发用）
│   └── models.py            # Pydantic 数据模型
└── client/                  # Linux 端客户端库
    ├── __init__.py
    ├── bridge_client.py     # HTTP + WebSocket 客户端
    ├── quote_subscriber.py  # 行情订阅管理
    └── order_manager.py     # 订单管理
```

---

## 任务清单

### Phase 1: 基础框架 + Mock 模式（可在 macOS/Linux 开发验证）

| # | 任务 | 产出 | 验证方式 |
|---|------|------|---------|
| **1.1** | 创建 FastAPI 项目骨架 | `server/main.py`, `requirements.txt` | `uvicorn main:app` 启动，访问 `/health` |
| **1.2** | Pydantic 数据模型 | `models.py` — Quote, Order, Account, Position 模型 | 导入测试 |
| **1.3** | 行情 REST API (`/api/bridge/quote`) | `routes/quote.py` | `curl GET /api/bridge/quote/000001.SZ?period=1m` → 返回K线 |
| **1.4** | 行情 Mock 数据生成器 | `xtquant/mock.py` — 模拟 1m/1d K线 | 行情 API 返回模拟数据 |
| **1.5** | 下单 REST API (`/api/bridge/order`) | `routes/order.py` | `curl POST /api/bridge/order` → 返回 mock 订单ID |
| **1.6** | 账户查询 API | `routes/account.py` — 资金/持仓/委托 | `curl GET /api/bridge/account` → 返回 mock 账户 |
| **1.7** | WebSocket 实时行情推送 | `routes/ws.py` — 订阅/推送 1m K线 | `wscat -c ws://localhost:5101/ws/quote` → 收到定时推送 |
| **1.8** | Mock 模式配置切换 | `config.py` — `MOCK_MODE=true/false` | 切换后 API 返回模拟/真实数据 |
| **1.9** | Phase 1 自测 | 全 API + WebSocket 测试脚本 | `python test_server.py` 全部通过 |

### Phase 2: 客户端开发（Linux 端）

| # | 任务 | 产出 | 验证方式 |
|---|------|------|---------|
| **2.1** | BridgeClient — HTTP 通信 | `client/bridge_client.py` | `client.get_quote("000001.SZ", "1m")` → 返回数据 |
| **2.2** | BridgeClient — WebSocket 连接 | `client/bridge_client.py` — 自动重连 | 订阅行情 → 收到推送 → 模拟断网 → 自动重连 |
| **2.3** | QuoteSubscriber — 行情订阅管理 | `client/quote_subscriber.py` | 订阅多只股票 → 推送到回调函数 |
| **2.4** | OrderManager — 订单管理 | `client/order_manager.py` | 下单 → 状态跟踪 → 成交回调 |
| **2.5** | 集成到 Flask trading_service | `backend/app/services/bridge_client.py` | 模拟盘升级实盘时通过 Bridge 提交订单 |
| **2.6** | Phase 2 自测 | 集成测试脚本 | Client ↔ Mock Server 全流程通过 |

### Phase 3: 行情落库

| # | 任务 | 产出 | 验证方式 |
|---|------|------|---------|
| **3.1** | 创建 stock_minute 表 | `init_tables` in repo | MySQL 表存在 |
| **3.2** | 行情数据写入服务 | `minute_data_service.py` | 接收 WebSocket 推送 → 批量写入 DB |
| **3.3** | 历史分钟线查询 API | `GET /api/data/minute?symbol=&date=` | 前端可查询分钟线 |

### Phase 4: Windows 真实环境部署

| # | 任务 | 产出 | 验证方式 |
|---|------|------|---------|
| **4.1** | xtquant SDK 安装与封装 | `server/xtquant/wrapper.py` — 真实实现 | 连接 miniQMT → 获取行情 |
| **4.2** | Windows 启动脚本 | `start_server.bat` / `install_service.ps1` | 开机自启 |
| **4.3** | 端到端实盘测试 | 信号→下单→成交→持仓更新 | 小额实盘交易验证 |

---

## Mock 模式设计

开发阶段不需要 Windows/miiniQMT，Mock 模式提供：

```
mock.py:
  - get_1m_kline(symbol, count) → 生成随机 1m K线数据
  - get_1d_kline(symbol, count) → 生成随机日K线数据
  - get_account() → {balance: 100000, available: 80000, positions: [...]}
  - submit_order(...) → {order_id: "MOCK-xxx", status: "filled"}
  - WebSocket 定时推送 → 每 5 秒推送一次模拟行情
```

切换方式：环境变量 `XTQUANT_MOCK=true` 或 `config.py` 中的 `MOCK_MODE`

---

## API 响应格式

与主平台统一：

```json
{
    "success": true,
    "data": {},
    "message": ""
}
```

## 待确认事项

- [ ] miniQMT 账号是否已开通？API 权限是否已申请？
- [ ] Windows 机器配置（CPU/内存/网络）？
- [ ] 局域网 IP 规划（Linux: ? / Windows: ?）
- [ ] 实盘交易标的是否有限制（仅 A 股 / 也包含 ETF）？
- [ ] 是否需要同时支持多个券商（华泰 + 国金）？
