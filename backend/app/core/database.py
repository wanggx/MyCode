# -*- coding: utf-8 -*-
"""
数据库引擎和查询工具
"""

from sqlalchemy import create_engine, text
from app.core.config import settings


def get_engine():
    """获取 SQLAlchemy 引擎"""
    url = f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}"
    return create_engine(url)


def get_db_connection():
    """获取 pymysql 原生连接（兼容旧代码的 DictCursor 查询）"""
    import pymysql
    try:
        connection = pymysql.connect(
            host=settings.DB_HOST,
            port=settings.DB_PORT,
            user=settings.DB_USER,
            password=settings.DB_PASSWORD,
            database=settings.DB_NAME,
            charset="utf8mb4",
            cursorclass=pymysql.cursors.DictCursor,
        )
        return connection
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
            return result.scalar() == 1
    except Exception as e:
        print(f"数据库连接测试失败: {e}")
        return False
