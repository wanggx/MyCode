# -*- coding: utf-8 -*-
"""回测服务：创建、查询、取消"""
import logging
import threading
import os

from app.core.config import settings
from app.repositories.backtest_repo import (
    create_job, get_job, list_jobs, count_running_jobs,
    update_job_status, delete_job_full,
    get_nav, get_trades, get_positions, get_daily_metrics, get_risk_metrics,
)
from app.repositories.strategy_repo import get_strategy, get_latest_version

logger = logging.getLogger("myapp")

# 存储活跃的回测取消事件: {backtest_id: threading.Event}
_active_cancel_events = {}


def create_backtest(user_id, strategy_id, version, config):
    """创建回测任务"""
    # 验证策略存在
    strategy = get_strategy(strategy_id)
    if not strategy:
        return None, "策略不存在"

    # 获取策略版本源码
    ver_row = get_latest_version(strategy_id)
    if not ver_row:
        return None, "策略没有可用版本，请先保存代码"
    source_code = ver_row["source_code"]

    # 检查并发限制
    running = count_running_jobs(user_id)
    if running >= settings.MAX_CONCURRENT_BACKTESTS:
        return None, f"已达到并发上限（{settings.MAX_CONCURRENT_BACKTESTS} 个/用户），请等待已有回测完成"

    # 创建 job
    job_id = create_job(
        user_id, strategy_id, ver_row["version"],
        strategy["name"], strategy["strategy_key"], config
    )
    if not job_id:
        return None, "创建回测任务失败"

    # 将 config 和源码存入 job（通过 event system / worker）
    # 这里简化：直接启动线程（后续可改为 worker 消费 task_job）
    _start_backtest_thread(job_id, config, source_code, strategy["strategy_key"])

    return {"id": job_id, "status": "pending"}, None


def _start_backtest_thread(backtest_id, config, source_code, strategy_key):
    """启动独立的回测线程"""
    from app.services.backtest_engine import run_backtest
    # 尝试获取 socketio 实例
    socketio = None
    try:
        from flask import current_app
        socketio = getattr(current_app, 'socketio', None)
    except Exception:
        pass

    cancel_event = threading.Event()
    _active_cancel_events[backtest_id] = cancel_event

    def _run():
        try:
            config["_backtest_id"] = backtest_id
            run_backtest(backtest_id, config, source_code, strategy_key, socketio)
        finally:
            _active_cancel_events.pop(backtest_id, None)

    t = threading.Thread(target=_run, daemon=True)
    t.start()


def get_backtests(page=1, page_size=20, strategy_id=None, status=None, user_id=None):
    result, err = list_jobs(page, page_size, strategy_id, status, user_id)
    if result and result.get("items"):
        for item in result["items"]:
            if item.get("config") and isinstance(item["config"], str):
                try: item["config"] = json.loads(item["config"])
                except Exception: pass
    return result, err


import json

def get_backtest_detail(backtest_id):
    row = get_job(backtest_id)
    if not row:
        return None
    # Parse JSON fields
    if row.get("config") and isinstance(row["config"], str):
        try: row["config"] = json.loads(row["config"])
        except Exception: pass
    # 兼容 datetime 序列化
    for k in ["start_time", "end_time", "created_at", "updated_at"]:
        if row.get(k):
            row[k] = str(row[k])
    return row


def cancel_backtest(backtest_id):
    job = get_job(backtest_id)
    if not job:
        return False, "回测不存在"
    if job["status"] != "running":
        return False, "只能取消运行中的回测"
    event = _active_cancel_events.get(backtest_id)
    if event:
        event.set()
    update_job_status(backtest_id, "cancelled")
    return True, None


def delete_backtest(backtest_id):
    job = get_job(backtest_id)
    if not job:
        return False, "回测不存在"
    if job["status"] == "running":
        return False, "请先取消运行中的回测"
    # 删除日志文件
    if job.get("log_path"):
        try:
            os.remove(job["log_path"])
        except Exception:
            pass
    delete_job_full(backtest_id)
    return True, None


def get_backtest_nav(backtest_id):
    return get_nav(backtest_id)


def get_backtest_trades(backtest_id, page=1, page_size=50):
    return get_trades(backtest_id, page, page_size)


def get_backtest_positions(backtest_id, trade_date=None):
    return get_positions(backtest_id, trade_date)


def get_backtest_daily_metrics(backtest_id):
    return get_daily_metrics(backtest_id)


def get_backtest_risk_metrics(backtest_id):
    return get_risk_metrics(backtest_id)


def get_backtest_logs(backtest_id, mode="full", lines=100):
    """读取回测日志"""
    log_path = None
    if mode == "full":
        log_path = os.path.join(settings.LOG_DIR, f"*/{backtest_id}.log")
    if not log_path:
        return None, "日志文件不存在"
    try:
        import glob
        matches = glob.glob(log_path)
        if not matches:
            return None, "日志文件不存在"
        with open(matches[0], "r") as f:
            all_lines = f.readlines()
        if mode == "tail":
            all_lines = all_lines[-lines:]
        return {"log_path": matches[0], "lines": all_lines, "size_bytes": len("".join(all_lines))}, None
    except Exception as e:
        return None, f"读取日志失败: {str(e)}"


def get_backtest_report(backtest_id):
    """聚合回测报告"""
    detail = get_job(backtest_id)
    if not detail: return None
    nav = get_nav(backtest_id)
    risk = get_risk_metrics(backtest_id)
    return {"summary": detail, "nav": nav, "risk": risk}, None
