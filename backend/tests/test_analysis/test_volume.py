# -*- coding: utf-8 -*-
"""
成交量分析测试
"""

import pandas as pd
import numpy as np
from app.analysis.volume_analysis import polyline, volmagnify, polylineslope


class TestPolyline:
    def test_polyline_returns_float(self):
        s = pd.Series(np.cumsum(np.random.randn(30)) + 100)
        result = polyline(s, 10)
        assert isinstance(result, (float, np.floating, np.ndarray))


class TestVolMagnify:
    def test_no_magnify(self):
        s = pd.Series([100] * 20)
        assert volmagnify(s) == 0

    def test_magnify(self):
        vals = [100] * 17 + [200, 100, 500]
        s = pd.Series(vals)
        result = volmagnify(s)
        assert result > 0


class TestPolylineslope:
    def test_empty_df(self):
        assert polylineslope(pd.DataFrame()) is None

    def test_normal_df(self):
        np.random.seed(42)
        n = 60
        df = pd.DataFrame({
            "ts_code": ["000001.SZ"] * n,
            "trade_date": [f"202401{i:02d}" for i in range(1, n + 1)],
            "open": 100,
            "high": 101,
            "low": 99,
            "close": 100 + np.cumsum(np.random.randn(n) * 0.3),
            "pre_close": 100,
            "vol": np.random.randint(1000, 10000, n),
        })
        result = polylineslope(df)
        assert result is not None
        assert "slope3" in result
        assert "vol_magnify" in result
