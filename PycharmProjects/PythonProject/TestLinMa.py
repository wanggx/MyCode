import schedule
import time

def job():
    print("定时任务已执行")

# 每10秒运行一次任务
schedule.every(10).seconds.do(job)

while True:
    schedule.run_pending()
    time.sleep(1)

# schedule.every().day.at("10:30").do(job)  # 每天10:30执行
# schedule.every().hour.do(job)            # 每小时执行一次
