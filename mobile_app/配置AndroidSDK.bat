@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo 配置 Android SDK 路径
echo ========================================
echo.
echo 此脚本将帮助您配置 Android SDK 路径
echo 用于在 WSL 环境中构建 Android APK
echo.

REM 获取脚本所在目录
cd /d "%~dp0"

REM ========================================
REM 检测 Android SDK 路径（Windows）
REM ========================================
echo [步骤1] 检测 Android SDK 路径...
echo.

set ANDROID_SDK_WIN=
set SDK_FOUND=0

REM 方法1：从环境变量获取
if defined ANDROID_HOME (
    set ANDROID_SDK_WIN=%ANDROID_HOME%
    set SDK_FOUND=1
    echo ✅ 从 ANDROID_HOME 环境变量找到：%ANDROID_SDK_WIN%
) else if defined ANDROID_SDK_ROOT (
    set ANDROID_SDK_WIN=%ANDROID_SDK_ROOT%
    set SDK_FOUND=1
    echo ✅ 从 ANDROID_SDK_ROOT 环境变量找到：%ANDROID_SDK_WIN%
)

REM 方法2：检查常见安装路径
if !SDK_FOUND! equ 0 (
    echo 正在检查常见安装路径...
    
    if exist "%LOCALAPPDATA%\Android\Sdk" (
        set ANDROID_SDK_WIN=%LOCALAPPDATA%\Android\Sdk
        set SDK_FOUND=1
        echo ✅ 找到 Android SDK：%ANDROID_SDK_WIN%
    ) else if exist "%USERPROFILE%\AppData\Local\Android\Sdk" (
        set ANDROID_SDK_WIN=%USERPROFILE%\AppData\Local\Android\Sdk
        set SDK_FOUND=1
        echo ✅ 找到 Android SDK：%ANDROID_SDK_WIN%
    )
)

REM 方法3：让用户手动输入
if !SDK_FOUND! equ 0 (
    echo.
    echo ⚠️  未自动检测到 Android SDK 路径
    echo.
    echo 请手动输入 Android SDK 路径
    echo 通常路径为：C:\Users\您的用户名\AppData\Local\Android\Sdk
    echo 或在 Android Studio 中查看：
    echo   File ^> Settings ^> Appearance ^& Behavior ^> System Settings ^> Android SDK
    echo.
    set /p ANDROID_SDK_WIN="请输入 Android SDK 路径（Windows路径）: "
    
    if "!ANDROID_SDK_WIN!"=="" (
        echo ❌ 未输入 SDK 路径，退出
        pause
        exit /b 1
    )
    
    if not exist "!ANDROID_SDK_WIN!" (
        echo ❌ 路径不存在：!ANDROID_SDK_WIN!
        pause
        exit /b 1
    )
    
    set SDK_FOUND=1
)

REM 验证 SDK 路径
if !SDK_FOUND! equ 1 (
    if not exist "!ANDROID_SDK_WIN!\platform-tools\adb.exe" (
        echo ⚠️  警告：SDK 路径可能不正确（未找到 adb.exe）
        echo 但继续配置...
    ) else (
        echo ✅ SDK 路径验证通过
    )
)

echo.
echo Windows 路径：!ANDROID_SDK_WIN!
echo.

REM ========================================
REM 转换为 WSL 路径
REM ========================================
echo [步骤2] 转换为 WSL 路径...
echo.

REM 将 Windows 路径转换为 WSL 路径
set ANDROID_SDK_WSL=!ANDROID_SDK_WIN!
set ANDROID_SDK_WSL=!ANDROID_SDK_WSL:C:\=/mnt/c/!
set ANDROID_SDK_WSL=!ANDROID_SDK_WSL:D:\=/mnt/d/!
set ANDROID_SDK_WSL=!ANDROID_SDK_WSL:E:\=/mnt/e/!
set ANDROID_SDK_WSL=!ANDROID_SDK_WSL:F:\=/mnt/f/!
set ANDROID_SDK_WSL=!ANDROID_SDK_WSL:\=/!

echo WSL 路径：!ANDROID_SDK_WSL!
echo.

REM ========================================
REM 检测 WSL
REM ========================================
echo [步骤3] 检测 WSL 环境...
echo.

wsl --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 未检测到 WSL 环境
    echo.
    echo 请先安装 WSL：
    echo   1. 以管理员身份运行 PowerShell
    echo   2. 执行：wsl --install
    echo   3. 重启电脑后从 Microsoft Store 安装 Ubuntu
    echo.
    pause
    exit /b 1
)

echo ✅ WSL 已安装
echo.

REM ========================================
REM 在 WSL 中验证路径
REM ========================================
echo [步骤4] 验证 WSL 路径...
echo.

wsl bash -c "if [ -d '!ANDROID_SDK_WSL!' ]; then echo '✅ WSL 路径存在且可访问'; ls -ld '!ANDROID_SDK_WSL!' | head -1; else echo '❌ WSL 路径不存在或不可访问'; exit 1; fi"
if errorlevel 1 (
    echo.
    echo ⚠️  警告：WSL 无法访问该路径
    echo 可能原因：
    echo   1. 路径转换不正确
    echo   2. WSL 未正确安装
    echo   3. 路径包含特殊字符
    echo.
    echo 请手动在 WSL 中验证路径：
    echo   wsl
    echo   ls !ANDROID_SDK_WSL!
    echo.
    pause
    exit /b 1
)

echo.

REM ========================================
REM 配置 WSL 环境变量
REM ========================================
echo [步骤5] 配置 WSL 环境变量...
echo.

echo 正在配置 WSL 环境变量...
echo.

REM 创建配置脚本
set CONFIG_SCRIPT=%TEMP%\configure_android_sdk.sh
(
    echo #!/bin/bash
    echo # Android SDK 路径配置
    echo # 此文件由 配置AndroidSDK.bat 自动生成
    echo.
    echo # 设置 Android SDK 路径
    echo export ANDROIDSDK="!ANDROID_SDK_WSL!"
    echo export ANDROID_HOME="!ANDROID_SDK_WSL!"
    echo export ANDROID_SDK_ROOT="!ANDROID_SDK_WSL!"
    echo.
    echo # 添加到 PATH（可选）
    echo export PATH="$ANDROIDSDK/platform-tools:$ANDROIDSDK/tools:$PATH"
) > "%CONFIG_SCRIPT%"

REM 将配置添加到 WSL 的 ~/.bashrc
echo 正在添加到 WSL 的 ~/.bashrc...
wsl bash -c "echo '' >> ~/.bashrc && echo '# Android SDK 配置（由配置AndroidSDK.bat自动添加）' >> ~/.bashrc && echo 'export ANDROIDSDK=\"!ANDROID_SDK_WSL!\"' >> ~/.bashrc && echo 'export ANDROID_HOME=\"$ANDROIDSDK\"' >> ~/.bashrc && echo 'export ANDROID_SDK_ROOT=\"$ANDROIDSDK\"' >> ~/.bashrc && echo 'export PATH=\"$ANDROIDSDK/platform-tools:$ANDROIDSDK/tools:$PATH\"' >> ~/.bashrc"

if errorlevel 1 (
    echo ❌ 配置失败
    pause
    exit /b 1
)

echo ✅ 配置成功
echo.

REM ========================================
REM 验证配置
REM ========================================
echo [步骤6] 验证配置...
echo.

echo 在 WSL 中验证环境变量：
wsl bash -c "source ~/.bashrc && echo 'ANDROIDSDK=' && echo $ANDROIDSDK && echo 'ANDROID_HOME=' && echo $ANDROID_HOME"

if errorlevel 1 (
    echo ⚠️  警告：环境变量可能未正确设置
    echo 请手动在 WSL 中运行：source ~/.bashrc
) else (
    echo ✅ 环境变量配置正确
)

echo.

REM ========================================
REM 创建配置文件
REM ========================================
echo [步骤7] 创建本地配置文件...
echo.

REM 创建 .android_sdk_path 文件供脚本使用
(
    echo # Android SDK 路径配置
    echo # 此文件由 配置AndroidSDK.bat 自动生成
    echo # Windows 路径：!ANDROID_SDK_WIN!
    echo ANDROID_SDK_WIN=!ANDROID_SDK_WIN!
    echo ANDROID_SDK_WSL=!ANDROID_SDK_WSL!
) > "android_sdk_config.txt"

echo ✅ 已创建配置文件：android_sdk_config.txt
echo.

REM ========================================
REM 完成
REM ========================================
echo ========================================
echo ✅ 配置完成！
echo ========================================
echo.
echo 配置信息：
echo   Windows 路径：!ANDROID_SDK_WIN!
echo   WSL 路径：!ANDROID_SDK_WSL!
echo.
echo 使用方法：
echo   1. 在 WSL 中运行构建脚本：build_android.sh
echo   2. 或使用批处理脚本：一键构建APK_完整版.bat
echo.
echo 注意：
echo   - 配置已添加到 WSL 的 ~/.bashrc
echo   - 下次打开 WSL 终端时自动生效
echo   - 如果当前已有 WSL 终端，运行：source ~/.bashrc
echo.
echo 验证配置：
echo   wsl
echo   echo $ANDROIDSDK
echo.
pause

