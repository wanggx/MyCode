# -*- coding: utf-8 -*-
"""策略 & 策略版本数据访问"""
import json
from app.core.database import get_db_connection


# === Strategy CRUD ===

def list_strategies(page=1, page_size=20, status=None, keyword=None, user_id=None):
    conn = get_db_connection()
    if not conn: return None, "DB error"
    try:
        with conn.cursor() as c:
            where, params = [], []
            if status: where.append("s.status = %s"); params.append(status)
            if keyword:
                where.append("(s.name LIKE %s OR s.description LIKE %s)")
                kw = f"%{keyword}%"; params.extend([kw, kw])
            if user_id: where.append("s.user_id = %s"); params.append(user_id)
            wc = ("WHERE " + " AND ".join(where)) if where else ""

            c.execute(f"SELECT COUNT(*) as total FROM strategy s {wc}", params)
            total = c.fetchone()["total"] or 0

            off = (page - 1) * page_size
            c.execute(f"""
                SELECT s.*, bj.total_return AS last_bt_return, bj.status AS last_bt_status
                FROM strategy s
                LEFT JOIN (
                    SELECT strategy_id, total_return, status,
                           ROW_NUMBER() OVER (PARTITION BY strategy_id ORDER BY created_at DESC) AS rn
                    FROM backtest_job
                ) bj ON s.id = bj.strategy_id AND bj.rn = 1
                {wc} ORDER BY s.updated_at DESC LIMIT %s OFFSET %s
            """, params + [page_size, off])
            rows = c.fetchall()
            items = []
            for r in rows:
                items.append({
                    "id": r["id"], "name": r["name"], "description": r.get("description", ""),
                    "strategy_type": r.get("strategy_type", "stock"),
                    "status": r["status"], "latest_version": r.get("latest_version", 0),
                    "strategy_key": r.get("strategy_key", ""),
                    "default_config": json.loads(r["default_config"]) if r.get("default_config") else None,
                    "tags": json.loads(r["tags"]) if r.get("tags") else None,
                    "last_backtest_status": r.get("last_bt_status"),
                    "last_backtest_return": r.get("last_bt_return"),
                    "created_at": str(r["created_at"]) if r.get("created_at") else None,
                    "updated_at": str(r["updated_at"]) if r.get("updated_at") else None,
                })
            return {"items": items, "total": total, "page": page, "page_size": page_size}, None
    except Exception as e:
        return None, f"查询失败: {str(e)}"
    finally:
        conn.close()


def get_strategy(strategy_id):
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor() as c:
            c.execute("SELECT * FROM strategy WHERE id = %s", (strategy_id,))
            return c.fetchone()
    finally:
        conn.close()


def create_strategy(name, description, strategy_type, user_id, strategy_key, default_config=None):
    conn = get_db_connection()
    if not conn: return None, "DB error"
    try:
        with conn.cursor() as c:
            config_json = json.dumps(default_config) if default_config else None
            c.execute(
                "INSERT INTO strategy (user_id, name, description, strategy_type, status, latest_version, default_config, strategy_key) VALUES (%s,%s,%s,%s,'draft',0,%s,%s)",
                (user_id, name, description, strategy_type, config_json, strategy_key)
            )
            conn.commit()
            return c.lastrowid, None
    except Exception as e:
        return None, f"创建失败: {str(e)}"
    finally:
        conn.close()


def update_strategy(strategy_id, **kwargs):
    conn = get_db_connection()
    if not conn: return False
    try:
        allowed = {"name", "description", "strategy_type", "default_config", "tags", "strategy_key"}
        sets, params = [], []
        for k, v in kwargs.items():
            if k in allowed:
                sets.append(f"{k} = %s")
                params.append(json.dumps(v) if k in ("default_config", "tags") else v)
        if not sets: return False
        params.append(strategy_id)
        with conn.cursor() as c:
            c.execute(f"UPDATE strategy SET {', '.join(sets)} WHERE id = %s", params)
            conn.commit()
        return True
    finally:
        conn.close()


def update_strategy_status(strategy_id, status):
    conn = get_db_connection()
    if not conn: return False
    try:
        with conn.cursor() as c:
            c.execute("UPDATE strategy SET status = %s WHERE id = %s", (status, strategy_id))
            conn.commit()
        return True
    finally:
        conn.close()


def delete_strategy(strategy_id):
    conn = get_db_connection()
    if not conn: return False
    try:
        with conn.cursor() as c:
            c.execute("SELECT COUNT(*) as cnt FROM backtest_job WHERE strategy_id = %s", (strategy_id,))
            if c.fetchone()["cnt"] > 0:
                return False  # has backtests, can't delete
            c.execute("DELETE FROM strategy_version WHERE strategy_id = %s", (strategy_id,))
            c.execute("DELETE FROM strategy WHERE id = %s", (strategy_id,))
            conn.commit()
        return True
    finally:
        conn.close()


# === Version CRUD ===

def list_versions(strategy_id):
    conn = get_db_connection()
    if not conn: return []
    try:
        with conn.cursor() as c:
            c.execute(
                "SELECT id, version, change_log, status, created_at FROM strategy_version WHERE strategy_id = %s ORDER BY version DESC",
                (strategy_id,))
            return list(c.fetchall())
    finally:
        conn.close()


def get_version(strategy_id, version=None):
    """获取特定版本或最新版本"""
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor() as c:
            if version:
                c.execute("SELECT * FROM strategy_version WHERE strategy_id = %s AND version = %s", (strategy_id, version))
            else:
                c.execute("SELECT * FROM strategy_version WHERE strategy_id = %s ORDER BY version DESC LIMIT 1", (strategy_id,))
            return c.fetchone()
    finally:
        conn.close()


get_latest_version = get_version  # alias


def create_version(strategy_id, source_code, change_log="", config=None):
    conn = get_db_connection()
    if not conn: return None
    try:
        with conn.cursor() as c:
            c.execute("SELECT MAX(version) as mv FROM strategy_version WHERE strategy_id = %s", (strategy_id,))
            row = c.fetchone()
            new_ver = (row["mv"] or 0) + 1
            c.execute(
                "INSERT INTO strategy_version (strategy_id, version, source_code, config, change_log) VALUES (%s,%s,%s,%s,%s)",
                (strategy_id, new_ver, source_code, json.dumps(config) if config else None, change_log))
            c.execute("UPDATE strategy SET latest_version = %s WHERE id = %s", (new_ver, strategy_id))
            conn.commit()
            return new_ver
    except Exception as e:
        print(f"create_version error: {e}")
        return None
    finally:
        conn.close()
