@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

echo ========================================
echo 重新初始化Git仓库并推送
echo ========================================
echo.

REM 切换到脚本所在目录（项目根目录）
cd /d "%~dp0"
if errorlevel 1 (
    echo ❌ 错误：无法切换到项目目录
    pause
    exit /b 1
)

echo ✅ 当前目录：%CD%
echo.

REM 删除可能存在的错误.git目录
if exist "%USERPROFILE%\.git" (
    echo 正在清理错误的.git目录...
    rd /s /q "%USERPROFILE%\.git" 2>nul
)

REM 初始化Git仓库
echo [1/5] 初始化Git仓库...
if exist ".git" (
    echo ✅ Git仓库已存在
) else (
    git init
    if errorlevel 1 (
        echo ❌ Git初始化失败
        pause
        exit /b 1
    )
    echo ✅ Git仓库初始化成功
)
echo.

REM 配置Git用户信息
echo [2/5] 配置Git用户信息...
git config user.name "八卦时钟开发者"
git config user.email "developer@baguaclock.local"
echo ✅ Git用户信息已配置
echo.

REM 添加远程仓库
echo [3/5] 配置远程仓库...
git remote remove origin 2>nul
git remote add origin https://github.com/linzhou-arse/baguaclock-mobile.git
if errorlevel 1 (
    echo ⚠️  添加远程仓库失败（可能已存在）
) else (
    echo ✅ 远程仓库已配置：https://github.com/linzhou-arse/baguaclock-mobile.git
)
echo.

REM 添加所有文件
echo [4/5] 添加文件到Git...
git add .
if errorlevel 1 (
    echo ⚠️  添加文件时出现问题
) else (
    echo ✅ 文件已添加到暂存区
)
echo.

REM 检查是否有需要提交的更改
git diff --cached --quiet
if errorlevel 1 (
    echo 正在创建提交...
    git commit -m "项目更新：清理冗余文件并优化项目结构"
    if errorlevel 1 (
        echo ⚠️  提交失败
    ) else (
        echo ✅ 提交成功
    )
) else (
    echo ℹ️  没有需要提交的更改
)
echo.

REM 设置主分支
git branch -M main 2>nul
echo.

REM 推送到GitHub
echo [5/5] 推送到GitHub...
echo.
echo [提示] 如果提示需要认证：
echo 1. 输入你的GitHub用户名
echo 2. 输入Personal Access Token（不是密码）
echo    创建Token：https://github.com/settings/tokens
echo    选择"repo"权限
echo.
echo 或者使用GitHub Desktop（更简单）
echo 下载：https://desktop.github.com/
echo.
pause

git push -u origin main

if errorlevel 1 (
    echo.
    echo ❌ 推送失败
    echo.
    echo 常见原因：
    echo 1. 需要GitHub认证（使用Personal Access Token）
    echo 2. 远程仓库不存在或没有权限
    echo 3. 网络连接问题
    echo.
    echo 建议使用GitHub Desktop推送：
    echo 1. 下载：https://desktop.github.com/
    echo 2. 登录GitHub账号
    echo 3. File → Add Local Repository
    echo 4. 选择项目目录：%CD%
    echo 5. 点击"Publish repository"
    echo.
) else (
    echo.
    echo ✅ 推送成功！
    echo.
    echo 现在可以：
    echo 1. 访问仓库：https://github.com/linzhou-arse/baguaclock-mobile
    echo 2. 点击"Actions"标签
    echo 3. 运行"Build Android APK"工作流
    echo.
)

pause

