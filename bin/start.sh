#!/bin/bash

# 应用名称
APP_NAME="my_stock_app"
# Python应用入口文件
# 修改 MAIN_PY 为基于 start.sh 所在目录的相对路径
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
MAIN_PY="$SCRIPT_DIR/../main.py"
# 日志输出文件
LOG_FILE="${APP_NAME}.log"

# 检查是否已经运行
PID=$(ps -ef | grep "$MAIN_PY" | grep -v "grep" | awk '{print $2}')
if [ -n "$PID" ]; then
  echo "$APP_NAME is already running (PID: $PID)"
  exit 1
fi

# 启动应用并记录日志
nohup python3.11 "$MAIN_PY" > "$LOG_FILE" 2>&1 &
echo "$APP_NAME started with PID: $!"

