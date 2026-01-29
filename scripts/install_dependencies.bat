@echo off
REM Agent Zero v8.0 - Phase 5 依赖一键安装脚本 (Windows)

echo ============================================================
echo    Agent Zero v8.0 - Phase 5 依赖安装
echo ============================================================
echo.

REM 检查 Python 是否安装
python --version >nul 2>&1
if errorlevel 1 (
    echo [错误] 未找到 Python，请先安装 Python 3.8+
    pause
    exit /b 1
)

echo [信息] 检测到 Python 版本:
python --version
echo.

REM 升级 pip
echo [步骤 1] 升级 pip...
python -m pip install --upgrade pip
echo.

REM 安装核心依赖
echo [步骤 2] 安装核心依赖...
echo.
python -m pip install pydantic>=2.0.0
python -m pip install PyYAML>=6.0.0
python -m pip install Jinja2>=3.0.0
echo.

REM 询问是否安装 UI 依赖
echo [步骤 3] 是否安装 UI 依赖（Streamlit）？
echo.
set /p install_ui="安装 UI 依赖？(y/n): "

if /i "%install_ui%"=="y" (
    echo.
    echo 安装 UI 依赖...
    python -m pip install streamlit>=1.30.0
    python -m pip install plotly>=5.0.0
    echo.
) else (
    echo.
    echo 跳过 UI 依赖安装
    echo.
)

REM 询问是否安装可选依赖
echo [步骤 4] 是否安装可选依赖？
echo.
set /p install_optional="安装可选依赖？(y/n): "

if /i "%install_optional%"=="y" (
    echo.
    echo 安装可选依赖...
    python -m pip install requests>=2.31.0
    python -m pip install aiohttp>=3.9.0
    python -m pip install loguru>=0.7.0
    echo.
) else (
    echo.
    echo 跳过可选依赖安装
    echo.
)

REM 完成
echo ============================================================
echo    安装完成！
echo ============================================================
echo.
echo 下一步:
echo   1. 运行快速测试: python quick_reference.py
if /i "%install_ui%"=="y" (
    echo   2. 启动 UI 界面: streamlit run app.py
)
echo   3. 查看文档: PHASE5_USAGE_SUMMARY.md
echo.
echo ============================================================

pause
