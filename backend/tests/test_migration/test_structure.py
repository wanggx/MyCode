# -*- coding: utf-8 -*-
"""
验证新旧目录结构完整性
"""

import os


BASE = os.path.join(os.path.dirname(__file__), "..", "..")


def test_new_directories_exist():
    """验证新目录结构完整"""
    dirs = [
        "app",
        "app/api",
        "app/services",
        "app/repositories",
        "app/analysis",
        "app/core",
        "app/utils",
        "hk",
        "tasks",
        "tests",
        "tests/test_core",
        "tests/test_api",
        "tests/test_analysis",
        "tests/test_migration",
    ]
    for d in dirs:
        path = os.path.join(BASE, d)
        assert os.path.isdir(path), f"缺少目录: {path}"


def test_new_files_exist():
    """验证关键新文件存在"""
    files = [
        "app/__init__.py",
        "app/core/config.py",
        "app/core/database.py",
        "app/core/security.py",
        "app/core/response.py",
        "app/core/logger.py",
        "app/utils/dateutil.py",
        "app/utils/notify.py",
        "run.py",
    ]
    for f in files:
        path = os.path.join(BASE, f)
        assert os.path.isfile(path), f"缺少文件: {path}"
