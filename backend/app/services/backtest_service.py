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
    # 运行中的回测：合并内存中的实时指标
    if row.get("status") == "running":
        from app.services.backtest_engine import get_live_metrics
        live = get_live_metrics(backtest_id)
        if live:
            row.update(live)
    return row


def rerun_backtest(backtest_id, user_id=None):
    """重新运行回测：复用原配置和源码，清除旧结果，重启线程"""
    from app.repositories.backtest_repo import update_job_status, clear_results
    from app.repositories.strategy_repo import get_version

    job = get_job(backtest_id)
    if not job:
        return None, "回测不存在"

    # 检查并发限制
    if user_id:
        running = count_running_jobs(user_id)
        if running >= settings.MAX_CONCURRENT_BACKTESTS:
            return None, f"已达到并发上限（{settings.MAX_CONCURRENT_BACKTESTS} 个/用户），请等待已有回测完成"

    # 获取原始版本源码
    ver_row = get_version(job["strategy_id"], job.get("strategy_version"))
    if not ver_row:
        return None, "策略版本源码不存在"
    source_code = ver_row["source_code"]

    # 解析 config
    config = job.get("config")
    if isinstance(config, str):
        import json
        try: config = json.loads(config)
        except Exception: config = {}
    if not config:
        return None, "回测配置缺失"

    # 清除旧结果数据
    clear_results(backtest_id)

    # 重置状态
    update_job_status(backtest_id, "pending", error_message=None)

    # 启动新线程
    _start_backtest_thread(backtest_id, config, source_code, job["strategy_key"])

    return {"id": backtest_id, "status": "pending"}, None


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
    log_path = job.get("log_path")
    if not log_path:
        # Fallback: glob 查找
        import glob
        matches = glob.glob(os.path.join(settings.LOG_DIR, f"*/{backtest_id}.log"))
        if matches:
            log_path = matches[0]
    if log_path:
        try:
            os.remove(log_path)
        except Exception:
            pass
    delete_job_full(backtest_id)
    return True, None


def get_backtest_nav(backtest_id):
    rows = get_nav(backtest_id)
    if not rows:
        return None
    # 转换为前端图表需要的格式 {dates: [], nav: [], benchmark_nav: []}
    dates, nav, bench = [], [], []
    for r in rows:
        dates.append(str(r.get("trade_date", "")))
        nav.append(float(r.get("unit_net_value", 1.0)))
        bench.append(float(r.get("benchmark_nav")) if r.get("benchmark_nav") else None)
    return {"dates": dates, "nav": nav, "benchmark_nav": bench}


def get_backtest_trades(backtest_id, page=1, page_size=50):
    result, err = get_trades(backtest_id, page, page_size)
    if result and result.get("items"):
        from datetime import date
        for item in result["items"]:
            for k in ("buy_date", "sell_date"):
                v = item.get(k)
                if isinstance(v, date):
                    item[k] = v.strftime("%Y-%m-%d %H:%M:%S")
                elif isinstance(v, str) and len(v) > 10:
                    item[k] = v[:19]
    return result, err


def get_backtest_positions(backtest_id, trade_date=None):
    return get_positions(backtest_id, trade_date)


def get_backtest_daily_metrics(backtest_id):
    return get_daily_metrics(backtest_id)


def get_backtest_risk_metrics(backtest_id):
    return get_risk_metrics(backtest_id)


def get_backtest_logs(backtest_id, mode="full", lines=100):
    """读取回测日志"""
    # 1. 先查 job 记录，按 strategy_key 定位日志
    job = get_job(backtest_id)
    if job and job.get("strategy_key"):
        log_path = os.path.join(settings.LOG_DIR, job["strategy_key"], f"{backtest_id}.log")
        if os.path.isfile(log_path):
            return _read_log_file(log_path, mode, lines)

    # 2. Fallback: glob 通配搜索
    pattern = os.path.join(settings.LOG_DIR, f"*/{backtest_id}.log")
    try:
        import glob
        matches = glob.glob(pattern)
        if matches:
            return _read_log_file(matches[0], mode, lines)
    except Exception as e:
        return None, f"读取日志失败: {str(e)}"

    return None, f"日志文件不存在: {pattern}"


def _read_log_file(log_path, mode, lines):
    """读取日志文件内容"""
    try:
        with open(log_path, "r", encoding="utf-8", errors="replace") as f:
            all_lines = f.readlines()
        if mode == "tail":
            all_lines = all_lines[-lines:]
        return {"log_path": log_path, "lines": all_lines, "size_bytes": len("".join(all_lines))}, None
    except Exception as e:
        return None, f"读取日志失败: {str(e)}"


def get_backtest_report(backtest_id):
    """聚合回测报告"""
    detail = get_job(backtest_id)
    if not detail: return None
    nav = get_nav(backtest_id)
    risk = get_risk_metrics(backtest_id)
    return {"summary": detail, "nav": nav, "risk": risk}, None
