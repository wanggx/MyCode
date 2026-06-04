# -*- coding: utf-8 -*-
"""
数据库引擎和查询工具
"""

import time
from functools import wraps

import pymysql
from sqlalchemy import create_engine, text
from sqlalchemy.exc import DisconnectionError, OperationalError

from app.core.config import settings

_engine = None


def get_engine():
    """获取 SQLAlchemy 引擎（单例，带连接池）"""
    global _engine
    if _engine is None:
        url = f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
        _engine = create_engine(
            url,
            pool_size=settings.DB_POOL_SIZE,
            max_overflow=settings.DB_POOL_OVERFLOW,
            pool_timeout=settings.DB_POOL_TIMEOUT,
            pool_recycle=settings.DB_POOL_RECYCLE,
            pool_pre_ping=settings.DB_POOL_PRE_PING,
        )
    return _engine


def get_db_connection():
    """获取池化的 pymysql 连接（DictCursor），用完 conn.close() 归还到池"""
    try:
        conn = get_engine().raw_connection()
        conn.driver_connection.cursorclass = pymysql.cursors.DictCursor
        return conn
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None


def execute_query(sql, params=None):
    """执行查询语句，返回 (结果列表, 错误信息)"""
    try:
        connection = get_db_connection()
        if not connection:
            return None, "数据库连接失败"

        cursor = connection.cursor()
        cursor.execute(sql, params or ())
        result = cursor.fetchall()

        cursor.close()
        connection.close()

        return result, None
    except Exception as e:
        return None, f"查询失败: {str(e)}"


def execute_count_query(sql, params=None):
    """执行计数查询，返回 (计数值, 错误信息)"""
    try:
        connection = get_db_connection()
        if not connection:
            return None, "数据库连接失败"

        cursor = connection.cursor()
        cursor.execute(sql, params or ())
        result = cursor.fetchone()
        count = result["total"] if result else 0

        cursor.close()
        connection.close()

        return count, None
    except Exception as e:
        return None, f"查询失败: {str(e)}"


def test_connection():
    """测试数据库连接"""
    try:
        engine = get_engine()
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return str(result.scalar()) == "1"
    except Exception as e:
        print(f"数据库连接测试失败: {e}")
        return False


def retry_on_db_failure(max_retries=2, base_delay=0.5):
    """数据库操作重试装饰器：捕获连接错误，invalidate 后重试

    用法:
        @retry_on_db_failure()
        def some_db_operation():
            ...
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_error = None
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except (OperationalError, DisconnectionError) as e:
                    last_error = e
                    if attempt < max_retries:
                        get_engine().pool.invalidate()
                        time.sleep(base_delay * (2 ** attempt))
            raise last_error
        return wrapper
    return decorator
