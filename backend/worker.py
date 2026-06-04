#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Worker 进程入口
用法: python backend/worker.py
"""

import sys
import os
import time
from datetime import datetime, timedelta

sys.path.insert(0, os.path.join(os.path.dirname(__file__)))

from app.core.logger import setup_logger
from app.repositories import task_repo
from app.repositories import backtest_repo
from app.services.data_service import download_daily_data

logger = setup_logger()


def _ensure_tables():
    """确保 task_job 和 task_step 表存在"""
    if not task_repo.init_tables():
        logger.error("数据库连接失败，退出")
        sys.exit(1)
    backtest_repo.init_tables()
    from app.repositories import portfolio_repo
    portfolio_repo.init_tables()


def execute_task(job):
    """根据 task_type 分发执行"""
    import json

    job_id = job["id"]
    task_type = job["task_type"]
    params = job.get("params_json")
    if isinstance(params, str):
        try:
            params = json.loads(params)
        except (json.JSONDecodeError, TypeError):
            params = {}

    logger.info(f"开始执行任务 #{job_id} type={task_type}")

    try:
        if task_type == "sync_daily_data":
            _execute_sync_daily(job_id, params or {})
        elif task_type == "repair_missing_data":
            _execute_repair_missing_data(job_id, params or {})
        elif task_type == "run_strategy":
            from app.services.strategy_service import execute_run
            execute_run(params["run_id"])
        elif task_type == "run_backtest":
            from app.services.backtest_service import execute_backtest
            execute_backtest(params["backtest_job_id"])
        elif task_type == "update_portfolio":
            from app.services.portfolio_service import update_portfolio_nav
            update_portfolio_nav(params["portfolio_id"])
        else:
            logger.warning(f"未实现的任务类型: {task_type}")
            task_repo.update_job_status(job_id, "failed", message=f"未实现的任务类型: {task_type}")
            return

        task_repo.update_job_status(job_id, "success", progress=100, message="完成")
        logger.info(f"任务 #{job_id} 执行成功")
    except Exception as e:
        logger.exception(f"任务 #{job_id} 执行失败: {e}")
        task_repo.update_job_status(job_id, "failed", message=str(e))


def _execute_sync_daily(job_id, params):
    """执行 sync_daily_data 任务"""
    step_id = task_repo.create_step(job_id, 1, "下载日线数据")
    task_repo.update_step_status(step_id, "running")

    try:
        start_date = params.get("start_date")
        end_date = params.get("end_date")
        if not start_date or not end_date:
            today = datetime.now()
            yesterday = today - timedelta(days=1)
            start_date = yesterday.strftime("%Y%m%d")
            end_date = today.strftime("%Y%m%d")

        download_daily_data(start_date, end_date)
        task_repo.update_step_status(step_id, "success", message=f"已下载 {start_date}~{end_date}")
        task_repo.update_job_status(job_id, "running", progress=80)
    except Exception as e:
        task_repo.update_step_status(step_id, "failed", message=str(e))
        raise


def _execute_repair_missing_data(job_id, params):
    """执行 repair_missing_data 任务"""
    from app.services.data_repair_service import execute_repair

    repair_job_id = params.get("repair_job_id")
    if not repair_job_id:
        raise ValueError("缺少 repair_job_id 参数")

    step_id = task_repo.create_step(job_id, 1, "执行数据修复")
    task_repo.update_step_status(step_id, "running")

    try:
        execute_repair(repair_job_id)
        task_repo.update_step_status(step_id, "success", message="修复完成")
        task_repo.update_job_status(job_id, "running", progress=80)
    except Exception as e:
        task_repo.update_step_status(step_id, "failed", message=str(e))
        raise


def main_loop():
    """每隔 5 秒扫描一次 pending 任务"""
    logger.info("Worker 启动，开始扫描任务...")
    while True:
        try:
            job = task_repo.claim_pending_job()
            if job:
                execute_task(job)
            else:
                time.sleep(5)
        except Exception as e:
            logger.exception(f"主循环异常: {e}")
            time.sleep(5)


if __name__ == "__main__":
    _ensure_tables()
    main_loop()
