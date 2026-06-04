# -*- coding: utf-8 -*-
"""
回测业务逻辑层：创建回测、执行回测（mock）、查询结果
"""

import json
import logging
import math
import random
from datetime import datetime, timedelta

from app.repositories import backtest_repo
from app.repositories import strategy_repo
from app.services import task_service

logger = logging.getLogger("myapp")


def _serialize(row):
    if not row:
        return None
    result = dict(row)
    for key in ("created_at", "started_at", "finished_at"):
        if result.get(key) and hasattr(result[key], "isoformat"):
            result[key] = result[key].isoformat()
    for json_key in ("params_json", "metrics_json"):
        val = result.get(json_key)
        if isinstance(val, str):
            try:
                result[json_key] = json.loads(val)
            except (json.JSONDecodeError, TypeError):
                pass
    return result


def create_backtest(strategy_id, version_id, start_date, end_date, params=None) -> dict:
    """
    1. 校验 strategy_id 存在
    2. 创建 backtest_job（status=pending）
    3. 创建 task_job（task_type='run_backtest', params={backtest_job_id: xxx}）
    4. 回填 backtest_job.task_job_id
    5. 返回 backtest_job
    """
    try:
        strategy = strategy_repo.get_strategy(strategy_id)
        if not strategy:
            return None

        job_id = backtest_repo.create_job({
            "strategy_id": strategy_id,
            "version_id": version_id,
            "start_date": start_date,
            "end_date": end_date,
            "status": "pending",
            "params_json": params or {},
        })
        if job_id is None:
            return None

        task = task_service.create_task(
            task_type="run_backtest",
            params={"backtest_job_id": job_id},
        )
        if task:
            backtest_repo.update_job(job_id, {"task_job_id": task["id"]})

        return _serialize(backtest_repo.get_job(job_id))
    except Exception as e:
        logger.error("create_backtest failed: %s", e)
        return None


def execute_backtest(backtest_job_id: int):
    """
    执行回测（mock 版）：
    1. 加载 backtest_job
    2. 更新 status=running, started_at=now
    3. 生成模拟净值数据（250 个交易日，随机净值曲线）
    4. 生成模拟持仓（3-5 只股票）
    5. 生成模拟交易记录
    6. 计算模拟风险指标（年化收益、夏普、最大回撤、年化波动、卡玛比率、胜率）
    7. 保存 nav/position/trade/metrics
    8. 更新 status=success, finished_at=now
    """
    try:
        job = backtest_repo.get_job(backtest_job_id)
        if not job:
            logger.error("execute_backtest: job not found id=%s", backtest_job_id)
            return

        backtest_repo.update_job(backtest_job_id, {"status": "running"})

        random.seed(backtest_job_id)
        daily_vol = 0.20 / math.sqrt(252)
        benchmark_daily_vol = 0.15 / math.sqrt(252)

        navs = []
        benchmark_navs = []
        base_date = datetime(2024, 1, 2)
        current_nav = 1.0
        current_benchmark = 1.0
        for i in range(250):
            trade_date = (base_date + timedelta(days=i * 7 // 5)).strftime("%Y%m%d")
            daily_return = random.gauss(0.0003, daily_vol)
            current_nav *= (1 + daily_return)
            benchmark_return = random.gauss(0.0001, benchmark_daily_vol)
            current_benchmark *= (1 + benchmark_return)

            peak = max(n["nav"] for n in navs) if navs else 1.0
            if current_nav > peak:
                peak = current_nav
            drawdown = (current_nav / peak) - 1 if peak > 0 else 0

            navs.append({
                "job_id": backtest_job_id,
                "trade_date": trade_date,
                "nav": round(current_nav, 4),
                "benchmark_nav": round(current_benchmark, 4),
                "drawdown": round(drawdown, 4),
            })

        backtest_repo.batch_insert_nav(navs)

        stock_pool = [
            ("000001.SZ", 12.50),
            ("600036.SH", 35.20),
            ("000858.SZ", 28.80),
            ("601318.SH", 45.60),
            ("600519.SH", 1800.00),
        ]
        selected = stock_pool[:random.randint(3, 5)]
        weight = round(1.0 / len(selected), 4)
        positions = []
        last_date = navs[-1]["trade_date"]
        for ts_code, price in selected:
            positions.append({
                "job_id": backtest_job_id,
                "trade_date": last_date,
                "ts_code": ts_code,
                "weight": weight,
                "market_value": round(current_nav * weight * 1000000, 2),
                "close_price": round(price * (1 + random.gauss(0, 0.02)), 4),
            })
        backtest_repo.batch_insert_positions(positions)

        trades = []
        trade_dates_sample = random.sample(range(250), min(20, 250))
        for idx in sorted(trade_dates_sample):
            td = navs[idx]["trade_date"]
            ts_code, base_price = random.choice(selected)
            side = random.choice(["buy", "sell"])
            price = round(base_price * (1 + random.gauss(0, 0.03)), 4)
            quantity = random.choice([100, 200, 500, 1000])
            amount = round(price * quantity, 2)
            fee = round(amount * 0.0003, 4)
            trades.append({
                "job_id": backtest_job_id,
                "trade_date": td,
                "ts_code": ts_code,
                "side": side,
                "price": price,
                "quantity": quantity,
                "amount": amount,
                "fee": fee,
                "reason": "mock" if side == "buy" else "mock",
            })
        backtest_repo.batch_insert_trades(trades)

        final_nav = navs[-1]["nav"]
        annual_return = (final_nav / 1.0) ** (252 / 250) - 1
        daily_returns = [(navs[i]["nav"] / navs[i - 1]["nav"] - 1) for i in range(1, len(navs))]
        mean_return = sum(daily_returns) / len(daily_returns) if daily_returns else 0
        variance = sum((r - mean_return) ** 2 for r in daily_returns) / len(daily_returns) if daily_returns else 0
        std_return = math.sqrt(variance) if variance > 0 else 0
        annual_vol = std_return * math.sqrt(252)
        sharpe = (annual_return - 0.03) / annual_vol if annual_vol > 0 else 0
        max_drawdown = min(n["drawdown"] for n in navs) if navs else 0
        calmar = annual_return / abs(max_drawdown) if max_drawdown != 0 else 0
        win_days = sum(1 for r in daily_returns if r > 0)
        win_rate = win_days / len(daily_returns) if daily_returns else 0

        metrics = {
            "annual_return": round(annual_return, 4),
            "annual_volatility": round(annual_vol, 4),
            "sharpe_ratio": round(sharpe, 4),
            "max_drawdown": round(max_drawdown, 4),
            "calmar_ratio": round(calmar, 4),
            "win_rate": round(win_rate, 4),
        }

        backtest_repo.update_job(backtest_job_id, {
            "status": "success",
            "metrics_json": json.dumps(metrics, ensure_ascii=False),
        })
        logger.info("execute_backtest success id=%s metrics=%s", backtest_job_id, metrics)
    except Exception as e:
        logger.exception("execute_backtest failed id=%s: %s", backtest_job_id, e)
        try:
            backtest_repo.update_job(backtest_job_id, {"status": "failed", "metrics_json": json.dumps({"error": str(e)})})
        except Exception:
            pass


def get_backtest_detail(backtest_job_id: int) -> dict:
    """获取回测详情（含风险指标）"""
    job = backtest_repo.get_job(backtest_job_id)
    if not job:
        return None
    return _serialize(job)


def get_backtests(strategy_id=None, status=None, page=1, page_size=20) -> dict:
    """分页查询回测任务列表"""
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 20
    result = backtest_repo.get_jobs(strategy_id, status, page, page_size)
    if result is None:
        return None
    result["items"] = [_serialize(item) for item in result.get("items", [])]
    return result


def get_nav(backtest_job_id: int) -> list:
    """获取净值列表"""
    navs = backtest_repo.get_navs(backtest_job_id)
    return [_serialize(n) for n in navs]


def get_positions(backtest_job_id: int, trade_date: str = None) -> list:
    """获取持仓列表"""
    positions = backtest_repo.get_positions(backtest_job_id, trade_date)
    return [_serialize(p) for p in positions]


def get_trades(backtest_job_id: int, page=1, page_size=20) -> dict:
    """获取交易明细（分页）"""
    if page < 1:
        page = 1
    if page_size < 1 or page_size > 100:
        page_size = 20
    result = backtest_repo.get_trades(backtest_job_id, page, page_size)
    if result is None:
        return None
    result["items"] = [_serialize(item) for item in result.get("items", [])]
    return result
