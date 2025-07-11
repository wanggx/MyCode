
import time
import threading
from flask import Flask, jsonify
import schedule
from flask_cors import CORS

from download_daily import download_daily

# 导入用户和股票模块
from backend.user import create_user_routes, test_database_connection
from backend.stock_list import create_stock_routes

from utils.logger import setup_logger
logger = setup_logger()

# 创建 Flask 应用实例
app = Flask(__name__)
CORS(app)  # 允许跨域请求

# 注册用户和股票路由
create_user_routes(app)
create_stock_routes(app)

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

# 健康检查接口
@app.route('/api/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'service': 'main-service',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
    }), 200

def job():
    """定时任务"""
    logger.info(f"定时任务已执行: {time.strftime('%Y-%m-%d %H:%M:%S')}")

def startScheduler():
    """启动调度器"""
    # 每10秒运行一次任务
    schedule.every(10).seconds.do(job)
    schedule.every().day.at("16:30").do(download_daily)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

# 启动 Flask 服务
if __name__ == '__main__':

    # 测试数据库连接
    print("正在测试数据库连接...")
    if not test_database_connection():
        print("数据库连接失败，请检查配置或先执行SQL初始化文件")
        exit(1)
    print("数据库连接成功")

    # 启动调度器线程
    scheduler_thread = threading.Thread(target=startScheduler)
    scheduler_thread.daemon = True  # 设置为守护线程，主程序结束时自动退出
    scheduler_thread.start()

    print("启动Flask服务...")
    print("服务地址: http://localhost:8080")
    print("API文档:")
    print("  - 用户注册: POST /api/user/register")
    print("  - 用户登录: POST /api/user/login")
    print("  - 获取用户信息: GET /api/user/info")
    print("  - 获取股票列表: GET /api/stocks")
    print("  - 获取股票详情: GET /api/stocks/<code>")
    print("  - 搜索股票: GET /api/stocks/search")
    print("  - 市场概览: GET /api/stocks/market-overview")
    print("  - 健康检查: GET /api/health")
    print("\n默认管理员账号:")
    print("用户名: admin")
    print("密码: 123456")
    print("\n注意: 请先执行 backend/init_database.sql 文件初始化数据库")

    app.run(debug=False, host='0.0.0.0', port=8080)
