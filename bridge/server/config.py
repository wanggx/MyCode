"""QuantBridge Server 配置"""
import os


# Mock 模式：非 Windows 环境下使用模拟数据
MOCK_MODE = os.getenv("XTQUANT_MOCK", "true").lower() == "true"

# 服务配置
HOST = os.getenv("BRIDGE_HOST", "0.0.0.0")
PORT = int(os.getenv("BRIDGE_PORT", "5101"))

# miniQMT 配置（Mock 模式忽略）
MINIQMT_PATH = os.getenv("MINIQMT_PATH", r"C:\国金证券QMT交易端")
MINIQMT_ACCOUNT = os.getenv("MINIQMT_ACCOUNT", "")

# WebSocket 推送间隔（Mock 模式下每 N 秒推送一次）
MOCK_PUSH_INTERVAL = int(os.getenv("MOCK_PUSH_INTERVAL", "5"))

# 订阅标的（默认）
DEFAULT_SYMBOLS = ["000001.SZ", "600036.SH", "000300.SH"]
