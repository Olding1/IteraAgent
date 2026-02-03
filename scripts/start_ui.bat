@echo off
REM Streamlit UI 启动脚本 (Windows)

echo ============================================================
echo    启动 IteraAgent Streamlit UI
echo ============================================================
echo.

REM 检查 Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python
    pause
    exit /b 1
)

REM 检查 streamlit 是否安装
python -c "import streamlit" >nul 2>&1
if errorlevel 1 (
    echo [错误] Streamlit 未安装
    echo.
    echo 请先运行: python install_dependencies.py
    echo 或手动安装: pip install streamlit plotly
    pause
    exit /b 1
)

echo [信息] 正在启动 Streamlit UI...
echo.
echo 浏览器将自动打开，或手动访问:
echo   http://localhost:8501
echo.
echo 按 Ctrl+C 停止服务器
echo.
echo ============================================================
echo.

REM 使用 python -m 方式启动（避免 PATH 问题）
python -m streamlit run app.py

pause
