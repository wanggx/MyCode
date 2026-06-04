# -*- coding: utf-8 -*-
from flask import Blueprint, request, jsonify

from app.services.select_service import get_vol_line_data
from app.core.security import require_auth

vol_line_bp = Blueprint("vol_line", __name__)


@vol_line_bp.route("/api/vol_line", methods=["GET"])
@require_auth
def get_vol_line_route():
    try:
        start_date = request.args.get("startDate")
        end_date = request.args.get("endDate")

        result, error = get_vol_line_data(start_date, end_date)
        if error:
            return jsonify({"error": error}), 400
        return jsonify({"message": "Success", "data": result}), 200
    except Exception as e:
        return jsonify({"error": f"Failed to get volume line data: {str(e)}"}), 500
