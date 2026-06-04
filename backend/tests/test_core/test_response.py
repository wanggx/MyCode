# -*- coding: utf-8 -*-
"""
响应格式测试
"""

from app import create_app
from app.core.response import success, error


class TestResponse:
    def _app_context(self):
        return create_app().app_context()

    def test_success_with_data(self):
        """测试成功响应带数据"""
        with self._app_context():
            resp, code = success({"key": "value"}, "操作成功")
        data = resp.json
        assert data["message"] == "操作成功"
        assert data["data"] == {"key": "value"}
        assert code == 200

    def test_success_without_data(self):
        """测试成功响应不带数据"""
        with self._app_context():
            resp, code = success()
        assert code == 200
        assert resp.json["message"] == "success"

    def test_error(self):
        """测试错误响应"""
        with self._app_context():
            resp, code = error("出错了", 400)
        assert resp.json["error"] == "出错了"
        assert code == 400

    def test_error_custom_status(self):
        """测试自定义状态码"""
        with self._app_context():
            resp, code = error("未授权", 401)
        assert resp.json["error"] == "未授权"
        assert code == 401
