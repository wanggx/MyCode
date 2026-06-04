# -*- coding: utf-8 -*-
"""
均线计算测试
"""

import pandas as pd
import numpy as np
from app.analysis.ma_analysis import ma, process_ma


def _make_ma_df():
    np.random.seed(42)
    n = 30
    close = 100 + np.cumsum(np.random.randn(n) * 0.3)
    return pd.DataFrame({
        "ts_code": ["000001.SZ"] * n,
        "trade_date": [f"202401{i:02d}" for i in range(1, n + 1)],
        "close": close,
    })


class TestMA:
    def test_ma_returns_series(self):
        df = _make_ma_df()
        result = ma(df)
        assert result is not None
        assert "ma3" in result
        assert "ma5" in result
        assert "ma35_3" in result

    def test_ma_empty(self):
        assert ma(pd.DataFrame()) is None

    def test_process_ma(self):
        df = _make_ma_df()
        result = process_ma(df)
        assert result is not None
        assert "ts_code" in result.columns
