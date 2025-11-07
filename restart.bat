@echo off
echo ========================================
echo 正在重启八卦时钟程序...
echo ========================================
echo.

REM 关闭所有Python进程（请确认是否需要）
echo [1/3] 检查是否有Python进程正在运行...
tasklist | find /i "python.exe" >nul
if %errorlevel%==0 (
    echo 发现Python进程，建议手动关闭八卦时钟窗口后再运行此脚本
    echo.
    pause
)

REM 清理旧的配置文件（如果存在问题）
echo [2/3] 检查配置文件...
if exist system_settings.json (
    echo 配置文件存在，检查缩放设置...
    findstr /C:"\"default_scale\": 60" system_settings.json >nul
    if %errorlevel%==0 (
        echo 发现错误的缩放设置，正在修复...
        del system_settings.json
        echo 已删除旧配置，程序将生成新的默认配置
    )
)

REM 启动程序
echo [3/3] 启动八卦时钟...
echo.
python bagua_clock.py

if %errorlevel% neq 0 (
    echo.
    echo ========================================
    echo 启动失败！错误代码: %errorlevel%
    echo ========================================
    pause
)
