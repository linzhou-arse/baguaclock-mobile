@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo GitHub Actions 设置向导
echo ========================================
echo.
echo 此脚本将帮助您设置GitHub Actions自动构建
echo.

REM 获取项目根目录
REM 如果脚本在mobile_app目录，则上一级；如果在根目录，则当前目录
cd /d "%~dp0"
if "%CD:~-10%"=="\mobile_app" (
    cd ..
)

echo 当前目录：%CD%
echo.

REM ========================================
REM 步骤1：检查Git
REM ========================================
echo [1/5] 检查Git安装...
git --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Git未安装
    echo.
    echo 请先安装Git：
    echo 1. 下载：https://git-scm.com/download/win
    echo 2. 安装后重启此脚本
    echo.
    pause
    exit /b 1
)
echo ✅ Git已安装
git --version
echo.

REM ========================================
REM 步骤2：检查Git仓库
REM ========================================
echo [2/5] 检查Git仓库...
if not exist ".git" (
    echo ⚠️  当前目录不是Git仓库
    echo.
    set /p init_git="是否初始化Git仓库？(Y/N，默认Y): "
    if /i "!init_git!"=="" set init_git=Y
    if /i "!init_git!"=="Y" (
        echo.
        echo 正在初始化Git仓库...
        git init
        if errorlevel 1 (
            echo ❌ Git初始化失败
            pause
            exit /b 1
        )
        echo ✅ Git仓库已初始化
        echo.
        echo 正在添加文件...
        git add .
        if errorlevel 1 (
            echo ⚠️  警告：部分文件可能未添加
        )
        echo.
        echo 正在创建初始提交...
        git commit -m "初始化项目 - 八卦时钟移动版"
        if errorlevel 1 (
            echo ⚠️  警告：提交可能失败（如果之前已提交）
        ) else (
            echo ✅ 初始提交已创建
        )
    ) else (
        echo 已取消，请手动初始化Git仓库
        echo 运行：git init
        pause
        exit /b 0
    )
) else (
    echo ✅ Git仓库已存在
    echo.
    echo 当前Git状态：
    git status --short
)
echo.

REM ========================================
REM 步骤3：检查GitHub Actions工作流
REM ========================================
echo [3/5] 检查GitHub Actions工作流...
if not exist ".github\workflows\build_apk.yml" (
    echo ⚠️  GitHub Actions工作流不存在
    echo.
    echo 正在创建工作流文件...
    
    REM 创建目录
    if not exist ".github" mkdir ".github"
    if not exist ".github\workflows" mkdir ".github\workflows"
    
    REM 创建工作流文件
    (
        echo name: Build Android APK
        echo.
        echo on:
        echo   workflow_dispatch:
        echo     inputs:
        echo       build_type:
        echo         description: '构建类型'
        echo         required: true
        echo         default: 'debug'
        echo         type: choice
        echo         options:
        echo           - debug
        echo           - release
        echo.
        echo jobs:
        echo   build:
        echo     runs-on: ubuntu-latest
        echo     
        echo     steps:
        echo       - name: Checkout code
        echo         uses: actions/checkout@v4
        echo         with:
        echo           fetch-depth: 0
        echo       
        echo       - name: Set up Python
        echo         uses: actions/setup-python@v4
        echo         with:
        echo           python-version: '3.9'
        echo       
        echo       - name: Install system dependencies
        echo         run: ^|
        echo           sudo apt-get update
        echo           sudo apt-get install -y ^
        echo             python3-pip ^
        echo             python3-dev ^
        echo             build-essential ^
        echo             git ^
        echo             unzip ^
        echo             openjdk-11-jdk ^
        echo             libffi-dev ^
        echo             libssl-dev ^
        echo             zlib1g-dev ^
        echo             libncurses5-dev ^
        echo             libbz2-dev ^
        echo             libreadline-dev ^
        echo             libsqlite3-dev ^
        echo             liblzma-dev
        echo       
        echo       - name: Install buildozer
        echo         run: ^|
        echo           pip3 install --upgrade pip
        echo           pip3 install buildozer
        echo           pip3 install cython
        echo       
        echo       - name: Copy modules
        echo         working-directory: mobile_app
        echo         run: ^|
        echo           python3 copy_modules.py ^|^| echo "模块复制可能有问题，继续构建"
        echo       
        echo       - name: Build APK
        echo         working-directory: mobile_app
        echo         env:
        echo           ANDROIDSDK: ${{ secrets.ANDROIDSDK }}
        echo         run: ^|
        echo           if [ "${{ github.event.inputs.build_type }}" = "release" ]; then
        echo             buildozer android release
        echo           else
        echo             buildozer android debug
        echo           fi
        echo       
        echo       - name: Upload APK
        echo         uses: actions/upload-artifact@v4
        echo         with:
        echo           name: apk-file
        echo           path: mobile_app/bin/*.apk
        echo           retention-days: 30
        echo       
        echo       - name: Upload build log
        echo         if: failure()
        echo         uses: actions/upload-artifact@v4
        echo         with:
        echo           name: build-log
        echo           path: mobile_app/.buildozer/
        echo           retention-days: 7
    ) > ".github\workflows\build_apk.yml"
    
    if exist ".github\workflows\build_apk.yml" (
        echo ✅ GitHub Actions工作流已创建
        echo    文件位置：.github\workflows\build_apk.yml
    ) else (
        echo ❌ 工作流文件创建失败
        pause
        exit /b 1
    )
) else (
    echo ✅ GitHub Actions工作流已存在
    echo    文件位置：.github\workflows\build_apk.yml
)
echo.

REM ========================================
REM 步骤4：添加并提交工作流文件
REM ========================================
echo [4/5] 添加GitHub Actions工作流到Git...
git add .github/workflows/build_apk.yml
if errorlevel 1 (
    echo ⚠️  警告：工作流文件可能已在Git中
) else (
    echo ✅ 工作流文件已添加到Git
)

REM 检查是否有未提交的更改
git diff --cached --quiet
if errorlevel 1 (
    echo.
    echo 正在提交更改...
    git commit -m "添加GitHub Actions自动构建工作流"
    if errorlevel 1 (
        echo ⚠️  警告：提交可能失败
    ) else (
        echo ✅ 更改已提交
    )
) else (
    echo ✅ 所有更改已提交
)
echo.

REM ========================================
REM 步骤5：推送到GitHub
REM ========================================
echo [5/5] 推送到GitHub...
echo.
echo ========================================
echo 下一步操作
echo ========================================
echo.
echo 1. 在GitHub上创建新仓库（如果还没有）：
echo    - 访问：https://github.com/new
echo    - 填写仓库名称（例如：baguaclock-mobile）
echo    - 选择"Public"或"Private"
echo    - 不要勾选"Initialize with README"
echo    - 点击"Create repository"
echo.
echo 2. 添加远程仓库并推送代码：
echo.
echo    方法A：使用HTTPS
echo       git remote add origin https://github.com/你的用户名/仓库名.git
echo       git branch -M main
echo       git push -u origin main
echo.
echo    方法B：使用SSH
echo       git remote add origin git@github.com:你的用户名/仓库名.git
echo       git branch -M main
echo       git push -u origin main
echo.
echo 3. 触发构建：
echo    - 在GitHub仓库页面，点击"Actions"标签
echo    - 选择"Build Android APK"工作流
echo    - 点击"Run workflow"
echo    - 选择构建类型（Debug或Release）
echo    - 点击"Run workflow"按钮
echo.
echo 4. 下载APK：
echo    - 等待构建完成（约10-30分钟）
echo    - 点击构建任务
echo    - 在"Artifacts"部分下载APK文件
echo.
echo ========================================
echo 详细说明
echo ========================================
echo.
echo 完整指南请查看：mobile_app\GitHub Actions构建指南.md
echo.
echo ========================================
set /p push_now="是否现在推送代码到GitHub？(Y/N，默认N): "
if /i "!push_now!"=="Y" (
    echo.
    echo 请输入GitHub仓库URL：
    echo 格式：https://github.com/用户名/仓库名.git
    echo 或：git@github.com:用户名/仓库名.git
    echo.
    set /p repo_url="GitHub仓库URL: "
    if not "!repo_url!"=="" (
        echo.
        echo 正在添加远程仓库...
        git remote remove origin 2>nul
        git remote add origin "!repo_url!"
        if errorlevel 1 (
            echo ❌ 添加远程仓库失败
            echo 请检查URL是否正确
        ) else (
            echo ✅ 远程仓库已添加
            echo.
            echo 正在推送代码...
            git branch -M main 2>nul
            git push -u origin main
            if errorlevel 1 (
                echo.
                echo ⚠️  推送可能失败，常见原因：
                echo 1. 需要先创建GitHub仓库
                echo 2. 需要配置GitHub认证
                echo 3. URL格式错误
                echo.
                echo 请手动执行：
                echo   git remote add origin !repo_url!
                echo   git push -u origin main
            ) else (
                echo.
                echo ✅ 代码已推送到GitHub！
                echo.
                echo 现在可以：
                echo 1. 访问您的GitHub仓库
                echo 2. 点击"Actions"标签
                echo 3. 运行"Build Android APK"工作流
                echo.
            )
        )
    ) else (
        echo 已跳过，请稍后手动推送
    )
)

echo.
echo ========================================
echo 设置完成！
echo ========================================
echo.
echo 如果还未推送代码，请按照上述步骤操作
echo.
pause

