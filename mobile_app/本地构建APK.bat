@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo 八卦时钟移动版 - 本地构建APK
echo ========================================
echo.
echo 此脚本将使用您的Android Studio SDK本地构建APK
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
REM 检测Android Studio SDK路径
REM ========================================
echo [检测] 正在检测Android Studio SDK...
echo.

set ANDROID_SDK=
set SDK_FOUND=0

REM 方法1：从环境变量获取
if defined ANDROID_HOME (
    set ANDROID_SDK=%ANDROID_HOME%
    set SDK_FOUND=1
    echo ✅ 从ANDROID_HOME环境变量找到：%ANDROID_SDK%
) else if defined ANDROID_SDK_ROOT (
    set ANDROID_SDK=%ANDROID_SDK_ROOT%
    set SDK_FOUND=1
    echo ✅ 从ANDROID_SDK_ROOT环境变量找到：%ANDROID_SDK%
)

REM 方法2：检查常见安装路径
if !SDK_FOUND! equ 0 (
    echo 正在检查常见安装路径...
    
    REM 检查用户目录下的Android SDK
    if exist "%LOCALAPPDATA%\Android\Sdk" (
        set ANDROID_SDK=%LOCALAPPDATA%\Android\Sdk
        set SDK_FOUND=1
        echo ✅ 找到Android SDK：%ANDROID_SDK%
    ) else if exist "%USERPROFILE%\AppData\Local\Android\Sdk" (
        set ANDROID_SDK=%USERPROFILE%\AppData\Local\Android\Sdk
        set SDK_FOUND=1
        echo ✅ 找到Android SDK：%ANDROID_SDK%
    )
)

REM 方法3：让用户手动输入
if !SDK_FOUND! equ 0 (
    echo.
    echo ⚠️  未自动检测到Android SDK路径
    echo.
    echo 请手动输入Android SDK路径
    echo 通常路径为：C:\Users\您的用户名\AppData\Local\Android\Sdk
    echo 或在Android Studio中查看：File ^> Settings ^> Appearance ^& Behavior ^> System Settings ^> Android SDK
    echo.
    set /p ANDROID_SDK="请输入Android SDK路径: "
    
    if "!ANDROID_SDK!"=="" (
        echo ❌ 未输入SDK路径，退出
        pause
        exit /b 1
    )
    
    if not exist "!ANDROID_SDK!" (
        echo ❌ 路径不存在：!ANDROID_SDK!
        pause
        exit /b 1
    )
    
    set SDK_FOUND=1
)

REM 验证SDK路径
if !SDK_FOUND! equ 1 (
    if not exist "!ANDROID_SDK!\platform-tools\adb.exe" (
        echo ⚠️  警告：SDK路径可能不正确（未找到adb.exe）
    ) else (
        echo ✅ SDK路径验证通过
    )
)

echo.
echo ========================================
echo 环境配置
echo ========================================
echo.

REM 设置环境变量
set ANDROIDSDK=!ANDROID_SDK!
set ANDROID_HOME=!ANDROID_SDK!
set ANDROID_SDK_ROOT=!ANDROID_SDK!

echo Android SDK路径：!ANDROID_SDK!
echo.

REM 检查Java
echo [检测] 检查Java环境...
where java >nul 2>&1
if errorlevel 1 (
    echo ⚠️  警告：未找到Java，buildozer可能需要Java 17
    echo 建议安装：https://adoptium.net/
) else (
    java -version
    echo ✅ Java已安装
)
echo.

REM 检查Python
echo [检测] 检查Python环境...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ 错误：未找到Python
    echo 请安装Python 3.9+：https://www.python.org/downloads/
    pause
    exit /b 1
)
python --version
echo ✅ Python已安装
echo.

REM 步骤1：复制模块
echo ========================================
echo [1/4] 复制项目模块
echo ========================================
echo.
if exist "copy_modules.py" (
    python copy_modules.py
    if errorlevel 1 (
        echo ⚠️  警告：模块复制可能有问题，但继续构建
    ) else (
        echo ✅ 模块复制完成
    )
) else (
    echo ⚠️  未找到copy_modules.py，跳过
)
echo.

REM 步骤2：检查buildozer
echo ========================================
echo [2/4] 检查buildozer
echo ========================================
echo.
python -c "import buildozer" >nul 2>&1
if errorlevel 1 (
    echo ⚠️  Buildozer未安装，正在安装...
    echo 这可能需要几分钟...
    pip install buildozer
    if errorlevel 1 (
        echo ❌ Buildozer安装失败
        echo 请手动运行：pip install buildozer
        pause
        exit /b 1
    )
    echo ✅ Buildozer安装完成
) else (
    echo ✅ Buildozer已安装
)
echo.

REM 步骤3：检查buildozer.spec
echo ========================================
echo [3/4] 检查配置文件
echo ========================================
echo.
if not exist "buildozer.spec" (
    echo ❌ 错误：未找到buildozer.spec文件
    pause
    exit /b 1
)
echo ✅ buildozer.spec文件存在
echo.

REM 步骤4：选择构建类型
echo ========================================
echo [4/4] 选择构建类型
echo ========================================
echo.
echo 1. Debug版本（调试版，适合测试）
echo 2. Release版本（发布版，适合正式使用）
echo.
set /p build_type="请输入选择 (1或2，默认1): "

if "%build_type%"=="" set build_type=1

echo.
echo ========================================
echo 开始构建APK
echo ========================================
echo.
echo [重要提示]
echo - 首次构建需要下载大量依赖（约500MB-1GB）
echo - 可能需要10-30分钟，请耐心等待
echo - 请确保网络连接正常
echo - 构建过程中请勿关闭此窗口
echo.
echo Android SDK路径：!ANDROID_SDK!
echo.

REM 执行构建
if "%build_type%"=="2" (
    echo 开始构建Release版本...
    set ANDROIDSDK=!ANDROID_SDK! buildozer android release
    if errorlevel 1 (
        goto :build_failed
    )
) else (
    echo 开始构建Debug版本...
    set ANDROIDSDK=!ANDROID_SDK! buildozer android debug
    if errorlevel 1 (
        goto :build_failed
    )
)

REM 构建成功
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
goto :end

:build_failed
echo.
echo ========================================
echo ❌ 构建失败
echo ========================================
echo.
echo 常见问题解决：
echo.
echo 1. Android SDK路径不正确
echo    请确保ANDROID_SDK路径正确
echo    当前路径：!ANDROID_SDK!
echo.
echo 2. Java版本问题
echo    buildozer需要Java 17，请安装Java 17
echo    下载：https://adoptium.net/
echo.
echo 3. 网络问题
echo    检查网络连接，或使用代理
echo.
echo 4. 需要WSL（Windows Subsystem for Linux）
echo    buildozer在Windows上需要WSL环境
echo    如果提示错误，请安装WSL：wsl --install
echo.
pause
exit /b 1

:end
pause

