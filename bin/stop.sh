#!/bin/bash

GREEN='\033[0;32m'
NC='\033[0m' # No Color

# 获取脚本所在目录的上层目录作为项目根目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo -e "${GREEN}🛑 正在停止 Vue + Python 项目...${NC}"

# 停止后端服务
stop_backend() {
    PID_FILE="$PROJECT_ROOT/.backend_pid"

    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null; then
            echo "Stopping backend with PID: $PID"
            kill $PID
        else
            echo "Backend process with PID $PID not found. Removing stale PID file."
        fi
        rm -f "$PID_FILE"
    else
        echo "No backend PID file found at $PID_FILE, skipping backend stop."
    fi
}

# 停止前端服务
stop_frontend() {
    PID_FILE="$PROJECT_ROOT/.frontend_pid"

    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if ps -p $PID > /dev/null; then
            echo "Stopping frontend with PID: $PID"
            kill $PID
        else
            echo "Frontend process with PID $PID not found. Removing stale PID file."
        fi
        rm -f "$PID_FILE"
    else
        echo "No frontend PID file found at $PID_FILE, skipping frontend stop."
    fi
}

# 执行停止流程
stop_backend
# stop_frontend

echo -e "${GREEN}✅ 服务已停止！${NC}"
