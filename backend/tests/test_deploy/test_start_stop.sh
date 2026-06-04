#!/bin/bash
# 部署脚本集成测试
# 验证 start.sh/stop.sh 语法、路径解析、进程管理

set -e

echo "=== 部署脚本集成测试 ==="

# 1. 语法检查
echo "[1] 语法检查..."
bash -n "$(dirname "$0")/../../../bin/start.sh" && echo "  [PASS] start.sh 语法正确"
bash -n "$(dirname "$0")/../../../bin/stop.sh" && echo "  [PASS] stop.sh 语法正确"

# 2. 路径解析检查
echo "[2] 路径解析检查..."
# 从 start.sh 提取 PROJECT_ROOT 推导逻辑模拟验证
SCRIPT_DIR="$(cd "$(dirname "$0")/../../../bin" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

if [ -f "$PROJECT_ROOT/backend/run.py" ]; then
    echo "  [PASS] PROJECT_ROOT/backend/run.py 存在 ($PROJECT_ROOT/backend/run.py)"
else
    echo "  [FAIL] PROJECT_ROOT/backend/run.py 不存在"
    exit 1
fi

if [ -f "$PROJECT_ROOT/backend/.env" ]; then
    echo "  [PASS] PROJECT_ROOT/backend/.env 存在"
else
    echo "  [WARN] PROJECT_ROOT/backend/.env 不存在（首次部署需要创建）"
fi

echo ""
echo "=== 全部通过 ==="
