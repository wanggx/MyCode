#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用入口
"""

import threading
from app import create_app
from app.core.database import test_connection
from tasks.scheduler import start_scheduler

app = create_app()

if __name__ == "__main__":
    print("正在测试数据库连接...")
    if not test_connection():
        print("数据库连接失败，请检查配置")
        exit(1)
    print("数据库连接成功")

    # 启动调度器线程
    scheduler_thread = threading.Thread(target=start_scheduler, daemon=True)
    scheduler_thread.start()

    print("启动Flask服务...")
    print("服务地址: http://localhost:5000")
    app.run(debug=False, host="0.0.0.0", port=5000)
