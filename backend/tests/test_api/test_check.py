# -*- coding: utf-8 -*-
"""
数据校验 API 集成测试
"""


class TestStockCheck:
    def test_check_query(self, client, auth_headers):
        """数据完整性检查"""
        resp = client.get("/api/stock/check?startDate=20250101&endDate=20250131", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["code"] == 0

    def test_check_with_date(self, client, auth_headers):
        """指定日期范围检查"""
        resp = client.get("/api/stock/check?startDate=20250101&endDate=20250131", headers=auth_headers)
        assert resp.status_code == 200

    def test_daily_add_invalid_date(self, client, auth_headers):
        """补录日期格式错误"""
        resp = client.post(
            "/api/stock/daily/add",
            headers=auth_headers,
            json={"start_date": "invalid", "end_date": "20250101"},
        )
        assert resp.status_code == 400  # 返回业务错误
        data = resp.get_json()
        assert data["success"] is False
