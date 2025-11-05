# Android SDK 路径配置说明

## 📋 概述

Buildozer 需要 Android SDK 路径才能构建 APK。本指南将帮助您配置 Android SDK 路径。

## 🚀 快速配置（推荐）

### 方法1：使用配置脚本（最简单）

1. **双击运行** `配置AndroidSDK.bat`
2. 脚本会自动：
   - 检测您的 Android SDK 路径（Windows）
   - 转换为 WSL 路径
   - 配置 WSL 环境变量
   - 创建配置文件

3. **验证配置**：
   ```bash
   wsl
   echo $ANDROIDSDK
   ```

### 方法2：手动配置

#### 步骤1：查找 Android SDK 路径

1. 打开 **Android Studio**
2. 点击 **File** → **Settings**（或 **Preferences** on macOS）
3. 导航到 **Appearance & Behavior** → **System Settings** → **Android SDK**
4. 查看 **"Android SDK Location"** 路径

**常见路径：**
- Windows: `C:\Users\YourName\AppData\Local\Android\Sdk`
- macOS: `~/Library/Android/sdk`
- Linux: `~/Android/Sdk`

#### 步骤2：转换为 WSL 路径

如果您在 Windows 上使用 WSL，需要将 Windows 路径转换为 WSL 路径：

**转换规则：**
- `C:\` → `/mnt/c/`
- `D:\` → `/mnt/d/`
- `E:\` → `/mnt/e/`
- 反斜杠 `\` → 正斜杠 `/`

**示例：**
```
Windows: C:\Users\张三\AppData\Local\Android\Sdk
WSL:     /mnt/c/Users/张三/AppData/Local/Android/Sdk
```

#### 步骤3：设置环境变量

在 WSL 终端中运行：

```bash
# 临时设置（仅当前会话有效）
export ANDROIDSDK=/mnt/c/Users/YourName/AppData/Local/Android/Sdk
export ANDROID_HOME=$ANDROIDSDK
export ANDROID_SDK_ROOT=$ANDROIDSDK

# 永久设置（添加到 ~/.bashrc）
echo 'export ANDROIDSDK=/mnt/c/Users/YourName/AppData/Local/Android/Sdk' >> ~/.bashrc
echo 'export ANDROID_HOME=$ANDROIDSDK' >> ~/.bashrc
echo 'export ANDROID_SDK_ROOT=$ANDROIDSDK' >> ~/.bashrc
source ~/.bashrc
```

## ✅ 验证配置

### 方法1：检查环境变量

```bash
wsl
echo $ANDROIDSDK
echo $ANDROID_HOME
```

### 方法2：检查 SDK 文件

```bash
ls $ANDROIDSDK/platform-tools/adb
ls $ANDROIDSDK/build-tools
```

### 方法3：运行构建脚本

运行构建脚本，它会自动检测并验证 SDK 路径：

```bash
cd mobile_app
bash build_android.sh
```

## 🔧 自动检测功能

`build_android.sh` 脚本现在支持自动检测 Android SDK 路径：

1. **检查环境变量**：`ANDROIDSDK`、`ANDROID_HOME`、`ANDROID_SDK_ROOT`
2. **读取配置文件**：`android_sdk_config.txt`（由配置脚本生成）
3. **检查常见路径**：自动检查常见的安装位置
4. **路径转换**：自动将 Windows 路径转换为 WSL 路径

如果自动检测失败，脚本会提供详细的配置说明。

## 📝 配置文件说明

运行 `配置AndroidSDK.bat` 后，会生成 `android_sdk_config.txt` 文件：

```
# Android SDK 路径配置
# Windows 路径：C:\Users\YourName\AppData\Local\Android\Sdk
ANDROID_SDK_WIN=C:\Users\YourName\AppData\Local\Android\Sdk
ANDROID_SDK_WSL=/mnt/c/Users/YourName/AppData/Local/Android/Sdk
```

构建脚本会自动读取此配置文件。

## ⚠️ 常见问题

### 问题1：路径不存在

**错误信息：** `SDK路径不存在`

**解决方法：**
1. 确认 Android SDK 已正确安装
2. 检查路径是否正确（注意大小写和斜杠方向）
3. 如果路径包含空格，使用引号：`export ANDROIDSDK="/mnt/c/Users/Your Name/AppData/Local/Android/Sdk"`

### 问题2：无法访问 Windows 路径

**错误信息：** `WSL路径不存在或不可访问`

**解决方法：**
1. 确保 WSL 已正确安装
2. 检查路径转换是否正确
3. 尝试在 WSL 中手动访问：`ls /mnt/c/Users/...`

### 问题3：adb 命令找不到

**错误信息：** `SDK路径可能不正确（未找到adb）`

**解决方法：**
1. 通过 Android Studio 的 SDK Manager 安装 Platform Tools
2. 确认 `platform-tools` 目录存在：`ls $ANDROIDSDK/platform-tools`

### 问题4：环境变量未生效

**解决方法：**
1. 重新打开 WSL 终端
2. 或运行：`source ~/.bashrc`
3. 验证：`echo $ANDROIDSDK`

## 📚 相关文档

- [本地构建指南.md](./本地构建指南.md)
- [WSL 安装指南.md](./WSL安装指南.md)（如果存在）

## 🆘 获取帮助

如果遇到问题：

1. 运行 `配置AndroidSDK.bat` 查看详细错误信息
2. 检查 Android Studio 中的 SDK 路径
3. 验证 WSL 可以访问 Windows 文件系统
4. 查看构建脚本的详细输出

---

**提示：** 首次配置后，以后构建时会自动使用配置的路径，无需重复配置。

