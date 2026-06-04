# -*- coding: utf-8 -*-
"""
股票 API 集成测试
"""


class TestStocks:
    def test_stocks_list(self, client, auth_headers):
        """股票列表查询"""
        resp = client.get("/api/stocks", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert "data" in data

    def test_stocks_pagination(self, client, auth_headers):
        """股票列表分页"""
        resp = client.get("/api/stocks?page=1&page_size=5", headers=auth_headers)
        assert resp.status_code == 200

    def test_stocks_search(self, client, auth_headers):
        """股票关键词搜索"""
        resp = client.get("/api/stocks?keyword=银行", headers=auth_headers)
        assert resp.status_code == 200

    def test_areas(self, client, auth_headers):
        """获取地域列表"""
        resp = client.get("/api/stocks/areas", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.get_json().get("data"), list)

    def test_industries(self, client, auth_headers):
        """获取行业列表"""
        resp = client.get("/api/stocks/industries", headers=auth_headers)
        assert resp.status_code == 200
        assert isinstance(resp.get_json().get("data"), list)

    def test_no_auth(self, client):
        """未认证访问"""
        resp = client.get("/api/stocks")
        assert resp.status_code == 401

    def test_daily_data_missing_params(self, client, auth_headers):
        """日线数据缺参数"""
        resp = client.get("/api/stock/data", headers=auth_headers)
        assert resp.status_code == 400
