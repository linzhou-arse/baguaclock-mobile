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

# 函数：转换Windows路径为WSL路径
convert_windows_path() {
    local win_path="$1"
    # 转换为小写并替换盘符
    win_path=$(echo "$win_path" | sed 's|^C:|/mnt/c|' | sed 's|^D:|/mnt/d|' | sed 's|^E:|/mnt/e|' | sed 's|^F:|/mnt/f|')
    # 替换反斜杠为正斜杠
    win_path=$(echo "$win_path" | sed 's|\\|/|g')
    echo "$win_path"
}

# 函数：自动检测Android SDK路径
auto_detect_sdk() {
    local sdk_path=""
    
    # 方法1：检查环境变量
    if [ -n "$ANDROIDSDK" ]; then
        echo "$ANDROIDSDK"
        return 0
    fi
    
    if [ -n "$ANDROID_HOME" ]; then
        echo "$ANDROID_HOME"
        return 0
    fi
    
    if [ -n "$ANDROID_SDK_ROOT" ]; then
        echo "$ANDROID_SDK_ROOT"
        return 0
    fi
    
    # 方法2：检查配置文件
    if [ -f "android_sdk_config.txt" ]; then
        local wsl_path=$(grep "^ANDROID_SDK_WSL=" android_sdk_config.txt | cut -d'=' -f2 | tr -d '"' | tr -d "'")
        if [ -n "$wsl_path" ] && [ -d "$wsl_path" ]; then
            echo "$wsl_path"
            return 0
        fi
    fi
    
    # 方法3：检查常见WSL路径
    local common_paths=(
        "$HOME/Android/Sdk"
        "/mnt/c/Users/$USER/AppData/Local/Android/Sdk"
        "/mnt/c/Users/$USER/AppData/Local/Android/Sdk"
    )
    
    for path in "${common_paths[@]}"; do
        if [ -d "$path" ] && [ -f "$path/platform-tools/adb" ]; then
            echo "$path"
            return 0
        fi
    done
    
    # 方法4：尝试从Windows路径转换
    if command -v wslpath >/dev/null 2>&1; then
        # 检查常见的Windows路径
        local win_paths=(
            "$HOME/AppData/Local/Android/Sdk"
            "/mnt/c/Users/$USER/AppData/Local/Android/Sdk"
        )
        
        for win_path in "${win_paths[@]}"; do
            local wsl_path=$(convert_windows_path "$win_path")
            if [ -d "$wsl_path" ] && [ -f "$wsl_path/platform-tools/adb" ]; then
                echo "$wsl_path"
                return 0
            fi
        done
    fi
    
    return 1
}

# 自动检测SDK路径
detected_sdk=$(auto_detect_sdk)

if [ -z "$ANDROIDSDK" ]; then
    if [ -n "$detected_sdk" ]; then
        export ANDROIDSDK="$detected_sdk"
        export ANDROID_HOME="$detected_sdk"
        export ANDROID_SDK_ROOT="$detected_sdk"
        echo "✅ 自动检测到Android SDK: $ANDROIDSDK"
        echo "   （已设置环境变量，仅当前会话有效）"
    else
        echo "⚠️  警告：未设置ANDROIDSDK环境变量且无法自动检测"
        echo
        echo "请选择以下方式之一配置："
        echo
        echo "方式1：使用配置脚本（推荐）"
        echo "  在Windows中运行：配置AndroidSDK.bat"
        echo
        echo "方式2：手动设置环境变量"
        echo "  export ANDROIDSDK=/mnt/c/Users/YourName/AppData/Local/Android/Sdk"
        echo "  export ANDROID_HOME=\$ANDROIDSDK"
        echo "  export ANDROID_SDK_ROOT=\$ANDROIDSDK"
        echo
        echo "方式3：添加到 ~/.bashrc（永久配置）"
        echo "  echo 'export ANDROIDSDK=/mnt/c/Users/YourName/AppData/Local/Android/Sdk' >> ~/.bashrc"
        echo "  echo 'export ANDROID_HOME=\$ANDROIDSDK' >> ~/.bashrc"
        echo "  echo 'export ANDROID_SDK_ROOT=\$ANDROIDSDK' >> ~/.bashrc"
        echo "  source ~/.bashrc"
        echo
        echo "查找Android SDK路径的方法："
        echo "  1. 打开Android Studio"
        echo "  2. File > Settings > Appearance & Behavior > System Settings > Android SDK"
        echo "  3. 查看 'Android SDK Location' 路径"
        echo "  4. 将Windows路径转换为WSL路径："
        echo "     C:\\Users\\... → /mnt/c/Users/..."
        echo
        read -p "是否继续构建？（可能会失败）[y/N]: " continue_build
        if [ "$continue_build" != "y" ] && [ "$continue_build" != "Y" ]; then
            echo "构建已取消"
            exit 1
        fi
    fi
else
    echo "✅ ANDROIDSDK已设置: $ANDROIDSDK"
fi

# 验证SDK路径
if [ -n "$ANDROIDSDK" ]; then
    if [ ! -d "$ANDROIDSDK" ]; then
        echo "⚠️  警告：SDK路径不存在: $ANDROIDSDK"
    elif [ ! -f "$ANDROIDSDK/platform-tools/adb" ]; then
        echo "⚠️  警告：SDK路径可能不正确（未找到adb）: $ANDROIDSDK"
    else
        echo "✅ SDK路径验证通过"
        echo "   platform-tools: $ANDROIDSDK/platform-tools"
    fi
fi

# 检查Java版本（sdkmanager需要Java 17或更高版本）
echo "检查Java版本..."
if [ -z "$JAVA_HOME" ]; then
    # 尝试自动检测Java 17
    if [ -d "/usr/lib/jvm/temurin-17-jdk-amd64" ]; then
        export JAVA_HOME="/usr/lib/jvm/temurin-17-jdk-amd64"
    elif [ -d "/usr/lib/jvm/java-17-openjdk-amd64" ]; then
        export JAVA_HOME="/usr/lib/jvm/java-17-openjdk-amd64"
    elif [ -d "/usr/lib/jvm/java-17" ]; then
        export JAVA_HOME="/usr/lib/jvm/java-17"
    fi
fi

if [ -n "$JAVA_HOME" ]; then
    export PATH="$JAVA_HOME/bin:$PATH"
    JAVA_VERSION=$(java -version 2>&1 | head -n 1 | awk -F '"' '{print $2}' | cut -d'.' -f1)
    if [ -n "$JAVA_VERSION" ] && [ "$JAVA_VERSION" -ge 17 ]; then
        echo "✅ Java版本检查通过：$JAVA_VERSION (JAVA_HOME: $JAVA_HOME)"
    else
        echo "⚠️  警告：Java版本可能过低（需要17+），当前：$JAVA_VERSION"
        echo "   如果构建失败，请安装Java 17："
        echo "   sudo apt-get install openjdk-17-jdk"
    fi
else
    echo "⚠️  警告：未设置JAVA_HOME"
    echo "   建议安装Java 17："
    echo "   sudo apt-get install openjdk-17-jdk"
    echo "   然后设置：export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64"
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
    echo "3. 找不到Java或Java版本过低"
    echo "   解决：安装Java JDK 17或更高版本（sdkmanager需要Java 17）"
    echo "   Ubuntu/Debian: sudo apt-get install openjdk-17-jdk"
    echo "   下载：https://adoptium.net/"
    echo "   设置：export JAVA_HOME=/usr/lib/jvm/java-17-openjdk-amd64"
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
