#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
冒烟测试：验证系统核心功能可用
独立运行，不依赖 pytest
"""

import sys
import os

# 确保 backend 在 path 中
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def check(step, result, detail=""):
    """输出检查结果"""
    status = "PASS" if result else "FAIL"
    print(f"  [{status}] {step}" + (f" - {detail}" if detail else ""))


def main():
    print("=" * 50)
    print("冒烟测试 - Stock Backend")
    print("=" * 50)

    # 1. 检查 Python 可导入 core 模块
    print("\n[1] 基础设施导入检查")
    try:
        from app.core.config import settings
        check("from app.core.config import settings", True)
    except Exception as e:
        check("from app.core.config import settings", False, str(e))
        print("\n❌ 核心模块导入失败，后续检查无法继续")
        sys.exit(1)

    try:
        from app.core.database import get_engine, test_connection
        check("from app.core.database import get_engine", True)
    except Exception as e:
        check("from app.core.database import get_engine", False, str(e))

    try:
        from app.core.security import hash_password, generate_token, verify_token, require_auth
        check("from app.core.security import ...", True)
    except Exception as e:
        check("from app.core.security import ...", False, str(e))

    try:
        from app.core.response import success, error
        check("from app.core.response import ...", True)
    except Exception as e:
        check("from app.core.response import ...", False, str(e))

    try:
        from app.core.logger import setup_logger
        check("from app.core.logger import setup_logger", True)
    except Exception as e:
        check("from app.core.logger import setup_logger", False, str(e))

    # 2. 检查 Flask app 可创建
    print("\n[2] Flask 应用创建检查")
    try:
        from app import create_app
        app = create_app()
        check("create_app()", app is not None)
    except Exception as e:
        check("create_app()", False, str(e))

    # 3. 检查 .env 已加载
    print("\n[3] 配置加载检查")
    try:
        from app.core.config import settings
        check("settings.DB_HOST not empty", bool(settings.DB_HOST))
    except Exception as e:
        check("settings.DB_HOST not empty", False, str(e))

    # 4. 检查 API 路由已注册
    print("\n[4] API 路由注册检查")
    if app:
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        expected = [
            "/api/health",
            "/api/user/register",
            "/api/user/login",
            "/api/user/info",
            "/api/user/change-password",
            "/api/stocks",
            "/api/stocks/areas",
            "/api/stocks/industries",
            "/api/stocks/sync",
            "/api/stock/data",
            "/api/stock_select",
            "/api/stock/select/mock",
            "/api/stock/check",
            "/api/stock/daily/add",
            "/api/vol_line",
        ]
        for route in expected:
            check(f"路由 {route}", route in routes)

    # 5. 数据库连接测试
    print("\n[5] 数据库连接检查")
    try:
        db_ok = test_connection()
        check("数据库连接", db_ok)
    except Exception as e:
        check("数据库连接", False, str(e))

    # 汇总
    print("\n" + "=" * 50)
    print("冒烟测试完成")
    print("=" * 50)


if __name__ == "__main__":
    main()
