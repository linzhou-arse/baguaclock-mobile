@echo off
chcp 65001 >nul
echo ========================================
echo 安装APK到手机
echo ========================================
echo.

cd /d "%~dp0"

REM 查找APK文件
set apk_file=
if exist "bin\*.apk" (
    for %%f in (bin\*.apk) do (
        set apk_file=%%f
        goto :found
    )
)

:found
if "%apk_file%"=="" (
    echo ❌ 错误：未找到APK文件
    echo 请先运行"一键构建APK.bat"构建APK
    pause
    exit /b 1
)

echo 找到APK文件：%apk_file%
echo.

REM 检查adb
adb version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到adb工具
    echo.
    echo 请安装Android SDK Platform Tools：
    echo 1. 下载：https://developer.android.com/studio/releases/platform-tools
    echo 2. 解压并添加到系统PATH环境变量
    echo.
    pause
    exit /b 1
)

echo ✅ adb工具已找到
echo.

REM 检查设备连接
echo 正在检查设备连接...
adb devices | find "device" >nul 2>&1
if errorlevel 1 (
    echo.
    echo ⚠️  警告：未检测到已连接的Android设备
    echo.
    echo 请确保：
    echo 1. 手机已通过USB连接到电脑
    echo 2. 手机已启用"开发者选项"和"USB调试"
    echo 3. 手机已授权此电脑的USB调试
    echo.
    echo 正在显示设备列表：
    adb devices
    echo.
    pause
    exit /b 1
)

echo ✅ 已检测到Android设备
echo.

REM 安装APK
echo 正在安装APK到手机...
echo.
adb install -r "%apk_file%"

if errorlevel 1 (
    echo.
    echo ❌ 安装失败
    echo.
    echo 可能的原因：
    echo 1. 设备未正确连接
    echo 2. USB调试未启用
    echo 3. 设备未授权此电脑
    echo 4. APK文件已存在且签名不同
    echo.
    echo 尝试卸载旧版本后重新安装...
    adb uninstall com.quanhang.baguaclock
    adb install "%apk_file%"
    
    if errorlevel 1 (
        echo.
        echo ❌ 安装仍然失败
        echo 请检查设备连接和权限设置
        pause
        exit /b 1
    )
)

echo.
echo ========================================
echo ✅ 安装成功！
echo ========================================
echo.
echo APK已成功安装到手机
echo 现在可以在手机上打开"八卦时钟"应用了
echo.
pause

