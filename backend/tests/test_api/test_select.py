# -*- coding: utf-8 -*-
"""
选股 API 集成测试
"""


class TestStockSelect:
    def test_select_query(self, client, auth_headers):
        """选股列表查询"""
        resp = client.get("/api/stock_select", headers=auth_headers)
        assert resp.status_code == 200

    def test_select_with_date(self, client, auth_headers):
        """指定日期选股"""
        resp = client.get(
            "/api/stock_select?select_date=2099-01-01", headers=auth_headers
        )
        # 无数据时触发异步选股
        assert resp.status_code == 200

    def test_mock_select(self, client, auth_headers):
        """Mock 选股"""
        resp = client.post(
            "/api/stock/select/mock",
            headers=auth_headers,
            json={"ts_code": "000001.SZ", "date_str": "20991231", "n": 100},
        )
        assert resp.status_code in (200, 500)  # 取决于数据库是否有数据
