
import time
import threading
from flask import Flask, jsonify
import schedule
from stock import download_daily


def job():
    print("定时任务已执行")

def startScheduler():

    # 每10秒运行一次任务
    schedule.every(10).seconds.do(job)
    schedule.every().day.at("16:30").do(download_daily.download_daily)

    while True:
        schedule.run_pending()
        time.sleep(1)

# 创建 Flask 应用实例
app = Flask(__name__)

# 定义路由和对应的处理函数
@app.route('/hello', methods=['GET'])
def hello_world():
    return 'Hello, World!'

# 定义一个返回 JSON 的接口
@app.route('/api/data', methods=['GET'])
def get_data():
    # 构造要返回的 JSON 数据
    data = {
        "message": "Hello, World!",
        "status": "success",
        "code": 200,
        "data": {
            "name": "Flask",
            "version": "2.0.3"
        }
    }
    # 使用 jsonify 返回 JSON 响应
    return jsonify(data)

# 启动 Flask 服务
if __name__ == '__main__':

    # 启动调度器线程
    scheduler_thread = threading.Thread(target=startScheduler)
    scheduler_thread.daemon = True  # 设置为守护线程，主程序结束时自动退出
    scheduler_thread.start()

    app.run(debug=True, port=80)
