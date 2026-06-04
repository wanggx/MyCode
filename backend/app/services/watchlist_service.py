# -*- coding: utf-8 -*-
"""
关注列表业务逻辑层
"""

import logging

from app.repositories import portfolio_repo

logger = logging.getLogger("myapp")


def _serialize(row):
    if not row:
        return None
    result = dict(row)
    for key in ("added_at", "removed_at"):
        if result.get(key) and hasattr(result[key], "isoformat"):
            result[key] = result[key].isoformat()
    return result


def get_watchlist() -> list:
    try:
        rows = portfolio_repo.get_watchlist()
        return [_serialize(r) for r in rows]
    except Exception as e:
        logger.error("get_watchlist failed: %s", e)
        return []


def add_to_watchlist(ts_code, name, market, source_signal_id=None, note=None) -> dict:
    try:
        data = {
            "ts_code": ts_code,
            "name": name,
            "market": market,
            "source_signal_id": source_signal_id,
            "note": note,
        }
        inserted_id = portfolio_repo.add_to_watchlist(data)
        if not inserted_id:
            return None
        rows = portfolio_repo.get_watchlist()
        for r in rows:
            if r.get("id") == inserted_id:
                return _serialize(r)
        return {"id": inserted_id, "ts_code": ts_code, "name": name, "market": market}
    except Exception as e:
        logger.error("add_to_watchlist failed: %s", e)
        return None


def remove_from_watchlist(watchlist_id: int) -> dict:
    try:
        ok = portfolio_repo.remove_from_watchlist(watchlist_id)
        if not ok:
            return None
        return {"id": watchlist_id, "status": "removed"}
    except Exception as e:
        logger.error("remove_from_watchlist failed: %s", e)
        return None
