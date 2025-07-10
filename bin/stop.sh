#!/bin/bash

GREEN='\033[0;32m'
NC='\033[0m' # No Color

# 获取脚本所在目录的上层目录作为项目根目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo -e "${GREEN}🛑 正在停止 Vue + Python 项目...${NC}"

# 停止后端服务
stop_backend() {
    if [ -f .backend_pid ]; then
        PID=$(cat .backend_pid)
        if ps -p $PID > /dev/null; then
            echo "Stopping backend with PID: $PID"
            kill $PID
        else
            echo "Backend process with PID $PID not found. Removing stale PID file."
        fi
        rm -f .backend_pid
    else
        echo "No backend PID file found, skipping backend stop."
    fi
}

# 停止前端服务
stop_frontend() {
    if [ -f .frontend_pid ]; then
        PID=$(cat .frontend_pid)
        if ps -p $PID > /dev/null; then
            echo "Stopping frontend with PID: $PID"
            kill $PID
        else
            echo "Frontend process with PID $PID not found. Removing stale PID file."
        fi
        rm -f .frontend_pid
    else
        echo "No frontend PID file found, skipping frontend stop."
    fi
}

# 执行停止流程
stop_backend
stop_frontend

echo -e "${GREEN}✅ 服务已停止！${NC}"
