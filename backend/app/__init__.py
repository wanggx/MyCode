# -*- coding: utf-8 -*-
"""
Flask 应用工厂
"""

from flask import Flask, jsonify
from flask_cors import CORS

from app.core.logger import setup_logger


def create_app():
    """创建并配置 Flask 应用"""
    app = Flask(__name__)
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

    app.register_blueprint(auth_bp)
    app.register_blueprint(stocks_bp)
    app.register_blueprint(select_bp)
    app.register_blueprint(check_bp)
    app.register_blueprint(vol_line_bp)
    app.register_blueprint(tasks_bp)
    app.register_blueprint(data_quality_bp)
    app.register_blueprint(strategies_bp)
    app.register_blueprint(signals_bp)
    app.register_blueprint(backtests_bp, url_prefix="/api/backtests")
    app.register_blueprint(portfolio_bp, url_prefix="/api/portfolio")
    app.register_blueprint(watchlist_bp, url_prefix="/api/watchlist")
    app.register_blueprint(factors_bp, url_prefix="/api/factors")

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
