# -*- coding: utf-8 -*-
"""
统一 API 响应格式
"""

from flask import jsonify


def success(data=None, message="success", status_code=200, code=None):
    """成功响应"""
    response = {"success": True, "message": message}
    if code is not None:
        response["code"] = code
    if data is not None:
        response["data"] = data
    return jsonify(response), status_code


def error(message, status_code=400, code=None):
    """错误响应"""
    response = {"error": message, "success": False}
    if code is not None:
        response["code"] = code
    return jsonify(response), status_code
