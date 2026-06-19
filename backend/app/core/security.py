# -*- coding: utf-8 -*-
"""
安全模块：密码哈希、JWT token、认证装饰器
支持 bcrypt（新）和 MD5（旧密码兼容）
"""
import hashlib
import datetime
from functools import wraps

import jwt
import bcrypt
from flask import request, jsonify

from app.core.config import settings


def hash_password(password: str) -> str:
    """密码哈希（bcrypt）"""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """验证密码（自动检测 bcrypt / MD5）"""
    if hashed.startswith("$2b$") or hashed.startswith("$2a$"):
        return bcrypt.checkpw(password.encode(), hashed.encode())
    # MD5 fallback
    return hashlib.md5(password.encode()).hexdigest() == hashed


def is_md5_hash(hashed: str) -> bool:
    """判断是否为 MD5 哈希"""
    return len(hashed) == 32 and not hashed.startswith("$")


def generate_token(user_id: int, username: str, role: str = "user") -> str:
    payload = {
        "user_id": user_id, "username": username, "role": role,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(hours=settings.JWT_EXPIRY_HOURS),
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm="HS256")


def verify_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.JWT_SECRET, algorithms=["HS256"])
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def require_auth(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"error": "缺少认证token"}), 401
        if token.startswith("Bearer "):
            token = token[7:]
        payload = verify_token(token)
        if not payload:
            return jsonify({"error": "无效的token"}), 401
        request.user = payload
        return f(*args, **kwargs)
    return decorated_function
