# -*- coding: utf-8 -*-
"""
交易中心服务 — 聚合实盘运行、信号、风控数据
"""

import logging

from app.repositories import task_repo, signal_repo, strategy_repo

logger = logging.getLogger(__name__)


class TradingService:
    """交易中心聚合服务"""

    def get_market_indices(self):
        return [
            {"code": "000001.XSHG", "name": "上证指数", "price": 3258.42, "change_pct": 0.82},
            {"code": "399001.XSHE", "name": "深证成指", "price": 11245.30, "change_pct": 1.15},
            {"code": "399006.XSHE", "name": "创业板指", "price": 2180.55, "change_pct": -0.38},
            {"code": "000300.XSHG", "name": "沪深300", "price": 4021.88, "change_pct": 0.65},
            {"code": "000905.XSHG", "name": "中证500", "price": 6385.12, "change_pct": 1.02},
            {"code": "000688.XSHG", "name": "科创50", "price": 985.60, "change_pct": 1.88},
        ]

    # ======================== 模拟盘 CRUD ========================

    def create_paper_run(self, strategy_id, initial_capital=100000, auto_start=True):
        """创建模拟盘运行"""
        import json
        try:
            strategy = strategy_repo.get_strategy(strategy_id)
            name = strategy.get("name", "未知策略") if strategy else "未知策略"
        except Exception:
            name = "未知策略"

        # Pass dict directly (pymysql handles JSON serialization for JSON columns)
        params = {
            "strategy_id": strategy_id,
            "strategy_name": name,
            "mode": "paper",
            "broker": "模拟撮合引擎",
            "initial_capital": initial_capital,
        }
        run_id = task_repo.create_job(
            task_type="strategy",
            priority=5,
            params=params,
            created_by="system",
        )
        if run_id and auto_start:
            task_repo.update_job_status(run_id, "running", "模拟盘运行中")
            task_repo.create_step(run_id, 1, "初始化模拟交易环境")
        return run_id

    def start_paper_run(self, run_id):
        """启动模拟盘运行"""
        task = task_repo.get_job(run_id)
        if not task:
            return False
        return task_repo.update_job_status(run_id, "running", "模拟盘已启动")

    def stop_paper_run(self, run_id):
        """停止模拟盘运行"""
        task = task_repo.get_job(run_id)
        if not task:
            return False
        return task_repo.update_job_status(run_id, "stopped", "模拟盘已停止")

    def delete_paper_run(self, run_id):
        """删除模拟盘运行"""
        task = task_repo.get_job(run_id)
        if not task:
            return False
        return task_repo.update_job_status(run_id, "deleted", "已删除")

    def promote_to_live(self, run_id, broker, capital=None):
        """模拟盘升级为实盘"""
        import json
        task = task_repo.get_job(run_id)
        if not task:
            return False
        params_raw = task.get("params")
        # pymysql returns JSON columns as dicts when passed correctly
        if isinstance(params_raw, str):
            try:
                params = json.loads(params_raw)
                if isinstance(params, str):  # double-encoded
                    params = json.loads(params)
            except Exception:
                params = {}
        elif isinstance(params_raw, dict):
            params = params_raw
        else:
            params = {}
        params["mode"] = "live"
        params["broker"] = broker or "国金证券 miniQMT"
        if capital:
            params["initial_capital"] = capital
        return task_repo.update_job_with_params(run_id, params)

    # ======================== 实盘运行 ========================

    def get_live_runs(self, page=1, page_size=20, mode=None):
        try:
            result = task_repo.get_jobs(task_type="strategy", page=page, page_size=page_size)
        except Exception as e:
            logger.error(f"get_live_runs 查询失败: {e}")
            result = None

        items = result.get("items", []) if result else []
        total = result.get("total", 0) if result else 0

        # Filter by mode if specified
        if mode:
            filtered = []
            for t in items:
                m = self._param(t, "mode", "paper")
                if m == mode:
                    filtered.append(t)
            items = filtered
            total = len(items)

        runs = []
        for t in items:
            strategy = self._get_strategy(t)
            runs.append({
                "id": t.get("id"),
                "strategy_id": self._param(t, "strategy_id", 0),
                "strategy_name": strategy.get("name", "未知策略"),
                "strategy_version": strategy.get("version", "v1"),
                "broker": self._param(t, "broker", "模拟引擎"),
                "mode": self._param(t, "mode", "paper"),
                "status": t.get("status", "running"),
                "start_date": self._fmt(t.get("started_at")),
                "initial_capital": self._param(t, "initial_capital", 100000),
                "pnl": 0,
                "pnl_pct": 0,
                "position_count": 0,
                "win_rate": 0,
                "sharpe": 0,
                "max_drawdown": 0,
                "annual_return": 0,
            })
        return {"items": runs, "total": total}

    def get_live_run_detail(self, run_id):
        t = task_repo.get_job(run_id)
        if not t:
            return None
        strategy = self._get_strategy(t)
        return {
            "id": t.get("id"),
            "strategy_name": strategy.get("name", "未知"),
            "strategy_version": strategy.get("version", "v1"),
            "broker": self._param(t, "broker", "模拟引擎"),
            "mode": self._param(t, "mode", "paper"),
            "status": t.get("status"),
            "start_date": self._fmt(t.get("started_at")),
            "initial_capital": self._param(t, "initial_capital", 100000),
            "final_value": self._param(t, "initial_capital", 100000),
            "pnl": 0, "pnl_pct": 0, "annual_return": 0,
            "max_drawdown": 0, "sharpe": 0, "sortino": 0,
            "win_rate": 0, "profit_loss_ratio": 0,
            "annual_volatility": 0, "alpha": 0, "beta": 0,
            "position_count": 0, "total_trades": 0,
        }

    def get_live_run_trades(self, run_id, page=1, page_size=20):
        try:
            result = signal_repo.get_signals(strategy_id=run_id, page=page, page_size=page_size)
        except Exception as e:
            logger.error(f"get_live_run_trades 查询失败: {e}")
            result = None
        items = result.get("items", []) if result else []
        total = result.get("total", 0) if result else 0
        return {
            "items": [{
                "id": s.get("id"),
                "trade_time": self._fmt(s.get("created_at")),
                "symbol": s.get("ts_code", ""),
                "name": s.get("name", ""),
                "direction": "buy" if (s.get("score", 0) or 0) > 0 else "sell",
                "price": 0, "quantity": 0, "amount": 0, "pnl": 0,
                "reason": s.get("reason_text", ""),
            } for s in items],
            "total": total,
        }

    def get_live_run_positions(self, run_id):
        return []

    def get_live_run_logs(self, run_id, page=1, page_size=50):
        try:
            steps = task_repo.get_steps(run_id) or []
        except Exception as e:
            logger.error(f"get_live_run_logs 查询失败: {e}")
            steps = []
        return {
            "items": [{
                "time": self._fmt(s.get("started_at") or s.get("finished_at")),
                "level": "INFO" if s.get("status") == "success" else ("ERROR" if s.get("status") == "failed" else "WARN"),
                "message": s.get("message") or s.get("step_name", ""),
            } for s in steps],
            "total": len(steps),
        }

    def get_live_run_metrics(self, run_id):
        t = task_repo.get_job(run_id)
        if not t:
            return None
        return {
            "annual_volatility": 0, "downside_volatility": 0,
            "var_95": 0, "cvar_95": 0, "calmar_ratio": 0,
            "information_ratio": 0, "tracking_error": 0,
            "alpha": 0, "beta": 0, "max_consecutive_wins": 0,
        }

    # ======================== 交易信号 ========================

    def get_trading_signals(self, page=1, page_size=20):
        try:
            result = signal_repo.get_signals(page=page, page_size=page_size)
        except Exception as e:
            logger.error(f"get_trading_signals 查询失败: {e}")
            result = None
        items = result.get("items", []) if result else []
        total = result.get("total", 0) if result else 0
        return {
            "items": [{
                "id": s.get("id"),
                "time": self._fmt(s.get("created_at")),
                "strategy_name": self._get_strategy_name(s.get("strategy_id")),
                "strategy_version": "",
                "symbol": s.get("ts_code", ""),
                "name": s.get("name", ""),
                "direction": "buy" if (s.get("score", 0) or 0) > 0 else "sell",
                "price": 0, "quantity": 0,
                "reason": s.get("reason_text", ""),
                "status": s.get("status", "new"),
            } for s in items],
            "total": total,
        }

    # ======================== 风控概览 ========================

    def get_risk_overview(self):
        try:
            result = task_repo.get_jobs(task_type="strategy", status="running", page=1, page_size=50)
        except Exception as e:
            logger.error(f"get_risk_overview 查询失败: {e}")
            result = None
        items = result.get("items", []) if result else []
        strategy_risks = []
        for t in items:
            strategy = self._get_strategy(t)
            strategy_risks.append({
                "strategy_name": strategy.get("name", "未知"),
                "strategy_version": strategy.get("version", ""),
                "position_ratio": 0, "daily_pnl": 0,
                "daily_pnl_pct": 0, "max_drawdown": 0,
                "stop_loss_triggered": 0, "status": "normal",
            })
        return {
            "position_ratio": 0, "position_limit": 80,
            "max_single_concentration": 0, "concentration_limit": 25,
            "daily_pnl": 0, "daily_pnl_pct": 0, "daily_loss_limit": 5,
            "max_drawdown": 0, "drawdown_limit": 20,
            "total_equity": 0, "strategy_risks": strategy_risks,
        }

    # ======================== helpers ========================

    @staticmethod
    def _fmt(val):
        return str(val)[:19] if val else ""

    @staticmethod
    def _param(task, key, default):
        params = task.get("params")
        if not params:
            return default
        import json
        try:
            p = json.loads(params) if isinstance(params, str) else params
            return p.get(key, default)
        except Exception:
            return default

    @staticmethod
    def _get_strategy(task):
        sid = TradingService._param(task, "strategy_id", 0)
        if sid:
            try:
                s = strategy_repo.get_strategy(sid)
                if s:
                    return {"name": s.get("name", "未知"), "version": s.get("version", "v1")}
            except Exception:
                pass
        return {"name": "未知策略", "version": "v1"}

    @staticmethod
    def _get_strategy_name(sid):
        if sid:
            try:
                s = strategy_repo.get_strategy(sid)
                if s:
                    return s.get("name", "")
            except Exception:
                pass
        return ""


trading_service = TradingService()
