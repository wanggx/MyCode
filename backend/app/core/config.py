# -*- coding: utf-8 -*-
"""
配置管理：从 .env 文件读取，提供 Settings 单例
"""

import os
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class Settings:
    """应用配置，从 .env 读取"""
    # 数据库
    DB_HOST: str = "localhost"
    DB_PORT: int = 3306
    DB_USER: str = "root"
    DB_PASSWORD: str = ""
    DB_NAME: str = "stock"

    # JWT
    JWT_SECRET: str = "your-secret-key-change-in-production"
    JWT_EXPIRY_HOURS: int = 24

    # Tushare
    TUSHARE_TOKEN: str = ""

    # WeChat
    WECHAT_WEBHOOK_KEY: str = ""

    # MySQL 连接池
    DB_POOL_SIZE: int = 10
    DB_POOL_OVERFLOW: int = 5
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    DB_POOL_PRE_PING: bool = True

    def __post_init__(self):
        # 支持从环境变量覆盖（.env 加载后自动注入环境变量）
        env_overrides = {
            "DB_HOST": os.environ.get("DB_HOST"),
            "DB_PORT": os.environ.get("DB_PORT"),
            "DB_USER": os.environ.get("DB_USER"),
            "DB_PASSWORD": os.environ.get("DB_PASSWORD"),
            "DB_NAME": os.environ.get("DB_NAME"),
            "JWT_SECRET": os.environ.get("JWT_SECRET"),
            "JWT_EXPIRY_HOURS": os.environ.get("JWT_EXPIRY_HOURS"),
            "TUSHARE_TOKEN": os.environ.get("TUSHARE_TOKEN"),
            "WECHAT_WEBHOOK_KEY": os.environ.get("WECHAT_WEBHOOK_KEY"),
            "DB_POOL_SIZE": os.environ.get("DB_POOL_SIZE"),
            "DB_POOL_OVERFLOW": os.environ.get("DB_POOL_OVERFLOW"),
            "DB_POOL_TIMEOUT": os.environ.get("DB_POOL_TIMEOUT"),
            "DB_POOL_RECYCLE": os.environ.get("DB_POOL_RECYCLE"),
            "DB_POOL_PRE_PING": os.environ.get("DB_POOL_PRE_PING"),
        }
        for key, value in env_overrides.items():
            if value is not None:
                if key in ("DB_PORT", "JWT_EXPIRY_HOURS", "DB_POOL_SIZE", "DB_POOL_OVERFLOW", "DB_POOL_TIMEOUT", "DB_POOL_RECYCLE"):
                    setattr(self, key, int(value))
                elif key == "DB_POOL_PRE_PING":
                    setattr(self, key, value.lower() in ("true", "1", "yes"))
                else:
                    setattr(self, key, value)


def load_settings() -> Settings:
    """加载 .env 文件并返回 Settings 实例"""
    from dotenv import load_dotenv

    # 查找 .env 文件：优先 backend/.env，再找项目根目录
    env_path = Path(__file__).resolve().parent.parent.parent / ".env"
    if env_path.exists():
        load_dotenv(dotenv_path=env_path, override=True)
    else:
        # 尝试当前工作目录
        load_dotenv(override=True)

    return Settings()


# 全局单例
settings = load_settings()
