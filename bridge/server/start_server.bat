@echo off
REM QuantBridge Server 启动脚本 (Windows)
REM 使用方法: 双击运行 或 放入启动文件夹实现开机自启

cd /d %~dp0..\..

REM 检查 Python 环境
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python 未安装或未添加到 PATH
    pause
    exit /b 1
)

REM 安装依赖（首次运行）
pip install fastapi uvicorn[standard] websockets xtquant -q

REM 启动服务（非 Mock 模式）
set XTQUANT_MOCK=false
set BRIDGE_PORT=5101

echo ============================================
echo   QuantBridge Server 启动中...
echo   模式: LIVE (miniQMT)
echo   端口: %BRIDGE_PORT%
echo ============================================

python -m uvicorn server.main:app --host 0.0.0.0 --port %BRIDGE_PORT% --log-level info

pause
