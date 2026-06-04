# -*- coding: utf-8 -*-
"""
认证 API 集成测试
"""

import datetime


class TestRegister:
    def test_register_success(self, client):
        """注册成功"""
        username = f"newuser_{datetime.datetime.now().strftime('%H%M%S%f')}"
        resp = client.post("/api/user/register", json={
            "username": username,
            "password": "pass123456",
        })
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["message"] == "注册成功"

    def test_register_duplicate(self, client):
        """重复注册"""
        dupuser = f"dup_{datetime.datetime.now().strftime('%H%M%S%f')}"
        client.post("/api/user/register", json={
            "username": dupuser,
            "password": "pass123456",
        })
        resp = client.post("/api/user/register", json={
            "username": dupuser,
            "password": "pass123456",
        })
        assert resp.status_code == 400
        assert "已存在" in resp.get_json()["error"]

    def test_register_missing_fields(self, client):
        """缺少必填字段"""
        resp = client.post("/api/user/register", json={"username": "nopass"})
        assert resp.status_code == 400

        resp = client.post("/api/user/register", json={"password": "nouser"})
        assert resp.status_code == 400


class TestLogin:
    def test_login_success(self, client):
        """登录成功"""
        loginuser = f"login_{datetime.datetime.now().strftime('%H%M%S%f')}"
        client.post("/api/user/register", json={
            "username": loginuser,
            "password": "pass123456",
        })
        resp = client.post("/api/user/login", json={
            "username": loginuser,
            "password": "pass123456",
        })
        assert resp.status_code == 200
        data = resp.get_json()
        assert "token" in data["data"]
        assert data["data"]["user"]["username"] == loginuser

    def test_login_wrong_password(self, client):
        """密码错误"""
        resp = client.post("/api/user/login", json={
            "username": "loginuser",
            "password": "wrongpass",
        })
        assert resp.status_code == 401

    def test_login_missing_fields(self, client):
        """缺少字段"""
        resp = client.post("/api/user/login", json={})
        assert resp.status_code == 401


class TestUserInfo:
    def test_get_info_success(self, client, auth_headers):
        """获取用户信息成功"""
        resp = client.get("/api/user/info", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["message"] == "获取成功"

    def test_get_info_no_auth(self, client):
        """未认证获取信息"""
        resp = client.get("/api/user/info")
        assert resp.status_code == 401


class TestChangePassword:
    def test_change_password_success(self, client):
        """改密成功"""
        username = f"chgok_{datetime.datetime.now().strftime('%H%M%S%f')}"
        client.post("/api/user/register", json={"username": username, "password": "test123456"})
        resp = client.post("/api/user/login", json={"username": username, "password": "test123456"})
        token = resp.get_json().get("data", {}).get("token", "")
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.post("/api/user/change-password", headers=headers, json={
            "old_password": "test123456",
            "new_password": "newpass789",
        })
        assert resp.status_code == 200
        assert resp.get_json()["success"] is True

    def test_change_password_wrong_old(self, client):
        """原密码错误"""
        username = f"chgw_{datetime.datetime.now().strftime('%H%M%S%f')}"
        client.post("/api/user/register", json={"username": username, "password": "test123456"})
        resp = client.post("/api/user/login", json={"username": username, "password": "test123456"})
        token = resp.get_json().get("data", {}).get("token", "")
        headers = {"Authorization": f"Bearer {token}"}

        resp = client.post("/api/user/change-password", headers=headers, json={
            "old_password": "wrongold",
            "new_password": "newpass789",
        })
        assert resp.status_code == 400
