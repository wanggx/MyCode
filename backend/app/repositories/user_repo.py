# -*- coding: utf-8 -*-
"""用户数据访问"""
from app.core.database import get_db_connection
from app.core.security import hash_password, verify_password, is_md5_hash


def find_user_by_username(username):
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor() as c:
            c.execute("SELECT id FROM users WHERE username = %s", (username,))
            return c.fetchone()
    finally:
        conn.close()


def create_user(username, plain_password, email=None):
    conn = get_db_connection()
    if not conn: return False, "数据库连接失败"
    try:
        with conn.cursor() as c:
            hashed = hash_password(plain_password)
            c.execute("INSERT INTO users (username, password, email) VALUES (%s, %s, %s)", (username, hashed, email))
            conn.commit()
        return True, "注册成功"
    except Exception as e:
        return False, f"注册失败: {str(e)}"
    finally:
        conn.close()


def verify_user_password(username, password):
    """验证用户名密码，返回用户信息或 None。自动升级旧 MD5 密码为 bcrypt"""
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor() as c:
            c.execute("SELECT id, username, password, email, role FROM users WHERE username = %s", (username,))
            user = c.fetchone()
            if not user: return None
            db_pw = user["password"]
            if not verify_password(password, db_pw):
                return None
            # 如果是旧 MD5 密码，自动升级为 bcrypt
            if is_md5_hash(db_pw):
                new_hash = hash_password(password)
                c.execute("UPDATE users SET password = %s WHERE id = %s", (new_hash, user["id"]))
                conn.commit()
            return {"id": user["id"], "username": user["username"], "email": user["email"], "role": user["role"]}
    finally:
        conn.close()


def get_user_by_id(user_id):
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor() as c:
            c.execute("SELECT id, username, email, role, created_at FROM users WHERE id = %s", (user_id,))
            return c.fetchone()
    finally:
        conn.close()


def update_user_password(user_id, new_plain_password):
    conn = get_db_connection()
    if not conn: return False
    try:
        with conn.cursor() as c:
            hashed = hash_password(new_plain_password)
            c.execute("UPDATE users SET password = %s WHERE id = %s", (hashed, user_id))
            conn.commit()
        return True
    finally:
        conn.close()


def check_user_password(user_id, plain_password):
    conn = get_db_connection()
    if not conn: return False
    try:
        with conn.cursor() as c:
            c.execute("SELECT password FROM users WHERE id = %s", (user_id,))
            user = c.fetchone()
            if not user: return False
            return verify_password(plain_password, user["password"])
    finally:
        conn.close()
