# -*- coding: utf-8 -*-
"""
认证服务：注册、登录、获取信息、修改密码
"""

from app.core.security import hash_password, generate_token
from app.repositories.user_repo import (
    find_user_by_username,
    create_user,
    verify_user_password,
    get_user_by_id,
    update_user_password,
    check_user_password,
)


def register(username, password, email=None):
    """注册新用户"""
    if not username or not password:
        return False, "用户名和密码不能为空"

    existing = find_user_by_username(username)
    if existing:
        return False, "用户名已存在"

    hashed = hash_password(password)
    return create_user(username, hashed, email)


def login(username, password):
    """用户登录，返回 token 和用户信息"""
    if not username or not password:
        return False, "用户名和密码不能为空", None

    user = verify_user_password(username, password)
    if not user:
        return False, "用户名或密码错误", None

    token = generate_token(user["id"], user["username"], user["role"])
    return True, "登录成功", {
        "token": token,
        "user": {
            "id": user["id"],
            "username": user["username"],
            "email": user["email"],
            "role": user["role"],
        },
    }


def get_info(user_id):
    """获取用户信息"""
    return get_user_by_id(user_id)


def change_password(user_id, old_password, new_password):
    """修改密码"""
    if not old_password or not new_password:
        return False, "原密码和新密码不能为空"

    if len(new_password) < 6:
        return False, "新密码长度不能少于6位"

    if not check_user_password(user_id, hash_password(old_password)):
        return False, "原密码错误"

    if update_user_password(user_id, hash_password(new_password)):
        return True, "密码修改成功"
    return False, "密码修改失败"
