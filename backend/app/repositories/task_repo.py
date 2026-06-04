# -*- coding: utf-8 -*-
"""
任务数据访问层：task_job / task_step 的 CRUD
"""

import json
import logging
from datetime import datetime

from app.core.database import get_db_connection
from app.repositories.base import paginate_sql

logger = logging.getLogger(__name__)


def init_tables():
    """确保 task_job 和 task_step 表存在"""
    conn = get_db_connection()
    if not conn:
        logger.error("数据库连接失败，无法初始化任务表")
        return False
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_job (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    task_type VARCHAR(50) NOT NULL COMMENT '任务类型',
                    status VARCHAR(20) NOT NULL DEFAULT 'pending' COMMENT 'pending/running/success/failed/canceled',
                    priority INT NOT NULL DEFAULT 0 COMMENT '优先级（越大越优先）',
                    params_json JSON COMMENT '任务参数JSON',
                    progress INT DEFAULT 0 COMMENT '进度0-100',
                    message TEXT COMMENT '状态消息/错误信息',
                    created_by VARCHAR(50) DEFAULT 'system' COMMENT '创建者',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    started_at DATETIME NULL,
                    finished_at DATETIME NULL,
                    INDEX idx_status_priority (status, priority, created_at),
                    INDEX idx_task_type (task_type)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS task_step (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    job_id INT NOT NULL COMMENT '关联任务ID',
                    step_order INT NOT NULL COMMENT '步骤序号',
                    step_name VARCHAR(100) NOT NULL COMMENT '步骤名',
                    status VARCHAR(20) DEFAULT 'pending' COMMENT 'pending/running/success/failed',
                    message TEXT COMMENT '步骤消息',
                    started_at DATETIME NULL,
                    finished_at DATETIME NULL,
                    INDEX idx_job_id (job_id, step_order)
                ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
            """)
        conn.commit()
        logger.info("任务表已就绪")
        return True
    finally:
        conn.close()


def create_job(task_type, priority=0, params_json=None, created_by="system"):
    """创建任务，返回 job_id"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            params_str = json.dumps(params_json, ensure_ascii=False) if params_json else None
            sql = """
                INSERT INTO task_job (task_type, status, priority, params_json, created_by)
                VALUES (%s, 'pending', %s, %s, %s)
            """
            cursor.execute(sql, [task_type, priority, params_str, created_by])
            job_id = cursor.lastrowid
        conn.commit()
        return job_id
    finally:
        conn.close()


def get_job(job_id):
    """获取单个任务"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM task_job WHERE id = %s", [job_id])
            return cursor.fetchone()
    finally:
        conn.close()


def get_jobs(status=None, task_type=None, page=1, page_size=20):
    """分页查询任务列表"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            conditions = []
            params = []
            if status:
                conditions.append("status = %s")
                params.append(status)
            if task_type:
                conditions.append("task_type = %s")
                params.append(task_type)
            where = (" WHERE " + " AND ".join(conditions)) if conditions else ""

            base_sql = f"SELECT * FROM task_job{where} ORDER BY priority DESC, created_at DESC"
            count_sql = f"SELECT COUNT(*) AS total FROM task_job{where}"
            return paginate_sql(base_sql, count_sql, params, page, page_size, cursor)
    finally:
        conn.close()


def update_job_status(job_id, status, message=None, progress=None):
    """更新任务状态"""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            sets = ["status = %s"]
            params = [status]

            if message is not None:
                sets.append("message = %s")
                params.append(message)
            if progress is not None:
                sets.append("progress = %s")
                params.append(progress)

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if status == "running":
                sets.append("started_at = %s")
                params.append(now)
            elif status in ("success", "failed", "canceled"):
                sets.append("finished_at = %s")
                params.append(now)

            params.append(job_id)
            sql = f"UPDATE task_job SET {', '.join(sets)} WHERE id = %s"
            cursor.execute(sql, params)
            affected = cursor.rowcount
        conn.commit()
        return affected > 0
    finally:
        conn.close()


def claim_pending_job():
    """原子性地抢占一条 pending 任务：设为 running 并返回"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM task_job WHERE status = 'pending' "
                "ORDER BY priority DESC, created_at ASC LIMIT 1 "
                "FOR UPDATE"
            )
            job = cursor.fetchone()
            if not job:
                return None
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute(
                "UPDATE task_job SET status = 'running', started_at = %s WHERE id = %s",
                [now, job["id"]],
            )
        conn.commit()
        job["status"] = "running"
        job["started_at"] = now
        return job
    finally:
        conn.close()


def create_step(job_id, step_order, step_name):
    """创建步骤记录，返回 step_id"""
    conn = get_db_connection()
    if not conn:
        return None
    try:
        with conn.cursor() as cursor:
            sql = """
                INSERT INTO task_step (job_id, step_order, step_name, status)
                VALUES (%s, %s, %s, 'pending')
            """
            cursor.execute(sql, [job_id, step_order, step_name])
            step_id = cursor.lastrowid
        conn.commit()
        return step_id
    finally:
        conn.close()


def update_step_status(step_id, status, message=None):
    """更新步骤状态"""
    conn = get_db_connection()
    if not conn:
        return False
    try:
        with conn.cursor() as cursor:
            sets = ["status = %s"]
            params = [status]

            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if status == "running":
                sets.append("started_at = %s")
                params.append(now)
            elif status in ("success", "failed"):
                sets.append("finished_at = %s")
                params.append(now)

            if message is not None:
                sets.append("message = %s")
                params.append(message)

            params.append(step_id)
            sql = f"UPDATE task_step SET {', '.join(sets)} WHERE id = %s"
            cursor.execute(sql, params)
            affected = cursor.rowcount
        conn.commit()
        return affected > 0
    finally:
        conn.close()


def get_steps(job_id):
    """获取任务的所有步骤"""
    conn = get_db_connection()
    if not conn:
        return []
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT * FROM task_step WHERE job_id = %s ORDER BY step_order",
                [job_id],
            )
            return cursor.fetchall()
    finally:
        conn.close()
