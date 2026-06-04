# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify

from app.services.auth_service import register, login, get_info, change_password
from app.core.security import require_auth

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/api/user/register", methods=["POST"])
def register_route():
    data = request.get_json() or {}
    success, message = register(
        data.get("username"), data.get("password"), data.get("email")
    )
    if success:
        return jsonify({"message": message}), 201
    return jsonify({"error": message}), 400


@auth_bp.route("/api/user/login", methods=["POST"])
def login_route():
    data = request.get_json() or {}
    success, message, result = login(data.get("username"), data.get("password"))
    if success:
        return jsonify({"message": message, "data": result}), 200
    return jsonify({"error": message}), 401


@auth_bp.route("/api/user/info", methods=["GET"])
@require_auth
def info_route():
    user_id = request.user["user_id"]
    user_info = get_info(user_id)
    if user_info:
        return jsonify({"message": "获取成功", "data": user_info}), 200
    return jsonify({"error": "获取用户信息失败"}), 500


@auth_bp.route("/api/user/change-password", methods=["POST"])
@require_auth
def change_password_route():
    data = request.get_json() or {}
    success, message = change_password(
        request.user["user_id"],
        data.get("old_password"),
        data.get("new_password"),
    )
    if success:
        return jsonify({"success": True, "message": message}), 200
    return jsonify({"error": message}), 400
