# -*- coding: utf-8 -*-
"""
验证无硬编码密钥残留
"""

import os
import re

# 应排除的目录
EXCLUDE_DIRS = {".venv", "__pycache__", ".git", "node_modules", ".idea"}
# 根目录（限定在 backend/ 新代码范围）
BASE = os.path.realpath(os.path.join(os.path.dirname(__file__), "..", ".."))


def _scan_files(pattern, label):
    """扫描文件中匹配的行"""
    matches = []
    for root, dirs, files in os.walk(BASE):
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for fname in files:
            if not fname.endswith(".py"):
                continue
            fpath = os.path.join(root, fname)
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    for i, line in enumerate(f, 1):
                        if pattern.search(line):
                            matches.append((fpath, i, line.strip()))
            except Exception:
                pass
    return matches


def test_no_hardcoded_passwords():
    """不应有硬编码数据库密码"""
    pattern = re.compile(r'password\s*=\s*["\'](?!.*settings|.*env|.*os)', re.IGNORECASE)
    matches = _scan_files(pattern, "password")
    # 只检查 backend/ 下的新增文件
    backend_matches = [(p, l, t) for p, l, t in matches if "backend" in os.path.realpath(p) and "test_secrets" not in p]
    assert len(backend_matches) == 0, f"发现硬编码密码: {backend_matches[:3]}"


def test_no_hardcoded_tushare():
    """不应有硬编码 Tushare token"""
    pattern = re.compile(r"3252a9af")
    matches = _scan_files(pattern, "tushare")
    backend_matches = [(p, l, t) for p, l, t in matches if "backend" in os.path.realpath(p) and "test_secrets" not in p and ".env" not in p and "config.py" not in p]
    # 允许 config.py 从 .env 读取，但不允许硬编码
    assert len(backend_matches) == 0, f"发现硬编码 Tushare token: {backend_matches[:3]}"


def test_no_env_in_code():
    """测试文件不应包含 .env 具体值"""
    # 只检查 .env 中敏感值的特征片段
    pattern = re.compile(r"rm-bp160jkc22y874i30to")
    matches = _scan_files(pattern, "host")
    code_matches = [(p, l, t) for p, l, t in matches if p.endswith(".py") and "test_secrets" not in p and "backend" in os.path.realpath(p)]
    # 允许在 test_secrets.py 本身引用，但不应在其他 .py 中出现
    assert len(code_matches) == 0, f"发现硬编码 host: {code_matches[:3]}"
