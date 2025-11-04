# APK构建说明

## 📍 一键构建APK.bat 位置

**文件位置：**
```
项目根目录/mobile_app/一键构建APK.bat
```

完整路径示例：
```
d:\xianmuweijianjia\py_suanming传统版 - 安卓版\mobile_app\一键构建APK.bat
```

## 🚀 快速开始

### 方法1：一键构建（最简单）

1. **打开文件夹**：进入 `mobile_app` 目录
2. **双击运行**：`一键构建APK.bat`
3. **选择构建类型**：
   - 输入 `1` 构建Debug版本（调试版，适合测试）
   - 输入 `2` 构建Release版本（发布版，适合正式使用）
4. **等待完成**：首次构建需要10-30分钟
5. **获取APK**：在 `bin/` 目录找到APK文件

### 方法2：命令行运行

```batch
cd mobile_app
一键构建APK.bat
```

## 📋 构建前准备

### 必须安装

- ✅ **Python 3.9+** 
  - 下载：https://www.python.org/downloads/
  - 安装时勾选"Add Python to PATH"

- ✅ **Buildozer**
  - 脚本会自动安装
  - 或手动安装：`pip install buildozer`

### 推荐安装（如果构建失败）

- ⚠️ **Android SDK**
  - 下载：https://developer.android.com/studio
  - 安装后设置环境变量：
    ```batch
    set ANDROIDSDK=C:\Users\YourName\AppData\Local\Android\Sdk
    ```

- ⚠️ **Java JDK 11+**
  - 下载：https://adoptium.net/
  - 设置环境变量：`JAVA_HOME`

## 📦 构建结果

### APK文件位置

构建成功后，APK文件在：
```
mobile_app/bin/baguaclock-2.0.0-arm64-v8a-debug.apk
```

### 文件说明

- **Debug版本**：`*-debug.apk` - 包含调试信息，适合测试
- **Release版本**：`*-release.apk` - 优化版本，适合正式发布

## 📱 安装到手机

### 方法1：USB连接安装（推荐）

1. **启用USB调试**：
   - 设置 → 关于手机 → 连续点击"版本号"7次
   - 返回设置 → 开发者选项 → 启用"USB调试"

2. **连接手机**：
   - 用USB线连接手机到电脑
   - 在手机上允许USB调试授权

3. **安装APK**：
   - 双击运行 `install_to_phone.bat`
   - 或手动运行：`adb install bin\*.apk`

### 方法2：直接传输安装

1. **复制APK**：
   - 将 `bin/` 目录下的APK文件复制到手机
   - 可以通过QQ、微信、云盘等方式传输

2. **安装APK**：
   - 在手机上找到APK文件
   - 点击APK文件开始安装
   - 如果提示"未知来源"，请允许安装

3. **允许未知来源**：
   - 设置 → 安全 → 允许安装未知来源应用
   - 或：设置 → 应用 → 特殊权限 → 安装未知应用

## ⚠️ 常见问题

### 问题1：构建失败 - 找不到Android SDK

**解决：**
1. 安装Android Studio：https://developer.android.com/studio
2. 设置环境变量：
   ```batch
   set ANDROIDSDK=C:\Users\YourName\AppData\Local\Android\Sdk
   ```
3. 重新运行构建脚本

### 问题2：构建时间很长

**说明：**
- 首次构建需要下载约500MB-1GB的依赖
- 需要10-30分钟，这是正常的
- 后续构建会快很多（5-10分钟）

### 问题3：模块找不到

**解决：**
1. 确保已运行 `copy_modules.py`
2. 检查 `mobile_app` 目录下是否有以下文件：
   - `sxtwl_adapter.py`
   - `local_mingli_analyzer_unified.py`
   - `classic_analyzer/`
   - `chinese_metaphysics_library/`

### 问题4：网络问题

**解决：**
1. 检查网络连接
2. 使用代理（如果网络受限）：
   ```batch
   set HTTP_PROXY=http://proxy:port
   set HTTPS_PROXY=http://proxy:port
   ```

### 问题5：安装失败

**解决：**
1. 确保手机已启用USB调试
2. 检查USB连接是否正常
3. 尝试卸载旧版本后重新安装
4. 检查手机存储空间是否充足

## ✅ 验证安装

安装完成后：
1. 在手机桌面找到"八卦时钟"应用图标
2. 点击打开应用
3. 测试各个功能：
   - 八字算命
   - 择日分析
   - 风水分析
   - 起名分析

## 🎉 完成！

现在您已经有了可以在手机上安装使用的APK文件！

---

**提示：**
- APK文件可以分享给其他人
- 建议在多个设备上测试
- 如需帮助，查看构建日志或联系技术支持
