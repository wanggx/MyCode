# -*- coding: utf-8 -*-
"""
Flask 应用工厂
"""

import datetime
from flask import Flask, jsonify
from flask_cors import CORS
from flask.json.provider import DefaultJSONProvider

from app.core.logger import setup_logger


class CustomJSONProvider(DefaultJSONProvider):
    """自定义 JSON 序列化：datetime → YYYY-MM-DD HH:MM:SS"""
    def default(self, obj):
        if isinstance(obj, (datetime.datetime, datetime.date)):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        return super().default(obj)


def create_app():
    """创建并配置 Flask 应用"""
    app = Flask(__name__)
    app.json = CustomJSONProvider(app)
    CORS(app)

    # 初始化日志
    setup_logger()

    # 注册 Blueprint
    from app.api.auth import auth_bp
    from app.api.stocks import stocks_bp
    from app.api.stock_select import select_bp
    from app.api.stock_check import check_bp
    from app.api.vol_line import vol_line_bp
    from app.api.tasks import tasks_bp
    from app.api.data_quality import data_quality_bp
    from app.api.strategies import strategies_bp
    from app.api.signals import signals_bp
    from app.api.backtests import backtests_bp
    from app.api.portfolio import portfolio_bp
    from app.api.watchlist import watchlist_bp
    from app.api.factors import factors_bp
    from app.api.trading import trading_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(stocks_bp)
    app.register_blueprint(select_bp)
    app.register_blueprint(check_bp)
    app.register_blueprint(vol_line_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(data_quality_bp)
    app.register_blueprint(strategies_bp)
    app.register_blueprint(signals_bp)
    app.register_blueprint(backtests_bp)
    app.register_blueprint(portfolio_bp, url_prefix="/api/portfolio")
    app.register_blueprint(watchlist_bp, url_prefix="/api/watchlist")
    app.register_blueprint(factors_bp, url_prefix="/api/factors")
    app.register_blueprint(trading_bp)

    # Phase 1: 数据中心
    from app.api.data import data_bp
    app.register_blueprint(data_bp)

    _init_all_tables()

    # 健康检查
    @app.route("/api/health", methods=["GET"])
    def health_check():
        import time
        return jsonify({
            "status": "healthy",
            "service": "main-service",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }), 200

    @app.route("/hello", methods=["GET"])
    def hello_world():
        return "Hello, World!"

    return app


def _init_all_tables():
    """初始化所有模块的数据库表，失败不阻塞应用启动"""
    import logging
    import importlib

    logger = logging.getLogger("myapp")

    repos = [
        ("任务", "app.repositories.task_repo"),
        ("信号", "app.repositories.signal_repo"),
        ("策略", "app.repositories.strategy_repo"),
        ("数据质量", "app.repositories.data_quality_repo"),
        ("组合风控", "app.repositories.portfolio_repo"),
        ("回测", "app.repositories.backtest_repo"),
        ("分钟线", "app.repositories.minute_repo"),
    ]
    for name, repo_path in repos:
        try:
            mod = importlib.import_module(repo_path)
            if hasattr(mod, 'init_tables'):
                ok = mod.init_tables()
                if ok:
                    logger.info(f"表初始化完成: {name}")
                else:
                    logger.warning(f"表初始化失败({name}): 数据库连接失败")
        except Exception as e:
            logger.warning(f"表初始化失败({name}): {e}")
