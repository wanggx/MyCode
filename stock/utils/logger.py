import logging
import os
from logging.handlers import TimedRotatingFileHandler

def setup_logger():
    # 创建 logs 目录（如果不存在）
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 日志格式
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # 主 logger
    logger = logging.getLogger('myapp')
    logger.setLevel(logging.INFO)

    # 文件处理器：按天滚动
    file_handler = TimedRotatingFileHandler(os.path.join(log_dir, 'app.log'), when='midnight', backupCount=7)
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO)

    # 防止重复添加 handler
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger
