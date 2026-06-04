# -*- coding: utf-8 -*-
"""
信号业务逻辑层：信号查询、状态更新、信号生成
"""

import json
import logging
from datetime import datetime

from app.repositories import signal_repo
from app.repositories import strategy_repo

logger = logging.getLogger("myapp")


def _serialize(row):
    if not row:
        return None
    result = dict(row)
    for key in ("created_at",):
        if result.get(key) and hasattr(result[key], "isoformat"):
            result[key] = result[key].isoformat()
    for json_key in ("factor_snapshot_json", "risk_snapshot_json"):
        val = result.get(json_key)
        if isinstance(val, str):
            try:
                result[json_key] = json.loads(val)
            except (json.JSONDecodeError, TypeError):
                pass
    return result


def get_signals(trade_date=None, strategy_id=None, market=None,
                min_score=0, page=1, page_size=20) -> dict:
    try:
        result = signal_repo.get_signals(
            trade_date, strategy_id, market, min_score, page, page_size,
        )
        if result is None:
            return None
        result["items"] = [_serialize(item) for item in result.get("items", [])]
        return result
    except Exception as e:
        logger.error("get_signals failed: %s", e)
        return None


def get_signal_detail(signal_id: int) -> dict:
    try:
        signal = signal_repo.get_signal(signal_id)
        if not signal:
            return None
        detail = _serialize(signal)
        strategy = strategy_repo.get_strategy(signal.get("strategy_id"))
        detail["strategy"] = _serialize(strategy)
        versions = strategy_repo.get_versions(signal.get("strategy_id"))
        version_id = signal.get("strategy_version_id")
        matched = [v for v in versions if v.get("id") == version_id]
        detail["version"] = _serialize(matched[0]) if matched else None
        return detail
    except Exception as e:
        logger.error("get_signal_detail failed: %s", e)
        return None


def update_status(signal_id: int, status: str) -> dict:
    try:
        valid = {"new", "watched", "portfolio", "ignored"}
        if status not in valid:
            logger.error("invalid signal status: %s", status)
            return None
        ok = signal_repo.update_signal_status(signal_id, status)
        if not ok:
            return None
        return _serialize(signal_repo.get_signal(signal_id))
    except Exception as e:
        logger.error("update_status failed: %s", e)
        return None


def generate_signals(strategy_run: dict, candidates: list) -> list:
    try:
        signals = []
        for c in candidates:
            factor = c.get("factor_snapshot", {})
            risk = c.get("risk_snapshot", {})
            signals.append({
                "trade_date": strategy_run.get("trade_date", datetime.now().strftime("%Y%m%d")),
                "ts_code": c.get("ts_code"),
                "name": c.get("name"),
                "market": c.get("market"),
                "strategy_id": strategy_run.get("strategy_id"),
                "strategy_version_id": strategy_run.get("version_id"),
                "strategy_run_id": strategy_run.get("id"),
                "score": c.get("score", 0),
                "reason_text": c.get("reason_text", ""),
                "factor_snapshot_json": factor,
                "risk_snapshot_json": risk,
            })
        return signals
    except Exception as e:
        logger.error("generate_signals failed: %s", e)
        return []
