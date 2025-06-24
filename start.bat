@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo.
echo ========================================
echo 🤖 AI新闻收集器 启动脚本
echo ========================================
echo.

:: 检查Python是否安装
echo 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误: 未找到Python
    echo 请先安装Python 3.7或更高版本
    echo 下载地址: https://www.python.org/downloads/
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version 2^>^&1') do set PYTHON_VERSION=%%i
echo ✅ Python版本: %PYTHON_VERSION%
echo.

:: 检查是否在正确的目录
if not exist "app.py" (
    echo ❌ 错误: 未找到app.py文件
    echo 请确保在正确的项目目录中运行此脚本
    pause
    exit /b 1
)

:: 检查虚拟环境
if exist "venv\Scripts\activate.bat" (
    echo 🔧 发现虚拟环境，正在激活...
    call venv\Scripts\activate.bat
    echo ✅ 虚拟环境已激活
) else (
    echo ⚠️  未发现虚拟环境
    set /p CREATE_VENV="是否创建虚拟环境? (推荐) [Y/n]: "
    if /i "!CREATE_VENV!"=="" set CREATE_VENV=Y
    if /i "!CREATE_VENV!"=="Y" (
        echo 🔧 正在创建虚拟环境...
        python -m venv venv
        if errorlevel 1 (
            echo ❌ 虚拟环境创建失败
            pause
            exit /b 1
        )
        call venv\Scripts\activate.bat
        echo ✅ 虚拟环境创建并激活成功
    )
)
echo.

:: 安装依赖
echo 🔧 检查并安装依赖包...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ 依赖包安装失败
    pause
    exit /b 1
)
echo ✅ 依赖包检查完成
echo.

:: 检查配置文件
if not exist "config.py" (
    if exist "config.example.py" (
        echo 🔧 正在创建配置文件...
        copy "config.example.py" "config.py" >nul
        echo ✅ 配置文件已创建
        echo ⚠️  请编辑 config.py 文件，配置您的API密钥
        echo.
    ) else (
        echo ❌ 错误: 未找到配置文件模板
        pause
        exit /b 1
    )
)

:: 启动应用
echo 🚀 启动AI新闻收集器...
echo ========================================
echo 📱 Web界面: http://localhost:5000
echo 📱 本地访问: http://127.0.0.1:5000
echo ========================================
echo 💡 提示: 按 Ctrl+C 停止应用
echo.

python run.py

echo.
echo 👋 应用已停止
pause