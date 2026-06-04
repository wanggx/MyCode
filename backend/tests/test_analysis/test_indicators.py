# -*- coding: utf-8 -*-
"""
MACD/KDJ 计算测试
"""

import pandas as pd
import numpy as np
from app.analysis.indicators import calc_macd_and_kdj, process_macd_and_kdj


def _make_sample_df():
    """生成样本数据用于测试"""
    np.random.seed(42)
    n = 50
    dates = [f"202401{i:02d}" for i in range(1, n + 1)]
    close = 100 + np.cumsum(np.random.randn(n) * 0.5)
    return pd.DataFrame({
        "ts_code": ["000001.SZ"] * n,
        "trade_date": dates,
        "open": close - 0.2,
        "high": close + 0.5,
        "low": close - 0.5,
        "close": close,
        "vol": np.random.randint(1000, 10000, n),
    })


class TestCalcMacdKdj:
    def test_calc_returns_last_row(self):
        df = _make_sample_df()
        result = calc_macd_and_kdj(df)
        assert len(result) == 1
        assert "dif" in result.columns
        assert "dea" in result.columns
        assert "macd" in result.columns
        assert "k" in result.columns
        assert "d" in result.columns

    def test_process_empty_df(self):
        result = process_macd_and_kdj(pd.DataFrame())
        assert len(result) == 0


class TestProcessMacdKdj:
    def test_process_multiple_stocks(self):
        df1 = _make_sample_df()
        df2 = _make_sample_df()
        df2["ts_code"] = "000002.SZ"
        combined = pd.concat([df1, df2])
        result = process_macd_and_kdj(combined)
        assert "ts_code" in result.columns
        assert len(result) > 0
