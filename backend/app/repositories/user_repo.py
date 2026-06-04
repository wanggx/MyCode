# -*- coding: utf-8 -*-
"""
用户数据访问
"""

from app.core.database import get_db_connection
from app.core.security import hash_password


def find_user_by_username(username):
    """按用户名查找用户"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            return cursor.fetchone()
    finally:
        conn.close()


def create_user(username, hashed_password, email=None):
    """创建新用户"""
    conn = get_db_connection()
    if not conn:
        return False, "数据库连接失败"
    try:
        with conn.cursor() as cursor:
            insert_sql = "INSERT INTO users (username, password, email) VALUES (%s, %s, %s)"
            cursor.execute(insert_sql, (username, hashed_password, email))
            conn.commit()
        return True, "注册成功"
    except Exception as e:
        return False, f"注册失败: {str(e)}"
    finally:
        conn.close()


def verify_user_password(username, password):
    """验证用户名密码，返回用户信息或 None"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            hashed = hash_password(password)
            cursor.execute(
                "SELECT id, username, email, role FROM users WHERE username = %s AND password = %s",
                (username, hashed),
            )
            return cursor.fetchone()
    finally:
        conn.close()


def get_user_by_id(user_id):
    """按 ID 获取用户信息"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, username, email, role, created_at FROM users WHERE id = %s",
                (user_id,),
            )
            return cursor.fetchone()
    finally:
        conn.close()


def update_user_password(user_id, new_hashed_password):
    """更新用户密码"""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE users SET password = %s WHERE id = %s",
                (new_hashed_password, user_id),
            )
            conn.commit()
        return True
    finally:
        conn.close()


def check_user_password(user_id, hashed_password):
    """验证用户密码是否正确"""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM users WHERE id = %s AND password = %s",
                (user_id, hashed_password),
            )
            return cursor.fetchone() is not None
    finally:
        conn.close()
