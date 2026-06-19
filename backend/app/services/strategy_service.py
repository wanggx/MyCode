# -*- coding: utf-8 -*-
"""策略服务：CRUD + 版本管理"""
import re
from app.repositories.strategy_repo import (
    list_strategies, get_strategy, create_strategy, update_strategy,
    update_strategy_status, delete_strategy,
    list_versions, get_version, create_version
)


def _generate_strategy_key(name):
    cleaned = re.sub(r'[^\w一-鿿]', '_', name).strip('_')
    try:
        import pypinyin
        parts = pypinyin.lazy_pinyin(name, style=pypinyin.NORMAL)
        key = '_'.join(parts).lower()
        return key[:64] if len(key) > 64 else key
    except ImportError:
        return re.sub(r'[^\w]', '_', name).lower()[:64]


def get_strategies(page=1, page_size=20, status=None, keyword=None, user_id=None):
    return list_strategies(page, page_size, status, keyword, user_id)


def get_strategy_detail(strategy_id):
    row = get_strategy(strategy_id)
    if not row: return None
    import json
    return {
        "id": row["id"], "name": row["name"], "description": row.get("description", ""),
        "strategy_type": row.get("strategy_type", "stock"), "status": row["status"],
        "latest_version": row.get("latest_version", 0), "strategy_key": row.get("strategy_key", ""),
        "default_config": json.loads(row["default_config"]) if row.get("default_config") else None,
        "tags": json.loads(row["tags"]) if row.get("tags") else None,
        "created_at": str(row["created_at"]) if row.get("created_at") else None,
        "updated_at": str(row["updated_at"]) if row.get("updated_at") else None,
    }


def create_strategy_svc(name, description, strategy_type, user_id, default_config=None):
    key = _generate_strategy_key(name)
    sid, err = create_strategy(name, description, strategy_type, user_id, key, default_config)
    if err: return None, err
    return {"id": sid, "strategy_key": key, "status": "draft", "latest_version": 0}, None


def update_strategy_svc(strategy_id, **kwargs):
    return update_strategy(strategy_id, **kwargs)


def change_strategy_status(strategy_id, status):
    if status not in ("draft", "active", "archived"): return False, "无效状态"
    return update_strategy_status(strategy_id, status), None


def delete_strategy_svc(strategy_id):
    ok = delete_strategy(strategy_id)
    if not ok: return False, "无法删除：该策略下存在回测记录，请先删除所有回测"
    return True, None


def get_versions(strategy_id):
    rows = list_versions(strategy_id)
    return [{"version": r["version"], "change_log": r.get("change_log", ""),
             "status": r.get("status", "active"),
             "created_at": str(r["created_at"]) if r.get("created_at") else None} for r in rows]


def get_version_detail(strategy_id, version):
    row = get_version(strategy_id, version)
    if not row: return None
    import json
    return {"version": row["version"], "source_code": row["source_code"],
            "config": json.loads(row["config"]) if row.get("config") else None,
            "change_log": row.get("change_log", ""), "status": row.get("status", "active"),
            "created_at": str(row["created_at"]) if row.get("created_at") else None}


def create_version_svc(strategy_id, source_code, change_log="", config=None):
    if not source_code or not source_code.strip(): return None, "策略代码不能为空"
    ver = create_version(strategy_id, source_code, change_log, config)
    if ver is None: return None, "创建版本失败"
    return {"version": ver, "strategy_id": strategy_id, "status": "active"}, None
