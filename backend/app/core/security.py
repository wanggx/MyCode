# -*- coding: utf-8 -*-
"""
安全模块：密码哈希、JWT token、认证装饰器
"""

import hashlib
import datetime
from functools import wraps

import jwt
from flask import request, jsonify

from app.core.config import settings


def hash_password(password: str) -> str:
    """MD5 密码加密（兼容现有数据库存储）"""
    return hashlib.md5(password.encode()).hexdigest()


def generate_token(user_id: int, username: str, role: str = "user") -> str:
    """生成 JWT token"""
    payload = {
        "user_id": user_id,
        "username": username,
        "role": role,
        "exp": datetime.datetime.utcnow()
        + datetime.timedelta(hours=settings.JWT_EXPIRY_HOURS),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def verify_token(token: str) -> dict | None:
    """验证 JWT token，返回 payload 或 None"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def require_auth(f):
    """认证装饰器：从 Authorization header 提取并验证 JWT"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "缺少认证token"}), 401

        # 移除 Bearer 前缀
        if token.startswith("Bearer "):
            token = token[7:]

        payload = verify_token(token)
        if not payload:
            return jsonify({"error": "无效的token"}), 401

        request.user = payload
        return f(*args, **kwargs)

    return decorated_function
