

import schedule
import time

def job():
    print("定时任务已执行")

# 每10秒运行一次任务
schedule.every(10).seconds.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)
