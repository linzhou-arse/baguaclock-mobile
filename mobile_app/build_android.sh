#!/bin/bash
# Android APK构建脚本（用于WSL/Linux环境）

set -e

echo "=========================================="
echo "八卦时钟移动版 - Android APK构建脚本"
echo "=========================================="
echo

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 检查Python
if ! command -v python3 &> /dev/null; then
    echo "❌ 错误：未找到Python3，请先安装Python 3.9+"
    exit 1
fi

echo "✅ Python已安装"
python3 --version
echo

# 步骤1：复制项目模块
echo "[1/4] 正在复制项目模块..."
if [ -f "copy_modules.py" ]; then
    python3 copy_modules.py
    if [ $? -eq 0 ]; then
        echo "✅ 模块复制完成"
    else
        echo "⚠️  警告：模块复制可能有问题，但继续构建..."
    fi
else
    echo "⚠️  未找到copy_modules.py，跳过此步骤"
fi
echo

# 步骤2：检查buildozer
echo "[2/4] 检查buildozer..."
if ! python3 -c "import buildozer" 2>/dev/null; then
    echo "⚠️  buildozer未安装，正在安装..."
    # Python 3.12需要特殊参数
    python3 -m pip install --break-system-packages buildozer cython
    if [ $? -ne 0 ]; then
        echo "❌ buildozer安装失败"
        echo "请手动运行：python3 -m pip install --break-system-packages buildozer cython"
        exit 1
    fi
    echo "✅ buildozer安装完成"
else
    echo "✅ buildozer已安装"
    # 尝试使用buildozer命令，如果失败则使用python3 -m buildozer
    if command -v buildozer >/dev/null 2>&1; then
        buildozer --version
    else
        export PATH="$HOME/.local/bin:$PATH"
        if command -v buildozer >/dev/null 2>&1; then
            buildozer --version
        else
            python3 -m buildozer --version
        fi
    fi
fi
echo

# 步骤3：检查buildozer.spec
echo "[3/4] 检查buildozer.spec配置文件..."
if [ ! -f "buildozer.spec" ]; then
    echo "❌ 错误：未找到buildozer.spec文件"
    exit 1
fi
echo "✅ buildozer.spec文件存在"
echo

# 步骤4：检查Android SDK环境
echo "[4/4] 检查Android SDK环境..."
if [ -z "$ANDROIDSDK" ]; then
    echo "⚠️  警告：未设置ANDROIDSDK环境变量"
    echo
    echo "如果构建失败，请设置："
    echo "export ANDROIDSDK=~/Android/Sdk"
    echo
    echo "或者添加到 ~/.bashrc："
    echo "echo 'export ANDROIDSDK=~/Android/Sdk' >> ~/.bashrc"
    echo "source ~/.bashrc"
    echo
else
    echo "✅ ANDROIDSDK已设置: $ANDROIDSDK"
fi
echo

# 构建APK
echo "=========================================="
echo "开始构建Android APK"
echo "=========================================="
echo
echo "[重要提示]"
echo "- 首次构建需要下载大量依赖（约500MB-1GB）"
echo "- 可能需要10-30分钟，请耐心等待"
echo "- 请确保网络连接正常"
echo "- 构建过程中请勿关闭此窗口"
echo

# 选择构建类型
build_type=${BUILD_TYPE:-debug}

# 确保能找到buildozer
export PATH="$HOME/.local/bin:$PATH"
BUILDOZER_CMD="buildozer"
if ! command -v buildozer >/dev/null 2>&1; then
    BUILDOZER_CMD="python3 -m buildozer"
fi

if [ "$build_type" = "release" ] || [ "$build_type" = "2" ]; then
    echo
    echo "开始构建Release版本APK..."
    echo "[注意] Release版本需要签名，可能需要更长时间"
    echo
    $BUILDOZER_CMD android release
    build_result=$?
else
    echo
    echo "开始构建Debug版本APK..."
    echo
    $BUILDOZER_CMD android debug
    build_result=$?
fi

if [ $build_result -ne 0 ]; then
    echo
    echo "=========================================="
    echo "❌ 构建失败！"
    echo "=========================================="
    echo
    echo "常见问题及解决方案："
    echo
    echo "1. 找不到Android SDK"
    echo "   解决：安装Android SDK并设置ANDROIDSDK环境变量"
    echo "   下载：https://developer.android.com/studio"
    echo "   设置：export ANDROIDSDK=~/Android/Sdk"
    echo
    echo "2. 找不到NDK"
    echo "   解决：通过Android Studio的SDK Manager安装NDK"
    echo "   路径：Tools > SDK Manager > SDK Tools > NDK"
    echo
    echo "3. 找不到Java"
    echo "   解决：安装Java JDK 11+"
    echo "   Ubuntu/Debian: sudo apt-get install openjdk-11-jdk"
    echo "   下载：https://adoptium.net/"
    echo
    echo "4. 网络问题导致依赖下载失败"
    echo "   解决：检查网络连接，或使用代理"
    echo "   设置代理：export HTTP_PROXY=http://proxy:port"
    echo
    echo "5. 模块导入错误"
    echo "   解决：确保已运行copy_modules.py复制所有模块"
    echo
    exit 1
fi

# 构建成功，查找APK文件
echo
echo "=========================================="
echo "✅ 构建成功！"
echo "=========================================="
echo

apk_files=$(find bin -name "*.apk" 2>/dev/null)
if [ -n "$apk_files" ]; then
    echo "📦 找到APK文件："
    for apk in $apk_files; do
        echo "   $apk"
        ls -lh "$apk" | awk '{print "      文件大小: " $5}'
    done
    echo
    echo "=========================================="
    echo "📱 安装APK到手机"
    echo "=========================================="
    echo
    echo "方法1：USB连接安装（推荐）"
    echo "  1. 在手机上启用"开发者选项"和"USB调试""
    echo "  2. 用USB线连接手机到电脑"
    echo "  3. 运行：adb install $apk_files"
    echo
    echo "方法2：直接传输安装"
    echo "  1. 将APK文件复制到手机"
    echo "  2. 在手机上找到APK文件并点击安装"
    echo "  3. 如果提示"未知来源"，请允许安装"
    echo
else
    echo "⚠️  警告：未在bin目录找到APK文件"
    echo "请检查构建日志，查看是否有错误信息"
fi

echo
echo "=========================================="
echo "构建完成！"
echo "=========================================="
echo
