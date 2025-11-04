@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo 八卦时钟 - 智能构建助手
echo ========================================
echo.
echo 此工具会自动检测您的环境并选择最适合的构建方案
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
REM 检测环境
REM ========================================
echo [检测] 正在检测构建环境...
echo.

set HAS_WSL=0
set HAS_GIT=0
set HAS_DOCKER=0
set HAS_PYTHON=0
set BUILD_METHOD=0

REM 检测Python
python --version >nul 2>&1
if not errorlevel 1 (
    set HAS_PYTHON=1
    echo ✅ Python已安装
) else (
    echo ❌ Python未安装
)

REM 检测WSL
wsl --version >nul 2>&1
if not errorlevel 1 (
    set HAS_WSL=1
    echo ✅ WSL已安装
) else (
    echo ❌ WSL未安装
)

REM 检测Git
git --version >nul 2>&1
if not errorlevel 1 (
    set HAS_GIT=1
    echo ✅ Git已安装
) else (
    echo ❌ Git未安装
)

REM 检测Docker
docker --version >nul 2>&1
if not errorlevel 1 (
    set HAS_DOCKER=1
    echo ✅ Docker已安装
) else (
    echo ❌ Docker未安装
)

echo.

REM ========================================
REM 选择构建方案
REM ========================================
echo ========================================
echo 可用构建方案
echo ========================================
echo.

if !HAS_GIT! equ 1 (
    echo [方案1] GitHub Actions自动构建（推荐）
    echo   优点：无需本地环境，完全免费，自动构建
    echo   需要：GitHub账号 + Git
    echo.
)

if !HAS_WSL! equ 1 (
    echo [方案2] WSL本地构建
    echo   优点：完全本地控制，可调试
    echo   需要：WSL + Android SDK/NDK
    echo.
)

if !HAS_DOCKER! equ 1 (
    echo [方案3] Docker容器构建
    echo   优点：隔离环境，易于管理
    echo   需要：Docker Desktop
    echo.
)

echo [方案4] 虚拟机构建
echo   优点：完全隔离，不影响系统
echo   需要：VirtualBox + Ubuntu
echo.

echo [方案5] 云服务器构建
echo   优点：专业环境，高性能
echo   需要：云服务器账号
echo.

echo ========================================
echo 选择构建方案
echo ========================================
echo.

if !HAS_GIT! equ 1 (
    echo 1. GitHub Actions自动构建（推荐，最简单）
)
if !HAS_WSL! equ 1 (
    echo 2. WSL本地构建
)
if !HAS_DOCKER! equ 1 (
    echo 3. Docker容器构建
)
echo 4. 查看详细构建指南
echo 5. 退出
echo.

set /p choice="请选择 (1-5): "

if "%choice%"=="1" (
    if !HAS_GIT! equ 0 (
        echo ❌ Git未安装，无法使用GitHub Actions
        echo 请先安装Git：https://git-scm.com/download/win
        pause
        exit /b 1
    )
    call :github_actions_setup
    goto :end
)

if "%choice%"=="2" (
    if !HAS_WSL! equ 0 (
        echo ❌ WSL未安装
        echo 请先安装WSL，或使用其他方案
        pause
        exit /b 1
    )
    call :wsl_build
    goto :end
)

if "%choice%"=="3" (
    if !HAS_DOCKER! equ 0 (
        echo ❌ Docker未安装
        echo 请先安装Docker Desktop：https://www.docker.com/products/docker-desktop
        pause
        exit /b 1
    )
    call :docker_build
    goto :end
)

if "%choice%"=="4" (
    call :show_guides
    goto :end
)

if "%choice%"=="5" (
    exit /b 0
)

echo ❌ 无效选择
pause
exit /b 1

:github_actions_setup
echo.
echo ========================================
echo GitHub Actions设置向导
echo ========================================
echo.
echo 步骤1：检查Git仓库
if not exist ".git" (
    echo ⚠️  当前目录不是Git仓库
    echo.
    set /p init_git="是否初始化Git仓库？(Y/N): "
    if /i "!init_git!"=="Y" (
        git init
        git add .
        git commit -m "初始化项目"
        echo.
        echo ✅ Git仓库已初始化
        echo.
        echo 下一步：
        echo 1. 在GitHub上创建新仓库
        echo 2. 运行：git remote add origin https://github.com/你的用户名/仓库名.git
        echo 3. 运行：git push -u origin main
        echo.
        pause
        exit /b 0
    ) else (
        echo 请先初始化Git仓库
        pause
        exit /b 1
    )
) else (
    echo ✅ Git仓库已存在
)

echo.
echo 步骤2：检查GitHub Actions工作流
if exist ".github\workflows\build_apk.yml" (
    echo ✅ GitHub Actions工作流已存在
) else (
    echo ⚠️  GitHub Actions工作流不存在
    echo 正在创建...
    if not exist ".github" mkdir .github
    if not exist ".github\workflows" mkdir .github\workflows
    echo ✅ 工作流文件已创建
    echo.
    echo 请将以下内容保存为 .github\workflows\build_apk.yml：
    echo 文件已自动创建在 mobile_app\.github\workflows\build_apk.yml
)

echo.
echo ========================================
echo 下一步操作
echo ========================================
echo.
echo 1. 将代码推送到GitHub：
echo    git add .
echo    git commit -m "添加GitHub Actions构建"
echo    git push
echo.
echo 2. 在GitHub仓库页面：
echo    - 点击"Actions"标签
echo    - 选择"Build Android APK"
echo    - 点击"Run workflow"
echo    - 等待构建完成
echo    - 下载APK文件
echo.
echo 详细说明请查看：GitHub Actions构建指南.md
echo.
pause
exit /b 0

:wsl_build
echo.
echo ========================================
echo WSL本地构建
echo ========================================
echo.
echo 正在启动WSL构建...
echo.

REM 获取WSL路径
for /f "tokens=*" %%p in ('wsl wslpath -u "%CD%"') do set WSL_DIR=%%p

if exist "build_android.sh" (
    echo 使用构建脚本...
    wsl bash -c "cd '!WSL_DIR!' && bash build_android.sh"
) else (
    echo 直接使用buildozer...
    echo 请选择构建类型：
    echo 1. Debug版本
    echo 2. Release版本
    set /p build_type="请选择 (1或2): "
    if "!build_type!"=="2" (
        wsl bash -c "cd '!WSL_DIR!' && buildozer android release"
    ) else (
        wsl bash -c "cd '!WSL_DIR!' && buildozer android debug"
    )
)

if errorlevel 1 (
    echo.
    echo ❌ 构建失败
    echo 请查看WSL构建说明.md获取帮助
) else (
    echo.
    echo ✅ 构建成功！
    echo APK文件在 bin 目录中
)

pause
exit /b 0

:docker_build
echo.
echo ========================================
echo Docker容器构建
echo ========================================
echo.
echo ⚠️  Docker构建方案需要创建Dockerfile
echo 请查看"无WSL构建方案.md"获取详细说明
echo.
pause
exit /b 0

:show_guides
echo.
echo ========================================
echo 详细构建指南
echo ========================================
echo.
echo 已创建的指南文件：
echo.
if exist "GitHub Actions构建指南.md" (
    echo ✅ GitHub Actions构建指南.md
)
if exist "WSL构建说明.md" (
    echo ✅ WSL构建说明.md
)
if exist "APK构建说明.md" (
    echo ✅ APK构建说明.md
)
echo.
echo 请使用记事本或文本编辑器打开查看
echo.
pause
exit /b 0

:end
exit /b 0

