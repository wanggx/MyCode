# -*- coding: utf-8 -*-
"""
pytest fixtures
"""

import time
import pytest
from app import create_app


@pytest.fixture
def app():
    """创建测试用的 Flask 应用"""
    application = create_app()
    application.config["TESTING"] = True
    return application


@pytest.fixture
def client(app):
    """Flask test client"""
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    """注册+登录，返回认证 header"""
    username = f"ath_{time.time_ns()}"
    client.post("/api/user/register", json={
        "username": username,
        "password": "test123456",
    })
    resp = client.post("/api/user/login", json={
        "username": username,
        "password": "test123456",
    })
    data = resp.get_json()
    if not data or "data" not in data:
        raise RuntimeError(f"login failed for {username}: {data}")
    token = data["data"].get("token", "")
    return {"Authorization": f"Bearer {token}"}
