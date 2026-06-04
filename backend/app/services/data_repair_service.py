# -*- coding: utf-8 -*-
"""
数据修复服务：创建修复任务、执行修复、自动复检
"""

import json
import logging
from datetime import datetime

from app.repositories import data_quality_repo as quality_repo
from app.services import task_service
from app.services import data_service

logger = logging.getLogger("myapp")


def create_repair(issue_id: int, repair_mode: str, options: dict) -> dict:
    try:
        issue = quality_repo.get_issue(issue_id)
        if not issue:
            return {"error": "issue not found", "repair_job_id": 0}

        task = task_service.create_task(
            task_type="repair_missing_data",
            priority=5,
            params={"issue_id": issue_id, "repair_mode": repair_mode, "options": options},
        )

        task_job_id = task["id"] if task else None

        repair_job_id = quality_repo.create_repair_job({
            "issue_id": issue_id,
            "task_job_id": task_job_id,
            "repair_mode": repair_mode,
            "status": "pending",
            "options_json": json.dumps(options or {}, ensure_ascii=False),
        })

        if repair_job_id > 0 and task_job_id:
            quality_repo.update_issue(issue_id, {"status": "repairing"})

        job = quality_repo.get_repair_job(repair_job_id)
        return dict(job) if job else {"repair_job_id": repair_job_id}
    except Exception as e:
        logger.error(f"create_repair error: {e}")
        return {"error": str(e), "repair_job_id": 0}


def execute_repair(repair_job_id: int):
    try:
        job = quality_repo.get_repair_job(repair_job_id)
        if not job:
            logger.error(f"repair_job {repair_job_id} not found")
            return

        issue = quality_repo.get_issue(job["issue_id"])
        if not issue:
            logger.error(f"issue {job['issue_id']} not found")
            quality_repo.update_repair_job(repair_job_id, {"status": "failed"})
            return

        quality_repo.update_repair_job(repair_job_id, {
            "status": "running",
            "started_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

        before_snapshot = {
            "expected_count": issue.get("expected_count", 0),
            "actual_count": issue.get("actual_count", 0),
            "missing_count": issue.get("missing_count", 0),
        }
        quality_repo.update_repair_job(repair_job_id, {
            "before_snapshot_json": json.dumps(before_snapshot, ensure_ascii=False),
        })

        if job["repair_mode"] == "ignore":
            quality_repo.update_issue(job["issue_id"], {"status": "ignored"})
            quality_repo.update_repair_job(repair_job_id, {
                "status": "success",
                "finished_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
            return

        start_date = issue["start_date"]
        end_date = issue["end_date"]
        market = issue.get("market", "A股")

        if market == "A股":
            data_service.download_daily_data(start_date, end_date)
        else:
            data_service._download_hk_daily()

        all_fixed = auto_recheck(job["issue_id"])

        after_snapshot = {"all_fixed": all_fixed}
        quality_repo.update_repair_job(repair_job_id, {
            "after_snapshot_json": json.dumps(after_snapshot, ensure_ascii=False),
            "finished_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        })

        if all_fixed:
            quality_repo.update_issue(job["issue_id"], {
                "status": "resolved",
                "resolved_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
            quality_repo.update_repair_job(repair_job_id, {"status": "success"})
        else:
            quality_repo.update_repair_job(repair_job_id, {"status": "failed"})
            quality_repo.update_issue(job["issue_id"], {"status": "failed"})

        report = {
            "issue_id": job["issue_id"],
            "repair_mode": job["repair_mode"],
            "date_range": f"{start_date}~{end_date}",
            "all_fixed": all_fixed,
        }
        quality_repo.update_repair_job(repair_job_id, {
            "report_json": json.dumps(report, ensure_ascii=False),
        })
    except Exception as e:
        logger.error(f"execute_repair error: {e}")
        try:
            quality_repo.update_repair_job(repair_job_id, {
                "status": "failed",
                "finished_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            })
        except Exception:
            pass


def auto_recheck(issue_id: int) -> bool:
    try:
        issue = quality_repo.get_issue(issue_id)
        if not issue:
            return False

        market = issue.get("market", "A股")
        start_date = issue["start_date"]
        end_date = issue["end_date"]

        details = quality_repo.get_issue_details(issue_id)
        if not details:
            return True

        missing_codes = set()
        for d in details:
            if d.get("issue_type") == "missing_daily":
                missing_codes.add(d["ts_code"])

        if not missing_codes:
            return True

        table = "stock_daily" if market == "A股" else "hk_stock_daily"
        from app.core.database import get_db_connection
        conn = get_db_connection()
        if not conn:
            return False
        try:
            with conn.cursor() as cursor:
                ph = ", ".join(["%s"] * len(missing_codes))
                cursor.execute(
                    f"SELECT DISTINCT ts_code FROM {table} "
                    f"WHERE trade_date BETWEEN %s AND %s AND ts_code IN ({ph})",
                    [start_date, end_date] + list(missing_codes),
                )
                found = {r["ts_code"] for r in cursor.fetchall()}
        finally:
            conn.close()

        still_missing = missing_codes - found
        return len(still_missing) == 0
    except Exception as e:
        logger.error(f"auto_recheck error: {e}")
        return False
