# -*- coding: utf-8 -*-
"""
周月聚合测试
"""

import pandas as pd
import numpy as np
from app.analysis.aggregation import fridayline, lastday, aggline, process_week_df


class TestFridayLine:
    def test_fridayline(self):
        result = fridayline("20240101")  # 周一
        assert isinstance(result, str)
        assert len(result) == 8


class TestAggLine:
    def test_aggline_returns_series(self):
        df = pd.DataFrame({
            "trade_date": ["20240101", "20240102", "20240103", "20240104", "20240105"],
            "open": [100, 101, 102, 103, 104],
            "high": [105, 106, 107, 108, 109],
            "low": [99, 100, 101, 102, 103],
            "close": [101, 102, 103, 104, 105],
            "vol": [1000] * 5,
            "amount": [100000] * 5,
        })
        result = aggline(df)
        assert result["open"] == 100
        assert result["close"] == 105
        assert result["high"] == 109
        assert result["low"] == 99


class TestProcessWeekDf:
    def test_process_empty(self):
        assert process_week_df(pd.DataFrame()) is None

    def test_process_normal(self):
        np.random.seed(42)
        n = 30
        df = pd.DataFrame({
            "ts_code": ["000001.SZ"] * n,
            "trade_date": [f"202401{i:02d}" for i in range(1, n + 1)],
            "open": 100,
            "high": 101,
            "low": 99,
            "close": 100 + np.cumsum(np.random.randn(n) * 0.3),
            "vol": np.random.randint(1000, 10000, n),
            "amount": np.random.randint(100000, 500000, n),
        })
        result = process_week_df(df)
        assert result is not None
        assert "ts_code" in result.columns
        assert "trade_date" in result.columns
