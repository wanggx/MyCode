# -*- coding: utf-8 -*-
"""
安全模块测试
"""

from app.core.security import hash_password, generate_token, verify_token


class TestHashPassword:
    def test_md5_hash(self):
        """测试 MD5 哈希"""
        h = hash_password("hello")
        assert h == "5d41402abc4b2a76b9719d911017c592"  # known MD5 of "hello"
        assert isinstance(h, str)

    def test_same_password_same_hash(self):
        """相同密码产生相同 hash"""
        assert hash_password("test") == hash_password("test")

    def test_different_password_different_hash(self):
        """不同密码产生不同 hash"""
        assert hash_password("test1") != hash_password("test2")


class TestJWT:
    def test_generate_and_verify(self):
        """测试 JWT 生成和验证"""
        token = generate_token(1, "admin", "admin")
        assert token is not None
        assert isinstance(token, str)

        payload = verify_token(token)
        assert payload is not None
        assert payload["user_id"] == 1
        assert payload["username"] == "admin"
        assert payload["role"] == "admin"

    def test_invalid_token(self):
        """测试无效 token"""
        assert verify_token("invalid-token") is None
        assert verify_token("") is None
