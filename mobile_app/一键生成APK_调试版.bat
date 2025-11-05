@echo off
chcp 65001
setlocal enabledelayedexpansion

echo.
echo ========================================
echo    🚀 一键生成 APK（调试版）
echo    八卦时钟移动版 - 全自动构建
echo ========================================
echo.
echo [调试模式] 将显示所有执行步骤和错误信息
echo.

REM 获取脚本所在目录
cd /d "%~dp0"
echo [调试] 当前目录：%CD%
echo.

REM 检查是否在正确的目录
if not exist "main.py" (
    echo ❌ 错误：未找到 main.py 文件
    echo 当前目录：%CD%
    echo 请确保在 mobile_app 目录下运行此脚本
    echo.
    pause
    exit /b 1
)

echo ✅ main.py 文件存在
echo.

REM ========================================
REM 检测 WSL
REM ========================================
echo [步骤1] 检测 WSL...
echo 执行命令：wsl --version
wsl --version
if errorlevel 1 (
    echo ❌ WSL 未安装或无法访问
    echo.
    echo 请尝试：
    echo 1. 运行：wsl --install
    echo 2. 检查 WSL 是否已启用
    echo 3. 重启电脑后重试
    echo.
    pause
    exit /b 1
)
echo ✅ WSL 检测通过
echo.

REM ========================================
REM 检测 buildozer
REM ========================================
echo [步骤2] 检测 Buildozer...
echo 执行命令：wsl bash -c "command -v buildozer || python3 -m buildozer --version"
wsl bash -c "export PATH=\$HOME/.local/bin:\$PATH; if command -v buildozer >/dev/null 2>&1; then echo 'buildozer found'; exit 0; elif python3 -m buildozer --version >/dev/null 2>&1; then echo 'buildozer found via python3'; exit 0; else echo 'buildozer not found'; exit 1; fi"
if errorlevel 1 (
    echo ⚠️  Buildozer 未安装
    echo 将在后续步骤中自动安装
) else (
    echo ✅ Buildozer 已安装
)
echo.

REM ========================================
REM 检测 Android SDK
REM ========================================
echo [步骤3] 检测 Android SDK 配置...
if exist "android_sdk_config.txt" (
    echo ✅ 找到配置文件：android_sdk_config.txt
    type android_sdk_config.txt
) else (
    echo ⚠️  未找到配置文件
    echo 将尝试自动检测...
    
    set ANDROID_SDK_WIN=
    if defined ANDROID_HOME (
        set ANDROID_SDK_WIN=!ANDROID_HOME!
        echo 从 ANDROID_HOME 找到：!ANDROID_SDK_WIN!
    ) else if exist "%LOCALAPPDATA%\Android\Sdk" (
        set ANDROID_SDK_WIN=%LOCALAPPDATA%\Android\Sdk
        echo 从默认路径找到：!ANDROID_SDK_WIN!
    )
    
    if defined ANDROID_SDK_WIN (
        echo 尝试转换路径...
        set ANDROID_SDK_WSL=!ANDROID_SDK_WIN!
        set ANDROID_SDK_WSL=!ANDROID_SDK_WSL:C:\=/mnt/c/!
        set ANDROID_SDK_WSL=!ANDROID_SDK_WSL:D:\=/mnt/d/!
        set ANDROID_SDK_WSL=!ANDROID_SDK_WSL:\=/!
        echo WSL 路径：!ANDROID_SDK_WSL!
        
        echo 验证路径...
        wsl bash -c "if [ -d '!ANDROID_SDK_WSL!' ]; then echo '路径存在'; exit 0; else echo '路径不存在'; exit 1; fi"
        if not errorlevel 1 (
            echo ✅ SDK 路径验证通过
        ) else (
            echo ⚠️  SDK 路径验证失败
        )
    )
)
echo.

REM ========================================
REM 转换路径
REM ========================================
echo [步骤4] 转换当前目录路径...
echo 当前 Windows 路径：%CD%
echo 执行命令：wsl wslpath -u "%CD%"
for /f "tokens=*" %%p in ('wsl wslpath -u "%CD%" 2^>^&1') do (
    set WSL_DIR=%%p
    echo WSL 路径：!WSL_DIR!
)
if not defined WSL_DIR (
    echo ❌ 路径转换失败
    echo.
    echo 请尝试：
    echo 1. 检查路径是否包含特殊字符
    echo 2. 运行：wsl echo test 测试 WSL 是否正常
    echo.
    pause
    exit /b 1
)
echo ✅ 路径转换成功
echo.

REM ========================================
REM 选择构建类型
REM ========================================
echo [步骤5] 选择构建类型...
echo.
echo 1. Debug 版本（调试版，适合测试）
echo 2. Release 版本（发布版，适合正式使用）
echo.
set /p build_type="请选择 (1 或 2，默认 1): "
if "%build_type%"=="" set build_type=1
if "%build_type%"=="2" (
    set BUILD_CMD=release
    echo ✅ 已选择：Release 版本
) else (
    set BUILD_CMD=debug
    echo ✅ 已选择：Debug 版本
)
echo.

REM ========================================
REM 执行构建
REM ========================================
echo [步骤6] 开始构建...
echo.
echo ========================================
echo 构建命令将在此处显示
echo ========================================
echo.

REM 设置环境变量
set WSL_ENV_VARS=
if defined ANDROID_SDK_WSL (
    set WSL_ENV_VARS=export ANDROIDSDK="!ANDROID_SDK_WSL!" && export ANDROID_HOME="!ANDROID_SDK_WSL!" && export ANDROID_SDK_ROOT="!ANDROID_SDK_WSL!" && 
    echo 环境变量：!WSL_ENV_VARS!
)

REM 构建命令
set BUILD_CMD_FULL=
if exist "build_android.sh" (
    echo 使用构建脚本：build_android.sh
    if "%BUILD_CMD%"=="release" (
        set BUILD_CMD_FULL=!WSL_ENV_VARS!export PATH=\$HOME/.local/bin:\$PATH && cd '!WSL_DIR!' && bash -c 'BUILD_TYPE=release bash build_android.sh'
    ) else (
        set BUILD_CMD_FULL=!WSL_ENV_VARS!export PATH=\$HOME/.local/bin:\$PATH && cd '!WSL_DIR!' && bash build_android.sh
    )
) else (
    echo 直接使用 buildozer
    if "%BUILD_CMD%"=="release" (
        set BUILD_CMD_FULL=!WSL_ENV_VARS!export PATH=\$HOME/.local/bin:\$PATH && cd '!WSL_DIR!' && buildozer android release
    ) else (
        set BUILD_CMD_FULL=!WSL_ENV_VARS!export PATH=\$HOME/.local/bin:\$PATH && cd '!WSL_DIR!' && buildozer android debug
    )
)

echo.
echo 执行命令：
echo wsl bash -c "!BUILD_CMD_FULL!"
echo.
echo 开始构建...
echo.

wsl bash -c "!BUILD_CMD_FULL!"

set BUILD_RESULT=%ERRORLEVEL%
echo.
echo ========================================
if %BUILD_RESULT% equ 0 (
    echo ✅ 构建成功！
    echo ========================================
    echo.
    
    if exist "bin\*.apk" (
        echo 📦 找到 APK 文件：
        for %%f in (bin\*.apk) do (
            echo   %%f
        )
        explorer bin
    ) else (
        echo ⚠️  未找到 APK 文件
    )
) else (
    echo ❌ 构建失败（错误代码：%BUILD_RESULT%）
    echo ========================================
    echo.
    echo 请检查上面的错误信息
)

echo.
pause

