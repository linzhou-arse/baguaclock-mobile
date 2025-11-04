@echo off
chcp 65001 >nul
echo ========================================
echo 手动启用WSL功能
echo ========================================
echo.
echo 此脚本需要管理员权限运行
echo.
echo 请以管理员身份运行此脚本：
echo 1. 右键点击此文件
echo 2. 选择"以管理员身份运行"
echo.
pause

echo.
echo ========================================
echo 步骤1：启用WSL功能
echo ========================================
echo.
dism.exe /online /enable-feature /featurename:Microsoft-Windows-Subsystem-Linux /all /norestart
if errorlevel 1 (
    echo ❌ 启用WSL功能失败
    echo 请确保以管理员身份运行此脚本
    pause
    exit /b 1
)
echo ✅ WSL功能已启用

echo.
echo ========================================
echo 步骤2：启用虚拟机平台
echo ========================================
echo.
dism.exe /online /enable-feature /featurename:VirtualMachinePlatform /all /norestart
if errorlevel 1 (
    echo ❌ 启用虚拟机平台失败
    echo 请确保以管理员身份运行此脚本
    pause
    exit /b 1
)
echo ✅ 虚拟机平台已启用

echo.
echo ========================================
echo 步骤3：设置WSL 2为默认版本
echo ========================================
echo.
wsl --set-default-version 2
if errorlevel 1 (
    echo ⚠️  设置WSL 2默认版本失败，但可以继续
    echo 这可能是正常的，如果WSL尚未安装
)

echo.
echo ========================================
echo ✅ 功能启用完成
echo ========================================
echo.
echo 重要：请重启电脑后继续
echo.
echo 重启后，请执行以下步骤：
echo 1. 打开Microsoft Store
echo 2. 搜索"Ubuntu"
echo 3. 点击"安装"
echo 4. 安装完成后启动Ubuntu，设置用户名和密码
echo.
echo 或者运行命令：
echo   wsl --install -d Ubuntu
echo.
pause

