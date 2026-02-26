#!/bin/bash

GREEN='\033[0;32m'
NC='\033[0m' # No Color

# 获取脚本所在目录的上层目录作为项目根目录
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Script directory: $SCRIPT_DIR"
echo "Project root: $PROJECT_ROOT"

echo -e "${GREEN}🚀 正在启动 Vue + Python 项目...${NC}"

# 启动后端 Python 应用
start_backend() {
    APP_NAME="my_stock_app"
    MAIN_PY="$PROJECT_ROOT/stock/main.py"  # 使用 PROJECT_ROOT 变量
    LOG_FILE="${APP_NAME}.log"

    # 检查是否已经运行
    PID=$(ps -ef | grep "$MAIN_PY" | grep -v "grep" | awk '{print $2}')
    if [ -n "$PID" ]; then
        echo "$APP_NAME is already running (PID: $PID)"
        exit 1
    fi

    # 启动应用并记录日志
    nohup python3.11 "$MAIN_PY" > "$LOG_FILE" 2>&1 &
    echo $! > "$PROJECT_ROOT/.backend_pid"
    echo "$APP_NAME started with PID: $!"
}


# 启动前端 Vue 开发服务器
start_frontend() {
    echo -e "${GREEN}🌐 正在启动 Vue 前端开发服务器...${NC}"
    cd "$PROJECT_ROOT/frontend" || exit

    npm run build

    rm -fr /data/html/*
    cp -r dist/* /data/html/
    ls -al /data/html/

    # 启动前端服务并记录 PID
    # npm run serve > frontend.log 2>&1 &
    # FRONTEND_PID=$!
    # echo $FRONTEND_PID > "$PROJECT_ROOT/.frontend_pid"
    # echo "Vue frontend started with PID: $FRONTEND_PID"
}

# 清理旧的进程记录
clean_up() {
    rm -f "$PROJECT_ROOT/.backend_pid" "$PROJECT_ROOT/.frontend_pid"
}

# 执行清理和启动
clean_up
start_backend
#start_frontend

echo -e "${GREEN}✅ 服务启动完成！${NC}"
