@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

REM 错误处理：确保任何错误都会显示
set "ERROR_OCCURRED=0"

echo.
echo ========================================
echo    🚀 一键生成 APK
echo    八卦时钟移动版 - 全自动构建
echo ========================================
echo.

REM 获取脚本所在目录
cd /d "%~dp0" 2>nul
if errorlevel 1 (
    echo ❌ 错误：无法切换到脚本目录
    pause
    exit /b 1
)

REM 检查是否在正确的目录
if not exist "main.py" (
    echo ❌ 错误：未找到 main.py 文件
    echo 当前目录：%CD%
    echo 请确保在 mobile_app 目录下运行此脚本
    echo.
    pause
    exit /b 1
)

echo ✅ 当前目录：%CD%
echo.

REM ========================================
REM 环境检测
REM ========================================
echo [1/6] 检测环境...
echo.

set HAS_WSL=0
set HAS_BUILDOZER=0
set HAS_SDK_CONFIG=0
set NEED_CONFIG=0

REM 检测 WSL
echo 正在检测 WSL...
wsl --version >nul 2>&1
if errorlevel 1 (
    echo ❌ WSL 未安装
    echo.
    echo 需要安装 WSL 才能构建 APK
    echo 请运行：wsl --install
    echo 或使用 GitHub Actions 自动构建（无需本地环境）
    echo.
    pause
    exit /b 1
)
set HAS_WSL=1
echo ✅ WSL 已安装

REM 检测 buildozer
echo 正在检测 Buildozer...
wsl bash -c "export PATH=\$HOME/.local/bin:\$PATH; if command -v buildozer >/dev/null 2>&1; then exit 0; elif python3 -m buildozer --version >/dev/null 2>&1; then exit 0; else exit 1; fi" 2>nul
if errorlevel 1 (
    echo ⚠️  Buildozer 未安装（将自动安装）
    set HAS_BUILDOZER=0
) else (
    set HAS_BUILDOZER=1
    echo ✅ Buildozer 已安装
)

REM 检测 Android SDK 配置
if exist "android_sdk_config.txt" (
    set HAS_SDK_CONFIG=1
    echo ✅ Android SDK 已配置
    for /f "tokens=2 delims==" %%a in ('findstr "^ANDROID_SDK_WSL=" android_sdk_config.txt') do (
        set ANDROID_SDK_WSL=%%a
        set ANDROID_SDK_WSL=!ANDROID_SDK_WSL:"=!
        set ANDROID_SDK_WSL=!ANDROID_SDK_WSL:'=!
    )
) else (
    echo ⚠️  Android SDK 未配置（将尝试自动检测）
    set NEED_CONFIG=1
)

echo.

REM ========================================
REM 自动配置 Android SDK（如果需要）
REM ========================================
if !NEED_CONFIG! equ 1 (
    echo [2/6] 自动配置 Android SDK...
    echo.
    
    REM 尝试自动检测 Windows SDK 路径
    set ANDROID_SDK_WIN=
    
    if defined ANDROID_HOME (
        set ANDROID_SDK_WIN=!ANDROID_HOME!
    ) else if defined ANDROID_SDK_ROOT (
        set ANDROID_SDK_WIN=!ANDROID_SDK_ROOT!
    ) else if exist "%LOCALAPPDATA%\Android\Sdk" (
        set ANDROID_SDK_WIN=%LOCALAPPDATA%\Android\Sdk
    ) else if exist "%USERPROFILE%\AppData\Local\Android\Sdk" (
        set ANDROID_SDK_WIN=%USERPROFILE%\AppData\Local\Android\Sdk
    )
    
    if defined ANDROID_SDK_WIN (
        echo ✅ 自动检测到 Android SDK：!ANDROID_SDK_WIN!
        
        REM 转换为 WSL 路径
        set ANDROID_SDK_WSL=!ANDROID_SDK_WIN!
        set ANDROID_SDK_WSL=!ANDROID_SDK_WSL:C:\=/mnt/c/!
        set ANDROID_SDK_WSL=!ANDROID_SDK_WSL:D:\=/mnt/d/!
        set ANDROID_SDK_WSL=!ANDROID_SDK_WSL:E:\=/mnt/e/!
        set ANDROID_SDK_WSL=!ANDROID_SDK_WSL:F:\=/mnt/f/!
        set ANDROID_SDK_WSL=!ANDROID_SDK_WSL:\=/!
        
        REM 验证 WSL 路径
        echo 正在验证 WSL 路径...
        wsl bash -c "if [ -d '!ANDROID_SDK_WSL!' ]; then exit 0; else exit 1; fi" 2>nul
        if errorlevel 1 (
            echo ⚠️  WSL 无法访问该路径，跳过自动配置
            echo 建议运行：配置AndroidSDK.bat
        ) else (
            echo ✅ WSL 路径验证通过：!ANDROID_SDK_WSL!
            
            REM 创建配置文件
            (
                echo # Android SDK 路径配置（自动生成）
                echo # Windows 路径：!ANDROID_SDK_WIN!
                echo ANDROID_SDK_WIN=!ANDROID_SDK_WIN!
                echo ANDROID_SDK_WSL=!ANDROID_SDK_WSL!
            ) > "android_sdk_config.txt"
            
            set HAS_SDK_CONFIG=1
            echo ✅ 已自动配置 Android SDK
        )
    ) else (
        echo ⚠️  无法自动检测 Android SDK 路径
        echo 建议运行：配置AndroidSDK.bat
        echo.
        echo 或继续构建（buildozer 可能会自动下载 SDK）
        set /p continue_anyway="是否继续？(Y/N，默认Y): "
        if /i not "!continue_anyway!"=="Y" if "!continue_anyway!" neq "" (
            echo 构建已取消
            pause
            exit /b 0
        )
    )
    echo.
)

REM ========================================
REM 安装 buildozer（如果需要）
REM ========================================
if !HAS_BUILDOZER! equ 0 (
    echo [3/6] 安装 Buildozer...
    echo.
    echo 这可能需要几分钟，请耐心等待...
    echo.
    
    echo 正在更新软件包列表...
    wsl bash -c "sudo apt-get update" 2>&1
    if errorlevel 1 (
        echo ⚠️  警告：软件包更新失败，继续尝试安装...
    )
    
    echo 正在安装依赖包...
    wsl bash -c "sudo apt-get install -y python3-pip python3-dev build-essential" 2>&1
    if errorlevel 1 (
        echo ❌ 依赖包安装失败
        echo.
        echo 请手动在 WSL 中运行：
        echo   sudo apt-get update
        echo   sudo apt-get install -y python3-pip python3-dev build-essential
        echo.
        pause
        exit /b 1
    )
    
    echo 正在安装 Buildozer 和 Cython...
    wsl bash -c "python3 -m pip install --break-system-packages buildozer cython" 2>&1
    
    if errorlevel 1 (
        echo ❌ Buildozer 安装失败
        echo.
        echo 请手动在 WSL 中运行：
        echo   python3 -m pip install --break-system-packages buildozer cython
        echo.
        pause
        exit /b 1
    )
    
    echo ✅ Buildozer 安装完成
    echo.
) else (
    echo [3/6] 跳过 Buildozer 安装（已安装）
    echo.
)

REM ========================================
REM 复制项目模块
REM ========================================
echo [4/6] 复制项目模块...
echo.

if exist "copy_modules.py" (
    echo 正在运行 copy_modules.py...
    python copy_modules.py
    if errorlevel 1 (
        echo ⚠️  警告：模块复制可能有问题，但继续构建...
    ) else (
        echo ✅ 模块复制完成
    )
) else (
    echo ⚠️  未找到 copy_modules.py，跳过
)
echo.

REM ========================================
REM 选择构建类型
REM ========================================
echo [5/6] 选择构建类型...
echo.
echo 1. Debug 版本（调试版，适合测试，构建更快）
echo 2. Release 版本（发布版，适合正式使用，需要签名）
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
REM 构建 APK
REM ========================================
echo [6/6] 开始构建 APK...
echo.
echo ========================================
echo 构建进行中...
echo ========================================
echo.
echo [重要提示]
echo - 首次构建需要下载大量依赖（约 500MB-1GB）
echo - 可能需要 10-30 分钟，请耐心等待
echo - 请确保网络连接正常
echo - 构建过程中请勿关闭此窗口
echo.
echo 正在构建，请稍候...
echo.

REM 获取 WSL 路径
echo 正在转换路径...
set WSL_DIR=
for /f "tokens=*" %%p in ('wsl wslpath -u "%CD%" 2^>nul') do set WSL_DIR=%%p
if not defined WSL_DIR (
    echo ❌ 错误：无法转换路径到 WSL 格式
    echo 当前路径：%CD%
    echo.
    echo 请尝试：
    echo 1. 确保路径不包含特殊字符
    echo 2. 检查 WSL 是否正常工作：wsl echo test
    echo.
    pause
    exit /b 1
)
echo ✅ 路径转换成功：!WSL_DIR!

REM 设置环境变量
set WSL_ENV_VARS=
if defined ANDROID_SDK_WSL (
    set WSL_ENV_VARS=export ANDROIDSDK="!ANDROID_SDK_WSL!" && export ANDROID_HOME="!ANDROID_SDK_WSL!" && export ANDROID_SDK_ROOT="!ANDROID_SDK_WSL!" && 
)

REM 执行构建
set BUILD_SUCCESS=0
echo 正在执行构建命令...
echo.

REM 构建命令（移除输出重定向以便看到错误）
if exist "build_android.sh" (
    REM 使用构建脚本
    echo 使用构建脚本：build_android.sh
    if "%BUILD_CMD%"=="release" (
        wsl bash -c "!WSL_ENV_VARS!export PATH=\$HOME/.local/bin:\$PATH && cd '!WSL_DIR!' && bash -c 'BUILD_TYPE=release bash build_android.sh'"
    ) else (
        wsl bash -c "!WSL_ENV_VARS!export PATH=\$HOME/.local/bin:\$PATH && cd '!WSL_DIR!' && bash build_android.sh"
    )
) else (
    REM 直接使用 buildozer
    echo 直接使用 buildozer 命令
    if "%BUILD_CMD%"=="release" (
        wsl bash -c "!WSL_ENV_VARS!export PATH=\$HOME/.local/bin:\$PATH && cd '!WSL_DIR!' && buildozer android release"
    ) else (
        wsl bash -c "!WSL_ENV_VARS!export PATH=\$HOME/.local/bin:\$PATH && cd '!WSL_DIR!' && buildozer android debug"
    )
)

set BUILD_EXIT_CODE=%ERRORLEVEL%
if %BUILD_EXIT_CODE% equ 0 (
    set BUILD_SUCCESS=1
) else (
    set BUILD_SUCCESS=0
    echo.
    echo ❌ 构建过程返回错误代码：%BUILD_EXIT_CODE%
)

echo.
echo ========================================

REM ========================================
REM 构建结果
REM ========================================
if !BUILD_SUCCESS! equ 1 (
    echo ✅ 构建成功！
    echo ========================================
    echo.
    
    REM 查找 APK 文件
    set APK_FOUND=0
    if exist "bin\*.apk" (
        echo 📦 找到 APK 文件：
        echo.
        for %%f in (bin\*.apk) do (
            echo   📱 %%f
            for %%s in ("%%f") do (
                set /a size_mb=%%~zs/1024/1024
                echo     文件大小：!size_mb! MB
            )
            set APK_FOUND=1
        )
        echo.
        
        echo ========================================
        echo 📱 安装说明
        echo ========================================
        echo.
        echo 方法1：USB 安装（推荐）
        echo   1. 启用手机"开发者选项"和"USB 调试"
        echo   2. 连接手机到电脑
        echo   3. 运行：adb install bin\*.apk
        echo.
        echo 方法2：直接传输
        echo   1. 将 APK 文件复制到手机
        echo   2. 在手机上点击安装
        echo   3. 允许"未知来源"安装
        echo.
        
        set /p open_bin="是否打开 bin 目录？(Y/N，默认 Y): "
        if /i "!open_bin!"=="Y" if "!open_bin!" neq "" (
            explorer bin
        ) else if "!open_bin!"=="" (
            explorer bin
        )
    ) else (
        echo ⚠️  警告：未在 bin 目录找到 APK 文件
        echo 请检查构建日志
    )
) else (
    echo ❌ 构建失败
    echo ========================================
    echo.
    echo 常见问题解决：
    echo.
    echo 1. Android SDK 未配置
    echo    运行：配置AndroidSDK.bat
    echo.
    echo 2. Java 未安装
    echo    在 WSL 中运行：sudo apt-get install openjdk-17-jdk
    echo.
    echo 3. 网络问题
    echo    检查网络连接，或使用代理
    echo.
    echo 4. 查看详细日志
    echo    检查 .buildozer 目录中的日志文件
    echo.
    echo 详细说明请查看：AndroidSDK配置说明.md
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo 构建完成！
echo ========================================
echo.

pause

