# -*- coding: utf-8 -*-
"""
定时任务调度器
"""

import time
import logging
import schedule

from app.services.data_service import download_daily_data

logger = logging.getLogger("myapp")


def job():
    """定时任务：每日 16:30 下载数据"""
    logger.info(f"定时任务已执行: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    try:
        from datetime import datetime, timedelta
        today = datetime.now().strftime("%Y%m%d")
        yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y%m%d")
        download_daily_data(yesterday, today)
    except Exception as e:
        logger.error(f"定时下载数据失败: {e}")


def start_scheduler():
    """启动调度器"""
    schedule.every().day.at("16:30").do(job)

    while True:
        schedule.run_pending()
        time.sleep(1)
