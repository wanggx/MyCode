# -*- coding: utf-8 -*-
"""
策略业务逻辑层：策略 CRUD、版本管理、运行调度
"""

import json
import logging
from datetime import datetime

from app.repositories import strategy_repo
from app.repositories import signal_repo
from app.services import task_service

logger = logging.getLogger("myapp")


def _serialize(row):
    if not row:
        return None
    result = dict(row)
    for key in ("created_at", "updated_at", "started_at", "finished_at"):
        if result.get(key) and hasattr(result[key], "isoformat"):
            result[key] = result[key].isoformat()
    for json_key in ("params_json", "buy_rules_json", "sell_rules_json"):
        val = result.get(json_key)
        if isinstance(val, str):
            try:
                result[json_key] = json.loads(val)
            except (json.JSONDecodeError, TypeError):
                pass
    return result


def create_strategy(data: dict) -> dict:
    try:
        strategy_id = strategy_repo.create_strategy(data)
        if strategy_id is None:
            return None
        return _serialize(strategy_repo.get_strategy(strategy_id))
    except Exception as e:
        logger.error("create_strategy failed: %s", e)
        return None


def get_strategies(enabled_only=False, page=1, page_size=20) -> dict:
    try:
        result = strategy_repo.get_strategies(enabled_only, page, page_size)
        if result is None:
            return None
        result["items"] = [_serialize(item) for item in result.get("items", [])]
        return result
    except Exception as e:
        logger.error("get_strategies failed: %s", e)
        return None


def get_strategy_detail(strategy_id: int) -> dict:
    try:
        strategy = strategy_repo.get_strategy(strategy_id)
        if not strategy:
            return None
        detail = _serialize(strategy)
        latest = strategy_repo.get_latest_version(strategy_id)
        detail["latest_version"] = _serialize(latest)
        return detail
    except Exception as e:
        logger.error("get_strategy_detail failed: %s", e)
        return None


def update_strategy(strategy_id: int, data: dict) -> dict:
    try:
        ok = strategy_repo.update_strategy(strategy_id, data)
        if not ok:
            return None
        return _serialize(strategy_repo.get_strategy(strategy_id))
    except Exception as e:
        logger.error("update_strategy failed: %s", e)
        return None


def create_version(strategy_id: int, data: dict) -> dict:
    try:
        data["strategy_id"] = strategy_id
        version_id = strategy_repo.create_version(data)
        if version_id is None:
            return None
        versions = strategy_repo.get_versions(strategy_id)
        for v in versions:
            if v["id"] == version_id:
                return _serialize(v)
        return None
    except Exception as e:
        logger.error("create_version failed: %s", e)
        return None


def get_versions(strategy_id: int) -> list:
    try:
        versions = strategy_repo.get_versions(strategy_id)
        return [_serialize(v) for v in versions]
    except Exception as e:
        logger.error("get_versions failed: %s", e)
        return []


def run_strategy(strategy_id: int, version_id=None) -> dict:
    try:
        strategy = strategy_repo.get_strategy(strategy_id)
        if not strategy:
            return None
        if version_id is None:
            latest = strategy_repo.get_latest_version(strategy_id)
            if not latest:
                return None
            version_id = latest["id"]
        trade_date = datetime.now().strftime("%Y%m%d")
        run_id = strategy_repo.create_run({
            "strategy_id": strategy_id,
            "version_id": version_id,
            "trade_date": trade_date,
            "status": "pending",
        })
        if run_id is None:
            return None
        task = task_service.create_task(
            task_type="run_strategy",
            params={"run_id": run_id},
        )
        if task:
            strategy_repo.update_run(run_id, {"task_job_id": task["id"]})
        return {"run_id": run_id, "task": task}
    except Exception as e:
        logger.error("run_strategy failed: %s", e)
        return None


def execute_run(run_id: int):
    try:
        from app.repositories.strategy_repo import get_strategy, get_runs, update_run
        from app.repositories.signal_repo import create_signals

        runs_result = strategy_repo.get_runs(run_id=run_id)
        logger.info("execute_run called for run_id=%s (mock implementation)", run_id)
        strategy_repo.update_run(run_id, {"status": "running"})

        mock_signals = [{
            "trade_date": datetime.now().strftime("%Y%m%d"),
            "ts_code": "000001.SZ",
            "name": "平安银行",
            "market": "A",
            "strategy_id": 1,
            "strategy_version_id": 1,
            "strategy_run_id": run_id,
            "score": 80.0,
            "reason_text": "mock signal",
        }]
        count = signal_repo.create_signals(mock_signals)
        strategy_repo.update_run(run_id, {
            "status": "success",
            "signal_count": count,
        })
    except Exception as e:
        logger.error("execute_run failed: %s", e)
        try:
            strategy_repo.update_run(run_id, {"status": "failed", "message": str(e)})
        except Exception:
            pass


def get_runs(strategy_id: int, page=1, page_size=20) -> dict:
    try:
        result = strategy_repo.get_runs(strategy_id, page, page_size)
        if result is None:
            return None
        result["items"] = [_serialize(item) for item in result.get("items", [])]
        return result
    except Exception as e:
        logger.error("get_runs failed: %s", e)
        return None
