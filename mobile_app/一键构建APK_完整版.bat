@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo 八卦时钟移动版 - 完整构建脚本
echo ========================================
echo.
echo 此脚本会自动检测环境并选择最佳构建方案
echo.

REM 获取脚本所在目录
cd /d "%~dp0"

REM 检查是否在正确的目录
if not exist "main.py" (
    echo ❌ 错误：未找到main.py文件
    echo 请确保在mobile_app目录下运行此脚本
    pause
    exit /b 1
)

echo ✅ 当前目录：%CD%
echo.

REM ========================================
REM 环境检测
REM ========================================
echo [检测] 正在检测环境...
echo.

set HAS_WSL=0
set HAS_BUILDOZER=0
set BUILD_METHOD=0

REM 检测WSL
wsl --version >nul 2>&1
if not errorlevel 1 (
    set HAS_WSL=1
    echo ✅ WSL已安装
) else (
    echo ❌ WSL未安装
)

REM 检测buildozer（在WSL中）
if !HAS_WSL! equ 1 (
    wsl bash -c "command -v buildozer" >nul 2>&1
    if not errorlevel 1 (
        set HAS_BUILDOZER=1
        echo ✅ Buildozer已安装（WSL中）
    ) else (
        echo ⚠️  Buildozer未安装（WSL中）
    )
)

echo.

REM ========================================
REM 选择构建方案
REM ========================================
if !HAS_WSL! equ 0 (
    echo ========================================
    echo ⚠️  未检测到WSL环境
    echo ========================================
    echo.
    echo 推荐方案：
    echo.
    echo [方案1] GitHub Actions自动构建（最简单）
    echo   无需本地环境，完全免费
    echo   运行：智能构建助手.bat 选择方案1
    echo.
    echo [方案2] 手动安装WSL
    echo   运行：手动启用WSL.bat（需要管理员权限）
    echo   然后重启电脑，从Microsoft Store安装Ubuntu
    echo.
    echo [方案3] 使用虚拟机
    echo   安装VirtualBox + Ubuntu，在虚拟机中构建
    echo.
    echo 详细说明请查看：
    echo   - GitHub Actions构建指南.md
    echo   - WSL安装指南.md
    echo.
    pause
    exit /b 1
)

REM ========================================
REM WSL构建流程
REM ========================================
echo ========================================
echo 开始WSL构建流程
echo ========================================
echo.

REM 步骤1：复制模块
echo [1/4] 复制项目模块...
if exist "copy_modules.py" (
    python copy_modules.py
    if errorlevel 1 (
        echo ⚠️  警告：模块复制可能有问题
    ) else (
        echo ✅ 模块复制完成
    )
) else (
    echo ⚠️  未找到copy_modules.py，跳过
)
echo.

REM 步骤2：检查buildozer
echo [2/4] 检查buildozer...
if !HAS_BUILDOZER! equ 0 (
    echo ⚠️  Buildozer未安装，正在安装...
    echo 这可能需要几分钟...
    wsl bash -c "sudo apt-get update && sudo apt-get install -y python3-pip && pip3 install buildozer"
    if errorlevel 1 (
        echo ❌ Buildozer安装失败
        echo 请手动在WSL中安装：pip3 install buildozer
        pause
        exit /b 1
    )
    echo ✅ Buildozer安装完成
) else (
    echo ✅ Buildozer已安装
)
echo.

REM 步骤3：检查buildozer.spec
echo [3/4] 检查配置文件...
if not exist "buildozer.spec" (
    echo ❌ 错误：未找到buildozer.spec文件
    pause
    exit /b 1
)
echo ✅ buildozer.spec文件存在
echo.

REM 步骤4：选择构建类型
echo [4/4] 选择构建类型...
echo.
echo 1. Debug版本 ^(调试版，适合测试^)
echo 2. Release版本 ^(发布版，适合正式使用^)
echo.
set /p build_type="请输入选择 (1或2，默认1): "

if "%build_type%"=="" set build_type=1

REM 获取WSL路径
for /f "tokens=*" %%p in ('wsl wslpath -u "%CD%"') do set WSL_DIR=%%p

REM 执行构建
echo.
echo ========================================
echo 开始构建APK
echo ========================================
echo.
echo [重要提示]
echo - 首次构建需要下载大量依赖 ^(约500MB-1GB^)
echo - 可能需要10-30分钟，请耐心等待
echo - 请确保网络连接正常
echo - 构建过程中请勿关闭此窗口
echo.

if exist "build_android.sh" (
    echo 使用构建脚本...
    if "%build_type%"=="2" (
        wsl bash -c "cd '!WSL_DIR!' && bash -c 'BUILD_TYPE=release bash build_android.sh'"
    ) else (
        wsl bash -c "cd '!WSL_DIR!' && bash build_android.sh"
    )
) else (
    echo 直接使用buildozer...
    if "%build_type%"=="2" (
        wsl bash -c "cd '!WSL_DIR!' && buildozer android release"
    ) else (
        wsl bash -c "cd '!WSL_DIR!' && buildozer android debug"
    )
)

set build_result=!errorlevel!

if !build_result! neq 0 (
    echo.
    echo ========================================
    echo ❌ 构建失败
    echo ========================================
    echo.
    echo 常见问题解决：
    echo.
    echo 1. Android SDK未安装
    echo    在WSL中设置：export ANDROIDSDK=~/Android/Sdk
    echo.
    echo 2. NDK未安装
    echo    通过Android Studio安装NDK
    echo.
    echo 3. Java未安装
    echo    在WSL中运行：sudo apt-get install openjdk-11-jdk
    echo.
    echo 4. 网络问题
    echo    检查网络连接，或使用代理
    echo.
    echo 详细说明请查看：WSL构建说明.md
    echo.
    pause
    exit /b 1
)

REM ========================================
REM 构建成功
REM ========================================
echo.
echo ========================================
echo ✅ 构建成功！
echo ========================================
echo.

REM 查找APK文件
set apk_found=0
if exist "bin\*.apk" (
    echo 📦 找到APK文件：
    for %%f in (bin\*.apk) do (
        echo    %%f
        set apk_found=1
        for %%s in ("%%f") do (
            echo    文件大小：%%~zs 字节
        )
    )
    echo.
    
    echo ========================================
    echo 📱 安装说明
    echo ========================================
    echo.
    echo 方法1：USB安装
    echo   1. 启用手机"开发者选项"和"USB调试"
    echo   2. 连接手机到电脑
    echo   3. 运行：adb install bin\app-debug.apk
    echo.
    echo 方法2：直接传输
    echo   1. 将APK文件复制到手机
    echo   2. 在手机上点击安装
    echo   3. 允许"未知来源"安装
    echo.
    
    set /p open_bin="是否打开bin目录？(Y/N，默认N): "
    if /i "!open_bin!"=="Y" (
        explorer bin
    )
) else (
    echo ⚠️  警告：未在bin目录找到APK文件
    echo 请检查构建日志
)

echo.
echo ========================================
echo 构建完成！
echo ========================================
echo.

pause

