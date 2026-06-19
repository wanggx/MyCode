# -*- coding: utf-8 -*-
"""回测数据访问层：backtest_job + 5 张结果表的 CRUD"""
import json
from datetime import datetime
from app.core.database import get_db_connection


# === Job CRUD ===

def create_job(user_id, strategy_id, strategy_version, strategy_name, strategy_key, config):
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor() as c:
            c.execute(
                "INSERT INTO backtest_job (user_id, strategy_id, strategy_version, strategy_name, strategy_key, status, config) VALUES (%s,%s,%s,%s,%s,'pending',%s)",
                (user_id, strategy_id, strategy_version, strategy_name, strategy_key, json.dumps(config))
            )
            conn.commit()
            return c.lastrowid
    finally:
        conn.close()


def get_job(backtest_id):
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor() as c:
            c.execute("SELECT * FROM backtest_job WHERE id = %s", (backtest_id,))
            return c.fetchone()
    finally:
        conn.close()


def list_jobs(page=1, page_size=20, strategy_id=None, status=None, user_id=None):
    conn = get_db_connection()
    if not conn: return None, "DB error"
    try:
        with conn.cursor() as c:
            where, params = [], []
            if strategy_id: where.append("strategy_id = %s"); params.append(strategy_id)
            if status: where.append("status = %s"); params.append(status)
            if user_id: where.append("user_id = %s"); params.append(user_id)
            wc = ("WHERE " + " AND ".join(where)) if where else ""
            c.execute(f"SELECT COUNT(*) as total FROM backtest_job {wc}", params)
            total = c.fetchone()["total"] or 0
            off = (page - 1) * page_size
            c.execute(f"SELECT * FROM backtest_job {wc} ORDER BY created_at DESC LIMIT %s OFFSET %s", params + [page_size, off])
            return {"items": list(c.fetchall()), "total": total, "page": page, "page_size": page_size}, None
    except Exception as e:
        return None, str(e)
    finally:
        conn.close()


def count_running_jobs(user_id=None):
    conn = get_db_connection()
    if not conn: return 0
    try:
        with conn.cursor() as c:
            if user_id:
                c.execute("SELECT COUNT(*) as cnt FROM backtest_job WHERE status='running' AND user_id=%s", (user_id,))
            else:
                c.execute("SELECT COUNT(*) as cnt FROM backtest_job WHERE status='running'")
            return c.fetchone()["cnt"] or 0
    finally:
        conn.close()


def update_job_status(backtest_id, status, error_message=None, start_time=False, log_path=None):
    conn = get_db_connection()
    if not conn: return
    try:
        with conn.cursor() as c:
            extra = ""
            params = [status]
            if error_message: extra += ", error_message = %s"; params.append(error_message)
            if start_time: extra += ", start_time = NOW()"
            if log_path: extra += ", log_path = %s"; params.append(log_path)
            params.append(backtest_id)
            c.execute(f"UPDATE backtest_job SET status = %s{extra} WHERE id = %s", params)
            conn.commit()
    finally:
        conn.close()


def update_job_progress(backtest_id, progress, current_date=None):
    conn = get_db_connection()
    if not conn: return
    try:
        with conn.cursor() as c:
            c.execute("UPDATE backtest_job SET progress = %s, `current_date` = %s WHERE id = %s",
                      (progress, current_date, backtest_id))
            conn.commit()
    finally:
        conn.close()


def update_job_result(backtest_id, summary):
    conn = get_db_connection()
    if not conn: return
    try:
        with conn.cursor() as c:
            c.execute("""
                UPDATE backtest_job SET status='completed', progress=100,
                    total_return=%s, annualized_return=%s, max_drawdown=%s,
                    sharpe_ratio=%s, sortino_ratio=%s, win_rate=%s,
                    profit_loss_ratio=%s, annual_volatility=%s,
                    alpha=%s, beta=%s, final_value=%s, total_trades=%s,
                    benchmark_return=%s, excess_return=%s,
                    end_time=NOW(), duration_ms=%s
                WHERE id=%s
            """, (
                summary.get("total_return"), summary.get("annualized_return"),
                summary.get("max_drawdown"), summary.get("sharpe_ratio"),
                summary.get("sortino_ratio"), summary.get("win_rate"),
                summary.get("profit_loss_ratio"), summary.get("annual_volatility"),
                summary.get("alpha"), summary.get("beta"),
                summary.get("final_value"), summary.get("total_trades", 0),
                summary.get("benchmark_return"), summary.get("excess_return"),
                summary.get("duration_ms"), backtest_id
            ))
            conn.commit()
    finally:
        conn.close()


def delete_job_full(backtest_id):
    """级联删除回测及所有关联数据"""
    conn = get_db_connection()
    if not conn: return
    try:
        with conn.cursor() as c:
            for t in ["backtest_nav", "backtest_trade", "backtest_position", "backtest_daily_metrics", "backtest_risk_metrics"]:
                c.execute(f"DELETE FROM {t} WHERE backtest_id = %s", (backtest_id,))
            c.execute("DELETE FROM backtest_job WHERE id = %s", (backtest_id,))
            conn.commit()
    finally:
        conn.close()


def clear_results(backtest_id):
    """清除回测结果数据（保留 job 记录），供 re-run 使用"""
    conn = get_db_connection()
    if not conn: return
    try:
        with conn.cursor() as c:
            for t in ["backtest_nav", "backtest_trade", "backtest_position", "backtest_daily_metrics", "backtest_risk_metrics"]:
                c.execute(f"DELETE FROM {t} WHERE backtest_id = %s", (backtest_id,))
            conn.commit()
    finally:
        conn.close()


# === Result Tables Writes ===

def batch_insert_nav(backtest_id, daily_nav):
    conn = get_db_connection()
    if not conn: return
    try:
        with conn.cursor() as c:
            if isinstance(daily_nav, dict):
                for date_str, nav_val in daily_nav.items():
                    c.execute(
                        "INSERT INTO backtest_nav (backtest_id, trade_date, unit_net_value) VALUES (%s,%s,%s)",
                        (backtest_id, date_str, nav_val))
            elif isinstance(daily_nav, list):
                for item in daily_nav:
                    if isinstance(item, dict):
                        c.execute(
                            "INSERT INTO backtest_nav (backtest_id, trade_date, unit_net_value, daily_return, benchmark_nav) VALUES (%s,%s,%s,%s,%s)",
                            (backtest_id, item.get("date"), item.get("nav"), item.get("daily_return"), item.get("benchmark_nav")))
            conn.commit()
    finally:
        conn.close()


def batch_insert_trades(backtest_id, trades):
    conn = get_db_connection()
    if not conn: return
    try:
        with conn.cursor() as c:
            for t in trades:
                if isinstance(t, dict):
                    c.execute(
                        "INSERT INTO backtest_trade (backtest_id, ts_code, buy_date, sell_date, buy_price, sell_price, quantity, buy_amount, sell_amount, pnl, pnl_pct) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                        (backtest_id, t.get("symbol", ""), t.get("buy_date"), t.get("sell_date"),
                         t.get("buy_price"), t.get("sell_price"), t.get("quantity", 0),
                         t.get("buy_amount"), t.get("sell_amount"), t.get("pnl"), t.get("pnl_pct")))
            conn.commit()
    finally:
        conn.close()


def batch_insert_positions(backtest_id, positions):
    conn = get_db_connection()
    if not conn: return
    try:
        with conn.cursor() as c:
            for p in positions:
                if isinstance(p, dict):
                    c.execute(
                        "INSERT INTO backtest_position (backtest_id, trade_date, ts_code, quantity, market_value, weight, cost, current_price) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                        (backtest_id, p.get("date"), p.get("symbol"), p.get("quantity", 0),
                         p.get("market_value", 0), p.get("weight", 0), p.get("cost", 0), p.get("current_price", 0)))
            conn.commit()
    finally:
        conn.close()


def batch_insert_daily_metrics(backtest_id, metrics):
    conn = get_db_connection()
    if not conn: return
    try:
        with conn.cursor() as c:
            for m in metrics:
                if isinstance(m, dict):
                    c.execute(
                        "INSERT INTO backtest_daily_metrics (backtest_id, trade_date, daily_return, cumulative_return, drawdown, portfolio_value, cash) VALUES (%s,%s,%s,%s,%s,%s,%s)",
                        (backtest_id, m.get("date"), m.get("daily_return"), m.get("cumulative_return"),
                         m.get("drawdown"), m.get("portfolio_value"), m.get("cash")))
            conn.commit()
    finally:
        conn.close()


def insert_risk_metrics(backtest_id, summary):
    conn = get_db_connection()
    if not conn: return
    try:
        with conn.cursor() as c:
            c.execute(
                "INSERT INTO backtest_risk_metrics (backtest_id, max_drawdown, annual_volatility) VALUES (%s,%s,%s)",
                (backtest_id, summary.get("max_drawdown"), summary.get("annual_volatility")))
            conn.commit()
    finally:
        conn.close()


# === Result Queries ===

def get_nav(backtest_id):
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor() as c:
            c.execute("SELECT trade_date, unit_net_value, benchmark_nav, excess_return FROM backtest_nav WHERE backtest_id=%s ORDER BY trade_date", (backtest_id,))
            return list(c.fetchall())
    finally:
        conn.close()


def get_trades(backtest_id, page=1, page_size=50):
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor() as c:
            c.execute("SELECT COUNT(*) as total FROM backtest_trade WHERE backtest_id=%s", (backtest_id,))
            total = c.fetchone()["total"] or 0
            off = (page - 1) * page_size
            c.execute("SELECT * FROM backtest_trade WHERE backtest_id=%s ORDER BY buy_date LIMIT %s OFFSET %s", (backtest_id, page_size, off))
            return {"items": list(c.fetchall()), "total": total, "page": page, "page_size": page_size}, None
    finally:
        conn.close()


def get_positions(backtest_id, trade_date=None):
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor() as c:
            if trade_date:
                c.execute("SELECT * FROM backtest_position WHERE backtest_id=%s AND trade_date=%s", (backtest_id, trade_date))
            else:
                c.execute("SELECT * FROM backtest_position WHERE backtest_id=%s ORDER BY trade_date, weight DESC LIMIT 500", (backtest_id,))
            return list(c.fetchall())
    finally:
        conn.close()


def get_daily_metrics(backtest_id):
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor() as c:
            c.execute("SELECT * FROM backtest_daily_metrics WHERE backtest_id=%s ORDER BY trade_date", (backtest_id,))
            return list(c.fetchall())
    finally:
        conn.close()


def get_risk_metrics(backtest_id):
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor() as c:
            c.execute("SELECT * FROM backtest_risk_metrics WHERE backtest_id=%s", (backtest_id,))
            return c.fetchone()
    finally:
        conn.close()
