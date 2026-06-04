# -*- coding: utf-8 -*-
"""
配置模块测试
"""

import os
from app.core.config import Settings


class TestSettings:
    def test_default_values(self, monkeypatch):
        """测试默认值"""
        monkeypatch.delenv("DB_HOST", raising=False)
        monkeypatch.delenv("DB_PORT", raising=False)
        monkeypatch.delenv("DB_NAME", raising=False)
        s = Settings()
        assert s.DB_HOST == "localhost"
        assert s.DB_PORT == 3306
        assert s.DB_NAME == "stock"

    def test_env_override(self, monkeypatch):
        """测试环境变量覆盖"""
        monkeypatch.setenv("DB_HOST", "test-host")
        monkeypatch.setenv("DB_PORT", "3307")
        monkeypatch.setenv("DB_PASSWORD", "test-pass")
        s = Settings()
        assert s.DB_HOST == "test-host"
        assert s.DB_PORT == 3307

    def test_jwt_default_expiry(self):
        """测试 JWT 默认过期时间"""
        s = Settings()
        assert s.JWT_EXPIRY_HOURS == 24
