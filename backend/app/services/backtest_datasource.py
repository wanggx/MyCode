# -*- coding: utf-8 -*-
"""QtDataSource: 从 MySQL stock_daily 加载行情数据，适配 rqalpha"""
import sys
import numpy as np

sys.path.insert(0, "/Users/gxwang/QT/rqalpha")
from rqalpha.data.base_data_source import BaseDataSource
from rqalpha.model.instrument import Instrument
from rqalpha.const import INSTRUMENT_TYPE, MARKET

from app.repositories.stock_repo import query_stock_list_df
from app.repositories.stock_daily_repo import query_stock_data_df

BAR_DTYPE = np.dtype([
    ('datetime', 'uint64'), ('open', 'float64'), ('high', 'float64'),
    ('low', 'float64'), ('close', 'float64'), ('volume', 'float64'),
    ('total_turnover', 'float64'),
])


def _ts_code_to_order_book_id(ts_code):
    parts = str(ts_code).split(".")
    return parts[1] + parts[0] if len(parts) == 2 else ts_code


def _order_book_id_to_ts_code(ob_id):
    return ob_id[2:] + "." + ob_id[:2]


class _FakeBaseConfig:
    data_bundle_path = "/tmp/rqalpha_nonexistent"
    future_info = {}


class MySQLDayBarStore:
    """MySQL-backed day bar store"""
    def __init__(self, start_date, end_date):
        self._start = start_date
        self._end = end_date
        self._cache = {}

    def get_bars(self, order_book_id, market=MARKET.CN):
        if order_book_id in self._cache:
            return self._cache[order_book_id]
        ts_code = _order_book_id_to_ts_code(order_book_id)
        try:
            s = self._start.replace("-", "")
            e = self._end.replace("-", "")
            df = query_stock_data_df(ts_code, s, e)
            if df is None or len(df) == 0:
                return np.array([], dtype=BAR_DTYPE)
            df = df.sort_values("trade_date")
            arr = np.zeros(len(df), dtype=BAR_DTYPE)
            dt_str = df["trade_date"].astype(str)
            arr["datetime"] = dt_str.apply(
                lambda x: np.datetime64(x[:4] + "-" + x[4:6] + "-" + x[6:8], "D").astype("uint64")
            ).values
            for col, f in [("open","open"),("high","high"),("low","low"),
                           ("close","close"),("volume","vol"),("total_turnover","amount")]:
                arr[col] = df[f].fillna(0).values.astype("float64")
            self._cache[order_book_id] = arr
            return arr
        except Exception:
            return np.array([], dtype=BAR_DTYPE)

    def get_date_range(self, order_book_id, market=MARKET.CN):
        bars = self.get_bars(order_book_id, market)
        if len(bars) > 0:
            return bars["datetime"][0], bars["datetime"][-1]
        return None, None


class EmptyBarStore:
    def get_bars(self, order_book_id, market=MARKET.CN):
        return np.array([], dtype=BAR_DTYPE)

    def get_date_range(self, order_book_id, market=MARKET.CN):
        return None, None


class QtDataSource(BaseDataSource):
    """从 MySQL stock_daily 读取行情，适配 rqalpha"""

    def __init__(self, start_date, end_date):
        import tempfile, os, json, pickle, h5py
        tmpdir = tempfile.mkdtemp(prefix="rqalpha_")
        # Empty instruments pickle
        with open(os.path.join(tmpdir, "instruments.pk"), "wb") as f: pickle.dump([], f)
        for fn in ["stock_info.json","bond_info.json","fund_info.json","share_transformation.json"]:
            with open(os.path.join(tmpdir, fn), "w") as f: json.dump({}, f)
        # future_info.json must have at least one entry with margin_rate
        with open(os.path.join(tmpdir, "future_info.json"), "w") as f:
            json.dump([{"order_book_id": "IF0000", "underlying_symbol": "IF",
                        "commission_type": "by_volume", "margin_rate": 0.1}], f)
        # Create all required HDF5 files for rqalpha BaseDataSource initialization
        for fn in ["stocks.h5","indexes.h5","funds.h5","futures.h5","dividends.h5",
                    "split_factor.h5","ex_cum_factor.h5","suspended_days.h5","st_stock_days.h5"]:
            with h5py.File(os.path.join(tmpdir, fn), "w") as f: pass
        # yield_curve.h5 needs 'data' dataset
        with h5py.File(os.path.join(tmpdir, "yield_curve.h5"), "w") as f:
            dt = np.dtype([('date', 'int64'), ('rate', 'float64')])
            f.create_dataset("data", data=np.array([(20050101, 0.03)], dtype=dt))

        cfg = _FakeBaseConfig()
        cfg.data_bundle_path = tmpdir
        super().__init__(cfg)
        self._start_date = start_date
        self._end_date = end_date
        self._tmpdir = tmpdir

        # Register MySQL-backed store for stocks
        mysql_store = MySQLDayBarStore(start_date, end_date)
        self.register_day_bar_store(INSTRUMENT_TYPE.CS, mysql_store, MARKET.CN)
        empty = EmptyBarStore()
        for it in [INSTRUMENT_TYPE.INDX, INSTRUMENT_TYPE.ETF, INSTRUMENT_TYPE.FUTURE,
                    INSTRUMENT_TYPE.BOND, INSTRUMENT_TYPE.OPTION]:
            self.register_day_bar_store(it, empty, MARKET.CN)

        # Register instruments
        self._init_instruments()

    def _init_instruments(self):
        try:
            df = query_stock_list_df()
        except Exception:
            df = None
        if df is None or len(df) == 0:
            return
        instruments = []
        for _, row in df.iterrows():
            ob_id = _ts_code_to_order_book_id(row["ts_code"])
            code = str(row.get("symbol", ""))
            exchange = "SZSE" if ob_id.startswith("SZ") else "SSE"
            board_type = "KSH" if code.startswith("688") else ("GEM" if code.startswith("300") or code.startswith("301") else "MainBoard")
            inst_dict = {
                "order_book_id": ob_id, "symbol": ob_id, "exchange": exchange,
                "type": "CS", "listed_date": str(row.get("list_date", "19900101")),
                "de_listed_date": "29991231", "round_lot": 100, "tick_size": 0.01,
                "board_type": board_type,
            }
            instruments.append(Instrument(inst_dict, market=MARKET.CN))
        self.register_instruments(iter(instruments))

    def available_data_range(self, frequency):
        return self._start_date, self._end_date

    def get_yield_curve(self, start_date=None, end_date=None, tenor=None):
        return np.array([(np.datetime64(start_date) if start_date else np.datetime64("now"), 0.03)],
                        dtype=[('date', 'datetime64[D]'), ('rate', 'float64')])
