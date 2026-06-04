# -*- coding: utf-8 -*-
"""
统一 API 响应格式
"""

from flask import jsonify


def success(data=None, message="success", status_code=200):
    """成功响应"""
    response = {"success": True, "message": message}
    if data is not None:
        response["data"] = data
    return jsonify(response), status_code


def error(message, status_code=400):
    """错误响应"""
    return jsonify({"error": message}), status_code
