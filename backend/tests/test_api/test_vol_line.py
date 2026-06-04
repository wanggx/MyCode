# -*- coding: utf-8 -*-
"""
成交量线 API 集成测试
"""


class TestVolLine:
    def test_vol_line_success(self, client, auth_headers):
        """成交量线查询"""
        resp = client.get("/api/vol_line?startDate=20250101&endDate=20250131", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.get_json()
        assert "data" in data

    def test_vol_line_missing_params(self, client, auth_headers):
        """缺参数"""
        resp = client.get("/api/vol_line", headers=auth_headers)
        assert resp.status_code == 400
