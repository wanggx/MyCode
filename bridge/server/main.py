"""QuantBridge Server — FastAPI 入口"""
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from server.config import MOCK_MODE, HOST, PORT
from server.routes import quote, order, account, ws

# 日志
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# 创建 FastAPI 应用
app = FastAPI(
    title="QuantBridge Server",
    description="miniQMT 桥接服务 — 提供行情查询 / 下单 / 账户查询 / 实时推送",
    version="0.1.0",
)

# CORS
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

# 注册路由
app.include_router(quote.router)
app.include_router(order.router)
app.include_router(account.router)
app.include_router(ws.router)


@app.get("/health")
async def health():
    return {"status": "ok", "mock_mode": MOCK_MODE, "version": "0.1.0"}


# ===== 启动入口 =====
if __name__ == "__main__":
    import uvicorn
    logger.info(f"启动 QuantBridge Server (Mock={MOCK_MODE})")
    uvicorn.run("server.main:app", host=HOST, port=PORT, reload=MOCK_MODE)
