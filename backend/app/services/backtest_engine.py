# -*- coding: utf-8 -*-
"""BacktestEngine: rqalpha 回测封装"""
import sys
import os
import json
import logging
import threading
import time
import builtins
import traceback

sys.path.insert(0, "/Users/gxwang/QT/rqalpha")
import rqalpha
from rqalpha.utils.config import parse_config as rq_parse_config

from app.core.config import settings
from app.services.backtest_datasource import QtDataSource

logger = logging.getLogger("myapp")


def run_backtest(backtest_id, bt_config, strategy_code, strategy_key, socketio=None):
    """
    在独立线程中执行 rqalpha 回测

    Args:
        backtest_id: backtest_job.id
        bt_config: dict {start_date, end_date, initial_capital, benchmark, frequency, commission, slippage}
        strategy_code: Python 策略源码字符串
        strategy_key: 策略标识，用于日志路径
        socketio: Flask-SocketIO 实例（用于推送进度）

    Returns:
        dict: {success: bool, summary: {...}, error: str|None}
    """
    from app.repositories.backtest_repo import update_job_status, update_job_progress, update_job_result

    # 1. Setup log file
    log_dir = os.path.join(settings.LOG_DIR, strategy_key)
    os.makedirs(log_dir, exist_ok=True)
    log_path = os.path.join(log_dir, f"{backtest_id}.log")
    file_handler = logging.FileHandler(log_path, encoding="utf-8")
    file_handler.setFormatter(logging.Formatter("%(asctime)s │ [%(levelname)-5s] %(message)s", datefmt="%H:%M:%S"))
    bt_logger = logging.getLogger(f"backtest.{backtest_id}")
    bt_logger.addHandler(file_handler)
    bt_logger.setLevel(logging.INFO)

    bt_logger.info("=" * 40)
    bt_logger.info(f"QT Backtest Engine Starting - Backtest #{backtest_id}")
    bt_logger.info(f"Strategy: {strategy_key}, Config: {json.dumps(bt_config)}")

    update_job_status(backtest_id, "running", start_time=True)
    start_ts = time.time()

    try:
        # 2. Build rqalpha config
        rq_config = _build_rqalpha_config(bt_config, backtest_id, strategy_key)

        # 3. Setup progress callback
        total_bars = _count_trading_days(bt_config["start_date"], bt_config["end_date"])
        bar_counter = [0]

        def progress_fn(current_date_str):
            bar_counter[0] += 1
            pct = min(round(bar_counter[0] / total_bars * 100, 1), 99.9)
            update_job_progress(backtest_id, pct, current_date_str)
            if socketio:
                try:
                    socketio.emit("backtest_progress", {
                        "backtest_id": backtest_id, "progress": pct,
                        "current_date": current_date_str,
                        "completed_bars": bar_counter[0], "total_bars": total_bars,
                    }, namespace="/ws/backtest")
                except Exception:
                    pass

        builtins._BT_PROGRESS_FN_ = progress_fn
        builtins._BT_TOTAL_BARS_ = total_bars
        builtins._BT_LOGGER_ = bt_logger

        # 4. Create custom data source (with temp bundle dir for BaseDataSource init)
        bt_logger.info(f"Loading data: {bt_config['start_date']} ~ {bt_config['end_date']}")
        ds = QtDataSource(bt_config["start_date"], bt_config["end_date"])
        instruments = list(ds.get_instruments())
        bt_logger.info(f"Loaded {len(instruments)} instruments")

        # Set bundle path in config to our temp dir so BaseDataSource init succeeds
        rq_config["base"]["data_bundle_path"] = ds._tmpdir

        # 5. Monkey-patch Environment to inject custom datasource
        from rqalpha.environment import Environment
        _orig_env_init = Environment.__init__

        def _patched_env_init(self, config, *args, **kwargs):
            _orig_env_init(self, config, *args, **kwargs)
            self.set_data_source(ds)
            bt_logger.info("Custom QtDataSource injected into rqalpha Environment")

        Environment.__init__ = _patched_env_init

        # 6. Build strategy wrapper code
        wrapped_code = _wrap_strategy_code(strategy_code)

        # 7. Run rqalpha
        bt_logger.info("Starting rqalpha main loop...")
        result = rqalpha.run_code(code=wrapped_code, config=rq_config)

        # 8. Restore original init
        Environment.__init__ = _orig_env_init

        # 7. Extract results
        elapsed = (time.time() - start_ts) * 1000
        bt_logger.info(f"Main loop completed in {elapsed:.0f}ms")

        summary = _extract_summary(result, bt_config, elapsed)

        # 8. Write results to DB
        update_job_result(backtest_id, summary)
        bt_logger.info(f"Results written: return={summary.get('total_return')}, sharpe={summary.get('sharpe_ratio')}")

        # 9. Push completion event
        if socketio:
            try:
                socketio.emit("backtest_completed", {
                    "backtest_id": backtest_id,
                    "total_return": summary.get("total_return"),
                    "sharpe_ratio": summary.get("sharpe_ratio"),
                    "duration_ms": elapsed,
                }, namespace="/ws/backtest")
            except Exception:
                pass

        bt_logger.info(f"Backtest #{backtest_id} completed successfully in {elapsed:.0f}ms")
        return {"success": True, "summary": summary, "error": None}

    except Exception as e:
        elapsed = (time.time() - start_ts) * 1000
        error_msg = f"{type(e).__name__}: {str(e)}\n{traceback.format_exc()}"
        bt_logger.error(f"Backtest #{backtest_id} FAILED: {error_msg}")
        update_job_status(backtest_id, "failed", error_message=error_msg)
        if socketio:
            try:
                socketio.emit("backtest_failed", {
                    "backtest_id": backtest_id, "error": str(e),
                }, namespace="/ws/backtest")
            except Exception:
                pass
        return {"success": False, "summary": None, "error": str(e)}

    finally:
        # Cleanup
        for key in ["_BT_PROGRESS_FN_", "_BT_TOTAL_BARS_", "_BT_LOGGER_"]:
            if hasattr(builtins, key):
                delattr(builtins, key)
        bt_logger.removeHandler(file_handler)
        file_handler.close()


def _build_rqalpha_config(bt_config, backtest_id, strategy_key):
    """Build rqalpha configuration dict"""
    return {
        "base": {
            "start_date": bt_config["start_date"],
            "end_date": bt_config["end_date"],
            "frequency": bt_config.get("frequency", "1d"),
            "accounts": {"stock": bt_config.get("initial_capital", 100000)},
            "benchmark": bt_config.get("benchmark") or None,
            "strategy_type": "stock",
        },
        "extra": {
            "log_level": "info",
            "log_file": os.path.join(settings.LOG_DIR, strategy_key, f"{backtest_id}.log"),
        },
        "mod": {
            "sys_analyser": {"enabled": True, "plot": False, "benchmark": bt_config.get("benchmark") or None},
            "sys_progress": {"enabled": False},
            "sys_simulation": {
                "enabled": True,
                "matching_type": "current_bar",
                "commission_multiplier": bt_config.get("commission", 0.0003),
                "slippage": bt_config.get("slippage", 0.01),
            },
            "sys_risk": {"enabled": True},
            "sys_transaction_cost": {"enabled": True},
        },
    }


def _wrap_strategy_code(user_code):
    """Wrap user strategy code to bridge rqalpha with progress/logging hooks"""
    return f"""
import builtins

_PROGRESS_FN_ = getattr(builtins, '_BT_PROGRESS_FN_', None)
_TOTAL_BARS_ = getattr(builtins, '_BT_TOTAL_BARS_', 0)
_BT_LOGGER_ = getattr(builtins, '_BT_LOGGER_', None)

def _log(msg):
    if _BT_LOGGER_:
        _BT_LOGGER_.info(msg)

_bar_count = [0]

# --- User Strategy Code ---
{user_code}

# --- Monkey-patch handle_bar for progress ---
_original_handle_bar = handle_bar if 'handle_bar' in dir() else None
if _original_handle_bar:
    def handle_bar(context, bar_dict):
        _bar_count[0] += 1
        if _PROGRESS_FN_:
            _PROGRESS_FN_(str(context.now))
        if _BT_LOGGER_ and _bar_count[0] % 50 == 0:
            pv = context.portfolio.total_value
            _BT_LOGGER_.info(f"[{{context.now.date()}}] BAR #{{_bar_count[0]}} | portfolio_value: ¥{{pv:,.0f}}")
        return _original_handle_bar(context, bar_dict)
"""


def _count_trading_days(start_date, end_date):
    """Estimate trading day count"""
    try:
        from datetime import date
        s = date.fromisoformat(start_date)
        e = date.fromisoformat(end_date)
        days = (e - s).days
        return max(int(days * 0.69), 1)
    except Exception:
        return 240


def _extract_summary(run_result, bt_config, elapsed_ms):
    """Extract performance metrics from rqalpha result"""
    summary = {
        "total_return": None, "annualized_return": None, "max_drawdown": None,
        "sharpe_ratio": None, "sortino_ratio": None, "win_rate": None,
        "profit_loss_ratio": None, "annual_volatility": None,
        "alpha": None, "beta": None,
        "final_value": bt_config.get("initial_capital", 100000),
        "total_trades": 0, "benchmark_return": None, "excess_return": None,
        "duration_ms": int(elapsed_ms),
    }

    if run_result and isinstance(run_result, dict):
        s = run_result.get("summary", {})
        if s:
            summary.update({
                "total_return": s.get("total_returns"),
                "annualized_return": s.get("annualized_returns"),
                "max_drawdown": s.get("max_drawdown"),
                "sharpe_ratio": s.get("sharpe"),
                "sortino_ratio": getattr(s, 'sortino', None),
                "win_rate": s.get("win_rate"),
                "annual_volatility": s.get("annual_volatility"),
                "alpha": s.get("alpha"), "beta": s.get("beta"),
                "final_value": s.get("total_value"),
                "total_trades": s.get("total_trades", 0),
                "benchmark_return": s.get("benchmark_total_returns"),
            })
            if summary["total_return"] is not None and summary["benchmark_return"] is not None:
                summary["excess_return"] = summary["total_return"] - summary["benchmark_return"]

        # Extract trades and nav
        trades = run_result.get("trades", [])
        if trades:
            _save_backtest_details(bt_config.get("_backtest_id"), trades, run_result.get("daily_nav", {}),
                                   run_result.get("positions", {}), summary, bt_config.get("_socketio"))

    return summary


def _save_backtest_details(backtest_id, trades, daily_nav, positions, summary, socketio):
    """Write detailed backtest results to DB tables"""
    if not backtest_id:
        return
    try:
        from app.repositories.backtest_repo import (
            batch_insert_nav, batch_insert_trades, batch_insert_positions,
            batch_insert_daily_metrics, insert_risk_metrics
        )
        if daily_nav:
            batch_insert_nav(backtest_id, daily_nav)
        if trades:
            batch_insert_trades(backtest_id, trades)
        if positions:
            batch_insert_positions(backtest_id, positions)
        insert_risk_metrics(backtest_id, summary)
    except Exception as e:
        logger.warning(f"Failed to save backtest details for #{backtest_id}: {e}")
