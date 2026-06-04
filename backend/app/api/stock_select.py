# -*- coding: utf-8 -*-
import datetime

from flask import Blueprint, request, jsonify

from app.services.select_service import (
    get_select_results,
    trigger_async_select,
    remove_select_results,
    is_task_running,
)
from app.core.security import require_auth

select_bp = Blueprint("stock_select", __name__)


@select_bp.route("/api/stock_select", methods=["GET"])
@require_auth
def get_stock_select():
    try:
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("page_size", 10))
        select_date = request.args.get("select_date", None)
        reselect = request.args.get("reselect", "false").lower() == "true"

        if select_date:
            try:
                date_obj = datetime.datetime.strptime(select_date, "%Y-%m-%d")
                select_date_str = date_obj.strftime("%Y%m%d")
            except ValueError:
                select_date_str = select_date
        else:
            select_date_str = None

        if reselect and select_date_str:
            remove_select_results(select_date_str)
        else:
            result, error = get_select_results(page, page_size, select_date_str)
            if error:
                return jsonify({"error": error}), 500

            if result and result.get("total", 0) > 0:
                return jsonify({"message": "获取成功", "data": result}), 200

        if select_date_str:
            _, msg = trigger_async_select(select_date_str)
            return jsonify({"error": msg, "total": 0}), 200

        return jsonify({"error": "获取选股列表失败"}), 500
    except Exception as e:
        return jsonify({"error": f"获取选股列表失败: {str(e)}"}), 500


@select_bp.route("/api/stock/select/mock", methods=["POST"])
@require_auth
def stock_select_mock():
    try:
        from app.services.select_service import mock_select

        ts_code = request.json.get("ts_code")
        date_str = request.json.get("date_str")
        n = int(request.json.get("n", 100))

        if not ts_code or not date_str:
            return jsonify({"error": "参数ts_code和date_str必填"}), 400

        df = mock_select(ts_code, date_str, n)
        if df is None or len(df) == 0:
            return jsonify({"result": "无数据"}), 200

        return jsonify({"result": df.to_json(orient="records", force_ascii=False)}), 200
    except Exception as e:
        return jsonify({"error": f"Mock选股失败: {str(e)}"}), 500
