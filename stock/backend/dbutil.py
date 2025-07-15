#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据库工具模块
"""

import pymysql
from .db_config import DB_CONFIG

def get_db_connection():
    """获取数据库连接"""
    try:
        connection = pymysql.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password'],
            database=DB_CONFIG['database'],
            charset=DB_CONFIG['charset'],
            cursorclass=pymysql.cursors.DictCursor
        )
        return connection
    except Exception as e:
        print(f"数据库连接失败: {e}")
        return None

def execute_query(sql, params=None):
    """执行查询语句"""
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
        print(f"查询执行失败: {e}")
        return None, f"查询失败: {str(e)}"

def execute_count_query(sql, params=None):
    """执行计数查询语句"""
    try:
        connection = get_db_connection()
        if not connection:
            return None, "数据库连接失败"
        
        cursor = connection.cursor()
        cursor.execute(sql, params or ())
        result = cursor.fetchone()
        count = result['total'] if result else 0
        
        cursor.close()
        connection.close()
        
        return count, None
    except Exception as e:
        print(f"计数查询执行失败: {e}")
        return None, f"查询失败: {str(e)}" 